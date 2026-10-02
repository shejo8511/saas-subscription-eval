from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine

from app.core.config import Settings


class Database:
    def __init__(self, settings: Settings) -> None:
        self.engine = create_async_engine(
            settings.database_url.encoded_string(),
            pool_pre_ping=True,
            connect_args={
                "timeout": settings.database_timeout,
                "server_settings": {"statement_timeout": "3000"},
            },
        )

    async def is_ready(self) -> bool:
        async with self.engine.connect() as connection:
            return bool(
                await connection.scalar(
                    text("SELECT EXISTS (SELECT 1 FROM pg_namespace WHERE nspname = 'b2b')")
                )
            )

    async def close(self) -> None:
        await self.engine.dispose()
