import uuid

from fastapi.testclient import TestClient


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


def _create_project(client: TestClient, token: str) -> uuid.UUID:
    response = client.post(
        "/projects",
        json={"name": "Estudios", "description": None},
        headers=_auth(token),
    )
    return uuid.UUID(response.json()["id"])


def _create_task(client: TestClient, token: str, project_id: uuid.UUID) -> uuid.UUID:
    response = client.post(
        f"/projects/{project_id}/tasks",
        json={"title": "Repasar"},
        headers=_auth(token),
    )
    return uuid.UUID(response.json()["id"])


def test_create_and_list_tag(client: TestClient) -> None:
    token = _register_and_login(client)
    response = client.post("/tags", json={"name": "Matemáticas"}, headers=_auth(token))
    assert response.status_code == 201
    assert response.json()["name"] == "Matemáticas"
    assert response.json()["color"]

    listing = client.get("/tags", headers=_auth(token))
    assert listing.status_code == 200
    assert len(listing.json()) == 1


def test_create_duplicate_tag_returns_409(client: TestClient) -> None:
    token = _register_and_login(client)
    client.post("/tags", json={"name": "Estudio"}, headers=_auth(token))
    response = client.post("/tags", json={"name": "estudio"}, headers=_auth(token))
    assert response.status_code == 409
    assert response.json()["detail"] == "Ya existe una etiqueta con ese nombre."


def test_assign_and_remove_tag_to_task(client: TestClient) -> None:
    token = _register_and_login(client)
    project_id = _create_project(client, token)
    task_id = _create_task(client, token, project_id)
    tag_id = uuid.UUID(
        client.post("/tags", json={"name": "Estudio"}, headers=_auth(token)).json()[
            "id"
        ]
    )

    assign = client.post(
        f"/tasks/{task_id}/tags",
        json={"tag_id": str(tag_id)},
        headers=_auth(token),
    )
    assert assign.status_code == 201

    detail = client.get(f"/tasks/{task_id}", headers=_auth(token))
    assert [t["name"] for t in detail.json()["tags"]] == ["Estudio"]

    remove = client.delete(f"/tasks/{task_id}/tags/{tag_id}", headers=_auth(token))
    assert remove.status_code == 200
    assert client.get(f"/tasks/{task_id}", headers=_auth(token)).json()["tags"] == []


def test_filter_tasks_by_tag(client: TestClient) -> None:
    token = _register_and_login(client)
    project_id = _create_project(client, token)
    task_a = _create_task(client, token, project_id)
    _create_task(client, token, project_id)
    tag_id = uuid.UUID(
        client.post("/tags", json={"name": "Física"}, headers=_auth(token)).json()["id"]
    )
    client.post(
        f"/tasks/{task_a}/tags", json={"tag_id": str(tag_id)}, headers=_auth(token)
    )

    listing = client.get(
        f"/projects/{project_id}/tasks?tag_id={tag_id}", headers=_auth(token)
    )
    assert listing.status_code == 200
    assert listing.json()["total"] == 1
    assert listing.json()["items"][0]["id"] == str(task_a)


def test_delete_tag_returns_204(client: TestClient) -> None:
    token = _register_and_login(client)
    tag_id = uuid.UUID(
        client.post("/tags", json={"name": "Idiomas"}, headers=_auth(token)).json()[
            "id"
        ]
    )
    response = client.delete(f"/tags/{tag_id}", headers=_auth(token))
    assert response.status_code == 204
    assert client.get("/tags", headers=_auth(token)).json() == []
