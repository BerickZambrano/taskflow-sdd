import uuid
from datetime import date

import pytest
from sqlalchemy.orm import Session

from app.core.database import SessionLocal
from app.core.enums import Priority, TaskStatus
from app.models.project import Project
from app.models.task import Task
from app.models.user import User
from app.repositories.task_repository import TaskRepository


@pytest.fixture()
def session() -> Session:
    db = SessionLocal()
    yield db
    db.close()


def _create_project(session: Session) -> uuid.UUID:
    owner = User(username="alice", email="alice@example.com", password_hash="hash")
    session.add(owner)
    session.flush()
    project = Project(name="Lanzamiento", owner_id=owner.id)
    session.add(project)
    session.flush()
    return project.id


def _create_task(
    session: Session,
    project_id: uuid.UUID,
    title: str,
    priority: Priority = Priority.MEDIUM,
    status: TaskStatus = TaskStatus.TODO,
    due_date: date | None = None,
) -> Task:
    task = Task(
        title=title,
        project_id=project_id,
        priority=priority,
        status=status,
        due_date=due_date,
    )
    session.add(task)
    session.flush()
    return task


def test_create_and_get_by_id(session: Session) -> None:
    project_id = _create_project(session)
    repo = TaskRepository(session)
    task = repo.create(
        project_id=project_id,
        title="Disenar landing",
        description="Diseno en Figma",
    )
    session.commit()

    fetched = repo.get_by_id(task.id)
    assert fetched is not None
    assert fetched.title == "Disenar landing"
    assert fetched.status == TaskStatus.TODO
    assert fetched.priority == Priority.MEDIUM


def test_has_incomplete(session: Session) -> None:
    project_id = _create_project(session)
    repo = TaskRepository(session)
    assert repo.has_incomplete(project_id) is False

    _create_task(session, project_id, "Pendiente", status=TaskStatus.TODO)
    session.commit()
    assert repo.has_incomplete(project_id) is True


def test_list_filters_by_status(session: Session) -> None:
    project_id = _create_project(session)
    repo = TaskRepository(session)
    _create_task(session, project_id, "T1", status=TaskStatus.TODO)
    _create_task(session, project_id, "T2", status=TaskStatus.DONE)
    session.commit()

    items, total = repo.list_by_project(project_id, status=TaskStatus.DONE)
    assert total == 1
    assert [t.title for t in items] == ["T2"]


def test_list_filters_by_priority(session: Session) -> None:
    project_id = _create_project(session)
    repo = TaskRepository(session)
    _create_task(session, project_id, "T1", priority=Priority.HIGH)
    _create_task(session, project_id, "T2", priority=Priority.LOW)
    session.commit()

    items, total = repo.list_by_project(project_id, priority=Priority.LOW)
    assert total == 1
    assert [t.title for t in items] == ["T2"]


def test_list_orders_by_priority_asc(session: Session) -> None:
    project_id = _create_project(session)
    repo = TaskRepository(session)
    _create_task(session, project_id, "Alta", priority=Priority.HIGH)
    _create_task(session, project_id, "Baja", priority=Priority.LOW)
    _create_task(session, project_id, "Media", priority=Priority.MEDIUM)
    session.commit()

    items, total = repo.list_by_project(project_id, sort_by="priority")
    assert total == 3
    assert [t.title for t in items] == ["Baja", "Media", "Alta"]


def test_list_orders_by_priority_desc(session: Session) -> None:
    project_id = _create_project(session)
    repo = TaskRepository(session)
    _create_task(session, project_id, "Alta", priority=Priority.HIGH)
    _create_task(session, project_id, "Baja", priority=Priority.LOW)
    session.commit()

    items, _ = repo.list_by_project(project_id, sort_by="priority", order="desc")
    assert [t.title for t in items] == ["Alta", "Baja"]


def test_list_orders_by_due_date_with_nulls_last(session: Session) -> None:
    project_id = _create_project(session)
    repo = TaskRepository(session)
    _create_task(session, project_id, "Tarde", due_date=date(2026, 9, 30))
    _create_task(session, project_id, "Sin fecha")
    _create_task(session, project_id, "Pronto", due_date=date(2026, 9, 15))
    session.commit()

    items, _ = repo.list_by_project(project_id, sort_by="due_date")
    assert [t.title for t in items] == ["Pronto", "Tarde", "Sin fecha"]


def test_list_paginates(session: Session) -> None:
    project_id = _create_project(session)
    repo = TaskRepository(session)
    for i in range(5):
        _create_task(session, project_id, f"T{i}")
    session.commit()

    page1, total = repo.list_by_project(project_id, page=1, page_size=2)
    page2, _ = repo.list_by_project(project_id, page=2, page_size=2)
    page3, _ = repo.list_by_project(project_id, page=3, page_size=2)

    assert total == 5
    assert len(page1) == 2
    assert len(page2) == 2
    assert len(page3) == 1


def test_delete_removes_task(session: Session) -> None:
    project_id = _create_project(session)
    repo = TaskRepository(session)
    task = _create_task(session, project_id, "T1")
    session.commit()

    repo.delete(task)
    session.commit()

    assert repo.get_by_id(task.id) is None
