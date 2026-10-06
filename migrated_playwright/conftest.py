import os

import pytest
from dotenv import load_dotenv

load_dotenv()


def require_env(name):
    value = os.getenv(name)
    if not value:
        pytest.exit(f"Missing environment variable {name}. Copy .env.example to .env.", returncode=2)
    return value


@pytest.fixture(scope="session")
def credentials():
    return {
        "standard": require_env("SAUCE_USERNAME"),
        "locked_out": require_env("SAUCE_LOCKED_OUT_USERNAME"),
        "password": require_env("SAUCE_PASSWORD"),
    }


@pytest.fixture(scope="session", autouse=True)
def use_data_test_attribute(playwright):
    playwright.selectors.set_test_id_attribute("data-test")


@pytest.fixture
def page(page):
    """pytest-playwright's page, opened on the login screen (base_url comes from pytest.ini)."""
    page.goto("/")
    return page
