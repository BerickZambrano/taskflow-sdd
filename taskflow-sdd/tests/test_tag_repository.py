import pytest
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.database import SessionLocal
from app.core.enums import ProjectStatus
from app.models.project import Project
from app.models.task import Task
from app.models.user import User
from app.repositories.tag_repository import TagRepository


@pytest.fixture()
def session() -> Session:
    db = SessionLocal()
    yield db
    db.close()


def _create_task(session: Session) -> Task:
    owner = User(username="alice", email="alice@example.com", password_hash="hash")
    session.add(owner)
    session.flush()
    project = Project(
        name="Lanzamiento", owner_id=owner.id, status=ProjectStatus.ACTIVE
    )
    session.add(project)
    session.flush()
    task = Task(title="Estudiar", project_id=project.id)
    session.add(task)
    session.flush()
    return task


def test_create_get_and_list_tags(session: Session) -> None:
    repo = TagRepository(session)
    tag = repo.create("Matemáticas", "#C4553A")
    session.commit()

    assert tag.id is not None
    assert repo.get_by_name("matemáticas") is not None
    assert len(repo.list_all()) == 1


def test_tag_name_unique_case_insensitive(session: Session) -> None:
    repo = TagRepository(session)
    repo.create("Matemáticas", "#C4553A")
    session.commit()

    with pytest.raises(IntegrityError):
        repo.create("matemáticas", "#A93F26")
    session.rollback()


def test_assign_and_remove_tag_to_task(session: Session) -> None:
    repo = TagRepository(session)
    task = _create_task(session)
    tag = repo.create("Estudio", "#4A7C59")
    session.commit()

    repo.assign_tag(task, tag)
    session.commit()
    assert repo.assigned_tags(task) == [tag]

    repo.remove_tag(task, tag)
    session.commit()
    assert repo.assigned_tags(task) == []


def test_assign_same_tag_twice_is_idempotent(session: Session) -> None:
    repo = TagRepository(session)
    task = _create_task(session)
    tag = repo.create("Estudio", "#4A7C59")
    session.commit()

    repo.assign_tag(task, tag)
    repo.assign_tag(task, tag)
    session.commit()

    assert len(repo.assigned_tags(task)) == 1


def test_delete_tag_removes_links(session: Session) -> None:
    repo = TagRepository(session)
    task = _create_task(session)
    tag = repo.create("Estudio", "#4A7C59")
    session.commit()
    repo.assign_tag(task, tag)
    session.commit()

    repo.delete(tag)
    session.commit()

    assert repo.get_by_id(tag.id) is None
    assert repo.assigned_tags(task) == []
