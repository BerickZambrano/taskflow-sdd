import pytest
from sqlalchemy.orm import Session

from app.core.database import SessionLocal
from app.models.user import User
from app.repositories.project_repository import ProjectRepository


@pytest.fixture()
def session() -> Session:
    db = SessionLocal()
    yield db
    db.close()


def _create_owner(session: Session, username: str = "alice") -> User:
    owner = User(
        username=username, email=f"{username}@example.com", password_hash="hash"
    )
    session.add(owner)
    session.flush()
    return owner


def test_create_and_get_by_id(session: Session) -> None:
    owner = _create_owner(session)
    repo = ProjectRepository(session)
    project = repo.create("Lanzamiento", "Descripción", owner.id)
    session.commit()

    fetched = repo.get_by_id(project.id)
    assert fetched is not None
    assert fetched.name == "Lanzamiento"
    assert fetched.owner_id == owner.id


def test_get_by_owner_returns_only_owner_projects(session: Session) -> None:
    owner_a = _create_owner(session, "alice")
    owner_b = _create_owner(session, "bob")
    repo = ProjectRepository(session)
    repo.create("Proyecto A", None, owner_a.id)
    repo.create("Proyecto B", None, owner_b.id)
    session.commit()

    projects = repo.get_by_owner(owner_a.id)
    assert [p.name for p in projects] == ["Proyecto A"]


def test_get_by_name_is_case_insensitive(session: Session) -> None:
    owner = _create_owner(session)
    repo = ProjectRepository(session)
    repo.create("Lanzamiento", None, owner.id)
    session.commit()

    found = repo.get_by_name_for_owner("lanzamiento", owner.id)
    assert found is not None
    assert found.name == "Lanzamiento"


def test_get_by_name_does_not_match_other_owner(session: Session) -> None:
    owner_a = _create_owner(session, "alice")
    owner_b = _create_owner(session, "bob")
    repo = ProjectRepository(session)
    repo.create("Lanzamiento", None, owner_a.id)
    session.commit()

    assert repo.get_by_name_for_owner("Lanzamiento", owner_b.id) is None


def test_update_project(session: Session) -> None:
    owner = _create_owner(session)
    repo = ProjectRepository(session)
    project = repo.create("Lanzamiento", "Antes", owner.id)
    session.commit()

    repo.update(project, name="Renombrado", description="Después")
    session.commit()

    fetched = repo.get_by_id(project.id)
    assert fetched is not None
    assert fetched.name == "Renombrado"
    assert fetched.description == "Después"
