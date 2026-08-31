import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator


class RegisterRequest(BaseModel):
    username: str = Field(min_length=3, max_length=50)
    email: str
    password: str = Field(min_length=8, max_length=128)

    @field_validator("email")
    @classmethod
    def validate_email(cls, value: str) -> str:
        if "@" not in value or "." not in value.split("@")[-1]:
            raise ValueError("El correo electrónico no es válido.")
        return value


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    username: str
    email: str
    created_at: datetime


class LoginRequest(BaseModel):
    identifier: str
    password: str


class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
