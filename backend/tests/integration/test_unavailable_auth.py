from datetime import timedelta
from uuid import uuid4

from fastapi.testclient import TestClient

from app.core.config import Settings
from app.core.security import encode_session, utcnow
from app.main import create_app


def test_unreachable_database_never_grants_authentication_or_fake_logout():
    config = Settings(
        database_url="postgresql+asyncpg://test:test@127.0.0.1:1/b2b_test_unavailable",
        database_timeout=0.2,
    )
    now = utcnow().replace(microsecond=0)
    token = encode_session(uuid4(), uuid4(), now, now + timedelta(seconds=1800), config)
    with TestClient(create_app(config), base_url=config.public_origin) as client:
        client.cookies.set("b2b_session", token)
        assert client.get("/api/v1/auth/me").status_code == 503
        csrf = client.get("/api/v1/auth/csrf").json()["csrf_token"]
        response = client.post(
            "/api/v1/auth/logout", headers={"Origin": config.public_origin, "X-CSRF-Token": csrf}
        )
        assert response.status_code == 503 and "set-cookie" not in response.headers
