import time
from shared.celery_app import celery_app
from shared.state import GraphState
from services.planner.graph import create_planner_graph

FAILED_STATES = {"openapi_failed", "planning_failed", "setup_failed"}

_graph = None


def get_graph():
    global _graph
    if _graph is None:
        _graph = create_planner_graph()
    return _graph


@celery_app.task(name="planner.run", bind=True, max_retries=2)
def run_planner(self, state_dict: dict) -> dict:
    print("[PLANNER TASK] démarrage")
    t0 = time.time()

    state = GraphState(**state_dict)
    result = get_graph().invoke(state)
    if isinstance(result, dict):
        result = GraphState(**result)

    duration = round(time.time() - t0, 1)

    if result.workflow_state in FAILED_STATES:
        print(f"[PLANNER TASK] ✗ ÉCHEC : {result.workflow_state}")
        raise RuntimeError(f"Planner failed ({result.workflow_state}): {result.error_log}")

    # ---- MÉTRIQUES ----
    result.metrics = dict(result.metrics or {})
    result.metrics["planner"] = {
        "duration_s": duration,
        "entities": len(result.dependency_graph or {}),
        "tasks_planned": len(result.task_queue or []),
        "started_at": round(t0, 1),
        "ended_at": round(t0 + duration, 1),
    }

    print(f"[PLANNER TASK] ✓ {len(result.task_queue or [])} tâches en {duration}s")
    return result.to_transport()