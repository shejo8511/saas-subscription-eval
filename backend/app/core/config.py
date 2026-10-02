from typing import Literal

from pydantic import Field, PostgresDsn, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=None, extra="ignore")

    environment: Literal["development", "test", "production"] = "development"
    database_url: PostgresDsn
    database_timeout: float = Field(default=3.0, gt=0, le=10)

    @field_validator("database_url")
    @classmethod
    def require_asyncpg(cls, value: PostgresDsn) -> PostgresDsn:
        if value.scheme != "postgresql+asyncpg":
            raise ValueError("Use postgresql+asyncpg for asynchronous PostgreSQL")
        return value
