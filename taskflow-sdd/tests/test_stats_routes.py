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


def _create_completed_task(
    client: TestClient, token: str, project_id: uuid.UUID
) -> uuid.UUID:
    task_id = uuid.UUID(
        client.post(
            f"/projects/{project_id}/tasks",
            json={"title": "Repasar"},
            headers=_auth(token),
        ).json()["id"]
    )
    client.patch(
        f"/tasks/{task_id}", json={"status": "in_progress"}, headers=_auth(token)
    )
    client.patch(f"/tasks/{task_id}", json={"status": "done"}, headers=_auth(token))
    return task_id


def test_create_time_entry(client: TestClient) -> None:
    token = _register_and_login(client)
    response = client.post(
        "/time-entries",
        json={"minutes": 45},
        headers=_auth(token),
    )
    assert response.status_code == 201
    assert response.json()["minutes"] == 45


def test_create_time_entry_rejects_invalid_minutes(client: TestClient) -> None:
    token = _register_and_login(client)
    response = client.post(
        "/time-entries",
        json={"minutes": 0},
        headers=_auth(token),
    )
    assert response.status_code == 422


def test_stats_returns_streak_and_aggregates(client: TestClient) -> None:
    token = _register_and_login(client)
    project_id = _create_project(client, token)
    task_id = _create_completed_task(client, token, project_id)
    client.post(
        "/time-entries",
        json={"minutes": 60, "task_id": str(task_id)},
        headers=_auth(token),
    )

    stats = client.get("/stats", headers=_auth(token))

    assert stats.status_code == 200
    body = stats.json()
    assert body["streak"] >= 1
    assert body["tasks_completed"] >= 1
    assert body["minutes_total"] >= 60
