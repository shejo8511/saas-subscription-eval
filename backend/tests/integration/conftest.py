import os
import subprocess
from pathlib import Path

import pytest
from sqlalchemy.engine import make_url


@pytest.fixture(scope="session")
def database_url() -> str:
    value = os.environ.get("TEST_DATABASE_URL", "")
    url = make_url(value)
    if not url.database or not url.database.startswith("b2b_test_"):
        raise RuntimeError("Integration tests require TEST_DATABASE_URL with database b2b_test_*")
    if url.drivername != "postgresql+asyncpg":
        raise RuntimeError("Integration tests require real PostgreSQL via asyncpg")
    return value


@pytest.fixture(scope="session", autouse=True)
def migrate(database_url: str) -> None:
    environment = {**os.environ, "DATABASE_URL": database_url}
    subprocess.run(
        ["alembic", "upgrade", "head"],
        cwd=Path(__file__).resolve().parents[2],
        env=environment,
        check=True,
    )
