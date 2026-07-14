import os
import sys
import subprocess

from shared.settings import GENERATED_PROJECT_PATH
from shared.state import GraphState
from services.backend.agents.test_generator import TestGenerator


class TesterAgent:
    def __init__(self):
        # Pas de LLM : la génération de tests est déterministe.
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

            # Le test n'est généré qu'UNE fois par entité :
            # les passages suivants (après le fixer) réutilisent le même fichier,
            # ce qui donne au fixer une cible stable.
            if current_entity not in state.tested_entities:
                generator = TestGenerator(state.task_queue, state.dependency_graph)
                test_code = generator.generate(current_entity)
                self._write_file(test_file, test_code)

                state.tested_entities.append(current_entity)
                state.retry_count = 0   # chaque entité repart avec son quota plein

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
                print(f"  ✓ Tests passed for {current_entity}")
            else:
                state.workflow_state = f"testing_failed:{current_entity}"
                state.error_log = (state.error_log or "") + f"\n[TEST ERROR] {current_entity}:\n{test_result['output']}"
                print(f"  ✗ Tests failed for {current_entity}")
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
    # RUN PYTEST  (plus de docker run)
    # =========================
    def _run_pytest(self, test_file: str) -> dict:
        test_file = test_file.replace("\\", "/")

        # PYTHONPATH : pour que "from app.database import ..." résolve
        env = os.environ.copy()
        env["PYTHONPATH"] = GENERATED_PROJECT_PATH

        try:
            result = subprocess.run(
                [sys.executable, "-m", "pytest", test_file, "-v", "--tb=short"],
                cwd=GENERATED_PROJECT_PATH,   # ← indispensable pour les imports
                capture_output=True,
                text=True,
                env=env,
                timeout=300,
            )
            output = result.stdout + result.stderr
            returncode = result.returncode

        except subprocess.TimeoutExpired:
            output = "TIMEOUT: pytest a dépassé 300 secondes."
            returncode = 1

        return {
            "status": "passed" if returncode == 0 else "failed",
            "output": output,
            "errors": output if returncode != 0 else None,
        }