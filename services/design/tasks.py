from shared.celery_app import celery_app
from shared.state import GraphState
from services.design.graph import create_design_graph

FAILED_STATES = {"figma_generation_failed"}

_graph = None


def get_graph():
    global _graph
    if _graph is None:
        _graph = create_design_graph()
    return _graph


@celery_app.task(name="design.run", bind=True, max_retries=1)
def run_design(self, state_dict: dict) -> dict:
    """
    Génère le frontend statique depuis Figma.

    Ne produit AUCUNE donnée pour le state : il écrit les pages .jsx
    directement sur le volume. Son seul rôle dans le state est de
    signaler qu'il a fini sans erreur.
    """
    print("[DESIGN TASK] démarrage du pipeline figma")

    state = GraphState(**state_dict)

    result = get_graph().invoke(state)
    if isinstance(result, dict):
        result = GraphState(**result)

    # ---- GARDE ----
    if result.workflow_state in FAILED_STATES:
        print(f"[DESIGN TASK] ✗ ÉCHEC : {result.workflow_state}")
        raise RuntimeError(f"Design failed: {result.error_log}")

    print("[DESIGN TASK] ✓ frontend statique généré")

    # on ne renvoie qu'un accusé minimal : le vrai résultat est sur le disque
    return {
        "workflow_state": result.workflow_state,
        "error_log": result.error_log,
    }