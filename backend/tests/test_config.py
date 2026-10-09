import pytest

from app.core.config import Settings


def test_demo_rejects_placeholder_secret():
    with pytest.raises(ValueError):
        Settings(APP_ENV="demo").validate_runtime_secrets()


def test_dev_allows_placeholder_secret():
    Settings(APP_ENV="dev").validate_runtime_secrets()

