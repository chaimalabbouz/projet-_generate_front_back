"""Authentification du back-office : hash bcrypt + JWT.
Aucun accès base de données."""
import os
import time
import pytest

os.environ.setdefault("ADMIN_JWT_SECRET", "test-secret-for-ci")

from services.admin.auth import (
    hash_password, verify_password,
    create_access_token, create_refresh_token, decode_token,
)
from fastapi import HTTPException


def test_password_is_hashed_not_stored_plain():
    h = hash_password("MonMotDePasse123")
    assert h != "MonMotDePasse123"
    assert h.startswith("$2")            # préfixe bcrypt


def test_password_verification():
    h = hash_password("MonMotDePasse123")
    assert verify_password("MonMotDePasse123", h) is True
    assert verify_password("mauvais", h) is False


def test_same_password_gives_different_hashes():
    """bcrypt utilise un sel aléatoire."""
    assert hash_password("abc12345") != hash_password("abc12345")


def test_access_token_roundtrip():
    token = create_access_token("chaima")
    assert decode_token(token, "access") == "chaima"


def test_refresh_token_roundtrip():
    token = create_refresh_token("chaima")
    assert decode_token(token, "refresh") == "chaima"


def test_access_token_rejected_as_refresh():
    """Un access token ne doit pas servir de refresh token."""
    token = create_access_token("chaima")
    with pytest.raises(HTTPException):
        decode_token(token, "refresh")


def test_invalid_token_is_rejected():
    with pytest.raises(HTTPException):
        decode_token("ceci.nest.pas.un.token", "access")


def test_tampered_token_is_rejected():
    token = create_access_token("chaima")
    tampered = token[:-4] + "AAAA"
    with pytest.raises(HTTPException):
        decode_token(tampered, "access")