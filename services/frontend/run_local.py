"""
Test du service Frontend SANS Celery.
Repart du plan sur disque + suppose que Design a déjà généré les pages.
Lance : python -m services.frontend.run_local
"""
import json
from pathlib import Path

from shared.state import GraphState
from shared.settings import INPUT_FILE, DEBUG_PATH, GENERATED_PROJECT_PATH
from services.frontend.graph import create_frontend_graph


def main():
    # on relit le plan du Planner (pour task_queue + dependency_graph)
    plan = json.loads((Path(DEBUG_PATH) / "debug_plan.json").read_text(encoding="utf-8"))

    state = GraphState(
        user_input=Path(INPUT_FILE).read_text(encoding="utf-8"),
        task_queue=plan["task_queue"],
        dependency_graph=plan["dependency_graph"],
        # openapi_spec absent du debug_plan -> l'api_client et le binding
        # échoueront proprement si besoin (c'est la limite de ce mode)
    )

    print("[FRONTEND] démarrage...\n")
    result = create_frontend_graph().invoke(state)
    if isinstance(result, dict):
        result = GraphState(**result)

    print("\n" + "=" * 50)
    print("workflow_state :", result.workflow_state)
    print("pages bindées  :", len(result.frontend_pages or {}))

    if result.error_log:
        print("\nerror_log:", result.error_log)


if __name__ == "__main__":
    main()