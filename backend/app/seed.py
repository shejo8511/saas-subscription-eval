"""Explicit one-shot development demo seed; never executed by workers."""

import asyncio
import json
from pathlib import Path
from uuid import NAMESPACE_URL, uuid5

from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import Settings
from app.core.security import password_hasher
from app.db.database import Database
from app.db.models import Company, Subscription, User


async def seed(session: AsyncSession, accounts: list[dict[str, str]], settings: Settings) -> None:
    if settings.environment != "development" or not settings.demo_seed:
        raise ValueError("Demo seed requires explicitly authorized development configuration")
    for account in accounts:
        company_id = uuid5(NAMESPACE_URL, "b2b-demo:" + account["company"])
        user_id = uuid5(NAMESPACE_URL, "b2b-demo:" + account["email"])
        await session.execute(
            insert(Company)
            .values(id=company_id, name=account["company"], state="active")
            .on_conflict_do_nothing(index_elements=[Company.id])
        )
        await session.execute(
            insert(Subscription)
            .values(
                id=company_id,
                company_id=company_id,
                state="active",
                max_licenses=3,
                monthly_api_limit=10,
            )
            .on_conflict_do_nothing(index_elements=[Subscription.id])
        )
        hashed = await asyncio.to_thread(password_hasher.hash, account["password"])
        await session.execute(
            insert(User)
            .values(
                id=user_id,
                company_id=company_id,
                name=account["name"],
                email=account["email"],
                role=account["role"],
                state="active",
                password_hash=hashed,
            )
            .on_conflict_do_nothing(index_elements=[User.id])
        )
    await session.commit()


async def main() -> None:
    settings = Settings()
    if not settings.demo_seed:
        return
    accounts = json.loads(await asyncio.to_thread(Path("/run/demo-credentials.json").read_text))
    database = Database(settings)
    try:
        async with database.sessions() as session:
            await seed(session, accounts, settings)
    finally:
        await database.close()


if __name__ == "__main__":
    asyncio.run(main())
