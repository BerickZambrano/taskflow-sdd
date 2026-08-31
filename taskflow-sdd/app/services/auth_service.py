from app.core.exceptions import ConflictError, UnauthorizedError
from app.core.security import create_access_token, hash_password, verify_password
from app.models.user import User
from app.repositories.user_repository import UserRepository


class AuthService:
    def __init__(self, user_repository: UserRepository) -> None:
        self._users = user_repository

    def register(self, username: str, email: str, password: str) -> User:
        if self._users.get_by_username(username) is not None:
            raise ConflictError("El nombre de usuario ya está en uso.")
        if self._users.get_by_email(email) is not None:
            raise ConflictError("El correo electrónico ya está registrado.")
        user = self._users.create(username, email, hash_password(password))
        self._users.commit()
        return user

    def login(self, identifier: str, password: str) -> str:
        user = self._users.get_by_username(identifier) or self._users.get_by_email(
            identifier
        )
        if user is None or not verify_password(password, user.password_hash):
            raise UnauthorizedError("Credenciales incorrectas.")
        return create_access_token(subject=str(user.id))
