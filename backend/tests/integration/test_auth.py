import secrets
from datetime import timedelta
from typing import Annotated
from uuid import UUID, uuid4

import jwt
import pytest
from fastapi import Depends
from fastapi.testclient import TestClient
from sqlalchemy import select, text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import Settings
from app.core.security import encode_session, password_hasher, utcnow
from app.db.models import AuthSession, Company, User
from app.main import create_app
from app.modules.auth.service import TenantContext, require_admin

pytestmark = pytest.mark.integration


@pytest.fixture
def auth(database_url):
    config = Settings(database_url=database_url, login_limit=30, database_timeout=10)
    app = create_app(config)

    @app.get("/__test/admin")
    async def admin(tenant: Annotated[TenantContext, Depends(require_admin)]):
        return {"company_id": str(tenant.company.id)}

    with TestClient(app, base_url=config.public_origin) as client:
        password = secrets.token_urlsafe(24)
        hashed = password_hasher.hash(password)

        async def initialize():
            async with app.state.database.sessions() as session:
                await session.execute(text("TRUNCATE b2b.companies, b2b.login_bucket CASCADE"))
                accounts = []
                for company_name in ("Empresa A", "Empresa B"):
                    company = Company(name=company_name)
                    session.add(company)
                    await session.flush()
                    for role in ("Admin", "User"):
                        user = User(
                            company_id=company.id,
                            name=f"{role} {company_name}",
                            email=f"{role.lower()}.{len(accounts)}@test.invalid",
                            role=role,
                            password_hash=hashed,
                        )
                        session.add(user)
                        await session.flush()
                        accounts.append(
                            {
                                "id": user.id,
                                "company_id": company.id,
                                "email": user.email,
                                "role": role,
                            }
                        )
                await session.commit()
                return accounts

        accounts = client.portal.call(initialize)
        yield client, accounts, password, config

        async def clean():
            async with app.state.database.sessions() as session:
                await session.execute(text("TRUNCATE b2b.companies, b2b.login_bucket CASCADE"))
                await session.commit()

        client.portal.call(clean)


def csrf(client):
    response = client.get("/api/v1/auth/csrf")
    assert response.status_code == 200
    return {"Origin": "http://localhost:3000", "X-CSRF-Token": response.json()["csrf_token"]}


def sign_in(client, account, password):
    return client.post(
        "/api/v1/auth/login",
        headers=csrf(client),
        json={"email": account["email"], "password": password},
    )


def mutate(client, callback):
    async def perform():
        async with client.app.state.database.sessions() as session:
            await callback(session)
            await session.commit()

    client.portal.call(perform)


@pytest.mark.parametrize("index", range(4))
def test_four_accounts_and_current_permissions(auth, index):
    client, accounts, password, config = auth
    account = accounts[index]
    response = sign_in(client, account, password)
    assert response.status_code == 200
    assert response.json()["role"] == account["role"]
    assert response.json()["company"]["id"] == str(account["company_id"])
    assert set(response.json()) == {"id", "name", "email", "role", "company", "expires_at"}
    cookies = response.headers.get_list("set-cookie")
    assert len(cookies) == 2
    assert "HttpOnly" in cookies[0] and "SameSite=strict" in cookies[0] and "Path=/" in cookies[0]
    assert "Domain=" not in cookies[0]
    assert "HttpOnly" not in cookies[1]
    me = client.get(
        "/api/v1/auth/me",
        headers={"X-Company-ID": str(accounts[2]["company_id"]), "X-Role": "Admin"},
    )
    assert me.json() == response.json()
    assert me.headers["cache-control"] == "no-store"
    assert client.get("/__test/admin").status_code == (200 if account["role"] == "Admin" else 403)

    async def change(session):
        user = await session.get(User, account["id"])
        user.role = "User" if account["role"] == "Admin" else "Admin"

    mutate(client, change)
    assert client.get("/__test/admin").status_code == (403 if account["role"] == "Admin" else 200)

    async def deactivate(session):
        user = await session.get(User, account["id"])
        user.state = "inactive"

    mutate(client, deactivate)
    assert client.get("/api/v1/auth/me").status_code == 401


@pytest.mark.parametrize("reason", ["unknown", "password", "inactive_user", "inactive_company"])
def test_uniform_login_failures(auth, reason):
    client, accounts, password, _ = auth
    account = accounts[0].copy()
    if reason == "unknown":
        account["email"] = "missing@test.invalid"
    if reason == "password":
        password = secrets.token_urlsafe(24)
    if reason.startswith("inactive"):

        async def deactivate(session):
            target = await session.get(
                User if reason == "inactive_user" else Company,
                account["id"] if reason == "inactive_user" else account["company_id"],
            )
            target.state = "inactive"

        mutate(client, deactivate)
    response = sign_in(client, account, password)
    assert response.status_code == 401
    assert response.json()["error"] == {
        "code": "INVALID_CREDENTIALS",
        "message": "Email o contraseña no válidos.",
    }
    assert "b2b_session" not in client.cookies


def test_validation_does_not_echo_sensitive_inputs(auth, caplog):
    client, accounts, password, _ = auth
    for body in [
        dict(email="invalid", password=password),
        dict(email=accounts[0]["email"], password="x" * 129),
        dict(email=accounts[0]["email"], password=password, role="Admin", company_id=str(uuid4())),
    ]:
        response = client.post("/api/v1/auth/login", headers=csrf(client), json=body)
        assert response.status_code == 422
        assert password not in response.text and password not in caplog.text
        assert response.json()["request_id"] == response.headers["x-request-id"]


@pytest.mark.parametrize(
    "reason", ["missing", "tampered", "cross_session", "origin", "null", "absent_origin"]
)
def test_csrf_rejection_on_login_and_logout(auth, reason):
    client, accounts, password, _ = auth
    headers = csrf(client)
    if reason == "missing":
        headers.pop("X-CSRF-Token")
    if reason == "tampered":
        headers["X-CSRF-Token"] += "x"
    if reason == "origin":
        headers["Origin"] = "http://attacker.invalid"
    if reason == "null":
        headers["Origin"] = "null"
    if reason == "absent_origin":
        headers.pop("Origin")
    if reason == "cross_session":
        old = headers["X-CSRF-Token"]
        assert sign_in(client, accounts[0], password).status_code == 200
        headers["X-CSRF-Token"] = old
    for route in ("login", "logout"):
        response = client.post(
            f"/api/v1/auth/{route}",
            headers=headers,
            json={"email": accounts[0]["email"], "password": password}
            if route == "login"
            else None,
        )
        assert response.status_code == 403


def test_logout_revocation_repetition_and_restart(auth):
    client, accounts, password, config = auth
    assert sign_in(client, accounts[0], password).status_code == 200
    token = client.cookies.get("b2b_session")
    original_csrf = client.get("/api/v1/auth/csrf").json()["csrf_token"]
    assert client.get("/api/v1/auth/csrf").json()["csrf_token"] == original_csrf
    with TestClient(create_app(config), base_url=config.public_origin) as restarted:
        restarted.cookies.set("b2b_session", token)
        assert restarted.get("/api/v1/auth/me").status_code == 200
    response = client.post("/api/v1/auth/logout", headers=csrf(client))
    assert response.status_code == 200
    assert len(response.headers.get_list("set-cookie")) == 2
    assert all("Max-Age=0" in cookie for cookie in response.headers.get_list("set-cookie"))
    assert "b2b_session" not in client.cookies and "b2b_csrf" not in client.cookies
    assert client.post("/api/v1/auth/logout", headers=csrf(client)).status_code == 200
    with TestClient(create_app(config), base_url=config.public_origin) as restarted:
        restarted.cookies.set("b2b_session", token)
        assert restarted.get("/api/v1/auth/me").status_code == 401
    client.cookies.set("b2b_session", token)
    assert client.get("/api/v1/auth/me").status_code == 401


@pytest.mark.parametrize(
    "case",
    [
        "missing",
        "mismatch",
        "expired_db",
        "revoked",
        "company_inactive",
        "stale_claims",
        "expired_jwt",
    ],
)
def test_persistent_session_authority(auth, case):
    client, accounts, password, config = auth
    assert sign_in(client, accounts[0], password).status_code == 200
    token = client.cookies.get("b2b_session")
    claims = jwt.decode(
        token, config.jwt_secret.get_secret_value(), algorithms=["HS256"], audience="b2b-web"
    )

    async def change(session):
        authentication = await session.get(AuthSession, UUID(claims["jti"]))
        match case:
            case "missing":
                await session.delete(authentication)
            case "mismatch":
                authentication.user_id = accounts[2]["id"]
            case "expired_db":
                authentication.created_at = utcnow() - timedelta(hours=2)
                authentication.expires_at = utcnow() - timedelta(hours=1)
            case "revoked":
                authentication.revoked_at = utcnow()
            case "company_inactive":
                (await session.get(Company, accounts[0]["company_id"])).state = "inactive"

    mutate(client, change)
    if case == "stale_claims":
        claims.update(role="User", company_id=str(accounts[2]["company_id"]))
        token = jwt.encode(claims, config.jwt_secret.get_secret_value(), algorithm="HS256")
    if case == "expired_jwt":
        now = utcnow()
        token = encode_session(
            accounts[0]["id"],
            UUID(claims["jti"]),
            now - timedelta(seconds=1801),
            now - timedelta(seconds=1),
            config,
        )
    client.cookies.clear()
    client.cookies.set("b2b_session", token)
    response = client.get("/api/v1/auth/me")
    assert response.status_code == (200 if case == "stale_claims" else 401)
    if case == "stale_claims":
        assert response.json()["role"] == "Admin" and response.json()["company"]["id"] == str(
            accounts[0]["company_id"]
        )
    if case == "expired_jwt":
        assert client.post("/api/v1/auth/logout", headers=csrf(client)).status_code == 200


def test_rate_limit_is_shared_and_expires_without_sleep(auth):
    client, accounts, password, config = auth
    config.login_limit = 2
    assert sign_in(client, accounts[0], password).status_code == 200
    account = dict(accounts[0], email=accounts[0]["email"].upper())
    assert sign_in(client, account, password).status_code == 200
    with TestClient(create_app(config), base_url=config.public_origin) as second_process:
        response = sign_in(second_process, account, password)
        assert response.status_code == 429 and 1 <= int(response.headers["retry-after"]) <= 60

    async def expire(session):
        await session.execute(
            text("UPDATE b2b.login_bucket SET expires_at = now() - interval '1 second'")
        )

    mutate(client, expire)
    assert sign_in(client, account, password).status_code == 200


@pytest.mark.parametrize("operation", ["login", "logout"])
def test_commit_failure_rolls_back_without_false_success(auth, monkeypatch, operation):
    client, accounts, password, _ = auth
    if operation == "logout":
        assert sign_in(client, accounts[0], password).status_code == 200
    headers = csrf(client)
    original = AsyncSession.commit
    calls = 0

    async def fail(session):
        nonlocal calls
        calls += 1
        if operation == "logout" or calls == 2:
            raise SQLAlchemyError("private SQL with credential")
        await original(session)

    monkeypatch.setattr(AsyncSession, "commit", fail)
    response = client.post(
        f"/api/v1/auth/{operation}",
        headers=headers,
        json={"email": accounts[0]["email"], "password": password}
        if operation == "login"
        else None,
    )
    assert response.status_code == 503 and "private" not in response.text
    assert "set-cookie" not in response.headers
    monkeypatch.setattr(AsyncSession, "commit", original)
    if operation == "logout":
        assert client.get("/api/v1/auth/me").status_code == 200
    else:

        async def count(session):
            assert list(await session.scalars(select(AuthSession))) == []

        mutate(client, count)
