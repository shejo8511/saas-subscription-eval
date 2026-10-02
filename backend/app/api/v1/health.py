from typing import Literal

from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from sqlalchemy.exc import SQLAlchemyError

router = APIRouter(prefix="/api/v1", tags=["health"])


class HealthResponse(BaseModel):
    status: Literal["ok"] = "ok"


class ReadinessResponse(BaseModel):
    status: Literal["ready", "unavailable"]
    database: Literal["ready", "unavailable"]


@router.get("/health", response_model=HealthResponse)
async def health() -> HealthResponse:
    return HealthResponse()


@router.get(
    "/ready",
    response_model=ReadinessResponse,
    responses={503: {"model": ReadinessResponse, "description": "Database not ready"}},
)
async def readiness(request: Request) -> JSONResponse:
    try:
        ready = await request.app.state.database.is_ready()
    except (SQLAlchemyError, OSError, TimeoutError):
        ready = False
    state: Literal["ready", "unavailable"] = "ready" if ready else "unavailable"
    return JSONResponse(
        status_code=200 if ready else 503,
        content=ReadinessResponse(status=state, database=state).model_dump(),
        headers={"Cache-Control": "no-store"},
    )
