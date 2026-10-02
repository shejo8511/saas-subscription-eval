from uuid import uuid4

import pytest
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from app.core.config import Settings
from app.db.database import Database
from app.db.models import Company, Subscription, User

pytestmark = pytest.mark.integration


@pytest.mark.parametrize(
    "invalid",
    [
        "email",
        "duplicate",
        "role",
        "user_state",
        "company_state",
        "fk",
        "quota",
        "subscription_state",
        "active_duplicate",
    ],
)
async def test_database_constraints(database_url: str, invalid: str) -> None:
    db = Database(Settings(database_url=database_url, database_timeout=10))
    try:
        async with db.sessions() as session:
            company = Company(name="Constraint probe")
            session.add(company)
            await session.flush()
            email = f"{uuid4()}@test.invalid"
            user = User(
                company_id=company.id, name="Probe", email=email, password_hash="hash", role="User"
            )
            session.add(user)
            await session.flush()
            sub = Subscription(company_id=company.id, max_licenses=3, monthly_api_limit=10)
            session.add(sub)
            await session.flush()
            match invalid:
                case "email":
                    user.email = email.upper()
                case "duplicate":
                    session.add(
                        User(
                            company_id=company.id,
                            name="Duplicate",
                            email=email,
                            password_hash="hash",
                            role="User",
                        )
                    )
                case "role":
                    user.role = "Owner"
                case "user_state":
                    user.state = "unknown"
                case "company_state":
                    company.state = "unknown"
                case "fk":
                    user.company_id = uuid4()
                case "quota":
                    sub.max_licenses = 0
                case "subscription_state":
                    sub.state = "unknown"
                case "active_duplicate":
                    session.add(
                        Subscription(company_id=company.id, max_licenses=1, monthly_api_limit=1)
                    )
            company_id = company.id
            with pytest.raises(IntegrityError):
                await session.flush()
            await session.rollback()
            assert await session.scalar(select(Company).where(Company.id == company_id)) is None
    finally:
        await db.close()
