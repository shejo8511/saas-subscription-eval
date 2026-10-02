from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    MetaData,
    String,
    func,
    text,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    metadata = MetaData(schema="b2b")


class Company(Base):
    __tablename__ = "companies"
    __table_args__ = (CheckConstraint("state IN ('active', 'inactive')", name="company_state"),)
    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    name: Mapped[str] = mapped_column(String(120))
    state: Mapped[str] = mapped_column(String(8), default="active")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )


class User(Base):
    __tablename__ = "users"
    __table_args__ = (
        CheckConstraint("role IN ('Admin', 'User')", name="user_role"),
        CheckConstraint("state IN ('active', 'inactive')", name="user_state"),
        CheckConstraint(
            "email = lower(btrim(email)) AND email LIKE '%@%'", name="normalized_email"
        ),
        Index("users_company", "company_id"),
    )
    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    company_id: Mapped[UUID] = mapped_column(ForeignKey("b2b.companies.id"))
    name: Mapped[str] = mapped_column(String(120))
    email: Mapped[str] = mapped_column(String(254), unique=True)
    password_hash: Mapped[str] = mapped_column(String(256))
    role: Mapped[str] = mapped_column(String(5))
    state: Mapped[str] = mapped_column(String(8), default="active")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )


class Subscription(Base):
    __tablename__ = "subscriptions"
    __table_args__ = (
        CheckConstraint("state IN ('active', 'inactive')", name="subscription_state"),
        CheckConstraint("max_licenses > 0 AND monthly_api_limit > 0", name="positive_quotas"),
        Index(
            "one_active_subscription",
            "company_id",
            unique=True,
            postgresql_where=text("state = 'active'"),
        ),
    )
    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    company_id: Mapped[UUID] = mapped_column(ForeignKey("b2b.companies.id"))
    state: Mapped[str] = mapped_column(String(8), default="active")
    max_licenses: Mapped[int] = mapped_column(Integer)
    monthly_api_limit: Mapped[int] = mapped_column(Integer)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )


class AuthSession(Base):
    __tablename__ = "auth_sessions"
    __table_args__ = (
        CheckConstraint("expires_at > created_at", name="session_expiry"),
        CheckConstraint(
            "revoked_at IS NULL OR revoked_at >= created_at", name="session_revocation"
        ),
        Index("sessions_user", "user_id"),
    )
    jti: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    user_id: Mapped[UUID] = mapped_column(ForeignKey("b2b.users.id"))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    revoked_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))


class LoginBucket(Base):
    """One bounded, shared service-wide fixed window; never trusts client IP headers."""

    __tablename__ = "login_bucket"
    __table_args__ = (
        CheckConstraint("id = 'login'", name="single_login_bucket"),
        CheckConstraint("attempts > 0", name="positive_attempts"),
    )
    id: Mapped[str] = mapped_column(String(5), primary_key=True)
    attempts: Mapped[int] = mapped_column(Integer)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
