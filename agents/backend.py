import os
import json
import re
from langchain_mistralai import ChatMistralAI
from langchain_core.messages import SystemMessage, HumanMessage
from config.settings import MISTRAL_API_KEY,BACKEND_MODEL, PROMPTS_PATH, GENERATED_PROJECT_PATH
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
                dependency_context = self._build_dependency_context(
                    task, state.generated_files
                )

                code = self._call_llm(task, dependency_context)

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
    # BUILD DEPENDENCY CONTEXT
    # =========================
    def _build_dependency_context(self, task: dict, generated_files: dict) -> str:
        depends_on = task.get("depends_on", [])

        if not depends_on:
            return "No dependencies."

        context_parts = []

        for dep_entity in depends_on:
            dep_entity_lower = dep_entity.lower()

            dep_files = {
                "model": f"app/models/{dep_entity_lower}.py",
                "schema": f"app/schemas/{dep_entity_lower}.py",
            }

            for dep_type, dep_path in dep_files.items():
                if dep_path in generated_files:
                    context_parts.append(
                        f"--- {dep_path} ---\n{generated_files[dep_path]}"
                    )

        return "\n\n".join(context_parts) if context_parts else "No dependencies found."

    # =========================
    # LLM CALL
    # =========================
    def _call_llm(self, task: dict, dependency_context: str) -> str:
        system_prompt = self.system_prompt_template.replace(
            "{dependency_context}", dependency_context
        ).replace(
            "{task}", json.dumps(task, indent=2)
        )

        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content="Generate the Python code now. Return ONLY the Python code, no explanation, no markdown, no backticks.")
        ]

        max_retries = 3
        last_error = None

        for attempt in range(max_retries):
            try:
                response = self.llm.invoke(messages)
                raw_output = response.content
                return self._clean_code(raw_output)

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