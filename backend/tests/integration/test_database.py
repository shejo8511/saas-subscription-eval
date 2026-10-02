import asyncio
import os
import subprocess
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import text

from app.core.config import Settings
from app.db.database import Database
from app.main import create_app

pytestmark = pytest.mark.integration
BACKEND_ROOT = Path(__file__).resolve().parents[2]


def test_health_and_readiness_against_postgresql(database_url: str) -> None:
    with TestClient(create_app(Settings(database_url=database_url))) as client:
        assert client.get("/api/v1/health").status_code == 200
        response = client.get("/api/v1/ready")
    assert response.status_code == 200
    assert response.json() == {"status": "ready", "database": "ready"}


async def test_connections_roll_back_uncommitted_data(database_url: str) -> None:
    database = Database(Settings(database_url=database_url))
    try:
        async with database.engine.begin() as connection:
            await connection.execute(text("CREATE TABLE public.rollback_probe (value integer)"))
        async with database.engine.connect() as connection:
            await connection.execute(text("INSERT INTO public.rollback_probe VALUES (42)"))
        async with database.engine.connect() as connection:
            assert await connection.scalar(text("SELECT count(*) FROM public.rollback_probe")) == 0
        async with database.engine.begin() as connection:
            await connection.execute(text("DROP TABLE public.rollback_probe"))
        assert await database.is_ready()
    finally:
        await database.close()


async def test_migrations_preserve_existing_data(database_url: str) -> None:
    database = Database(Settings(database_url=database_url))
    environment = {**os.environ, "DATABASE_URL": database_url}
    cwd = BACKEND_ROOT
    try:
        async with database.engine.begin() as connection:
            await connection.execute(text("CREATE TABLE public.migration_probe (value text)"))
            await connection.execute(
                text("INSERT INTO public.migration_probe VALUES ('preserved')")
            )
        await asyncio.to_thread(
            subprocess.run, ["alembic", "downgrade", "base"], cwd=cwd, env=environment, check=True
        )
        assert not await database.is_ready()
        await asyncio.to_thread(
            subprocess.run, ["alembic", "upgrade", "head"], cwd=cwd, env=environment, check=True
        )
        await asyncio.to_thread(
            subprocess.run, ["alembic", "upgrade", "head"], cwd=cwd, env=environment, check=True
        )
        async with database.engine.begin() as connection:
            assert (
                await connection.scalar(text("SELECT value FROM public.migration_probe"))
                == "preserved"
            )
            assert (
                await connection.scalar(text("SELECT version_num FROM alembic_version"))
                == "0001_bootstrap"
            )
            await connection.execute(text("DROP TABLE public.migration_probe"))
        assert await database.is_ready()
    finally:
        await database.close()


def test_unreachable_postgresql_returns_503() -> None:
    settings = Settings(
        database_url="postgresql+asyncpg://test:test@127.0.0.1:1/b2b_test_unavailable",
        database_timeout=0.2,
    )
    with TestClient(create_app(settings)) as client:
        assert client.get("/api/v1/health").status_code == 200
        assert client.get("/api/v1/ready").status_code == 503
