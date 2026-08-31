from uuid import UUID

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.core.database import SessionLocal
from app.core.enums import TaskStatus
from app.models.task import Task


def _register_and_login(client: TestClient, username: str = "alice") -> str:
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


def _auth(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


def _add_task(project_id: UUID, status: TaskStatus = TaskStatus.TODO) -> None:
    db: Session = SessionLocal()
    db.add(Task(title="Tarea", project_id=project_id, status=status))
    db.commit()
    db.close()


def _create_project(client: TestClient, token: str, name: str = "Lanzamiento") -> UUID:
    response = client.post(
        "/projects",
        json={"name": name, "description": "Descripción"},
        headers=_auth(token),
    )
    return UUID(response.json()["id"])


def test_create_project_returns_201(client: TestClient) -> None:
    token = _register_and_login(client)
    response = client.post(
        "/projects",
        json={"name": "Lanzamiento", "description": "Descripción"},
        headers=_auth(token),
    )
    assert response.status_code == 201
    body = response.json()
    assert body["name"] == "Lanzamiento"
    assert body["status"] == "active"


def test_create_project_duplicate_name_returns_409(client: TestClient) -> None:
    token = _register_and_login(client)
    payload = {"name": "Lanzamiento", "description": None}
    client.post("/projects", json=payload, headers=_auth(token))
    response = client.post("/projects", json=payload, headers=_auth(token))
    assert response.status_code == 409
    assert response.json()["detail"] == "Ya existe un proyecto con ese nombre."


def test_create_project_duplicate_name_case_insensitive_returns_409(
    client: TestClient,
) -> None:
    token = _register_and_login(client)
    client.post(
        "/projects",
        json={"name": "Lanzamiento", "description": None},
        headers=_auth(token),
    )
    response = client.post(
        "/projects",
        json={"name": "lanzamiento", "description": None},
        headers=_auth(token),
    )
    assert response.status_code == 409


def test_list_projects_returns_200(client: TestClient) -> None:
    token = _register_and_login(client)
    _create_project(client, token)
    response = client.get("/projects", headers=_auth(token))
    assert response.status_code == 200
    assert len(response.json()) == 1


def test_get_project_returns_200(client: TestClient) -> None:
    token = _register_and_login(client)
    project_id = _create_project(client, token)
    response = client.get(f"/projects/{project_id}", headers=_auth(token))
    assert response.status_code == 200
    assert response.json()["id"] == str(project_id)


def test_get_nonexistent_project_returns_404(client: TestClient) -> None:
    token = _register_and_login(client)
    response = client.get(f"/projects/{UUID(int=1)}", headers=_auth(token))
    assert response.status_code == 404
    assert response.json()["detail"] == "El proyecto no existe."


def test_get_other_users_project_returns_404(client: TestClient) -> None:
    token_a = _register_and_login(client, "alice")
    project_id = _create_project(client, token_a)
    token_b = _register_and_login(client, "bob")

    response = client.get(f"/projects/{project_id}", headers=_auth(token_b))

    assert response.status_code == 404


def test_update_project_name_returns_200(client: TestClient) -> None:
    token = _register_and_login(client)
    project_id = _create_project(client, token)
    response = client.patch(
        f"/projects/{project_id}",
        json={"name": "Renombrado"},
        headers=_auth(token),
    )
    assert response.status_code == 200
    assert response.json()["name"] == "Renombrado"


def test_update_project_description_returns_200(client: TestClient) -> None:
    token = _register_and_login(client)
    project_id = _create_project(client, token)
    response = client.patch(
        f"/projects/{project_id}",
        json={"description": "Nueva descripción"},
        headers=_auth(token),
    )
    assert response.status_code == 200
    assert response.json()["description"] == "Nueva descripción"


def test_update_project_duplicate_name_returns_409(client: TestClient) -> None:
    token = _register_and_login(client)
    first = _create_project(client, token, "Primero")
    _create_project(client, token, "Segundo")
    response = client.patch(
        f"/projects/{first}",
        json={"name": "Segundo"},
        headers=_auth(token),
    )
    assert response.status_code == 409


def test_delete_project_with_incomplete_tasks_returns_409(client: TestClient) -> None:
    token = _register_and_login(client)
    project_id = _create_project(client, token)
    _add_task(project_id, TaskStatus.TODO)

    response = client.delete(f"/projects/{project_id}", headers=_auth(token))

    assert response.status_code == 409
    assert (
        response.json()["detail"]
        == "Todas las tareas deben estar completadas para inactivar el proyecto."
    )


def test_delete_project_all_tasks_done_returns_204(client: TestClient) -> None:
    token = _register_and_login(client)
    project_id = _create_project(client, token)
    _add_task(project_id, TaskStatus.DONE)

    response = client.delete(f"/projects/{project_id}", headers=_auth(token))

    assert response.status_code == 204
    detail = client.get(f"/projects/{project_id}", headers=_auth(token))
    assert detail.status_code == 200
    assert detail.json()["status"] == "inactive"


def test_projects_require_auth_returns_401(client: TestClient) -> None:
    response = client.get("/projects")
    assert response.status_code == 401
