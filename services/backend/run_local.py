"""
Test du service Backend SANS Celery.

Deux modes :
  1) reprendre le résultat d'un run Planner déjà fait (recommandé)
     python -m services.backend.run_local <task_id_du_planner>

  2) relancer le Planner puis le Backend (plus lent, ~2 min de plus)
     python -m services.backend.run_local
"""
import sys
import json
from pathlib import Path

from shared.state import GraphState
from shared.settings import INPUT_FILE
from services.backend.graph import create_backend_graph

FAILED_STATES = {"backend_failed", "testing_error", "fixer_error", "fixer_max_retries"}


def get_planner_output(task_id: str | None) -> dict:
    """Récupère le state sortant du Planner."""

    # --- MODE DEBUG : on relit le dernier plan sur le disque (0 appel LLM) ---
    if task_id == "debug":
        from shared.settings import DEBUG_PATH, INPUT_FILE

        plan_path = Path(DEBUG_PATH) / "debug_plan.json"
        if not plan_path.exists():
            raise FileNotFoundError(f"Pas de plan à relire : {plan_path}")

        plan = json.loads(plan_path.read_text(encoding="utf-8"))
        print(f"[INPUT] plan relu depuis {plan_path} (aucun appel LLM)")

        return {
            "user_input": Path(INPUT_FILE).read_text(encoding="utf-8"),
            "dependency_graph": plan["dependency_graph"],
            "file_plan": plan["file_plan"],
            "task_queue": plan["task_queue"],
            "workflow_state": "setup_done",
        }

    if task_id:
        # on relit le résultat stocké dans Redis par le worker Celery
        from celery.result import AsyncResult
        from shared.celery_app import celery_app

        res = AsyncResult(task_id, app=celery_app)
        if not res.successful():
            raise RuntimeError(f"La tâche {task_id} n'est pas en SUCCESS (statut: {res.status})")
        print(f"[INPUT] state repris du Planner (task {task_id[:8]}...)")
        return res.get()

    # sinon : on relance le Planner en direct
    print("[INPUT] pas de task_id -> on relance le Planner (2 appels LLM, ~2 min)")
    from services.planner.graph import create_planner_graph

    user_input = Path(INPUT_FILE).read_text(encoding="utf-8")
    result = create_planner_graph().invoke(GraphState(user_input=user_input))
    if isinstance(result, dict):
        result = GraphState(**result)

    if result.workflow_state != "setup_done":
        raise RuntimeError(f"Planner a échoué : {result.workflow_state}\n{result.error_log}")

    return result.to_transport()


def main():
    task_id = sys.argv[1] if len(sys.argv) > 1 else None

    state_dict = get_planner_output(task_id)
    state = GraphState(**state_dict)

    print(f"[INPUT] {len(state.task_queue or [])} tâches à générer")
    print(f"[INPUT] entités : {list((state.dependency_graph or {}).keys())}")
    print("\n" + "=" * 60 + "\n")

    graph = create_backend_graph()
    result = graph.invoke(state, config={"recursion_limit": 200})

    if isinstance(result, dict):
        result = GraphState(**result)

    # ---------- RAPPORT ----------
    print("\n" + "=" * 60)
    print("workflow_state :", result.workflow_state)

    tasks = result.task_queue or []
    done = [t for t in tasks if t.get("status") == "done"]
    pending = [t for t in tasks if t.get("status") == "pending"]

    print(f"\nfichiers générés : {len(done)}/{len(tasks)}")
    if pending:
        print(f"⚠ restés pending : {[t['file'] for t in pending]}")

    routes = [t for t in tasks if t.get("type") == "route"]
    passed = [t for t in routes if t.get("test_status") == "passed"]
    failed = [t for t in routes if t.get("test_status") == "failed"]

    print(f"tests passés     : {len(passed)}/{len(routes)}")
    if failed:
        print(f"❌ tests échoués : {[t['entity'] for t in failed]}")

    print(f"retry_count      : {result.retry_count}")
    print(f"entités testées  : {result.tested_entities}")

    if result.workflow_state in FAILED_STATES:
        print("\n❌ ÉCHEC DU SERVICE")
        print(result.error_log)
        return

    if failed:
        print("\n⚠ TERMINÉ AVEC DES TESTS EN ÉCHEC")
    else:
        print("\n✅ SUCCÈS COMPLET")

    # ---------- TEST DE SÉRIALISATION ----------
    print("\n--- test de transport vers le Frontend ---")
    transported = result.to_transport()
    raw = json.dumps(transported)
    GraphState(**json.loads(raw))   # doit se reconstruire sans erreur

    print("taille JSON            :", len(raw), "octets")
    print("generated_files exclu  :", "generated_files" not in transported)
    print("test_results exclu     :", "test_results" not in transported)
    print("openapi_spec présent   :", transported.get("openapi_spec") is not None)


if __name__ == "__main__":
    main()