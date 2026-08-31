from unittest.mock import create_autospec, patch

import pytest

from app.core.exceptions import ConflictError, UnauthorizedError
from app.core.security import hash_password
from app.models.user import User
from app.repositories.user_repository import UserRepository
from app.services.auth_service import AuthService


def _build_user(
    username: str = "alice",
    email: str = "alice@example.com",
    password: str = "clave-secreta",
) -> User:
    return User(username=username, email=email, password_hash=hash_password(password))


def test_register_success() -> None:
    repo = create_autospec(UserRepository)
    repo.get_by_username.return_value = None
    repo.get_by_email.return_value = None
    repo.create.return_value = _build_user()
    service = AuthService(repo)

    user = service.register("alice", "alice@example.com", "clave-secreta")

    assert user.username == "alice"
    repo.create.assert_called_once()
    assert repo.create.call_args.args[2] != "clave-secreta"
    repo.commit.assert_called_once()


def test_register_rejects_duplicate_username() -> None:
    repo = create_autospec(UserRepository)
    repo.get_by_username.return_value = _build_user()
    service = AuthService(repo)

    with pytest.raises(ConflictError):
        service.register("alice", "alice@example.com", "clave-secreta")
    repo.create.assert_not_called()


def test_register_rejects_duplicate_email() -> None:
    repo = create_autospec(UserRepository)
    repo.get_by_username.return_value = None
    repo.get_by_email.return_value = _build_user()
    service = AuthService(repo)

    with pytest.raises(ConflictError):
        service.register("alice", "alice@example.com", "clave-secreta")
    repo.create.assert_not_called()


def test_login_success_returns_token() -> None:
    repo = create_autospec(UserRepository)
    repo.get_by_username.return_value = _build_user()
    service = AuthService(repo)

    with patch("app.services.auth_service.create_access_token", return_value="token-x"):
        token = service.login("alice", "clave-secreta")

    assert token == "token-x"


def test_login_rejects_unknown_identifier() -> None:
    repo = create_autospec(UserRepository)
    repo.get_by_username.return_value = None
    repo.get_by_email.return_value = None
    service = AuthService(repo)

    with pytest.raises(UnauthorizedError):
        service.login("ghost", "clave-secreta")


def test_login_rejects_wrong_password() -> None:
    repo = create_autospec(UserRepository)
    repo.get_by_username.return_value = _build_user()
    service = AuthService(repo)

    with pytest.raises(UnauthorizedError):
        service.login("alice", "clave-incorrecta")
