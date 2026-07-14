"""
Test du service Planner SANS Celery, SANS Docker.
Lance :  python -m services.planner.run_local
"""
import json
from pathlib import Path

from shared.state import GraphState
from shared.settings import INPUT_FILE
from services.planner.graph import create_planner_graph

FAILED_STATES = {"openapi_failed", "planning_failed", "setup_failed"}


def load_user_input() -> str:
    path = Path(INPUT_FILE)
    if not path.exists():
        raise FileNotFoundError(f"Input introuvable : {path.resolve()}")
    return path.read_text(encoding="utf-8")


def main():
    user_input = load_user_input()
    print(f"[INPUT] {len(user_input)} caractères lus depuis {INPUT_FILE}")

    initial_state = GraphState(user_input=user_input)

    graph = create_planner_graph()
    result = graph.invoke(initial_state)

    if isinstance(result, dict):
        result = GraphState(**result)

    print("\n" + "=" * 50)
    print("workflow_state :", result.workflow_state)

    if result.workflow_state in FAILED_STATES:
        print("❌ ÉCHEC")
        print(result.error_log)
        return

    print("✅ SUCCÈS")
    print("entités       :", list((result.dependency_graph or {}).keys()))
    print("tâches        :", len(result.task_queue or []))
    print("fichiers créés:", len(result.filesystem_state or []))

    print("\n--- test de sérialisation ---")
    transported = result.to_transport()
    raw = json.dumps(transported)
    rebuilt = GraphState(**json.loads(raw))

    print("taille JSON        :", len(raw), "octets")
    print("task_queue OK      :", len(rebuilt.task_queue or []) == len(result.task_queue or []))
    print("openapi_spec OK    :", rebuilt.openapi_spec is not None)


if __name__ == "__main__":
    main()