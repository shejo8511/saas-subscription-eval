from unittest.mock import AsyncMock

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.exc import SQLAlchemyError

from app.core.config import Settings
from app.db.database import Database
from app.main import create_app


def settings() -> Settings:
    return Settings(database_url="postgresql+asyncpg://unit:unit@localhost/b2b_test_unit")


def test_process_health_does_not_require_database() -> None:
    with TestClient(create_app(settings())) as client:
        assert client.get("/api/v1/health").json() == {"status": "ok"}
        assert client.get("/api/v1/health").status_code == 200
        assert client.get("/api/v1/usage").status_code == 404
        assert client.get("/api/v1/auth/me").status_code == 404


@pytest.mark.parametrize("ready,status", [(True, 200), (False, 503)])
def test_readiness_matches_database_state(monkeypatch, ready, status) -> None:
    monkeypatch.setattr(Database, "is_ready", AsyncMock(return_value=ready))
    with TestClient(create_app(settings())) as client:
        response = client.get("/api/v1/ready")
    assert response.status_code == status
    assert response.json() == {
        "status": "ready" if ready else "unavailable",
        "database": "ready" if ready else "unavailable",
    }
    assert response.headers["cache-control"] == "no-store"


@pytest.mark.parametrize(
    "error", [SQLAlchemyError("private SQL"), OSError("private host"), TimeoutError()]
)
def test_readiness_failure_does_not_leak_details(monkeypatch, error) -> None:
    monkeypatch.setattr(Database, "is_ready", AsyncMock(side_effect=error))
    with TestClient(create_app(settings())) as client:
        response = client.get("/api/v1/ready")
    assert response.status_code == 503
    assert response.json() == {"status": "unavailable", "database": "unavailable"}
    assert "private" not in response.text


def test_configuration_loaded_from_environment(monkeypatch) -> None:
    monkeypatch.setenv("DATABASE_URL", "postgresql+asyncpg://unit:unit@localhost/b2b_test_unit")
    monkeypatch.setattr(Database, "is_ready", AsyncMock(return_value=True))
    with TestClient(create_app()) as client:
        assert client.get("/api/v1/ready").status_code == 200
        specification = client.get("/api/openapi.json").json()
    assert specification["info"]["version"] == "0.1.0"
    assert "503" in specification["paths"]["/api/v1/ready"]["get"]["responses"]
