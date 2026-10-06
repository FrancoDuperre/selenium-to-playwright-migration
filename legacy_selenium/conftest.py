import os
from pathlib import Path

import pytest
from dotenv import load_dotenv
from selenium import webdriver

load_dotenv()

SCREENSHOT_DIR = Path("screenshots")


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


@pytest.fixture
def driver(base_url):
    options = webdriver.ChromeOptions()
    options.add_argument("--headless=new")
    options.add_argument("--window-size=1920,1080")
    options.add_experimental_option(
        "prefs",
        {
            "credentials_enable_service": False,
            "profile.password_manager_enabled": False,
            "profile.password_manager_leak_detection": False,
        },
    )
    driver = webdriver.Chrome(options=options)
    driver.get(base_url)
    yield driver
    driver.quit()


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """Save a screenshot by hand when a test fails."""
    outcome = yield
    report = outcome.get_result()
    if report.when == "call" and report.failed:
        driver = item.funcargs.get("driver")
        if driver is not None:
            SCREENSHOT_DIR.mkdir(exist_ok=True)
            driver.save_screenshot(str(SCREENSHOT_DIR / f"{item.name}.png"))
