import pytest
from playwright.sync_api import expect

from migrated_playwright.data import BACKPACK, BIKE_LIGHT, CUSTOMER
from migrated_playwright.pages.cart_page import CartPage
from migrated_playwright.pages.checkout_page import CheckoutPage
from migrated_playwright.pages.inventory_page import InventoryPage
from migrated_playwright.pages.login_page import LoginPage


@pytest.fixture
def inventory(page, credentials):
    LoginPage(page).login(credentials["standard"], credentials["password"])
    return InventoryPage(page)


def test_add_items_to_cart(page, inventory):
    inventory.add_to_cart(BACKPACK)
    inventory.add_to_cart(BIKE_LIGHT)

    expect(inventory.cart_badge).to_have_text("2")
    inventory.open_cart()
    expect(CartPage(page).item_names).to_have_text([BACKPACK, BIKE_LIGHT])


def test_remove_item_from_cart(page, inventory):
    inventory.add_to_cart(BACKPACK)
    inventory.add_to_cart(BIKE_LIGHT)
    inventory.open_cart()
    cart = CartPage(page)

    cart.remove(BACKPACK)

    expect(cart.item_names).to_have_text([BIKE_LIGHT])
    expect(cart.cart_badge).to_have_text("1")


def test_cart_totals_match_order_summary(page, inventory):
    inventory.add_to_cart(BACKPACK)
    inventory.add_to_cart(BIKE_LIGHT)
    inventory.open_cart()
    cart = CartPage(page)
    cart_sum = sum(cart.prices())
    cart.checkout()
    checkout = CheckoutPage(page)
    checkout.fill_information(**CUSTOMER)
    checkout.continue_checkout()

    assert checkout.subtotal() == pytest.approx(cart_sum)
    assert checkout.total() == pytest.approx(checkout.subtotal() + checkout.tax())
