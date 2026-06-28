import os
import subprocess

from config.settings import GENERATED_PROJECT_PATH
from orchestrator.state import GraphState
from agents.test_generator import TestGenerator


class TesterAgent:
    def __init__(self):
        # Plus de LLM, plus de prompt a charger : la generation est deterministe.
        pass

    # =========================
    # MAIN NODE (LANGGRAPH)
    # =========================
    def run(self, state: GraphState) -> GraphState:
        try:
            current_entity = self._get_current_entity(state.task_queue)

            if current_entity is None:
                state.workflow_state = "testing_done"
                return state

            if state.tested_entities is None:
                state.tested_entities = []

            test_file = f"tests/test_{current_entity.lower()}.py"

            # ---- On NE genere le test qu'une seule fois PAR ENTITE PAR EXECUTION ----
            # - 1er passage (entite absente de tested_entities) -> on genere.
            # - passages suivants (apres le fixer) -> on reutilise le meme fichier,
            #   ce qui donne au fixer une cible stable.
            if current_entity not in state.tested_entities:
                generator = TestGenerator(state.task_queue, state.dependency_graph)
                test_code = generator.generate(current_entity)
                self._write_file(test_file, test_code)

                state.tested_entities.append(current_entity)
                # chaque entite repart avec son quota de retries plein
                state.retry_count = 0

            # ---- execution pytest (toujours) ----
            test_result = self._run_pytest(test_file)

            if state.test_results is None:
                state.test_results = {}
            state.test_results[current_entity] = test_result

            # maj test_status dans la task_queue
            new_task_queue = []
            for task in state.task_queue:
                if task.get("entity") == current_entity and task.get("type") == "route":
                    task = dict(task)
                    task["test_status"] = "passed" if test_result["status"] == "passed" else "failed"
                new_task_queue.append(task)
            state.task_queue = new_task_queue

            if test_result["status"] == "passed":
                state.workflow_state = f"testing_passed:{current_entity}"
                print(f"  \u2713 Tests passed for {current_entity}")
            else:
                state.workflow_state = f"testing_failed:{current_entity}"
                state.error_log = (state.error_log or "") + f"\n[TEST ERROR] {current_entity}:\n{test_result['output']}"
                print(f"  \u2717 Tests failed for {current_entity}")
                print(test_result["output"])

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
