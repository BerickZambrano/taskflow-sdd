import uuid
from datetime import date, datetime, timedelta

import pytest

from app.core.database import SessionLocal
from app.core.enums import ProjectStatus, TaskStatus
from app.core.security import hash_password
from app.models.project import Project
from app.models.tag import Tag
from app.models.task import Task
from app.models.user import User
from app.repositories.time_entry_repository import TimeEntryRepository
from app.services.stats_service import StatsService


@pytest.fixture()
def session():
    db = SessionLocal()
    yield db
    db.close()


def _setup_project_with_tag(session) -> tuple[uuid.UUID, Tag]:
    owner = User(
        username="alice", email="alice@example.com", password_hash=hash_password("x")
    )
    session.add(owner)
    session.flush()
    project = Project(name="Estudios", owner_id=owner.id, status=ProjectStatus.ACTIVE)
    session.add(project)
    session.flush()
    tag = Tag(name="Matemáticas", color="#C4553A")
    session.add(tag)
    session.flush()
    return project.id, tag


def _complete_task(session, project_id, due: date, tag: Tag | None = None) -> Task:
    task = Task(title="Tarea", project_id=project_id, status=TaskStatus.DONE)
    task.id = uuid.uuid4()
    task.completed_at = datetime.combine(due, datetime.min.time())
    if tag is not None:
        task.tags.append(tag)
    session.add(task)
    session.flush()
    return task


def test_streak_continuous_days(session) -> None:
    project_id, _ = _setup_project_with_tag(session)
    today = date.today()
    for back in (0, 1, 2):
        _complete_task(session, project_id, today - timedelta(days=back))
    session.commit()

    stats = StatsService(session, TimeEntryRepository(session)).get_stats()

    assert stats["streak"] == 3  # hoy + 2 anteriores


def test_streak_gives_grace_for_today(session) -> None:
    project_id, _ = _setup_project_with_tag(session)
    today = date.today()
    _complete_task(session, project_id, today - timedelta(days=1))
    _complete_task(session, project_id, today - timedelta(days=2))
    session.commit()

    stats = StatsService(session, TimeEntryRepository(session)).get_stats()

    # sin actividad hoy, pero ayer y anteayer sí -> racha 2
    assert stats["streak"] == 2


def test_streak_zero_without_completions(session) -> None:
    project_id, _ = _setup_project_with_tag(session)
    session.commit()

    stats = StatsService(session, TimeEntryRepository(session)).get_stats()

    assert stats["streak"] == 0
    assert stats["tasks_completed"] == 0


def test_streak_stops_at_gap(session) -> None:
    project_id, _ = _setup_project_with_tag(session)
    today = date.today()
    _complete_task(session, project_id, today)
    _complete_task(session, project_id, today - timedelta(days=2))
    session.commit()

    stats = StatsService(session, TimeEntryRepository(session)).get_stats()

    assert stats["streak"] == 1  # hueco ayer -> se detiene


def test_aggregates_time_by_tag_and_project(session) -> None:
    project_id, tag = _setup_project_with_tag(session)
    task = _complete_task(session, project_id, date.today(), tag)
    session.commit()
    repo = TimeEntryRepository(session)
    repo.create(minutes=30, entry_date=date.today(), task_id=task.id)
    repo.create(minutes=20, entry_date=date.today(), task_id=task.id)
    repo.commit()

    stats = StatsService(session, TimeEntryRepository(session)).get_stats()

    assert stats["minutes_total"] == 50
    assert stats["days_studied"] >= 1
    assert any(
        t["name"] == "Matemáticas" and t["minutes"] == 50
        for t in stats["minutes_by_tag"]
    )
