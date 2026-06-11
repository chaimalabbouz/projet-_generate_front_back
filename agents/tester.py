import os
import json
import re
import subprocess
from langchain_mistralai import ChatMistralAI
from langchain_core.messages import SystemMessage, HumanMessage
from config.settings import MISTRAL_API_KEY,TESTER_MODEL, PROMPTS_PATH, GENERATED_PROJECT_PATH
from orchestrator.state import GraphState




class TesterAgent:
    def __init__(self):
        self.llm = ChatMistralAI(
            api_key=MISTRAL_API_KEY,
            model=TESTER_MODEL,
            temperature=0.1,
        )

        prompt_path = os.path.join(PROMPTS_PATH, "tester.txt")
        with open(prompt_path, "r", encoding="utf-8") as f:
            self.system_prompt_template = f.read()

    # =========================
    # MAIN NODE (LANGGRAPH)
    # =========================
    def run(self, state: GraphState) -> GraphState:
        try:
            current_entity = self._get_current_entity(state.task_queue)

            if current_entity is None:
                state.workflow_state = "testing_done"
                return state

            entity_context = self._build_entity_context(
                current_entity, state.generated_files
            )

            endpoints = self._get_entity_endpoints(
                current_entity, state.task_queue
            )

            test_code = self._call_llm(current_entity, entity_context, endpoints)

            test_file = f"tests/test_{current_entity.lower()}.py"
            self._write_file(test_file, test_code)

            test_result = self._run_pytest(test_file)

            if state.test_results is None:
                state.test_results = {}

            state.test_results[current_entity] = test_result

            # mettre a jour test_status dans la task_queue
            new_task_queue = []
            for task in state.task_queue:
                if task.get("entity") == current_entity and task.get("type") == "route":
                    task = dict(task)
                    task["test_status"] = "passed" if test_result["status"] == "passed" else "failed"
                new_task_queue.append(task)
            state.task_queue = new_task_queue

            if test_result["status"] == "passed":
                state.workflow_state = f"testing_passed:{current_entity}"
                print(f"  ✓ Tests passed for {current_entity}")
            else:
                state.workflow_state = f"testing_failed:{current_entity}"
                state.error_log = (state.error_log or "") + f"\n[TEST ERROR] {current_entity}:\n{test_result['output']}"
                print(f"  ✗ Tests failed for {current_entity}")

        except Exception as e:
            state.workflow_state = "testing_error"
            state.error_log = (state.error_log or "") + f"\n[TESTER ERROR] {str(e)}"

        return state

    # =========================
    # GET CURRENT ENTITY
    # =========================
    def _get_current_entity(self, task_queue: list) -> str:
        for task in task_queue:
            if (
                task.get("type") == "route"
                and task.get("status") == "done"
                and task.get("test_status") == "pending"
            ):
                return task.get("entity")
        return None

    # =========================
    # BUILD ENTITY CONTEXT
    # =========================
    def _build_entity_context(self, entity: str, generated_files: dict) -> str:
        entity_lower = entity.lower()
        files_to_read = [
            f"app/models/{entity_lower}.py",
            f"app/schemas/{entity_lower}.py",
            f"app/services/{entity_lower}.py",
            f"app/routes/{entity_lower}.py",
        ]

        context_parts = []
        for file_path in files_to_read:
            if file_path in generated_files:
                context_parts.append(
                    f"--- {file_path} ---\n{generated_files[file_path]}"
                )

        return "\n\n".join(context_parts) if context_parts else "No context available."

    # =========================
    # GET ENTITY ENDPOINTS
    # =========================
    def _get_entity_endpoints(self, entity: str, task_queue: list) -> list:
        for task in task_queue:
            if task.get("entity") == entity and task.get("type") == "route":
                return task.get("endpoints", [])
        return []

    # =========================
    # LLM CALL
    # =========================
    def _call_llm(self, entity: str, entity_context: str, endpoints: list) -> str:
        system_prompt = self.system_prompt_template.replace(
            "{entity_context}", entity_context
        ).replace(
            "{entity}", entity.lower()
        ).replace(
            "{endpoints}", json.dumps(endpoints, indent=2)
        )

        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=f"Generate complete pytest integration tests for {entity}. Return ONLY Python code, no explanation, no markdown, no backticks.")
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

    # =========================
    # RUN PYTEST
    # =========================
    def _run_pytest(self, test_file: str) -> dict:
        if os.name == "nt":
            python_path = os.path.join(GENERATED_PROJECT_PATH, "venv", "Scripts", "python")
        else:
            python_path = os.path.join(GENERATED_PROJECT_PATH, "venv", "bin", "python")

        full_test_path = os.path.join(GENERATED_PROJECT_PATH, test_file)

        result = subprocess.run(
            [python_path, "-m", "pytest", full_test_path, "-v", "--tb=short"],
            capture_output=True,
            text=True,
            cwd=GENERATED_PROJECT_PATH
        )

        output = result.stdout + result.stderr

        return {
            "status": "passed" if result.returncode == 0 else "failed",
            "output": output,
            "errors": result.stderr if result.returncode != 0 else None
        }