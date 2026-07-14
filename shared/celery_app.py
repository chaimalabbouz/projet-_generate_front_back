from celery import Celery
from shared.settings import REDIS_URL

celery_app = Celery(
    "codegen",
    broker=REDIS_URL,      # la file d'attente
    backend=REDIS_URL,     # le stockage des résultats
    include=[
        "services.planner.tasks",
        "services.backend.tasks",    
        # "services.frontend.tasks",
    ],
)

celery_app.conf.update(
    # --- sérialisation : JSON uniquement (pas de pickle) ---
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],

    # --- ROUTAGE : chaque tâche va dans SA file ---
    # Sans ça, le worker frontend pourrait piocher une tâche planner.
    task_routes={
        "planner.run":  {"queue": "planner"},
        "backend.run":  {"queue": "backend"},
        "frontend.run": {"queue": "frontend"},
    },

    # --- LLM lents : un worker ne réserve qu'UNE tâche à la fois ---
    worker_prefetch_multiplier=1,

    # --- la tâche n'est ack'ée qu'APRÈS exécution ---
    # si le worker crashe en plein LLM, la tâche est reprise, pas perdue
    task_acks_late=True,

    # --- Redis : ne PAS redistribuer une tâche avant 2h ---
    # (défaut = 1h, trop court pour un pipeline LLM long)
    broker_transport_options={"visibility_timeout": 7200},

    result_expires=86400,   # les résultats vivent 24h
)