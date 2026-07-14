"""Envoie une tâche planner au worker. Lance : python test_celery.py"""
import time
from pathlib import Path

from shared.settings import INPUT_FILE
from services.planner.tasks import run_planner

user_input = Path(INPUT_FILE).read_text(encoding="utf-8")

# .delay() = dépose la tâche dans Redis et RACCROCHE (ne bloque pas)
async_result = run_planner.delay({"user_input": user_input})

print(f"task_id : {async_result.id}")
print("statut  :", async_result.status)

# on suit l'avancement (c'est ce que fera l'orchestrateur FastAPI)
while not async_result.ready():
    print("  ... en cours :", async_result.status)
    time.sleep(3)

print("\nstatut final :", async_result.status)

if async_result.successful():
    result = async_result.get()
    print("✅ SUCCÈS")
    print("entités :", list((result.get("dependency_graph") or {}).keys()))
    print("tâches  :", len(result.get("task_queue") or []))
else:
    print("❌ ÉCHEC")
    print(async_result.traceback)