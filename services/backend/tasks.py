import time
from shared.celery_app import celery_app
from shared.state import GraphState
from services.backend.graph import create_backend_graph

FAILED_STATES = {"backend_failed", "testing_error", "fixer_error"}

_graph = None


def get_graph():
    global _graph
    if _graph is None:
        _graph = create_backend_graph()
    return _graph


@celery_app.task(name="backend.run", bind=True, max_retries=1)
def run_backend(self, state_dict: dict) -> dict:
    print("[BACKEND TASK] démarrage")
    t0 = time.time()

    state = GraphState(**state_dict)
    print(f"[BACKEND TASK] {len(state.task_queue or [])} tâches à générer")

    result = get_graph().invoke(state, config={"recursion_limit": 200})
    if isinstance(result, dict):
        result = GraphState(**result)

    duration = round(time.time() - t0, 1)

    if result.workflow_state in FAILED_STATES:
        raise RuntimeError(f"Backend failed ({result.workflow_state}): {result.error_log}")

    routes = [t for t in (result.task_queue or []) if t.get("type") == "route"]
    passed = [t for t in routes if t.get("test_status") == "passed"]
    abandoned = result.abandoned_entities or []
    done = [t for t in (result.task_queue or []) if t.get("status") == "done"]

    if routes and not passed:
        raise RuntimeError(f"Backend : aucune entité générée avec succès. Abandonnées : {abandoned}")

    # ---- MÉTRIQUES ----
    result.metrics = dict(result.metrics or {})
    result.metrics["backend"] = {
        "duration_s": duration,
        "entities_total": len(routes),
        "entities_passed": len(passed),
        "entities_abandoned": abandoned,
        "success_rate_pct": round(len(passed) / len(routes) * 100) if routes else 0,
        "files_generated": len(done),
        "files_planned": len(result.task_queue or []),
        "started_at": round(t0, 1),
        "ended_at": round(t0 + duration, 1),
    }

    print(f"[BACKEND TASK] ✓ {len(passed)}/{len(routes)} entités en {duration}s")
    if abandoned:
        print(f"[BACKEND TASK] ⚠ abandonnées : {abandoned}")

    return result.to_transport()