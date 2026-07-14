from shared.celery_app import celery_app
from shared.state import GraphState
from services.backend.graph import create_backend_graph

FAILED_STATES = {"backend_failed", "testing_error", "fixer_error", "fixer_max_retries"}

_graph = None


def get_graph():
    global _graph
    if _graph is None:
        _graph = create_backend_graph()
    return _graph


@celery_app.task(name="backend.run", bind=True, max_retries=1)
def run_backend(self, state_dict: dict) -> dict:
    """
    Entrée : dict venant du Planner (via chain Celery)
    Sortie : dict allégé, pour le service Frontend
    """
    print("[BACKEND TASK] démarrage")

    state = GraphState(**state_dict)
    print(f"[BACKEND TASK] {len(state.task_queue or [])} tâches à générer")

    result = get_graph().invoke(state, config={"recursion_limit": 200})
    if isinstance(result, dict):
        result = GraphState(**result)

    # ---- GARDE ----
    if result.workflow_state in FAILED_STATES:
        print(f"[BACKEND TASK] ✗ ÉCHEC : {result.workflow_state}")
        raise RuntimeError(
            f"Backend failed ({result.workflow_state}): {result.error_log}"
        )

    # ---- garde supplémentaire : des tests ont-ils échoué ? ----
    routes = [t for t in (result.task_queue or []) if t.get("type") == "route"]
    failed = [t["entity"] for t in routes if t.get("test_status") == "failed"]
    if failed:
        raise RuntimeError(f"Backend: tests toujours en échec pour {failed}")

    done = len([t for t in (result.task_queue or []) if t.get("status") == "done"])
    print(f"[BACKEND TASK] ✓ {done} fichiers générés, {len(routes)} entités testées")

    return result.to_transport()