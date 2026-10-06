import time

from legacy_selenium.pages.base_page import BasePage


class InventoryPage(BasePage):
    TITLE = '[data-test="title"]'
    CART_LINK = '[data-test="shopping-cart-link"]'

    def title(self):
        return self.text_of(self.TITLE)

    def add_to_cart(self, product_slug):
        self.click(f'[data-test="add-to-cart-{product_slug}"]')
        time.sleep(0.5)  # wait for the badge to update

    def open_cart(self):
        self.click(self.CART_LINK)
        time.sleep(1)
