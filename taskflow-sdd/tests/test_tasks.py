from uuid import UUID

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


def _create_project(client: TestClient, token: str) -> UUID:
    response = client.post(
        "/projects",
        json={"name": "Lanzamiento", "description": None},
        headers=_auth(token),
    )
    return UUID(response.json()["id"])


def _create_task(
    client: TestClient, token: str, project_id: UUID, title: str = "Tarea"
) -> UUID:
    response = client.post(
        f"/projects/{project_id}/tasks",
        json={"title": title},
        headers=_auth(token),
    )
    assert response.status_code == 201
    return UUID(response.json()["id"])


def _transition_to_done(client: TestClient, token: str, task_id: UUID) -> None:
    client.patch(
        f"/tasks/{task_id}",
        json={"status": "in_progress"},
        headers=_auth(token),
    )
    client.patch(
        f"/tasks/{task_id}",
        json={"status": "done"},
        headers=_auth(token),
    )


def test_create_task_returns_201_with_defaults(client: TestClient) -> None:
    token = _register_and_login(client)
    project_id = _create_project(client, token)

    response = client.post(
        f"/projects/{project_id}/tasks",
        json={"title": "Disenar landing"},
        headers=_auth(token),
    )

    assert response.status_code == 201
    body = response.json()
    assert body["title"] == "Disenar landing"
    assert body["status"] == "todo"
    assert body["priority"] == "medium"
    assert body["project_id"] == str(project_id)


def test_create_task_with_priority_and_due_date(client: TestClient) -> None:
    token = _register_and_login(client)
    project_id = _create_project(client, token)

    response = client.post(
        f"/projects/{project_id}/tasks",
        json={"title": "Tarea alta", "priority": "high", "due_date": "2026-09-30"},
        headers=_auth(token),
    )

    assert response.status_code == 201
    assert response.json()["priority"] == "high"
    assert response.json()["due_date"] == "2026-09-30"


def test_create_task_nonexistent_project_returns_404(client: TestClient) -> None:
    token = _register_and_login(client)
    response = client.post(
        f"/projects/{UUID(int=1)}/tasks",
        json={"title": "Tarea"},
        headers=_auth(token),
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "El proyecto no existe."


def test_create_task_other_owners_project_returns_404(client: TestClient) -> None:
    token_a = _register_and_login(client, "alice")
    project_id = _create_project(client, token_a)
    token_b = _register_and_login(client, "bob")

    response = client.post(
        f"/projects/{project_id}/tasks",
        json={"title": "Tarea"},
        headers=_auth(token_b),
    )

    assert response.status_code == 404


def test_list_tasks_returns_paginated_structure(client: TestClient) -> None:
    token = _register_and_login(client)
    project_id = _create_project(client, token)
    _create_task(client, token, project_id, "T1")
    _create_task(client, token, project_id, "T2")

    response = client.get(f"/projects/{project_id}/tasks", headers=_auth(token))

    assert response.status_code == 200
    body = response.json()
    assert body["total"] == 2
    assert body["page"] == 1
    assert body["page_size"] == 20
    assert len(body["items"]) == 2


def test_list_tasks_filters_by_status(client: TestClient) -> None:
    token = _register_and_login(client)
    project_id = _create_project(client, token)
    task_id = _create_task(client, token, project_id, "T1")
    _transition_to_done(client, token, task_id)

    response = client.get(
        f"/projects/{project_id}/tasks?status=done", headers=_auth(token)
    )

    assert response.status_code == 200
    assert response.json()["total"] == 1


def test_list_tasks_orders_by_priority(client: TestClient) -> None:
    token = _register_and_login(client)
    project_id = _create_project(client, token)
    client.post(
        f"/projects/{project_id}/tasks",
        json={"title": "Alta", "priority": "high"},
        headers=_auth(token),
    )
    client.post(
        f"/projects/{project_id}/tasks",
        json={"title": "Baja", "priority": "low"},
        headers=_auth(token),
    )

    response = client.get(
        f"/projects/{project_id}/tasks?sort_by=priority&order=asc",
        headers=_auth(token),
    )

    titles = [item["title"] for item in response.json()["items"]]
    assert titles == ["Baja", "Alta"]


def test_list_tasks_filters_by_priority(client: TestClient) -> None:
    token = _register_and_login(client)
    project_id = _create_project(client, token)
    client.post(
        f"/projects/{project_id}/tasks",
        json={"title": "Alta", "priority": "high"},
        headers=_auth(token),
    )
    client.post(
        f"/projects/{project_id}/tasks",
        json={"title": "Baja", "priority": "low"},
        headers=_auth(token),
    )

    response = client.get(
        f"/projects/{project_id}/tasks?priority=high", headers=_auth(token)
    )

    assert response.status_code == 200
    assert response.json()["total"] == 1
    assert response.json()["items"][0]["title"] == "Alta"


def test_list_tasks_paginates(client: TestClient) -> None:
    token = _register_and_login(client)
    project_id = _create_project(client, token)
    for i in range(3):
        _create_task(client, token, project_id, f"T{i}")

    response = client.get(
        f"/projects/{project_id}/tasks?page=1&page_size=2", headers=_auth(token)
    )
    page_two = client.get(
        f"/projects/{project_id}/tasks?page=2&page_size=2", headers=_auth(token)
    )

    assert response.json()["total"] == 3
    assert len(response.json()["items"]) == 2
    assert len(page_two.json()["items"]) == 1


def test_list_tasks_invalid_status_returns_422(client: TestClient) -> None:
    token = _register_and_login(client)
    project_id = _create_project(client, token)
    response = client.get(
        f"/projects/{project_id}/tasks?status=bloqueada", headers=_auth(token)
    )
    assert response.status_code == 422


def test_list_tasks_nonexistent_project_returns_404(client: TestClient) -> None:
    token = _register_and_login(client)
    response = client.get(f"/projects/{UUID(int=1)}/tasks", headers=_auth(token))
    assert response.status_code == 404


def test_get_task_returns_200(client: TestClient) -> None:
    token = _register_and_login(client)
    project_id = _create_project(client, token)
    task_id = _create_task(client, token, project_id)

    response = client.get(f"/tasks/{task_id}", headers=_auth(token))

    assert response.status_code == 200
    assert response.json()["id"] == str(task_id)


def test_get_task_nonexistent_returns_404(client: TestClient) -> None:
    token = _register_and_login(client)
    response = client.get(f"/tasks/{UUID(int=1)}", headers=_auth(token))
    assert response.status_code == 404


def test_get_task_other_owner_returns_404(client: TestClient) -> None:
    token_a = _register_and_login(client, "alice")
    project_id = _create_project(client, token_a)
    task_id = _create_task(client, token_a, project_id)
    token_b = _register_and_login(client, "bob")

    response = client.get(f"/tasks/{task_id}", headers=_auth(token_b))

    assert response.status_code == 404


def test_patch_task_returns_200(client: TestClient) -> None:
    token = _register_and_login(client)
    project_id = _create_project(client, token)
    task_id = _create_task(client, token, project_id)

    response = client.patch(
        f"/tasks/{task_id}",
        json={"title": "Renombrada"},
        headers=_auth(token),
    )

    assert response.status_code == 200
    assert response.json()["title"] == "Renombrada"


def test_patch_task_clears_description(client: TestClient) -> None:
    token = _register_and_login(client)
    project_id = _create_project(client, token)
    task_id = _create_task(client, token, project_id)
    client.patch(
        f"/tasks/{task_id}",
        json={"description": "Algo"},
        headers=_auth(token),
    )

    response = client.patch(
        f"/tasks/{task_id}",
        json={"description": None},
        headers=_auth(token),
    )

    assert response.status_code == 200
    assert response.json()["description"] is None


def test_patch_done_task_blocked_returns_409(client: TestClient) -> None:
    token = _register_and_login(client)
    project_id = _create_project(client, token)
    task_id = _create_task(client, token, project_id)
    _transition_to_done(client, token, task_id)

    response = client.patch(
        f"/tasks/{task_id}",
        json={"title": "Cambio"},
        headers=_auth(token),
    )

    assert response.status_code == 409
    assert response.json()["detail"] == "No se puede modificar una tarea completada."


def test_patch_valid_transition_returns_200(client: TestClient) -> None:
    token = _register_and_login(client)
    project_id = _create_project(client, token)
    task_id = _create_task(client, token, project_id)

    response = client.patch(
        f"/tasks/{task_id}",
        json={"status": "in_progress"},
        headers=_auth(token),
    )

    assert response.status_code == 200
    assert response.json()["status"] == "in_progress"


def test_patch_invalid_transition_returns_409(client: TestClient) -> None:
    token = _register_and_login(client)
    project_id = _create_project(client, token)
    task_id = _create_task(client, token, project_id)

    response = client.patch(
        f"/tasks/{task_id}",
        json={"status": "done"},
        headers=_auth(token),
    )

    assert response.status_code == 409
    assert response.json()["detail"] == "No se puede retroceder el estado de la tarea."


def test_delete_task_returns_204(client: TestClient) -> None:
    token = _register_and_login(client)
    project_id = _create_project(client, token)
    task_id = _create_task(client, token, project_id)

    response = client.delete(f"/tasks/{task_id}", headers=_auth(token))

    assert response.status_code == 204
    assert client.get(f"/tasks/{task_id}", headers=_auth(token)).status_code == 404


def test_delete_task_nonexistent_returns_404(client: TestClient) -> None:
    token = _register_and_login(client)
    response = client.delete(f"/tasks/{UUID(int=1)}", headers=_auth(token))
    assert response.status_code == 404


def test_tasks_require_auth_returns_401(client: TestClient) -> None:
    response = client.get("/projects/00000000-0000-0000-0000-000000000000/tasks")
    assert response.status_code == 401
