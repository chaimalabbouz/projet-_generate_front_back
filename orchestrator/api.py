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
    page_context: dict | None = None


class GenerateResponse(BaseModel):
    task_id: str
    status: str

# ---------- classification des erreurs ----------
def classify_error(traceback_text: str) -> tuple[str, str]:
    """
    Analyse le traceback Celery et renvoie (error_code, message lisible).
    Permet à l'extension et à n8n de réagir précisément au type d'échec.
    """
    tb = (traceback_text or "").lower()

    if "429" in tb and "figma" in tb:
        return "FIGMA_RATE_LIMIT", "Quota de l'API Figma dépassé. Réessayez dans une heure."
    if "404" in tb and "figma" in tb:
        return "FIGMA_NOT_FOUND", "Design Figma introuvable. Vérifiez l'identifiant du fichier."
    if "403" in tb and "figma" in tb:
        return "FIGMA_TOKEN_INVALID", "Token Figma invalide ou expiré."
    if "figma_generation_failed" in tb or "design failed" in tb:
        return "DESIGN_FAILED", "Échec de la génération du design."

    if "plan rejeté" in tb or "plan rejete" in tb:
        return "PLANNER_SECURITY", "La description contient des éléments non autorisés."
    if "openapi_failed" in tb:
        return "PLANNER_OPENAPI", "Impossible de générer la spécification OpenAPI depuis la description."
    if "planning_failed" in tb or "planner failed" in tb:
        return "PLANNER_FAILED", "Échec de la planification. Vérifiez la description du projet."
    if "setup_failed" in tb:
        return "SETUP_FAILED", "Échec de la création de l'arborescence du projet."

    if "aucune entité générée" in tb or "backend failed" in tb:
        return "BACKEND_FAILED", "Échec de la génération du code backend."

    if "frontend failed" in tb or "binding" in tb:
        return "FRONTEND_FAILED", "Échec du binding des pages au backend."

    if "connection" in tb or "timeout" in tb:
        return "INFRA_ERROR", "Problème d'infrastructure (base de données ou réseau)."

    return "UNKNOWN", "Une erreur inattendue est survenue."

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
        "page_context": req.page_context, 
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
    """Résultat final. Renvoie un error_code typé en cas d'échec."""
    res = AsyncResult(task_id, app=celery_app)

    if not res.ready():
        return {"task_id": task_id, "status": res.status, "result": None}

    # ---------- échec ----------
    if res.failed():
        code, message = classify_error(str(res.traceback))
        return {
            "task_id": task_id,
            "status": "FAILURE",
            "error_code": code,
            "error_message": message,
            "traceback": str(res.traceback)[-800:],   # extrait, pour le debug
        }

    # ---------- succès ----------
    out = res.get()
    tasks = out.get("task_queue") or []
    done = [t for t in tasks if t.get("status") == "done"]
    metrics = out.get("metrics", {})

    return {
        "task_id": task_id,
        "status": "SUCCESS",
        "error_code": None,
        "error_message": None,
        "summary": {
            "workflow_state": out.get("workflow_state"),
            "backend_files": f"{len(done)}/{len(tasks)}",
            "pages_bound": metrics.get("frontend", {}).get("pages_bound", 0),
            "entities": list((out.get("dependency_graph") or {}).keys()),
        },
        "metrics": metrics,
    }