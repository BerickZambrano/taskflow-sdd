import uuid
from collections.abc import Generator

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.core.database import SessionLocal
from app.core.exceptions import UnauthorizedError
from app.core.security import decode_access_token
from app.models.user import User
from app.repositories.user_repository import UserRepository

security = HTTPBearer(auto_error=False)


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(security),
    db: Session = Depends(get_db),
) -> User:
    if credentials is None:
        raise UnauthorizedError("Se requiere autenticación.")
    subject = decode_access_token(credentials.credentials)
    if subject is None:
        raise UnauthorizedError("Sesión no válida o expirada.")
    user = UserRepository(db).get_by_id(uuid.UUID(subject))
    if user is None:
        raise UnauthorizedError("Sesión no válida o expirada.")
    return user
