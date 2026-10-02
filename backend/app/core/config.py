import re
from typing import Literal, Self
from urllib.parse import urlsplit

from pydantic import Field, PostgresDsn, SecretStr, field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=None, extra="ignore", hide_input_in_errors=True)
    environment: Literal["development", "test", "production"] = "development"
    database_url: PostgresDsn
    database_timeout: float = Field(default=3.0, gt=0, le=10)
    jwt_secret: SecretStr
    csrf_secret: SecretStr
    public_origin: str = "http://localhost:3000"
    cookie_secure: bool = False
    session_seconds: int = Field(default=1800, ge=60, le=3600)
    login_limit: int = Field(default=30, ge=1, le=1000)
    login_window_seconds: int = Field(default=60, ge=1, le=3600)
    demo_seed: bool = False

    @field_validator("database_url")
    @classmethod
    def require_asyncpg(cls, value: PostgresDsn) -> PostgresDsn:
        if value.scheme != "postgresql+asyncpg":
            raise ValueError("Use postgresql+asyncpg for asynchronous PostgreSQL")
        return value

    @field_validator("jwt_secret", "csrf_secret")
    @classmethod
    def require_random_secret(cls, value: SecretStr) -> SecretStr:
        secret = value.get_secret_value()
        if not re.fullmatch(r"[0-9a-f]{64}", secret) or len(set(secret)) < 10:
            raise ValueError("Provide an independently generated 32-byte random hex secret")
        return value

    @model_validator(mode="after")
    def secure_configuration(self) -> Self:
        origin = urlsplit(self.public_origin)
        if (
            origin.scheme not in ("http", "https")
            or not origin.netloc
            or origin.path
            or origin.query
            or origin.fragment
            or origin.username
        ):
            raise ValueError("PUBLIC_ORIGIN must be an exact HTTP(S) origin")
        if origin.scheme == "https" and not self.cookie_secure:
            raise ValueError("HTTPS requires Secure cookies in every environment")
        if self.jwt_secret == self.csrf_secret:
            raise ValueError("JWT and CSRF keys must be independent")
        if self.environment == "production":
            if origin.scheme != "https" or not self.cookie_secure or self.demo_seed:
                raise ValueError("Production requires HTTPS, Secure cookies and no demo seed")
        elif self.environment == "development" and not self.cookie_secure:
            if origin.hostname not in ("localhost", "127.0.0.1"):
                raise ValueError("Insecure development cookies are restricted to localhost")
        if self.demo_seed and self.environment != "development":
            raise ValueError("Demo seed is restricted to explicit development configuration")
        return self
