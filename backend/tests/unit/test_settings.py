import pytest
from pydantic import ValidationError

from app.core.config import Settings


@pytest.mark.parametrize(
    "url", ["sqlite:///local.db", "not-a-url", "postgresql://localhost/b2b_test_unit"]
)
def test_only_postgresql_urls_accepted(url: str) -> None:
    with pytest.raises(ValidationError):
        Settings(database_url=url)


@pytest.mark.parametrize("timeout", [0, -1, 11])
def test_connection_timeout_is_bounded(timeout: float) -> None:
    with pytest.raises(ValidationError):
        Settings(
            database_url="postgresql+asyncpg://localhost/b2b_test_unit", database_timeout=timeout
        )


def test_invalid_environment_rejected() -> None:
    with pytest.raises(ValidationError):
        Settings(database_url="postgresql+asyncpg://localhost/b2b_test_unit", environment="typo")
