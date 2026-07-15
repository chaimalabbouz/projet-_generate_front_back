from shared.celery_app import celery_app
from shared.state import GraphState
from services.frontend.graph import create_frontend_graph

FAILED_STATES = {
    "seed_failed", "frontend_api_failed", "binding_error", "binding_no_pages",
}

_graph = None


def get_graph():
    global _graph
    if _graph is None:
        _graph = create_frontend_graph()
    return _graph


@celery_app.task(name="frontend.run", bind=True, max_retries=1)
def run_frontend(self, chord_results: list) -> dict:
    """
    Callback du chord. Reçoit une LISTE :
      [ state_du_backend (dict riche),  ack_du_design (dict minimal) ]

    On repart du state Backend (il a openapi_spec, task_queue...).
    Le Design n'apporte rien au state : ses pages sont déjà sur le disque.
    """
    print("[FRONTEND TASK] démarrage")

    backend_state, design_ack = chord_results

    # garde : le Design a-t-il échoué ?
    if (design_ack or {}).get("workflow_state") == "figma_generation_failed":
        raise RuntimeError(f"Design a échoué : {design_ack.get('error_log')}")

    state = GraphState(**backend_state)

    result = get_graph().invoke(state)
    if isinstance(result, dict):
        result = GraphState(**result)

    # garde : le Frontend a-t-il échoué ?
    if result.workflow_state in FAILED_STATES:
        print(f"[FRONTEND TASK] ✗ ÉCHEC : {result.workflow_state}")
        raise RuntimeError(
            f"Frontend failed ({result.workflow_state}): {result.error_log}"
        )

    bound = len(result.frontend_pages or {})
    print(f"[FRONTEND TASK] ✓ {bound} pages bindées")

    return result.to_transport()