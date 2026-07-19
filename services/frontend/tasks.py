import time
from shared.celery_app import celery_app
from shared.state import GraphState
from services.frontend.graph import create_frontend_graph

FAILED_STATES = {"seed_failed", "frontend_api_failed", "binding_error"}

_graph = None


def get_graph():
    global _graph
    if _graph is None:
        _graph = create_frontend_graph()
    return _graph


@celery_app.task(name="frontend.run", bind=True, max_retries=1)
def run_frontend(self, chord_results: list) -> dict:
    print("[FRONTEND TASK] démarrage")
    t0 = time.time()

    backend_state, design_ack = chord_results

    if (design_ack or {}).get("workflow_state") == "figma_generation_failed":
        raise RuntimeError(f"Design a échoué : {design_ack.get('error_log')}")

    state = GraphState(**backend_state)

    # récupère les métriques du Design (branche parallèle)
    design_metrics = (design_ack or {}).get("metrics", {})
    state.metrics = {**(state.metrics or {}), **design_metrics}

    result = get_graph().invoke(state)
    if isinstance(result, dict):
        result = GraphState(**result)

    duration = round(time.time() - t0, 1)

    if result.workflow_state in FAILED_STATES:
        raise RuntimeError(f"Frontend failed ({result.workflow_state}): {result.error_log}")

    # ---- MÉTRIQUES + CALCUL DU PARALLÉLISME ----
    m = dict(result.metrics or {})
    m["frontend"] = {
        "duration_s": duration,
        "pages_bound": len(result.frontend_pages or {}),
    }

    # temps total réel vs séquentiel
    all_starts = [v["started_at"] for v in m.values() if "started_at" in v]
    all_ends = [v["ended_at"] for v in m.values() if "ended_at" in v]
    sequential = sum(v["duration_s"] for v in m.values() if "duration_s" in v)

    if all_starts and all_ends:
        real = round(max(all_ends) - min(all_starts) + duration, 1)
        m["pipeline"] = {
            "total_real_s": real,
            "total_sequential_s": round(sequential, 1),
            "parallelism_gain_pct": round((1 - real / sequential) * 100) if sequential else 0,
        }

    result.metrics = m
    print(f"[FRONTEND TASK] ✓ {len(result.frontend_pages or {})} pages bindées en {duration}s")

    return result.to_transport()