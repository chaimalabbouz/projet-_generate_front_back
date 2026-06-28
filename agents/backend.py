import os
import json
import re
from langchain_mistralai import ChatMistralAI
from langchain_core.messages import SystemMessage, HumanMessage
from config.settings import MISTRAL_API_KEY, BACKEND_MODEL, PROMPTS_PATH, GENERATED_PROJECT_PATH
from orchestrator.state import GraphState
 
 
class BackendAgent:
    def __init__(self):
        self.llm = ChatMistralAI(
            api_key=MISTRAL_API_KEY,
            model=BACKEND_MODEL,
            temperature=0.1,
        )
 
        prompt_path = os.path.join(PROMPTS_PATH, "backend.txt")
        with open(prompt_path, "r", encoding="utf-8") as f:
            self.system_prompt_template = f.read()
 
    # =========================
    # MAIN NODE (LANGGRAPH)
    # =========================
    def run(self, state: GraphState) -> GraphState:
        try:
            if not state.task_queue:
                raise ValueError("task_queue is missing from state")
 
            if state.generated_files is None:
                state.generated_files = {}
 
            current_entity = self._get_current_entity(state.task_queue)
 
            if current_entity is None:
                state.workflow_state = "backend_done"
                return state
 
            entity_tasks = self._get_entity_tasks(state.task_queue, current_entity)
 
            for task in entity_tasks:
                # contexte = SPEC des dépendances (pas le code généré),
                # pour que le LLM ne s'aligne jamais sur un fichier pollué
                dependency_context = self._build_dependency_context(
                    task, state.task_queue
                )
 
                code = self._generate_validated_code(task, dependency_context, state)
 
                self._write_file(task["file"], code)
                state.generated_files[task["file"]] = code
                task["status"] = "done"
 
                print(f"  ✓ Generated: {task['file']}")
 
            state.workflow_state = f"entity_done:{current_entity}"
 
        except Exception as e:
            state.workflow_state = "backend_failed"
            state.error_log = (state.error_log or "") + f"\n[BACKEND ERROR] {str(e)}"
 
        return state
 
    # =========================
    # GET CURRENT ENTITY
    # =========================
    def _get_current_entity(self, task_queue: list):
        for task in task_queue:
            if task.get("status") == "pending" and task.get("entity") is not None:
                return task["entity"]
 
        for task in task_queue:
            if task.get("status") == "pending" and task.get("type") == "main":
                return "main"
 
        return None
 
    # =========================
    # GET ENTITY TASKS
    # =========================
    def _get_entity_tasks(self, task_queue: list, entity: str) -> list:
        if entity == "main":
            return [t for t in task_queue if t.get("type") == "main" and t.get("status") == "pending"]
 
        return [
            t for t in task_queue
            if t.get("entity") == entity and t.get("status") == "pending"
        ]
 
    # =========================
    # BUILD DEPENDENCY CONTEXT (SPEC-BASED)
    # =========================
    def _build_dependency_context(self, task: dict, task_queue: list) -> str:
        """
        Injecte la SPEC autoritative des dépendances (champs/schemas tirés de la
        task_queue), et non le code généré. depends_on contient des chemins de
        fichiers (ex: "app/models/category.py").
        """
        depends_on = task.get("depends_on", [])
        if not depends_on:
            return "No dependencies."
 
        # index rapide chemin -> task
        by_file = {t.get("file"): t for t in task_queue}
 
        context_parts = []
        for dep_path in depends_on:
            dep_task = by_file.get(dep_path)
            if not dep_task:
                continue
 
            dep_type = dep_task.get("type")
 
            if dep_type == "model":
                fields = dep_task.get("fields", [])
                field_lines = [
                    f"  - {f['name']}: {f.get('type', '?')}"
                    + (" (PK)" if f.get("primary_key") else "")
                    + (f" (FK -> {f['foreign_key']})" if f.get("foreign_key") else "")
                    for f in fields
                ]
                context_parts.append(
                    f"--- MODEL SPEC: {dep_path} ---\n"
                    f"Entity: {dep_task.get('entity')}\n"
                    f"Columns (EXACT, do not add others):\n" + "\n".join(field_lines)
                )
 
            elif dep_type == "schema":
                schemas = dep_task.get("schemas", [])
                schema_lines = []
                for s in schemas:
                    fnames = ", ".join(fld["name"] for fld in s.get("fields", []))
                    schema_lines.append(f"  {s['name']}({fnames})")
                context_parts.append(
                    f"--- SCHEMA SPEC: {dep_path} ---\n" + "\n".join(schema_lines)
                )
 
        return "\n\n".join(context_parts) if context_parts else "No dependencies found."
 
    # =========================
    # GENERATION + VALIDATION
    # =========================
    def _generate_validated_code(self, task: dict, dependency_context: str, state: GraphState) -> str:
        """
        Génère le code, puis (pour les modèles) valide mécaniquement que les
        colonnes produites correspondent EXACTEMENT à task["fields"].
        Si divergence -> régénère avec un message correctif. Au pire, écrit la
        meilleure version et log l'écart (sans crasher le graphe).
        """
        correction = None
        last_code = ""
 
        for attempt in range(3):
            last_code = self._call_llm(task, dependency_context, correction)
 
            # validation uniquement pour les modèles
            if task.get("type") != "model":
                return last_code
 
            is_valid, message = self._validate_model(last_code, task)
            if is_valid:
                return last_code
 
            correction = (
                "Your previous output did NOT respect the contract. "
                + message
                + " Regenerate the FULL file, using ONLY the columns in task['fields'], "
                "with no relationship(), no back_populates, and no extra columns."
            )
 
        # échec après retries : on garde la meilleure version mais on trace l'écart
        _, final_msg = self._validate_model(last_code, task)
        state.error_log = (state.error_log or "") + (
            f"\n[BACKEND VALIDATION] {task['file']} still diverges from spec: {final_msg}"
        )
        print(f"  ⚠ Validation warning for {task['file']}: {final_msg}")
        return last_code
 
    # =========================
    # VALIDATE MODEL AGAINST SPEC
    # =========================
    def _validate_model(self, code: str, task: dict):
        expected = [f["name"] for f in task.get("fields", [])]
        actual = self._extract_model_columns(code)
 
        extra = [c for c in actual if c not in expected]
        missing = [c for c in expected if c not in actual]
        uses_relationship = ("relationship(" in code) or ("back_populates" in code)
 
        problems = []
        if extra:
            problems.append(f"extra columns not in spec: {extra}")
        if missing:
            problems.append(f"missing columns from spec: {missing}")
        if uses_relationship:
            problems.append("uses forbidden relationship()/back_populates")
 
        if problems:
            return False, "; ".join(problems) + "."
        return True, "ok"
 
    # =========================
    # EXTRACT COLUMN NAMES FROM MODEL CODE
    # =========================
    def _extract_model_columns(self, code: str) -> list:
        # capture les lignes du type:   name = Column( ...
        pattern = re.compile(
            r"^\s*([a-zA-Z_][a-zA-Z0-9_]*)\s*=\s*Column\s*\(",
            re.MULTILINE,
        )
        return [m.group(1) for m in pattern.finditer(code)]
 
    # =========================
    # LLM CALL
    # =========================
    def _call_llm(self, task: dict, dependency_context: str, correction: str = None) -> str:
        system_prompt = self.system_prompt_template.replace(
            "{dependency_context}", dependency_context
        ).replace(
            "{task}", json.dumps(task, indent=2)
        )
 
        human_content = (
            "Generate the Python code now. Return ONLY the Python code, "
            "no explanation, no markdown, no backticks."
        )
        if correction:
            human_content = correction + "\n\n" + human_content
 
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=human_content),
        ]
 
        max_retries = 3
        last_error = None
 
        for attempt in range(max_retries):
            try:
                response = self.llm.invoke(messages)
                return self._clean_code(response.content)
            except Exception as e:
                last_error = e
                continue
 
        raise Exception(f"LLM call failed after 3 retries: {str(last_error)}")
 
    # =========================
    # CLEAN CODE
    # =========================
    def _clean_code(self, text: str) -> str:
        cleaned = re.sub(r"```(?:python)?\s*", "", text)
        cleaned = cleaned.replace("```", "").strip()
        return cleaned
 
    # =========================
    # WRITE FILE
    # =========================
    def _write_file(self, relative_path: str, content: str):
        full_path = os.path.join(GENERATED_PROJECT_PATH, relative_path)
        os.makedirs(os.path.dirname(full_path), exist_ok=True)
        with open(full_path, "w", encoding="utf-8") as f:
            f.write(content)