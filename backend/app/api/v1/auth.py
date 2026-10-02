from fastapi import APIRouter, Request, Response

from app.core.errors import ErrorResponse
from app.core.security import (
    CSRF_COOKIE,
    SESSION_COOKIE,
    check_csrf,
    clear_cookies,
    csrf_binding,
    encode_session,
    issue_csrf,
    set_cookie,
)
from app.modules.auth.schemas import CsrfResponse, Identity, LoginInput, LogoutResponse
from app.modules.auth.service import SessionDependency, TenantDependency, login, logout

router = APIRouter(
    prefix="/api/v1/auth",
    tags=["Authentication"],
    responses={code: {"model": ErrorResponse} for code in (401, 403, 422, 429, 500, 503)},
)


@router.get("/csrf", response_model=CsrfResponse)
async def csrf(request: Request, response: Response) -> CsrfResponse:
    settings = request.app.state.settings
    token = issue_csrf(
        response, csrf_binding(request, settings), settings, request.cookies.get(CSRF_COOKIE, "")
    )
    return CsrfResponse(csrf_token=token)


@router.post("/login", response_model=Identity)
async def authenticate(
    data: LoginInput, request: Request, response: Response, session: SessionDependency
) -> Identity:
    settings = request.app.state.settings
    check_csrf(request, settings)
    tenant = await login(session, data, settings, request.app.state.dummy_hash)
    token = encode_session(
        tenant.user.id,
        tenant.session.jti,
        tenant.session.created_at,
        tenant.session.expires_at,
        settings,
    )
    set_cookie(response, SESSION_COOKIE, token, settings, http_only=True)
    issue_csrf(response, str(tenant.session.jti), settings)
    return tenant.public()


@router.get("/me", response_model=Identity)
async def me(tenant: TenantDependency) -> Identity:
    return tenant.public()


@router.post("/logout", response_model=LogoutResponse)
async def sign_out(
    request: Request, response: Response, session: SessionDependency
) -> LogoutResponse:
    settings = request.app.state.settings
    check_csrf(request, settings)
    await logout(session, request.cookies.get(SESSION_COOKIE, ""), settings)
    clear_cookies(response, settings)
    return LogoutResponse()
