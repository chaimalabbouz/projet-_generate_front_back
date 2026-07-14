"""Planner -> Backend enchaînés par Celery. Lance : python test_chain.py"""
import time
from pathlib import Path
from celery import chain

from shared.settings import INPUT_FILE
from services.planner.tasks import run_planner
from services.backend.tasks import run_backend

user_input = Path(INPUT_FILE).read_text(encoding="utf-8")

# LE CHAIN : la sortie de planner devient l'entrée de backend
pipeline = chain(
    run_planner.s({"user_input": user_input}),
    run_backend.s(),
)

result = pipeline.apply_async()

print(f"task_id : {result.id}")
print("(le client ne bloque pas — il interroge le statut)\n")

while not result.ready():
    print("  ... ", result.status)
    time.sleep(5)

print("\nstatut final :", result.status)

if result.successful():
    out = result.get()
    tasks = out.get("task_queue") or []
    done = [t for t in tasks if t.get("status") == "done"]
    print("✅ PIPELINE COMPLET")
    print(f"fichiers générés : {len(done)}/{len(tasks)}")
    print(f"entités          : {list((out.get('dependency_graph') or {}).keys())}")
else:
    print("❌ ÉCHEC")
    print(result.traceback)