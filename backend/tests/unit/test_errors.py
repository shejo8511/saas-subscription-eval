from fastapi.testclient import TestClient

from app.core.config import Settings
from app.main import create_app
from app.seed import main


def test_unexpected_errors_never_expose_traceback_or_secrets(caplog):
    app = create_app(Settings(database_url="postgresql+asyncpg://localhost/b2b_test_errors"))

    @app.get("/__test/failure")
    async def failure():
        raise RuntimeError("private password SQL token")

    with TestClient(app) as client:
        response = client.get("/__test/failure")
        assert response.status_code == 500
        assert response.json()["error"]["code"] == "INTERNAL_ERROR"
        assert response.headers["x-request-id"] == response.json()["request_id"]
        assert "private" not in response.text and "private" not in caplog.text


async def test_demo_cli_is_noop_when_disabled(monkeypatch):
    monkeypatch.setenv("DATABASE_URL", "postgresql+asyncpg://localhost/b2b_test_errors")
    monkeypatch.setenv("DEMO_SEED", "false")
    await main()
