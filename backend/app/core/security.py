import secrets
from datetime import UTC, datetime
from hmac import compare_digest
from typing import Any
from urllib.parse import urlsplit
from uuid import UUID

import jwt
from argon2 import PasswordHasher
from argon2.exceptions import InvalidHashError, VerificationError
from fastapi import Request, Response

from app.core.config import Settings
from app.core.errors import ApiError

SESSION_COOKIE = "b2b_session"
CSRF_COOKIE = "b2b_csrf"
ISSUER = "b2b-api"
AUDIENCE = "b2b-web"
password_hasher = PasswordHasher()


def utcnow() -> datetime:
    return datetime.now(UTC)


def verify_password(password: str, hashed: str) -> bool:
    try:
        return password_hasher.verify(hashed, password)
    except (VerificationError, InvalidHashError):
        return False


def encode_session(
    sub: UUID, jti: UUID, issued: datetime, expires: datetime, settings: Settings
) -> str:
    return jwt.encode(
        {
            "sub": str(sub),
            "jti": str(jti),
            "iat": int(issued.timestamp()),
            "exp": int(expires.timestamp()),
            "iss": ISSUER,
            "aud": AUDIENCE,
        },
        settings.jwt_secret.get_secret_value(),
        algorithm="HS256",
    )


def decode_session(
    token: str, settings: Settings, *, allow_expired: bool = False
) -> dict[str, Any]:
    try:
        claims = jwt.decode(
            token,
            settings.jwt_secret.get_secret_value(),
            algorithms=["HS256"],
            issuer=ISSUER,
            audience=AUDIENCE,
            options={"require": ["sub", "jti", "iat", "exp"], "verify_exp": not allow_expired},
        )
        UUID(claims["sub"])
        UUID(claims["jti"])
        if (
            type(claims["iat"]) is not int
            or type(claims["exp"]) is not int
            or claims["iat"] < 0
            or claims["iat"] >= claims["exp"]
            or claims["exp"] - claims["iat"] > settings.session_seconds
        ):
            raise ValueError("Invalid lifetime")
        return claims
    except (jwt.InvalidTokenError, ValueError, TypeError, AttributeError) as error:
        raise ApiError(401, "UNAUTHENTICATED", "Sesión no válida o expirada.") from error


def csrf_binding(request: Request, settings: Settings) -> str:
    token = request.cookies.get(SESSION_COOKIE)
    if token:
        try:
            return str(decode_session(token, settings, allow_expired=True)["jti"])
        except ApiError:
            pass
    return "anonymous"


def valid_csrf(token: str, binding: str, settings: Settings) -> bool:
    try:
        claims = jwt.decode(
            token,
            settings.csrf_secret.get_secret_value(),
            algorithms=["HS256"],
            issuer=ISSUER,
            audience="b2b-csrf",
            options={"require": ["exp", "iat", "binding", "nonce"]},
        )
        return (
            claims["binding"] == binding
            and isinstance(claims["nonce"], str)
            and len(claims["nonce"]) == 43
        )
    except jwt.InvalidTokenError:
        return False


def set_cookie(
    response: Response, name: str, value: str, settings: Settings, *, http_only: bool
) -> None:
    response.set_cookie(
        name,
        value,
        max_age=settings.session_seconds,
        path="/",
        secure=settings.cookie_secure,
        httponly=http_only,
        samesite="strict",
    )


def issue_csrf(response: Response, binding: str, settings: Settings, existing: str = "") -> str:
    token = existing
    if not valid_csrf(token, binding, settings):
        now = int(utcnow().timestamp())
        token = jwt.encode(
            {
                "binding": binding,
                "nonce": secrets.token_urlsafe(32),
                "iat": now,
                "exp": now + settings.session_seconds,
                "iss": ISSUER,
                "aud": "b2b-csrf",
            },
            settings.csrf_secret.get_secret_value(),
            algorithm="HS256",
        )
        set_cookie(response, CSRF_COOKIE, token, settings, http_only=False)
    return token


def check_csrf(request: Request, settings: Settings) -> None:
    origin = request.headers.get("origin")
    referer = request.headers.get("referer", "")
    try:
        parsed = urlsplit(referer)
    except ValueError as error:
        raise ApiError(403, "CSRF_REJECTED", "Origen no válido.") from error
    source = origin if origin is not None else f"{parsed.scheme}://{parsed.netloc}"
    cookie = request.cookies.get(CSRF_COOKIE, "")
    header = request.headers.get("x-csrf-token", "")
    if (
        source != settings.public_origin
        or not cookie
        or len(header) > 2048
        or not cookie.isascii()
        or not header.isascii()
        or len(cookie) > 2048
        or not compare_digest(cookie, header)
        or not valid_csrf(cookie, csrf_binding(request, settings), settings)
    ):
        raise ApiError(403, "CSRF_REJECTED", "Solicitud no autorizada. Actualiza la página.")


def clear_cookies(response: Response, settings: Settings) -> None:
    for name in (SESSION_COOKIE, CSRF_COOKIE):
        response.delete_cookie(
            name,
            path="/",
            secure=settings.cookie_secure,
            httponly=name == SESSION_COOKIE,
            samesite="strict",
        )
