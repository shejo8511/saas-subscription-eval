import logging
from collections.abc import Mapping
from uuid import uuid4

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from pydantic import BaseModel
from sqlalchemy.exc import SQLAlchemyError
from starlette.exceptions import HTTPException
from starlette.responses import JSONResponse

logger = logging.getLogger("b2b.errors")


class ErrorBody(BaseModel):
    code: str
    message: str


class ErrorResponse(BaseModel):
    error: ErrorBody
    request_id: str


class ApiError(Exception):
    def __init__(
        self, status: int, code: str, message: str, headers: Mapping[str, str] | None = None
    ):
        self.status, self.code, self.message = status, code, message
        self.headers = headers or {}


def error_response(
    request: Request, status: int, code: str, message: str, headers: Mapping[str, str] | None = None
) -> JSONResponse:
    request_id = getattr(request.state, "request_id", str(uuid4()))
    logger.warning("request_id=%s code=%s status=%s", request_id, code, status)
    return JSONResponse(
        status_code=status,
        content={
            "error": {"code": code, "message": message},
            "request_id": request_id,
        },
        headers={"Cache-Control": "no-store", "X-Request-ID": request_id, **(headers or {})},
    )


def install_error_handlers(app: FastAPI) -> None:
    @app.exception_handler(ApiError)
    async def expected(request: Request, error: ApiError) -> JSONResponse:
        return error_response(request, error.status, error.code, error.message, error.headers)

    @app.exception_handler(RequestValidationError)
    async def validation(request: Request, error: RequestValidationError) -> JSONResponse:
        return error_response(request, 422, "VALIDATION_ERROR", "Revisa los campos enviados.")

    @app.exception_handler(HTTPException)
    async def http_error(request: Request, error: HTTPException) -> JSONResponse:
        return error_response(
            request, error.status_code, "HTTP_ERROR", "Solicitud no disponible.", error.headers
        )

    @app.exception_handler(SQLAlchemyError)
    @app.exception_handler(OSError)
    @app.exception_handler(TimeoutError)
    async def database_error(request: Request, error: Exception) -> JSONResponse:
        return error_response(
            request, 503, "SERVICE_UNAVAILABLE", "Servicio temporalmente no disponible."
        )

    @app.exception_handler(Exception)
    async def unexpected(request: Request, error: Exception) -> JSONResponse:
        return error_response(request, 500, "INTERNAL_ERROR", "No se pudo completar la solicitud.")
