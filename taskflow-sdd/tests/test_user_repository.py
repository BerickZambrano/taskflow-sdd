import pytest
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.database import SessionLocal
from app.repositories.user_repository import UserRepository


@pytest.fixture()
def session() -> Session:
    db = SessionLocal()
    yield db
    db.close()


def test_create_and_get_by_id(session: Session) -> None:
    repo = UserRepository(session)
    user = repo.create(
        username="alice", email="alice@example.com", password_hash="hash"
    )
    assert user.id is not None

    fetched = repo.get_by_id(user.id)
    assert fetched is not None
    assert fetched.username == "alice"
    assert fetched.email == "alice@example.com"


def test_get_by_username_and_email(session: Session) -> None:
    repo = UserRepository(session)
    repo.create(username="alice", email="alice@example.com", password_hash="hash")
    session.commit()

    assert repo.get_by_username("alice") is not None
    assert repo.get_by_email("alice@example.com") is not None
    assert repo.get_by_username("missing") is None
    assert repo.get_by_email("missing@example.com") is None


def test_duplicate_username_rejected(session: Session) -> None:
    repo = UserRepository(session)
    repo.create(username="alice", email="alice@example.com", password_hash="h1")
    session.commit()

    with pytest.raises(IntegrityError):
        repo.create(username="alice", email="other@example.com", password_hash="h2")


def test_duplicate_email_rejected(session: Session) -> None:
    repo = UserRepository(session)
    repo.create(username="alice", email="alice@example.com", password_hash="h1")
    session.commit()

    with pytest.raises(IntegrityError):
        repo.create(username="bob", email="alice@example.com", password_hash="h2")
