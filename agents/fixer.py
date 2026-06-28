import os
import json
from langchain_mistralai import ChatMistralAI
from langchain_core.tools import tool
from langgraph.prebuilt import create_react_agent
from config.settings import MISTRAL_API_KEY, PROMPTS_PATH, GENERATED_PROJECT_PATH
from orchestrator.state import GraphState

FIXER_MODEL = "devstral-latest"


# =========================
# TOOLS
# =========================
@tool
def read_file(path: str) -> str:
    """Read a file from the generated project directory (including test files, read-only)."""
    full_path = os.path.join(GENERATED_PROJECT_PATH, path)
    if os.path.exists(full_path):
        with open(full_path, "r", encoding="utf-8") as f:
            return f.read()
    return f"File not found: {path}"


@tool
def write_file(path: str, content: str) -> str:
    """
    Write fixed code to an APPLICATION file (models / schemas / services / routes).
    Test files are READ-ONLY: any write under 'tests/' is refused.
    """
    normalized = path.replace("\\", "/").lstrip("/")
    if normalized.startswith("tests/") or "/tests/" in normalized:
        return (
            f"REFUSED: '{path}' is a test file. Tests are the source of truth and "
            f"cannot be modified. Fix the application code instead "
            f"(app/models, app/schemas, app/services, app/routes)."
        )

    full_path = os.path.join(GENERATED_PROJECT_PATH, path)
    os.makedirs(os.path.dirname(full_path), exist_ok=True)
    with open(full_path, "w", encoding="utf-8") as f:
        f.write(content)
    return f"File written successfully: {path}"


@tool
def list_entity_files(entity: str) -> str:
    """List all files related to an entity. The test file is read-only (do not write it)."""
    entity_lower = entity.lower()
    app_files = [
        f"app/models/{entity_lower}.py",
        f"app/schemas/{entity_lower}.py",
        f"app/services/{entity_lower}.py",
        f"app/routes/{entity_lower}.py",
    ]
    test_file = f"tests/test_{entity_lower}.py"

    result = []
    for f in app_files:
        full_path = os.path.join(GENERATED_PROJECT_PATH, f)
        exists = "EXISTS" if os.path.exists(full_path) else "NOT FOUND"
        result.append(f"{f} → {exists} (writable)")

    full_test = os.path.join(GENERATED_PROJECT_PATH, test_file)
    test_exists = "EXISTS" if os.path.exists(full_test) else "NOT FOUND"
    result.append(f"{test_file} → {test_exists} (READ-ONLY, do not modify)")

    return "\n".join(result)


class FixerAgent:
    def __init__(self):
        self.llm = ChatMistralAI(
            api_key=MISTRAL_API_KEY,
            model=FIXER_MODEL,
            temperature=0.1,
        )

        prompt_path = os.path.join(PROMPTS_PATH, "fixer.txt")
        with open(prompt_path, "r", encoding="utf-8") as f:
            self.system_prompt = f.read()

        self.tools = [read_file, write_file, list_entity_files]

        self.agent = create_react_agent(
            model=self.llm,
            tools=self.tools,
        )

    # =========================
    # MAIN NODE (LANGGRAPH)
    # =========================
    def run(self, state: GraphState) -> GraphState:
        try:
            current_entity = self._get_failed_entity(state.task_queue)

            if current_entity is None:
                state.workflow_state = "fixer_done"
                return state

            if state.retry_count >= state.max_retries:
                state.workflow_state = "fixer_max_retries"
                state.error_log = (state.error_log or "") + f"\n[FIXER] Max retries reached for {current_entity}"
                return state

            error_output = self._get_error_output(current_entity, state.test_results)

            # SPEC autoritative (entité + dépendances) tirée de la task_queue
            spec_context = self._build_spec_context(
                current_entity, state.task_queue, state.dependency_graph
            )

            prompt = f"""{self.system_prompt}

ENTITY TO FIX: {current_entity}

═══════════════════════════════════════
AUTHORITATIVE SPEC (source of truth — the code MUST match this)
═══════════════════════════════════════
{spec_context}

═══════════════════════════════════════
RULES FOR THIS FIX
═══════════════════════════════════════
- The test file is the source of truth and is READ-ONLY. NEVER write to tests/.
- Fix the APPLICATION code so it conforms to the SPEC above and passes the test.
- NEVER modify a file in a way that diverges from the SPEC (no invented columns,
  no relationship(), no back_populates).
- If a name is used but not imported (e.g. Optional, List, date), add the import.

═══════════════════════════════════════
ERROR OUTPUT
═══════════════════════════════════════
{error_output}

Use your tools to:
1. List the entity files with list_entity_files("{current_entity}")
2. Read each file with read_file (read the test file too, to understand expectations)
3. Analyze the error and identify which APPLICATION file is wrong
4. Write ONLY the application files that need fixing with write_file
"""

            result = self.agent.invoke({
                "messages": [{"role": "user", "content": prompt}]
            })

            for message in result["messages"]:
                if hasattr(message, "tool_calls") and message.tool_calls:
                    for tool_call in message.tool_calls:
                        if tool_call["name"] == "write_file":
                            path = tool_call["args"]["path"]
                            # ne pas refléter dans le state une écriture qui a été refusée
                            normalized = path.replace("\\", "/").lstrip("/")
                            if normalized.startswith("tests/") or "/tests/" in normalized:
                                print(f"  ⛔ Ignored test write attempt: {path}")
                                continue
                            content = tool_call["args"]["content"]
                            state.generated_files[path] = content
                            print(f"  🔧 Fixed: {path}")

            # remettre l'entité en test (le tester ne régénère pas, il relance pytest)
            new_task_queue = []
            for task in state.task_queue:
                if task.get("entity") == current_entity and task.get("type") == "route":
                    task = dict(task)
                    task["test_status"] = "pending"
                new_task_queue.append(task)
            state.task_queue = new_task_queue

            state.retry_count += 1
            state.workflow_state = f"fixer_done:{current_entity}"

        except Exception as e:
            state.workflow_state = "fixer_error"
            state.error_log = (state.error_log or "") + f"\n[FIXER ERROR] {str(e)}"

        return state

    # =========================
    # GET FAILED ENTITY
    # =========================
    def _get_failed_entity(self, task_queue: list) -> str:
        for task in task_queue:
            if task.get("type") == "route" and task.get("test_status") == "failed":
                return task.get("entity")
        return None

    # =========================
    # GET ERROR OUTPUT
    # =========================
    def _get_error_output(self, entity: str, test_results: dict) -> str:
        if test_results and entity in test_results:
            return test_results[entity].get("output", "No error output available")
        return "No error output available"

    # =========================
    # BUILD SPEC CONTEXT (source de vérité = task_queue)
    # =========================
    def _build_spec_context(self, entity: str, task_queue: list, dependency_graph: dict) -> str:
        parts = []

        # entité courante : modèle + schémas
        model_fields = self._get_model_fields(entity, task_queue)
        if model_fields:
            lines = [self._fmt_field(f) for f in model_fields]
            parts.append(f"--- {entity} MODEL columns (EXACT) ---\n" + "\n".join(lines))

        schemas = self._get_schemas(entity, task_queue)
        for s in schemas:
            fnames = ", ".join(fld["name"] for fld in s.get("fields", []))
            parts.append(f"--- {entity} SCHEMA {s.get('name')} ---\n  {fnames}")

        # fonctions de service (signatures attendues)
        svc = self._get_service_functions(entity, task_queue)
        if svc:
            svc_lines = []
            for fn in svc:
                params = ", ".join(
                    f"{p['name']}: {p.get('type', '?')}" for p in fn.get("input_parameters", [])
                )
                svc_lines.append(f"  {fn['name']}({params}) -> {fn.get('output_type', '?')}")
            parts.append(f"--- {entity} SERVICE functions (expected signatures) ---\n" + "\n".join(svc_lines))

        # dépendances : modèle
        deps = []
        if dependency_graph and entity in dependency_graph:
            deps = dependency_graph.get(entity, []) or []
        for dep in deps:
            dep_fields = self._get_model_fields(dep, task_queue)
            if dep_fields:
                lines = [self._fmt_field(f) for f in dep_fields]
                parts.append(f"--- DEPENDENCY {dep} MODEL columns (EXACT) ---\n" + "\n".join(lines))

        return "\n\n".join(parts) if parts else "No spec available."

    def _fmt_field(self, f: dict) -> str:
        extra = ""
        if f.get("primary_key"):
            extra += " (PK, auto)"
        if f.get("foreign_key"):
            extra += f" (FK -> {f['foreign_key']})"
        if f.get("nullable") is False:
            extra += " (required)"
        return f"  - {f['name']}: {f.get('type', '?')}{extra}"

    def _get_model_fields(self, entity: str, task_queue: list) -> list:
        for task in task_queue:
            if task.get("entity") == entity and task.get("type") == "model":
                return task.get("fields", [])
        return []

    def _get_schemas(self, entity: str, task_queue: list) -> list:
        for task in task_queue:
            if task.get("entity") == entity and task.get("type") == "schema":
                return task.get("schemas", [])
        return []

    def _get_service_functions(self, entity: str, task_queue: list) -> list:
        for task in task_queue:
            if task.get("entity") == entity and task.get("type") == "service":
                return task.get("functions", [])
        return []