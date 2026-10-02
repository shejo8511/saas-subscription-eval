import asyncio
import math
from collections.abc import AsyncIterator
from dataclasses import dataclass
from datetime import timedelta
from typing import Annotated, cast
from uuid import UUID, uuid4

from fastapi import Depends, Request
from sqlalchemy import case, func, select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import Settings
from app.core.errors import ApiError
from app.core.security import SESSION_COOKIE, decode_session, utcnow, verify_password
from app.db.models import AuthSession, Company, LoginBucket, User
from app.modules.auth.schemas import Identity, LoginInput, PublicCompany


async def get_session(request: Request) -> AsyncIterator[AsyncSession]:
    async with request.app.state.database.sessions() as session:
        yield session


SessionDependency = Annotated[AsyncSession, Depends(get_session)]


@dataclass
class TenantContext:
    user: User
    company: Company
    session: AuthSession

    def public(self) -> Identity:
        return Identity(
            id=self.user.id,
            name=self.user.name,
            email=self.user.email,
            role=self.user.role,
            company=PublicCompany(id=self.company.id, name=self.company.name),
            expires_at=self.session.expires_at,
        )


async def current_tenant(request: Request, session: SessionDependency) -> TenantContext:
    token = request.cookies.get(SESSION_COOKIE, "")
    settings: Settings = request.app.state.settings
    claims = decode_session(token, settings)
    result = (
        await session.execute(
            select(User, Company, AuthSession)
            .join(Company, User.company_id == Company.id)
            .join(AuthSession, AuthSession.user_id == User.id)
            .where(
                User.id == UUID(claims["sub"]),
                AuthSession.jti == UUID(claims["jti"]),
                AuthSession.revoked_at.is_(None),
                AuthSession.expires_at > utcnow(),
                User.state == "active",
                Company.state == "active",
            )
        )
    ).first()
    if result is None or int(result[2].expires_at.timestamp()) != claims["exp"]:
        raise ApiError(401, "UNAUTHENTICATED", "Sesión no válida o expirada.")
    return TenantContext(result[0], result[1], result[2])


TenantDependency = Annotated[TenantContext, Depends(current_tenant)]


async def require_admin(tenant: TenantDependency) -> TenantContext:
    if tenant.user.role != "Admin":
        raise ApiError(403, "FORBIDDEN", "Esta operación requiere el rol Admin.")
    return tenant


async def limit_login(session: AsyncSession, settings: Settings) -> None:
    now = utcnow()
    reset = LoginBucket.expires_at <= now
    statement = insert(LoginBucket).values(
        id="login", attempts=1, expires_at=now + timedelta(seconds=settings.login_window_seconds)
    )
    count_statement = statement.on_conflict_do_update(
        index_elements=[LoginBucket.id],
        set_={
            "attempts": case(
                (reset, 1), else_=func.least(LoginBucket.attempts + 1, settings.login_limit + 1)
            ),
            "expires_at": case(
                (reset, statement.excluded.expires_at), else_=LoginBucket.expires_at
            ),
        },
    ).returning(LoginBucket.attempts, LoginBucket.expires_at)
    row = (await session.execute(count_statement)).one()
    await session.commit()
    if row.attempts > settings.login_limit:
        retry = max(1, math.ceil((row.expires_at - now).total_seconds()))
        raise ApiError(
            429,
            "RATE_LIMITED",
            "Demasiados intentos. Vuelve a intentar más tarde.",
            {"Retry-After": str(retry)},
        )


async def login(
    session: AsyncSession, data: LoginInput, settings: Settings, dummy_hash: str
) -> TenantContext:
    await limit_login(session, settings)
    row = (
        await session.execute(select(User, Company).join(Company).where(User.email == data.email))
    ).first()
    hashed = row[0].password_hash if row else dummy_hash
    valid = await asyncio.to_thread(verify_password, data.password.get_secret_value(), hashed)
    if not valid or row is None or row[0].state != "active" or row[1].state != "active":
        raise ApiError(401, "INVALID_CREDENTIALS", "Email o contraseña no válidos.")
    user, company = cast(tuple[User, Company], row)
    now = utcnow().replace(microsecond=0)
    authentication = AuthSession(
        jti=uuid4(),
        user_id=user.id,
        created_at=now,
        expires_at=now + timedelta(seconds=settings.session_seconds),
    )
    session.add(authentication)
    await session.commit()
    return TenantContext(user, company, authentication)


async def logout(session: AsyncSession, token: str, settings: Settings) -> None:
    if not token:
        return
    try:
        claims = decode_session(token, settings, allow_expired=True)
    except ApiError:
        return
    authentication = await session.get(AuthSession, UUID(claims["jti"]))
    if (
        authentication
        and authentication.user_id == UUID(claims["sub"])
        and authentication.revoked_at is None
    ):
        authentication.revoked_at = utcnow()
    await session.commit()
