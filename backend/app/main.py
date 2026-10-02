from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.v1.health import router
from app.core.config import Settings
from app.db.database import Database


def create_app(settings: Settings | None = None) -> FastAPI:
    configuration = settings or Settings()

    @asynccontextmanager
    async def lifespan(app: FastAPI) -> AsyncIterator[None]:
        database = Database(configuration)
        app.state.database = database
        try:
            yield
        finally:
            await database.close()

    app = FastAPI(
        title="B2B Subscriptions API",
        version="0.1.0",
        description="Phase 1: process health and PostgreSQL readiness only.",
        lifespan=lifespan,
        docs_url="/api/docs",
        openapi_url="/api/openapi.json",
        redoc_url=None,
    )
    app.include_router(router)
    return app
