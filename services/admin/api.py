"""
Back-office MoonPilot — API d'administration.

    POST /admin/login          → access + refresh token
    POST /admin/refresh        → nouveau access token
    GET  /admin/me             → profil de l'admin connecté

Lance : uvicorn services.admin.api:app --reload --port 8081
"""
from datetime import datetime
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel
from services.admin.db import moonpilot_cursor
from services.admin.auth import (
    authenticate_admin,
    create_access_token,
    create_refresh_token,
    decode_token,
    require_admin,
    touch_last_login,
)
from services.admin.db import llm_cursor
from typing import Optional

app = FastAPI(title="MoonPilot Admin API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------- schémas ----------------
class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RefreshRequest(BaseModel):
    refresh_token: str


# ---------------- routes publiques ----------------
@app.get("/")
def health():
    return {"status": "ok", "service": "admin"}


@app.post("/admin/login", response_model=TokenResponse)
def login(form: OAuth2PasswordRequestForm = Depends()):
    """Authentifie un admin et renvoie une paire de tokens."""
    admin = authenticate_admin(form.username, form.password)

    if not admin:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Identifiants invalides",
            headers={"WWW-Authenticate": "Bearer"},
        )

    touch_last_login(admin["username"])

    return TokenResponse(
        access_token=create_access_token(admin["username"]),
        refresh_token=create_refresh_token(admin["username"]),
    )


@app.post("/admin/refresh", response_model=TokenResponse)
def refresh(payload: RefreshRequest):
    """Échange un refresh token valide contre une nouvelle paire."""
    username = decode_token(payload.refresh_token, expected_type="refresh")

    return TokenResponse(
        access_token=create_access_token(username),
        refresh_token=create_refresh_token(username),
    )


# ---------------- routes protégées ----------------
@app.get("/admin/me")
def me(admin: dict = Depends(require_admin)):
    """Profil de l'admin connecté. Sert aussi à valider un token côté UI."""
    return admin

# ---------------- DONNÉES ----------------
@app.get("/admin/stats")
def stats(admin: dict = Depends(require_admin)):
    """Les 4 chiffres clés du dashboard."""
    with moonpilot_cursor() as cur:
        cur.execute("SELECT COUNT(*) AS n FROM users")
        users = cur.fetchone()["n"]

        cur.execute("SELECT COUNT(*) AS n FROM generations")
        total = cur.fetchone()["n"]

        cur.execute(
            "SELECT COUNT(*) AS n FROM generations "
            "WHERE LOWER(status) IN ('success', 'succeeded')"
        )
        success = cur.fetchone()["n"]

    return {
        "users": users,
        "generations_total": total,
        "generations_success": success,
        "success_rate_pct": round(success / total * 100) if total else 0,
    }


@app.get("/admin/users")
def list_users(admin: dict = Depends(require_admin)):
    """Liste des utilisateurs avec leur nombre de générations."""
    with moonpilot_cursor() as cur:
        cur.execute("""
            SELECT u.id, u.github_login, u.email, u.name, u.created_at,
                   COUNT(g.id) AS generations_count
            FROM users u
            LEFT JOIN generations g ON g.user_id = u.id
            GROUP BY u.id
            ORDER BY u.created_at DESC
        """)
        return cur.fetchall()


@app.get("/admin/generations")
def list_generations(admin: dict = Depends(require_admin)):
    """Historique des générations avec leurs métriques."""
    with moonpilot_cursor() as cur:
        cur.execute("""
            SELECT g.id, g.figma_file_id, g.status, g.error_message,
                   g.metrics, g.started_at, g.finished_at,
                   u.github_login
            FROM generations g
            LEFT JOIN users u ON u.id = g.user_id
            ORDER BY g.id DESC
            LIMIT 100
        """)
        return cur.fetchall()    
# ---------------- PROMPTS LLM ----------------
class PromptUpdate(BaseModel):
    prompt: str


class ConfigUpdate(BaseModel):
    model_id: Optional[int] = None
    temperature: Optional[float] = None
    max_tokens: Optional[int] = None


@app.get("/admin/prompts")
def list_prompts(admin: dict = Depends(require_admin)):
    """Liste des prompts figma avec leur configuration LLM."""
    with llm_cursor() as cur:
        cur.execute("""
            SELECT p.id AS prompt_id, p.nom_prompt, p.version,
                   LEFT(p.prompt, 160) AS preview, CHAR_LENGTH(p.prompt) AS length,
                   mpc.id AS config_id, mpc.temperature, mpc.max_tokens,
                   m.id AS model_id, m.model_name, m.provider
            FROM prompts p
            LEFT JOIN model_prompt_config mpc ON mpc.prompt_id = p.id
            LEFT JOIN models m ON m.id = mpc.model_id
            ORDER BY p.id
        """)
        return cur.fetchall()


@app.get("/admin/prompts/{prompt_id}")
def get_prompt(prompt_id: int, admin: dict = Depends(require_admin)):
    """Contenu complet d'un prompt."""
    with llm_cursor() as cur:
        cur.execute(
            "SELECT id, nom_prompt, prompt, version FROM prompts WHERE id = %s",
            (prompt_id,),
        )
        row = cur.fetchone()

    if not row:
        raise HTTPException(status_code=404, detail="Prompt introuvable")
    return row


@app.put("/admin/prompts/{prompt_id}")
def update_prompt(prompt_id: int, payload: PromptUpdate,
                  admin: dict = Depends(require_admin)):
    """Modifie le texte d'un prompt et incrémente sa version."""
    if not payload.prompt.strip():
        raise HTTPException(status_code=400, detail="Le prompt ne peut pas être vide")

    with llm_cursor() as cur:
        cur.execute("SELECT id FROM prompts WHERE id = %s", (prompt_id,))
        if not cur.fetchone():
            raise HTTPException(status_code=404, detail="Prompt introuvable")

        cur.execute(
            "UPDATE prompts SET prompt = %s, version = version + 1 WHERE id = %s",
            (payload.prompt, prompt_id),
        )

    return {"status": "updated", "prompt_id": prompt_id}


@app.get("/admin/models")
def list_models(admin: dict = Depends(require_admin)):
    """Modèles LLM disponibles (pour le sélecteur)."""
    with llm_cursor() as cur:
        cur.execute("SELECT id, model_name, provider FROM models ORDER BY id")
        return cur.fetchall()


@app.put("/admin/configs/{config_id}")
def update_config(config_id: int, payload: ConfigUpdate,
                  admin: dict = Depends(require_admin)):
    """Modifie le modèle, la température ou max_tokens d'un prompt."""
    fields, values = [], []

    if payload.model_id is not None:
        fields.append("model_id = %s")
        values.append(payload.model_id)
    if payload.temperature is not None:
        if not 0 <= payload.temperature <= 2:
            raise HTTPException(status_code=400, detail="temperature doit être entre 0 et 2")
        fields.append("temperature = %s")
        values.append(payload.temperature)
    if payload.max_tokens is not None:
        fields.append("max_tokens = %s")
        values.append(payload.max_tokens)

    if not fields:
        raise HTTPException(status_code=400, detail="Aucun champ à modifier")

    values.append(config_id)

    with llm_cursor() as cur:
        cur.execute(
            f"UPDATE model_prompt_config SET {', '.join(fields)} WHERE id = %s",
            tuple(values),
        )
        if cur.rowcount == 0:
            raise HTTPException(status_code=404, detail="Configuration introuvable")

    return {"status": "updated", "config_id": config_id}        
