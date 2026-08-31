import os

os.environ.setdefault(
    "DATABASE_URL",
    "postgresql+psycopg://taskflow:taskflow@localhost:5432/taskflow_test",
)
os.environ.setdefault("SECRET_KEY", "test-secret-key-longer-than-thirty-two-bytes")

from collections.abc import Callable

import pytest
from alembic.config import Config as AlembicConfig
from fastapi.testclient import TestClient
from sqlalchemy import text

from alembic import command
from app.core.config import get_settings
from app.core.database import engine
from app.main import app


def _apply_migrations() -> None:
    config = AlembicConfig("alembic.ini")
    config.set_main_option("sqlalchemy.url", get_settings().database_url)
    command.upgrade(config, "head")


@pytest.fixture(scope="session", autouse=True)
def _database() -> None:
    _apply_migrations()
    yield


@pytest.fixture(autouse=True)
def _clean_database() -> None:
    yield
    with engine.begin() as conn:
        conn.execute(
            text("TRUNCATE TABLE tasks, projects, users RESTART IDENTITY CASCADE")
        )


@pytest.fixture()
def client() -> TestClient:
    return TestClient(app)


@pytest.fixture()
def auth_token(client: TestClient) -> Callable[[str], str]:
    def _make(username: str = "alice") -> str:
        client.post(
            "/auth/register",
            json={
                "username": username,
                "email": f"{username}@example.com",
                "password": "clave-secreta",
            },
        )
        response = client.post(
            "/auth/login",
            json={"identifier": username, "password": "clave-secreta"},
        )
        return response.json()["access_token"]

    return _make


@pytest.fixture()
def authenticated_client(
    client: TestClient, auth_token: Callable[[str], str]
) -> TestClient:
    token = auth_token()
    client.headers.update({"Authorization": f"Bearer {token}"})
    return client
