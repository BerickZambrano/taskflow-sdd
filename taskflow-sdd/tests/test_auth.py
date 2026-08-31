from collections.abc import Callable

from fastapi import Depends, FastAPI
from fastapi.testclient import TestClient

from app.api.deps import get_current_user
from app.core.exceptions import register_exception_handlers
from app.models.user import User


def _protected_app() -> FastAPI:
    app = FastAPI()
    register_exception_handlers(app)

    @app.get("/protected")
    def protected(user: User = Depends(get_current_user)) -> dict[str, str]:
        return {"id": str(user.id)}

    return app


def test_register_creates_account(client: TestClient) -> None:
    response = client.post(
        "/auth/register",
        json={
            "username": "alice",
            "email": "alice@example.com",
            "password": "clave-secreta",
        },
    )
    assert response.status_code == 201
    assert response.json()["username"] == "alice"
    assert "password_hash" not in response.json()


def test_register_rejects_duplicate_username(client: TestClient) -> None:
    payload = {
        "username": "alice",
        "email": "alice@example.com",
        "password": "clave-secreta",
    }
    client.post("/auth/register", json=payload)
    response = client.post("/auth/register", json=payload)
    assert response.status_code == 409
    assert response.json()["detail"] == "El nombre de usuario ya está en uso."


def test_register_rejects_duplicate_email(client: TestClient) -> None:
    client.post(
        "/auth/register",
        json={
            "username": "alice",
            "email": "alice@example.com",
            "password": "clave-secreta",
        },
    )
    response = client.post(
        "/auth/register",
        json={
            "username": "bob",
            "email": "alice@example.com",
            "password": "clave-secreta",
        },
    )
    assert response.status_code == 409
    assert response.json()["detail"] == "El correo electrónico ya está registrado."


def test_login_returns_access_token(
    client: TestClient, auth_token: Callable[[str], str]
) -> None:
    auth_token()
    response = client.post(
        "/auth/login",
        json={"identifier": "alice", "password": "clave-secreta"},
    )
    assert response.status_code == 200
    assert response.json()["token_type"] == "bearer"
    assert response.json()["access_token"]


def test_login_rejects_wrong_credentials(
    client: TestClient, auth_token: Callable[[str], str]
) -> None:
    auth_token()
    response = client.post(
        "/auth/login",
        json={"identifier": "alice", "password": "clave-incorrecta"},
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Credenciales incorrectas."


def test_protected_route_without_token_returns_401() -> None:
    client = TestClient(_protected_app())
    assert client.get("/protected").status_code == 401


def test_protected_route_with_invalid_token_returns_401() -> None:
    client = TestClient(_protected_app())
    response = client.get(
        "/protected", headers={"Authorization": "Bearer token-invalido"}
    )
    assert response.status_code == 401


def test_protected_route_with_valid_token_returns_200(
    auth_token: Callable[[str], str],
) -> None:
    token = auth_token()
    client = TestClient(_protected_app())
    response = client.get("/protected", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
