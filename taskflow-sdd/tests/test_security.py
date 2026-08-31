import time

import jwt

from app.core.config import get_settings
from app.core.security import (
    create_access_token,
    decode_access_token,
    hash_password,
    verify_password,
)


def test_password_hash_is_never_plaintext() -> None:
    hashed = hash_password("mi-clave")
    assert hashed != "mi-clave"
    assert verify_password("mi-clave", hashed)


def test_password_hash_rejects_wrong_password() -> None:
    hashed = hash_password("mi-clave")
    assert not verify_password("otra-clave", hashed)


def test_create_and_decode_access_token() -> None:
    token = create_access_token(subject="user-123")
    assert decode_access_token(token) == "user-123"


def test_decode_rejects_invalid_token() -> None:
    assert decode_access_token("token-invalido") is None


def test_decode_rejects_expired_token() -> None:
    settings = get_settings()
    payload = {"sub": "user-123", "exp": int(time.time()) - 10}
    expired = jwt.encode(payload, settings.secret_key, algorithm="HS256")
    assert decode_access_token(expired) is None
