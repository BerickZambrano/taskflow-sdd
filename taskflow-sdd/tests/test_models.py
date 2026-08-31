import pytest
from sqlalchemy.orm import Session

from app.core.database import SessionLocal
from app.core.enums import Priority, ProjectStatus, TaskStatus
from app.models.project import Project
from app.models.task import Task
from app.models.user import User


@pytest.fixture()
def session() -> Session:
    db = SessionLocal()
    yield db
    db.close()


def test_models_created_and_persist(session: Session) -> None:
    user = User(username="alice", email="alice@example.com", password_hash="hash")
    session.add(user)
    session.flush()

    project = Project(
        name="Lanzamiento web",
        description="Proyecto del sitio publico",
        owner_id=user.id,
    )
    session.add(project)
    session.flush()

    task = Task(
        title="Disenar landing",
        description="Diseno en Figma",
        project_id=project.id,
    )
    session.add(task)
    session.commit()

    stored_user = session.get(User, user.id)
    stored_project = session.get(Project, project.id)
    stored_task = session.get(Task, task.id)

    assert stored_user is not None
    assert stored_project is not None
    assert stored_project.status == ProjectStatus.ACTIVE
    assert stored_task is not None
    assert stored_task.status == TaskStatus.TODO
    assert stored_task.priority == Priority.MEDIUM


def test_unique_username_and_email(session: Session) -> None:
    session.add(User(username="alice", email="alice@example.com", password_hash="h1"))
    session.commit()

    duplicate = User(username="alice", email="alice@example.com", password_hash="h2")
    session.add(duplicate)
    with pytest.raises(Exception):
        session.commit()


def test_unique_project_name_case_insensitive_per_owner(session: Session) -> None:
    owner = User(username="bob", email="bob@example.com", password_hash="hash")
    session.add(owner)
    session.flush()

    session.add(Project(name="Lanzamiento", owner_id=owner.id))
    session.commit()

    duplicate = Project(name="lanzamiento", owner_id=owner.id)
    session.add(duplicate)
    with pytest.raises(Exception):
        session.commit()
