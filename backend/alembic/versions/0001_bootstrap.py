"""Reserve the application's PostgreSQL namespace; no business models yet."""

from alembic import op

revision = "0001_bootstrap"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("CREATE SCHEMA b2b")


def downgrade() -> None:
    op.execute("DROP SCHEMA b2b")
