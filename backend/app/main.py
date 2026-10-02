import asyncio
import secrets
from collections.abc import AsyncIterator, Awaitable, Callable
from contextlib import asynccontextmanager
from uuid import uuid4

from fastapi import FastAPI, Request
from starlette.responses import Response

from app.api.v1.auth import router as auth_router
from app.api.v1.health import router
from app.core.config import Settings
from app.core.errors import error_response, install_error_handlers
from app.core.security import password_hasher
from app.db.database import Database


def create_app(settings: Settings | None = None) -> FastAPI:
    configuration = settings or Settings()

    @asynccontextmanager
    async def lifespan(app: FastAPI) -> AsyncIterator[None]:
        database = Database(configuration)
        app.state.database = database
        app.state.dummy_hash = await asyncio.to_thread(
            password_hasher.hash, secrets.token_urlsafe(32)
        )
        try:
            yield
        finally:
            await database.close()

    app = FastAPI(
        title="B2B Subscriptions API",
        version="0.1.0",
        description="Phase 2: company-scoped, revocable cookie sessions with JWT and CSRF.",
        lifespan=lifespan,
        docs_url="/api/docs",
        openapi_url="/api/openapi.json",
        redoc_url=None,
    )
    app.state.settings = configuration
    install_error_handlers(app)

    @app.middleware("http")
    async def request_metadata(
        request: Request, call_next: Callable[[Request], Awaitable[Response]]
    ) -> Response:
        request.state.request_id = str(uuid4())
        try:
            response = await call_next(request)
        except Exception:
            response = error_response(
                request, 500, "INTERNAL_ERROR", "No se pudo completar la solicitud."
            )
        response.headers["X-Request-ID"] = request.state.request_id
        if request.url.path.startswith("/api/v1/auth"):
            response.headers["Cache-Control"] = "no-store"
        return response

    app.include_router(router)
    app.include_router(auth_router)
    return app
