import time

from legacy_selenium.pages.base_page import BasePage, parse_price


class CartPage(BasePage):
    ITEM_NAME = '[data-test="inventory-item-name"]'
    ITEM_PRICE = '[data-test="inventory-item-price"]'
    CHECKOUT = '[data-test="checkout"]'

    def item_names(self):
        return [element.text for element in self.find_all(self.ITEM_NAME)]

    def item_prices(self):
        return [parse_price(element.text) for element in self.find_all(self.ITEM_PRICE)]

    def remove(self, product_slug):
        self.click(f'[data-test="remove-{product_slug}"]')
        time.sleep(0.5)

    def checkout(self):
        self.click(self.CHECKOUT)
        time.sleep(1)
