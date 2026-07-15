"""
Pipeline complet en CHORD (parallèle).

    ┌─ chain(planner → backend) ─┐
    │                            ├─► frontend
    └─ design ───────────────────┘

Lance : python run_pipeline.py
"""
import time
from pathlib import Path
from celery import chain, group, chord

from shared.settings import INPUT_FILE
from services.planner.tasks import run_planner
from services.backend.tasks import run_backend
from services.design.tasks import run_design
from services.frontend.tasks import run_frontend

user_input = Path(INPUT_FILE).read_text(encoding="utf-8")
payload = {"user_input": user_input}

# --- la structure ---
# branche 1 : planner PUIS backend (séquentiel)
# branche 2 : design (en parallèle de la branche 1)
# callback  : frontend, lancé quand LES DEUX branches ont fini
workflow = chord(
    group(
        chain(run_planner.s(payload), run_backend.s()),
        run_design.s(payload),
    ),
    run_frontend.s(),
)

result = workflow.apply_async()

print(f"chord id : {result.id}")
print("(planner→backend et design tournent EN PARALLÈLE)\n")

while not result.ready():
    print("  ...", result.status)
    time.sleep(5)

print("\nstatut final :", result.status)

if result.successful():
    out = result.get()
    print("✅ PIPELINE COMPLET (4 services)")
    print("workflow_state :", out.get("workflow_state"))
    print("pages bindées  :", len(out.get("frontend_pages") or {}))
    tasks = out.get("task_queue") or []
    done = [t for t in tasks if t.get("status") == "done"]
    print(f"fichiers backend : {len(done)}/{len(tasks)}")
else:
    print("❌ ÉCHEC")
    print(result.traceback)