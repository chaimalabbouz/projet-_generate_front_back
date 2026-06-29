import os
import re
import json

from langchain_mistralai import ChatMistralAI
from langchain_core.tools import tool
from langgraph.prebuilt import create_react_agent

from config.settings import MISTRAL_API_KEY, PROMPTS_PATH, GENERATED_PROJECT_PATH
from orchestrator.state import GraphState
from agents.api_client_node import ApiClientGenerator

BINDING_MODEL = "devstral-latest"

# Frontend root inside the generated project.
FRONTEND_ROOT = os.path.join(GENERATED_PROJECT_PATH, "frontend")


# =========================================================================
# PAGE_CONTEXT  (manual for now — describes the relation between pages so the
# agent knows whether a page needs an id and which one. Later this can be
# auto-derived from the Figma prototype. Keep the SAME shape when you do.)
# =========================================================================
PAGE_CONTEXT = {
    "Homepage.jsx": {
        "shows": "Category",        # les cards sont des catégories
        "needs_id": None,           # page d'accueil, ne reçoit aucun id
        "from": None,
        "navigate_to": {
            "target": "Products.jsx",   # un clic sur une catégorie mène ici
            "passes": "category_id"     # en passant l'id de la catégorie cliquée
        }
    },
    "Products.jsx": {
        "shows": "Product",         # affiche les produits
        "needs_id": "category_id",  # reçoit l'id de catégorie depuis Homepage
        "from": "Homepage.jsx",
        "navigate_to": {
            "target": "ProductDescription.jsx",
            "passes": "product_id"
        }
    },
    "ProductDescription.jsx": {
        "shows": "Product",         # affiche UN produit en détail
        "needs_id": "product_id",   # reçoit l'id du produit cliqué
        "from": "Products.jsx",
        "navigate_to": None         # page finale, ne navigue plus
    },
}


# =========================================================================
# Module-level context injected at run() time (mirrors the fixer's pattern).
# Tools are module-level, so they read these globals.
# =========================================================================
_SPEC = {}                  # state.openapi_spec
_API_FUNCTIONS_TEXT = ""    # cached human-readable list of available API functions


# =========================================================================
# LAYOUT GUARDRAIL
# The agent may rename tags (div -> input) and inject values ({product.name}),
# but must NEVER introduce a className that was not already in the page.
# That single invariant catches any restyling / layout tampering.
# =========================================================================
def _extract_classnames(code: str) -> set:
    classes = set()
    # className="...."
    for m in re.findall(r'className\s*=\s*"([^"]*)"', code):
        classes.add(m.strip())
    # className={`....`}
    for m in re.findall(r'className\s*=\s*\{`([^`]*)`\}', code):
        classes.add(m.strip())
    return classes


def _layout_violations(original: str, new: str) -> set:
    """className values present in `new` but absent from `original` (= tampering)."""
    return _extract_classnames(new) - _extract_classnames(original)


# =========================================================================
# TOOLS
# =========================================================================
@tool
def list_entities() -> str:
    """
    List the backend entities and the API client functions available to call.
    Use this to discover what real data exists. If a page corresponds to none
    of these, do NOT bind it.
    """
    return _API_FUNCTIONS_TEXT or "No entities available."


@tool
def get_entity_schema(name: str) -> str:
    """
    Return the exact fields (and types) of one entity, so you only bind fields
    that really exist. NEVER use a field that is not listed here.
    """
    schemas = _SPEC.get("components", {}).get("schemas", {})
    # accept "Product" or "ProductCreate"
    candidates = [name, name.capitalize(), f"{name}Create"]
    for cand in candidates:
        if cand in schemas:
            props = schemas[cand].get("properties", {})
            lines = [f"{cand}:"]
            for field, prop in props.items():
                t = prop.get("type", prop.get("$ref", "?"))
                lines.append(f"  - {field}: {t}")
            return "\n".join(lines)
    available = ", ".join(schemas.keys())
    return f"Entity '{name}' not found. Available: {available}"


@tool
def read_page(path: str) -> str:
    """Read a frontend file (e.g. 'src/pages/Homepage.jsx'). Read-only."""
    full = os.path.join(FRONTEND_ROOT, path.replace("\\", "/").lstrip("/"))
    if os.path.exists(full):
        with open(full, "r", encoding="utf-8") as f:
            return f.read()
    return f"File not found: {path}"


@tool
def write_page(path: str, content: str) -> str:
    """
    Write the bound version of a frontend page. The write is REFUSED if it
    introduces any className that was not in the original page (layout must be
    preserved — you may only rename tags and inject data values, never restyle).
    Only files under src/pages or src/components can be written.
    """
    normalized = path.replace("\\", "/").lstrip("/")
    if not (normalized.startswith("src/pages/") or normalized.startswith("src/components/")):
        return f"REFUSED: '{path}' is outside src/pages or src/components."
    if not normalized.endswith((".jsx", ".tsx")):
        return f"REFUSED: '{path}' is not a .jsx/.tsx page."

    full = os.path.join(FRONTEND_ROOT, normalized)
    original = ""
    if os.path.exists(full):
        with open(full, "r", encoding="utf-8") as f:
            original = f.read()

    violations = _layout_violations(original, content)
    if violations:
        sample = ", ".join(list(violations)[:3])
        return (
            "REFUSED: layout would change. You introduced className values that "
            f"were not in the original page (e.g.: {sample}). Do NOT modify or add "
            "any className/styles. Only rename tags and inject data values, then "
            "write again."
        )

    os.makedirs(os.path.dirname(full), exist_ok=True)
    with open(full, "w", encoding="utf-8") as f:
        f.write(content)
    return f"Page written successfully: {path}"


class BindingAgent:
    def __init__(self):
        self.llm = ChatMistralAI(
            api_key=MISTRAL_API_KEY,
            model=BINDING_MODEL,
            temperature=0.1,
        )

        prompt_path = os.path.join(PROMPTS_PATH, "binding.txt")
        with open(prompt_path, "r", encoding="utf-8") as f:
            self.system_prompt = f.read()

        self.tools = [list_entities, get_entity_schema, read_page, write_page]
        self.agent = create_react_agent(model=self.llm, tools=self.tools)

    # =========================
    # MAIN NODE (LANGGRAPH)
    # =========================
    def run(self, state: GraphState) -> GraphState:
        global _SPEC, _API_FUNCTIONS_TEXT
        try:
            if not state.openapi_spec:
                raise ValueError("openapi_spec is missing from state")

            # inject context for the module-level tools
            _SPEC = state.openapi_spec
            _API_FUNCTIONS_TEXT = self._build_api_functions_text(state.openapi_spec)

            pages = self._list_pages()
            if not pages:
                state.workflow_state = "binding_no_pages"
                return state

            if state.frontend_pages is None:
                state.frontend_pages = {}

            for page_rel in pages:
                page_name = os.path.basename(page_rel)
                ctx = PAGE_CONTEXT.get(page_name, {})
                prompt = self._build_prompt(page_rel, page_name, ctx)

                result = self.agent.invoke({
                    "messages": [{"role": "user", "content": prompt}]
                })

                # record successful writes (the tool already enforced the guardrail)
                for message in result["messages"]:
                    if hasattr(message, "tool_calls") and message.tool_calls:
                        for tc in message.tool_calls:
                            if tc["name"] == "write_page":
                                wpath = tc["args"].get("path", "")
                                wcontent = tc["args"].get("content", "")
                                norm = wpath.replace("\\", "/").lstrip("/")
                                # only reflect writes that the guardrail would accept
                                full = os.path.join(FRONTEND_ROOT, norm)
                                original = ""
                                if os.path.exists(full):
                                    with open(full, "r", encoding="utf-8") as f:
                                        original = f.read()
                                if not _layout_violations(original, wcontent):
                                    state.frontend_pages[norm] = wcontent
                                    print(f"  \U0001f517 Bound: {norm}")

            state.workflow_state = "binding_done"

        except Exception as e:
            state.workflow_state = "binding_error"
            state.error_log = (state.error_log or "") + f"\n[BINDING ERROR] {str(e)}"

        return state

    # =========================
    # HELPERS
    # =========================
    def _list_pages(self) -> list:
        pages_dir = os.path.join(FRONTEND_ROOT, "src", "pages")
        if not os.path.isdir(pages_dir):
            return []
        out = []
        for fname in os.listdir(pages_dir):
            if fname.endswith((".jsx", ".tsx")):
                out.append(f"src/pages/{fname}")
        return sorted(out)

    def _build_api_functions_text(self, spec: dict) -> str:
        """Human-readable catalogue of callable functions, grouped by entity."""
        gen = ApiClientGenerator(spec)
        lines = []
        for path, methods in gen.paths.items():
            for method, op in methods.items():
                if method.lower() not in ("get", "post", "put", "patch", "delete"):
                    continue
                op_id = op.get("operationId")
                if not op_id:
                    continue
                ret = gen._success_response_type(op)
                body = gen._body_type(op)
                params = [p["name"] for p in op.get("parameters", []) if p.get("in") == "path"]
                sig_args = ", ".join(params + (["data"] if body else []))
                from agents.api_client_node import _camel
                lines.append(f"  {_camel(op_id)}({sig_args}) -> {ret}")
        return "Available API functions (import from '../api/client'):\n" + "\n".join(lines)

    def _build_prompt(self, page_rel: str, page_name: str, ctx: dict) -> str:
        ctx_text = json.dumps(ctx, indent=2) if ctx else "(no navigation context for this page)"
        return f"""{self.system_prompt}

PAGE TO PROCESS: {page_rel}

PAGE NAVIGATION CONTEXT (from PAGE_CONTEXT):
{ctx_text}

STEPS:
1. read_page("{page_rel}") to see the current static page.
2. Decide if this page is meant to display real data of a backend entity.
   - Call list_entities() to see what exists.
   - If NOTHING matches (decorative page, lorem ipsum, static marketing), DO NOT
     write anything. Leave the page untouched and stop.
3. If it matches an entity:
   - get_entity_schema(<Entity>) to know the exact fields.
   - Use the navigation context to choose the right function (list vs by-id).
   - Inject the data into the EXISTING elements. You may change a tag's TYPE
     when needed (a static text div meant for input -> <input>), but you must
     keep every className and style byte-for-byte identical.
   - Wire navigation with the real id where applicable.
4. write_page(...) with the result. If the write is refused for layout reasons,
   you changed a className — revert that and write again.
"""