import pytest

from legacy_selenium.data import BACKPACK, CUSTOMER, ERRORS
from legacy_selenium.pages.cart_page import CartPage
from legacy_selenium.pages.checkout_page import CheckoutPage
from legacy_selenium.pages.inventory_page import InventoryPage
from legacy_selenium.pages.login_page import LoginPage


@pytest.fixture
def checkout(driver, credentials):
    LoginPage(driver).login(credentials["standard"], credentials["password"])
    inventory = InventoryPage(driver)
    inventory.add_to_cart(BACKPACK)
    inventory.open_cart()
    CartPage(driver).checkout()
    return CheckoutPage(driver)


def test_checkout_happy_path(driver, checkout):
    checkout.fill_information(**CUSTOMER)
    checkout.continue_checkout()
    checkout.finish()

    assert "checkout-complete.html" in driver.current_url
    assert checkout.complete_header() == "Thank you for your order!"


@pytest.mark.parametrize(
    "missing, error",
    [
        ("first_name", ERRORS["first_name_required"]),
        ("last_name", ERRORS["last_name_required"]),
        ("postal_code", ERRORS["postal_code_required"]),
    ],
)
def test_checkout_requires_field(checkout, missing, error):
    checkout.fill_information(**{**CUSTOMER, missing: ""})
    checkout.continue_checkout()

    assert checkout.error_message() == error
