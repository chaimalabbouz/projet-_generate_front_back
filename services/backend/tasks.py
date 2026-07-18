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

    # ---- garde : on échoue seulement si AUCUNE entité n'a réussi ----
    routes = [t for t in (result.task_queue or []) if t.get("type") == "route"]
    passed = [t for t in routes if t.get("test_status") == "passed"]
    abandoned = result.abandoned_entities or []

    if routes and not passed:
        raise RuntimeError(f"Backend : aucune entité générée avec succès. Abandonnées : {abandoned}")

    done = len([t for t in (result.task_queue or []) if t.get("status") == "done"])
    print(f"[BACKEND TASK] ✓ {done} fichiers, {len(passed)}/{len(routes)} entités OK")
    if abandoned:
        print(f"[BACKEND TASK] ⚠ entités abandonnées : {abandoned}")





    return result.to_transport()