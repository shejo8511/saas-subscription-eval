"""Ephemeral accounts for an isolated E2E database; never touches development data."""

import asyncio
import json
import os
import secrets
from pathlib import Path

from sqlalchemy.engine import make_url

from app.core.config import Settings
from app.core.security import password_hasher
from app.db.database import Database
from app.db.models import Company, Subscription, User


async def prepare() -> None:
    url = os.environ["TEST_DATABASE_URL"]
    parsed = make_url(url)
    if parsed.drivername != "postgresql+asyncpg" or not (parsed.database or "").startswith(
        "b2b_test_"
    ):
        raise RuntimeError("E2E fixtures require an isolated real PostgreSQL test database")
    db = Database(Settings(database_url=url))
    accounts = []
    try:
        async with db.sessions() as session:
            for name in ("Empresa Prueba A", "Empresa Prueba B"):
                company = Company(name=name)
                session.add(company)
                await session.flush()
                session.add(
                    Subscription(company_id=company.id, max_licenses=3, monthly_api_limit=10)
                )
                for role in ("Admin", "User"):
                    password = secrets.token_urlsafe(24)
                    email = f"{role.lower()}.{len(accounts)}@e2e.invalid"
                    hashed = await asyncio.to_thread(password_hasher.hash, password)
                    session.add(
                        User(
                            company_id=company.id,
                            name=f"{role} {name}",
                            email=email,
                            password_hash=hashed,
                            role=role,
                        )
                    )
                    accounts.append(dict(email=email, password=password, role=role, company=name))
            await session.commit()
        content = json.dumps(accounts)
        await asyncio.to_thread(write_accounts, content)
    finally:
        await db.close()


def write_accounts(content: str) -> None:
    destination = Path("/fixtures/accounts.json")
    descriptor = os.open(destination, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
    with os.fdopen(descriptor, "w") as stream:
        stream.write(content)


if __name__ == "__main__":
    asyncio.run(prepare())
