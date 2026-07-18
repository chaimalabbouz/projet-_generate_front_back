import os
import json
from langchain_mistralai import ChatMistralAI
from langchain_core.tools import tool
from langgraph.prebuilt import create_react_agent
from shared.settings import MISTRAL_API_KEY,  GENERATED_PROJECT_PATH
from shared.state import GraphState
PROMPTS_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "prompts")
FIXER_MODEL = "devstral-latest"

# =========================
# SKILLS PATH
# =========================
# Le dossier skills/ est dans prompts/skills/
SKILLS_PATH = os.path.join(PROMPTS_PATH, "skills")
SKILLS_ENTRIES_PATH = os.path.join(SKILLS_PATH, "entries")


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


@tool
def read_skill(skill_name: str) -> str:
    """
    Read a specific skill entry from the skills catalog.
    Only use this AFTER consulting the index and identifying a matching skill.

    Args:
        skill_name: The name of the skill file WITHOUT extension.
                    Example: 'none_required_shadowing' (not 'none_required_shadowing.md').
    """
    # Nettoie le nom au cas où le LLM ajoute .md ou un chemin
    clean_name = skill_name.strip().replace(".md", "").replace("entries/", "").replace("\\", "/").split("/")[-1]
    skill_path = os.path.join(SKILLS_ENTRIES_PATH, f"{clean_name}.md")

    if not os.path.exists(skill_path):
        available = []
        if os.path.exists(SKILLS_ENTRIES_PATH):
            available = [f.replace(".md", "") for f in os.listdir(SKILLS_ENTRIES_PATH) if f.endswith(".md")]
        return (
            f"Skill '{clean_name}' not found in the catalog.\n"
            f"Available skills: {', '.join(available)}"
        )

    with open(skill_path, "r", encoding="utf-8") as f:
        return f.read()


class FixerAgent:
    def __init__(self):
        self.llm = ChatMistralAI(
            api_key=MISTRAL_API_KEY,
            model=FIXER_MODEL,
            temperature=0.1,
        )

        # Prompt principal du fixer
        prompt_path = os.path.join(PROMPTS_PATH, "fixer.txt")
        with open(prompt_path, "r", encoding="utf-8") as f:
            self.system_prompt = f.read()

        # Charge le protocole (README.md du dossier skills)
        skills_readme_path = os.path.join(SKILLS_PATH, "README.md")
        with open(skills_readme_path, "r", encoding="utf-8") as f:
            self.skills_protocol = f.read()

        # Charge l'index (envoyé à chaque appel)
        skills_index_path = os.path.join(SKILLS_PATH, "index.md")
        with open(skills_index_path, "r", encoding="utf-8") as f:
            self.skills_index = f.read()

        # Ajout de l'outil read_skill
        self.tools = [read_file, write_file, list_entity_files, read_skill]

        self.agent = create_react_agent(
            model=self.llm,
            tools=self.tools,
        )

    # =========================
    # MAIN NODE (LANGGRAPH)
    # =========================
    def run(self, state: GraphState) -> GraphState:
        try:
            current_entity = self._get_failed_entity(state.task_queue, state.abandoned_entities)

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

═══════════════════════════════════════
SKILLS PROTOCOL (MANDATORY — read carefully)
═══════════════════════════════════════
{self.skills_protocol}

═══════════════════════════════════════
SKILLS INDEX (bug catalog — consult BEFORE any diagnosis)
═══════════════════════════════════════
{self.skills_index}

═══════════════════════════════════════
ENTITY TO FIX: {current_entity}
═══════════════════════════════════════

AUTHORITATIVE SPEC (source of truth — the code MUST match this)
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

═══════════════════════════════════════
MANDATORY PROCEDURE (follow in order, no exception)
═══════════════════════════════════════
STEP 1 — Extract the literal error message from the ERROR OUTPUT above
         (exception type, exact message, file, line).

STEP 2 — Consult the SKILLS INDEX above. For each entry, explicitly state:
         "entry <X>: matches / does not match — reason".
         This step is MANDATORY even if you think you know the answer.

STEP 3 — Decide the match result:
         - Clear match → announce the entry, go to STEP 4.
         - Partial match → announce your hesitation, go to STEP 4 with the best candidate.
         - No match → announce "no skill entry matches", proceed with normal reasoning.

STEP 4 — If a skill matched, call read_skill("<skill_name>") to read the FULL detail.
         Read ALL sections: Symptom, Context, Root cause, Fix, Anti-fixes, Confirmation.

STEP 5 — Use your tools to gather context:
         - list_entity_files("{current_entity}") to see the files
         - read_file(...) to read the relevant application files
           (route + service if the skill suggests an inter-file bug; read the test too)

STEP 6 — Before writing anything, verbalize your diagnosis in this exact format:
         > Diagnostic: The error <message> matches skill <name>.
         > Root cause: <one sentence summary>.
         > Fix applied: <precise action> in <file>.
         > Anti-fixes respected: <list what the skill forbids and you are NOT doing>.

STEP 7 — Apply the fix using write_file. ONLY modify application files
         (app/models, app/schemas, app/services, app/routes).
"""

            result = self.agent.invoke({
                "messages": [{"role": "user", "content": prompt}]
            })

            for message in result["messages"]:
                if hasattr(message, "tool_calls") and message.tool_calls:
                    for tool_call in message.tool_calls:
                        if tool_call["name"] == "write_file":
                            path = tool_call["args"]["path"]
                            normalized = path.replace("\\", "/").lstrip("/")
                            if normalized.startswith("tests/") or "/tests/" in normalized:
                                print(f"  ⛔ Ignored test write attempt: {path}")
                                continue
                            content = tool_call["args"]["content"]
                            state.generated_files[path] = content
                            print(f"  🔧 Fixed: {path}")
                        elif tool_call["name"] == "read_skill":
                            skill_name = tool_call["args"].get("skill_name", "?")
                            print(f"  📖 Consulted skill: {skill_name}")

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
    def _get_failed_entity(self, task_queue: list, abandoned: list = None) -> str:
        abandoned = abandoned or []
        for task in task_queue:
            if (task.get("type") == "route"
                    and task.get("test_status") == "failed"
                    and task.get("entity") not in abandoned):
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

        model_fields = self._get_model_fields(entity, task_queue)
        if model_fields:
            lines = [self._fmt_field(f) for f in model_fields]
            parts.append(f"--- {entity} MODEL columns (EXACT) ---\n" + "\n".join(lines))

        schemas = self._get_schemas(entity, task_queue)
        for s in schemas:
            fnames = ", ".join(fld["name"] for fld in s.get("fields", []))
            parts.append(f"--- {entity} SCHEMA {s.get('name')} ---\n  {fnames}")

        svc = self._get_service_functions(entity, task_queue)
        if svc:
            svc_lines = []
            for fn in svc:
                params = ", ".join(
                    f"{p['name']}: {p.get('type', '?')}" for p in fn.get("input_parameters", [])
                )
                svc_lines.append(f"  {fn['name']}({params}) -> {fn.get('output_type', '?')}")
            parts.append(f"--- {entity} SERVICE functions (expected signatures) ---\n" + "\n".join(svc_lines))

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