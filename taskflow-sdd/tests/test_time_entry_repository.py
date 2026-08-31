from datetime import date

import pytest
from sqlalchemy.orm import Session

from app.core.database import SessionLocal
from app.models.task import Task
from app.repositories.time_entry_repository import TimeEntryRepository


@pytest.fixture()
def session() -> Session:
    db = SessionLocal()
    yield db
    db.close()


def _create_task(session: Session) -> Task:
    from app.core.enums import ProjectStatus
    from app.models.project import Project
    from app.models.user import User

    owner = User(username="alice", email="alice@example.com", password_hash="hash")
    session.add(owner)
    session.flush()
    project = Project(name="Estudios", owner_id=owner.id, status=ProjectStatus.ACTIVE)
    session.add(project)
    session.flush()
    task = Task(title="Repasar", project_id=project.id)
    session.add(task)
    session.flush()
    return task


def test_create_time_entry(session: Session) -> None:
    repo = TimeEntryRepository(session)
    entry = repo.create(minutes=45, entry_date=date(2026, 8, 31))
    session.commit()

    assert entry.id is not None
    assert entry.minutes == 45


def test_create_time_entry_with_task(session: Session) -> None:
    task = _create_task(session)
    repo = TimeEntryRepository(session)
    entry = repo.create(minutes=30, entry_date=date(2026, 8, 31), task_id=task.id)
    session.commit()

    assert entry.task_id == task.id


def test_list_between_filters_and_orders(session: Session) -> None:
    repo = TimeEntryRepository(session)
    repo.create(minutes=20, entry_date=date(2026, 8, 30))
    repo.create(minutes=30, entry_date=date(2026, 8, 31))
    repo.create(minutes=40, entry_date=date(2026, 9, 2))
    session.commit()

    entries = repo.list_between(start=date(2026, 8, 31), end=date(2026, 9, 2))
    assert [e.entry_date for e in entries] == [date(2026, 8, 31), date(2026, 9, 2)]
