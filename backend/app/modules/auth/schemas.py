from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, SecretStr, field_validator


class LoginInput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    email: str = Field(min_length=3, max_length=254, pattern=r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
    password: SecretStr = Field(min_length=1, max_length=128)

    @field_validator("email", mode="before")
    @classmethod
    def normalize(cls, value: object) -> object:
        return value.strip().lower() if isinstance(value, str) else value


class PublicCompany(BaseModel):
    id: UUID
    name: str


class Identity(BaseModel):
    id: UUID
    name: str
    email: str
    role: Literal["Admin", "User"]
    company: PublicCompany
    expires_at: datetime


class CsrfResponse(BaseModel):
    csrf_token: str


class LogoutResponse(BaseModel):
    status: Literal["logged_out"] = "logged_out"
