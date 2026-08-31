import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.core.exceptions import (
    ConflictError,
    NotFoundError,
    UnauthorizedError,
    register_exception_handlers,
)


@pytest.fixture()
def client() -> TestClient:
    app = FastAPI()
    register_exception_handlers(app)

    @app.get("/raise/not-found")
    def raise_not_found() -> None:
        raise NotFoundError("El proyecto no existe.")

    @app.get("/raise/conflict")
    def raise_conflict() -> None:
        raise ConflictError("Ya existe un proyecto con ese nombre.")

    @app.get("/raise/unauthorized")
    def raise_unauthorized() -> None:
        raise UnauthorizedError("Credenciales incorrectas.")

    return TestClient(app)


def test_not_found_error(client: TestClient) -> None:
    response = client.get("/raise/not-found")
    assert response.status_code == 404
    assert response.json() == {"detail": "El proyecto no existe."}


def test_conflict_error(client: TestClient) -> None:
    response = client.get("/raise/conflict")
    assert response.status_code == 409
    assert response.json() == {"detail": "Ya existe un proyecto con ese nombre."}


def test_unauthorized_error(client: TestClient) -> None:
    response = client.get("/raise/unauthorized")
    assert response.status_code == 401
    assert response.json() == {"detail": "Credenciales incorrectas."}
