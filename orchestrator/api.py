"""
Orchestrateur FastAPI — la façade HTTP du pipeline.

    POST /generate       lance le pipeline, renvoie un task_id
    GET  /status/{id}    suit l'avancement
    GET  /result/{id}    récupère le résultat final

Lance : uvicorn orchestrator.api:app --reload --port 8080
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from celery import chain, group, chord
from celery.result import AsyncResult

from shared.celery_app import celery_app
from services.planner.tasks import run_planner
from services.backend.tasks import run_backend
from services.design.tasks import run_design
from services.frontend.tasks import run_frontend

app = FastAPI(title="Codegen Orchestrator")

# CORS : pour que ton extension VS Code puisse appeler l'API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------- schémas ----------
class GenerateRequest(BaseModel):
    user_input: str
    figma_file_id: str | None = None    # optionnel : sinon celui du .env


class GenerateResponse(BaseModel):
    task_id: str
    status: str


# ---------- routes ----------
@app.get("/")
def health():
    return {"status": "ok", "service": "orchestrator"}


@app.post("/generate", response_model=GenerateResponse)
def generate(req: GenerateRequest):
    """Lance le pipeline complet et rend la main immédiatement."""
    if not req.user_input.strip():
        raise HTTPException(status_code=400, detail="user_input est vide")

    payload = {
        "user_input": req.user_input,
        "figma_file_id": req.figma_file_id,
    }

    workflow = chord(
        group(
            chain(run_planner.s(payload), run_backend.s()),
            run_design.s(payload),
        ),
        run_frontend.s(),
    )

    result = workflow.apply_async()
    return GenerateResponse(task_id=result.id, status="PENDING")


@app.get("/status/{task_id}")
def status(task_id: str):
    """Renvoie l'état d'avancement (PENDING / STARTED / SUCCESS / FAILURE)."""
    res = AsyncResult(task_id, app=celery_app)
    return {
        "task_id": task_id,
        "status": res.status,
        "ready": res.ready(),
    }


@app.get("/result/{task_id}")
def result(task_id: str):
    """Renvoie le résultat final (à appeler quand status == SUCCESS)."""
    res = AsyncResult(task_id, app=celery_app)

    if not res.ready():
        return {"task_id": task_id, "status": res.status, "result": None}

    if res.failed():
        raise HTTPException(status_code=500, detail=str(res.traceback))

    out = res.get()
    tasks = out.get("task_queue") or []
    done = [t for t in tasks if t.get("status") == "done"]

    return {
        "task_id": task_id,
        "status": "SUCCESS",
        "summary": {
            "workflow_state": out.get("workflow_state"),
            "backend_files": f"{len(done)}/{len(tasks)}",
            "pages_bound": len(out.get("frontend_pages") or {}),
            "entities": list((out.get("dependency_graph") or {}).keys()),
        },
    }