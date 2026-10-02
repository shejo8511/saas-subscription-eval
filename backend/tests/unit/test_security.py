from datetime import timedelta
from uuid import uuid4

import jwt
import pytest
from pydantic import ValidationError
from starlette.requests import Request
from starlette.responses import Response

from app.core.config import Settings
from app.core.errors import ApiError
from app.core.security import (
    check_csrf,
    decode_session,
    encode_session,
    issue_csrf,
    password_hasher,
    utcnow,
    valid_csrf,
    verify_password,
)
from app.modules.auth.schemas import LoginInput


def settings(**kwargs) -> Settings:
    return Settings(database_url="postgresql+asyncpg://localhost/b2b_test_security", **kwargs)


def test_password_is_not_modified_and_argon2_rejects_invalid_hash() -> None:
    password = "  preserved whitespace  "
    hashed = password_hasher.hash(password)
    assert verify_password(password, hashed)
    assert not verify_password(password.strip(), hashed)
    assert not verify_password(password, "invalid")
    assert LoginInput(email=" ADMIN@Test.Invalid ", password=password).email == "admin@test.invalid"
    assert (
        LoginInput(email="a@test.invalid", password=password).password.get_secret_value()
        == password
    )


@pytest.mark.parametrize(
    "case",
    [
        "tampered",
        "expired",
        "future",
        "missing_sub",
        "missing_jti",
        "missing_exp",
        "missing_iat",
        "algorithm",
        "issuer",
        "audience",
        "sub",
        "jti",
        "time_type",
        "time_bool",
        "lifetime",
        "backwards",
        "malformed",
    ],
)
def test_invalid_jwt_claims(case: str) -> None:
    config = settings()
    now = int(utcnow().timestamp())
    claims = dict(
        sub=str(uuid4()), jti=str(uuid4()), iat=now, exp=now + 1800, iss="b2b-api", aud="b2b-web"
    )
    algorithm = "HS256"
    match case:
        case "expired":
            claims.update(iat=now - 1801, exp=now - 1)
        case "future":
            claims.update(iat=now + 30, exp=now + 1800)
        case "algorithm":
            algorithm = "HS384"
        case "issuer":
            claims["iss"] = "other"
        case "audience":
            claims["aud"] = "other"
        case "sub" | "jti":
            claims[case] = "invalid"
        case "time_type":
            claims["iat"] = str(now)
        case "time_bool":
            claims["iat"] = True
        case "lifetime":
            claims["exp"] = now + 3601
        case "backwards":
            claims["iat"] = now
            claims["exp"] = now
        case _:
            if case.startswith("missing_"):
                claims.pop(case.removeprefix("missing_"))
    token = jwt.encode(claims, config.jwt_secret.get_secret_value(), algorithm=algorithm)
    if case == "tampered":
        token = token[:-10] + "abcdefghij"
    if case == "malformed":
        token = "malformed"
    with pytest.raises(ApiError) as failure:
        decode_session(token, config)
    assert failure.value.status == 401


def test_signed_csrf_binding_rotation_reuse_and_origin_policy() -> None:
    config = settings()
    response = Response()
    first = issue_csrf(response, "anonymous", config)
    assert valid_csrf(first, "anonymous", config)
    assert not valid_csrf(first, "different", config)
    assert issue_csrf(Response(), "anonymous", config, first) == first
    rotated = issue_csrf(Response(), "session", config, first)
    assert rotated != first
    now = utcnow()
    token = encode_session(
        uuid4(), uuid4(), now - timedelta(seconds=1801), now - timedelta(seconds=1), config
    )
    assert decode_session(token, config, allow_expired=True)
    for source in [None, "null", "http://attacker.invalid"]:
        headers = [(b"cookie", f"b2b_csrf={first}".encode()), (b"x-csrf-token", first.encode())]
        if source:
            headers.append((b"origin", source.encode()))
        request = Request({"type": "http", "headers": headers})
        with pytest.raises(ApiError):
            check_csrf(request, config)
    request = Request(
        {
            "type": "http",
            "headers": [
                (b"cookie", f"b2b_csrf={first}".encode()),
                (b"x-csrf-token", first.encode()),
                (b"referer", b"http://localhost:3000/login"),
            ],
        }
    )
    check_csrf(request, config)


@pytest.mark.parametrize(
    "kwargs",
    [
        {"public_origin": "https://localhost:3000"},
        {"jwt_secret": "demo"},
        {"csrf_secret": "0" * 64},
        {"public_origin": "http://localhost:3000/path"},
        {"public_origin": "http://external.invalid", "environment": "development"},
        {"environment": "production"},
        {"demo_seed": True, "environment": "test"},
    ],
)
def test_insecure_configuration_rejected(kwargs) -> None:
    with pytest.raises(ValidationError):
        settings(**kwargs)


def test_secure_production_configuration_and_independent_keys() -> None:
    assert settings(
        environment="production", public_origin="https://example.test", cookie_secure=True
    )
    config = settings()
    with pytest.raises(ValidationError):
        settings(csrf_secret=config.jwt_secret)
