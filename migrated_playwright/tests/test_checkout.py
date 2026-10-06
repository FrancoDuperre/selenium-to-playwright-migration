import re

import pytest
from playwright.sync_api import expect

from migrated_playwright.data import BACKPACK, CUSTOMER, ERRORS
from migrated_playwright.pages.cart_page import CartPage
from migrated_playwright.pages.checkout_page import CheckoutPage
from migrated_playwright.pages.inventory_page import InventoryPage
from migrated_playwright.pages.login_page import LoginPage


@pytest.fixture
def checkout(page, credentials):
    LoginPage(page).login(credentials["standard"], credentials["password"])
    inventory = InventoryPage(page)
    inventory.add_to_cart(BACKPACK)
    inventory.open_cart()
    CartPage(page).checkout()
    return CheckoutPage(page)


def test_checkout_happy_path(page, checkout):
    checkout.fill_information(**CUSTOMER)
    checkout.continue_checkout()
    checkout.finish()

    expect(page).to_have_url(re.compile(r"checkout-complete\.html"))
    expect(checkout.complete_header).to_have_text("Thank you for your order!")


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

    expect(checkout.error).to_have_text(error)
