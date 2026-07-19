"""
Authentification JWT du back-office.

- mots de passe hashés en bcrypt (jamais stockés en clair)
- access token court (30 min) + refresh token long (7 jours)
- toute route protégée passe par `require_admin`
"""
import os
from datetime import datetime, timedelta, timezone
from typing import Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext

from services.admin.db import moonpilot_cursor


# ---------------- CONFIG ----------------
SECRET_KEY = os.getenv("ADMIN_JWT_SECRET", "CHANGE-ME-IN-ENV")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 7

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/admin/login")


# ---------------- MOTS DE PASSE ----------------
def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)


# ---------------- TOKENS ----------------
def _create_token(data: dict, expires: timedelta, token_type: str) -> str:
    payload = data.copy()
    payload.update({
        "exp": datetime.now(timezone.utc) + expires,
        "iat": datetime.now(timezone.utc),
        "type": token_type,
    })
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def create_access_token(username: str) -> str:
    return _create_token(
        {"sub": username},
        timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
        "access",
    )


def create_refresh_token(username: str) -> str:
    return _create_token(
        {"sub": username},
        timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS),
        "refresh",
    )


def decode_token(token: str, expected_type: str = "access") -> str:
    """Renvoie le username, ou lève une 401."""
    credentials_error = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Token invalide ou expiré",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except JWTError:
        raise credentials_error

    if payload.get("type") != expected_type:
        raise credentials_error

    username = payload.get("sub")
    if not username:
        raise credentials_error

    return username


# ---------------- ACCÈS BASE ----------------
def get_admin_by_username(username: str) -> Optional[dict]:
    with moonpilot_cursor() as cur:
        cur.execute(
            "SELECT id, username, email, password_hash, is_active "
            "FROM admins WHERE username = %s",
            (username,),
        )
        return cur.fetchone()


def authenticate_admin(username: str, password: str) -> Optional[dict]:
    admin = get_admin_by_username(username)
    if not admin:
        return None
    if not admin["is_active"]:
        return None
    if not verify_password(password, admin["password_hash"]):
        return None
    return admin


def touch_last_login(username: str) -> None:
    with moonpilot_cursor() as cur:
        cur.execute(
            "UPDATE admins SET last_login = NOW() WHERE username = %s",
            (username,),
        )


# ---------------- DÉPENDANCE DE PROTECTION ----------------
def require_admin(token: str = Depends(oauth2_scheme)) -> dict:
    """À mettre en Depends sur toute route protégée."""
    username = decode_token(token, "access")
    admin = get_admin_by_username(username)

    if not admin or not admin["is_active"]:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Compte introuvable ou désactivé",
        )

    admin.pop("password_hash", None)   # ne jamais le laisser fuiter
    return admin