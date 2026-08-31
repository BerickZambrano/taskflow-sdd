from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.api.schemas.auth import LoginRequest, LoginResponse, RegisterRequest, UserOut
from app.repositories.user_repository import UserRepository
from app.services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=UserOut, status_code=201)
def register(payload: RegisterRequest, db: Session = Depends(get_db)) -> UserOut:
    service = AuthService(UserRepository(db))
    return service.register(payload.username, payload.email, payload.password)


@router.post("/login", response_model=LoginResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)) -> LoginResponse:
    service = AuthService(UserRepository(db))
    token = service.login(payload.identifier, payload.password)
    return LoginResponse(access_token=token)
