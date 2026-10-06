from legacy_selenium.data import ERRORS
from legacy_selenium.pages.inventory_page import InventoryPage
from legacy_selenium.pages.login_page import LoginPage


def test_valid_login(driver, credentials):
    LoginPage(driver).login(credentials["standard"], credentials["password"])

    assert "inventory.html" in driver.current_url
    assert InventoryPage(driver).title() == "Products"


def test_wrong_password(driver, credentials):
    login_page = LoginPage(driver)
    login_page.login(credentials["standard"], "wrong-password")

    assert login_page.error_message() == ERRORS["invalid_credentials"]


def test_locked_out_user(driver, credentials):
    login_page = LoginPage(driver)
    login_page.login(credentials["locked_out"], credentials["password"])

    assert login_page.error_message() == ERRORS["locked_out"]
