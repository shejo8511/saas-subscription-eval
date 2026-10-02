"""Companies, users, subscriptions, revocable sessions and a bounded login limiter."""

import sqlalchemy as sa

from alembic import op

revision = "0002_auth_tenancy"
down_revision = "0001_bootstrap"
branch_labels = None
depends_on = None


def timestamps():
    return [
        sa.Column(
            "created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()
        ),
        sa.Column(
            "updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()
        ),
    ]


def upgrade() -> None:
    op.create_table(
        "companies",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("name", sa.String(120), nullable=False),
        sa.Column("state", sa.String(8), nullable=False),
        *timestamps(),
        sa.CheckConstraint("state IN ('active', 'inactive')", name="company_state"),
        schema="b2b",
    )
    op.create_table(
        "users",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("company_id", sa.Uuid(), sa.ForeignKey("b2b.companies.id"), nullable=False),
        sa.Column("name", sa.String(120), nullable=False),
        sa.Column("email", sa.String(254), nullable=False, unique=True),
        sa.Column("password_hash", sa.String(256), nullable=False),
        sa.Column("role", sa.String(5), nullable=False),
        sa.Column("state", sa.String(8), nullable=False),
        *timestamps(),
        sa.CheckConstraint("role IN ('Admin', 'User')", name="user_role"),
        sa.CheckConstraint("state IN ('active', 'inactive')", name="user_state"),
        sa.CheckConstraint(
            "email = lower(btrim(email)) AND email LIKE '%@%'", name="normalized_email"
        ),
        schema="b2b",
    )
    op.create_index("users_company", "users", ["company_id"], schema="b2b")
    op.create_table(
        "subscriptions",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("company_id", sa.Uuid(), sa.ForeignKey("b2b.companies.id"), nullable=False),
        sa.Column("state", sa.String(8), nullable=False),
        sa.Column("max_licenses", sa.Integer(), nullable=False),
        sa.Column("monthly_api_limit", sa.Integer(), nullable=False),
        *timestamps(),
        sa.CheckConstraint("state IN ('active', 'inactive')", name="subscription_state"),
        sa.CheckConstraint("max_licenses > 0 AND monthly_api_limit > 0", name="positive_quotas"),
        schema="b2b",
    )
    op.create_index(
        "one_active_subscription",
        "subscriptions",
        ["company_id"],
        unique=True,
        postgresql_where=sa.text("state = 'active'"),
        schema="b2b",
    )
    op.create_table(
        "auth_sessions",
        sa.Column("jti", sa.Uuid(), primary_key=True),
        sa.Column("user_id", sa.Uuid(), sa.ForeignKey("b2b.users.id"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("revoked_at", sa.DateTime(timezone=True)),
        sa.CheckConstraint("expires_at > created_at", name="session_expiry"),
        sa.CheckConstraint(
            "revoked_at IS NULL OR revoked_at >= created_at", name="session_revocation"
        ),
        schema="b2b",
    )
    op.create_index("sessions_user", "auth_sessions", ["user_id"], schema="b2b")
    op.create_table(
        "login_bucket",
        sa.Column("id", sa.String(5), primary_key=True),
        sa.Column("attempts", sa.Integer(), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint("id = 'login'", name="single_login_bucket"),
        sa.CheckConstraint("attempts > 0", name="positive_attempts"),
        schema="b2b",
    )


def downgrade() -> None:
    for table in ["login_bucket", "auth_sessions", "subscriptions", "users", "companies"]:
        op.drop_table(table, schema="b2b")
