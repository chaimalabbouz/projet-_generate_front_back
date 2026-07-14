from shared.celery_app import celery_app
from shared.state import GraphState
from services.planner.graph import create_planner_graph

FAILED_STATES = {"openapi_failed", "planning_failed", "setup_failed"}

# le graphe est construit UNE fois au démarrage du worker,
# pas à chaque tâche (les agents chargent leurs prompts à l'init)
_graph = None


def get_graph():
    global _graph
    if _graph is None:
        _graph = create_planner_graph()
    return _graph


@celery_app.task(name="planner.run", bind=True, max_retries=2)
def run_planner(self, state_dict: dict) -> dict:
    """
    Entrée : dict du GraphState (venant de l'orchestrateur)
    Sortie : dict allégé, pour le service Backend
    """
    print("[PLANNER TASK] démarrage")

    state = GraphState(**state_dict)

    result = get_graph().invoke(state)
    if isinstance(result, dict):
        result = GraphState(**result)

    # ---- LA GARDE ----
    # Sans ça, Celery croit que tout va bien et enchaîne sur Backend
    # avec une task_queue vide.
    if result.workflow_state in FAILED_STATES:
        print(f"[PLANNER TASK] ✗ ÉCHEC : {result.workflow_state}")
        raise RuntimeError(
            f"Planner failed ({result.workflow_state}): {result.error_log}"
        )

    print(f"[PLANNER TASK] ✓ {len(result.task_queue or [])} tâches planifiées")

    return result.to_transport()