import secrets
from uuid import NAMESPACE_URL, uuid5

import pytest
from sqlalchemy import select, text

from app.core.config import Settings
from app.core.security import verify_password
from app.db.database import Database
from app.db.models import Company, Subscription, User
from app.seed import seed

pytestmark = pytest.mark.integration


async def test_seed_is_idempotent_and_preserves_owner_changes(database_url):
    settings = Settings(database_url=database_url, environment="development", demo_seed=True)
    db = Database(settings)
    accounts = [
        dict(
            company=company,
            name=role,
            email=f"{role.lower()}@{company}.invalid",
            role=role,
            password=secrets.token_urlsafe(24),
        )
        for company in ["a", "b"]
        for role in ["Admin", "User"]
    ]
    try:
        async with db.sessions() as session:
            await session.execute(text("TRUNCATE b2b.companies CASCADE"))
            await seed(session, accounts, settings)
            users = list(await session.scalars(select(User)))
            assert len(users) == 4
            assert len(list(await session.scalars(select(Company)))) == 2
            assert len(list(await session.scalars(select(Subscription)))) == 2
            user = await session.get(User, uuid5(NAMESPACE_URL, "b2b-demo:" + accounts[0]["email"]))
            assert verify_password(accounts[0]["password"], user.password_hash)
            original_hash = user.password_hash
            user.role = "User"
            user.state = "inactive"
            company = await session.get(Company, user.company_id)
            company.state = "inactive"
            subscription = await session.get(Subscription, user.company_id)
            subscription.max_licenses = 7
            subscription.state = "inactive"
            await session.commit()
            accounts[0]["password"] = secrets.token_urlsafe(24)
            await seed(session, accounts, settings)
            await session.refresh(user)
            await session.refresh(company)
            await session.refresh(subscription)
            assert (
                user.role == "User"
                and user.state == "inactive"
                and user.password_hash == original_hash
            )
            assert (
                company.state == "inactive"
                and subscription.max_licenses == 7
                and subscription.state == "inactive"
            )
            assert len(list(await session.scalars(select(User)))) == 4
            with pytest.raises(ValueError):
                await seed(session, accounts, Settings(database_url=database_url))
            await session.execute(text("TRUNCATE b2b.companies CASCADE"))
            await session.commit()
    finally:
        await db.close()
