FROM ghcr.io/astral-sh/uv:0.12.7@sha256:95f2aa1fe59274951cfe9b0cbc7972e879ff1004bc8945d130a32eb0dbd85945 AS uv
FROM python:3.12.15-slim-bookworm@sha256:7ec4715ec1f0fc9a6d4835b995d2b6e921ea23ff8b354c33f6f9fb82f5882ac7 AS base
COPY --from=uv /uv /usr/local/bin/uv
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 UV_LINK_MODE=copy
WORKDIR /app
COPY backend/pyproject.toml backend/uv.lock ./

FROM base AS test
RUN uv sync --frozen
COPY backend/ ./
COPY scripts/ /workspace/scripts/
ENV PATH="/app/.venv/bin:$PATH" RUFF_CACHE_DIR=/tmp/ruff MYPY_CACHE_DIR=/tmp/mypy
CMD ["sh", "/workspace/scripts/check-backend.sh"]

FROM base AS runtime
RUN uv sync --frozen --no-dev && useradd --uid 10001 --create-home app
COPY backend/app ./app
COPY backend/alembic ./alembic
COPY backend/alembic.ini ./alembic.ini
ENV PATH="/app/.venv/bin:$PATH"
USER 10001
EXPOSE 8000
CMD ["uvicorn", "app.main:create_app", "--factory", "--host", "0.0.0.0", "--port", "8000", "--no-proxy-headers", "--no-access-log"]
