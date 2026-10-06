import pytest

from legacy_selenium.data import BACKPACK, BIKE_LIGHT, CUSTOMER
from legacy_selenium.pages.cart_page import CartPage
from legacy_selenium.pages.checkout_page import CheckoutPage
from legacy_selenium.pages.inventory_page import InventoryPage
from legacy_selenium.pages.login_page import LoginPage


@pytest.fixture
def inventory(driver, credentials):
    LoginPage(driver).login(credentials["standard"], credentials["password"])
    return InventoryPage(driver)


def test_add_items_to_cart(driver, inventory):
    inventory.add_to_cart(BACKPACK)
    inventory.add_to_cart(BIKE_LIGHT)

    assert inventory.cart_badge_count() == "2"
    inventory.open_cart()
    assert CartPage(driver).item_names() == ["Sauce Labs Backpack", "Sauce Labs Bike Light"]


def test_remove_item_from_cart(driver, inventory):
    inventory.add_to_cart(BACKPACK)
    inventory.add_to_cart(BIKE_LIGHT)
    inventory.open_cart()
    cart = CartPage(driver)

    cart.remove(BACKPACK)

    assert cart.item_names() == ["Sauce Labs Bike Light"]
    assert cart.cart_badge_count() == "1"


def test_cart_totals_match_order_summary(driver, inventory):
    inventory.add_to_cart(BACKPACK)
    inventory.add_to_cart(BIKE_LIGHT)
    inventory.open_cart()
    cart = CartPage(driver)
    cart_sum = sum(cart.item_prices())
    cart.checkout()
    checkout = CheckoutPage(driver)
    checkout.fill_information(**CUSTOMER)
    checkout.continue_checkout()

    assert checkout.subtotal() == pytest.approx(cart_sum)
    assert checkout.total() == pytest.approx(checkout.subtotal() + checkout.tax())
