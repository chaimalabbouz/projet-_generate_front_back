import time
from pathlib import Path
from shared.celery_app import celery_app
from shared.state import GraphState
from shared.settings import GENERATED_PROJECT_PATH
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
    print("[DESIGN TASK] démarrage du pipeline figma")
    t0 = time.time()

    state = GraphState(**state_dict)
    result = get_graph().invoke(state)
    if isinstance(result, dict):
        result = GraphState(**result)

    duration = round(time.time() - t0, 1)

    if result.workflow_state in FAILED_STATES:
        raise RuntimeError(f"Design failed: {result.error_log}")

    # compte les pages produites sur le disque
    pages_dir = Path(GENERATED_PROJECT_PATH) / "frontend" / "src" / "pages"
    pages = len(list(pages_dir.glob("*.tsx")) + list(pages_dir.glob("*.jsx"))) if pages_dir.is_dir() else 0

    print(f"[DESIGN TASK] ✓ {pages} pages en {duration}s")

    return {
        "workflow_state": result.workflow_state,
        "error_log": result.error_log,
        "metrics": {
            "design": {
                "duration_s": duration,
                "pages_generated": pages,
                "started_at": round(t0, 1),
                "ended_at": round(t0 + duration, 1),
            }
        },
    }