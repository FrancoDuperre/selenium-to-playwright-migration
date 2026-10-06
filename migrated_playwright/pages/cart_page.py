from playwright.sync_api import Page

from migrated_playwright.pages.base_page import BasePage, parse_price


class CartPage(BasePage):
    def __init__(self, page: Page):
        super().__init__(page)
        self.items = page.get_by_test_id("inventory-item")
        self.item_names = page.get_by_test_id("inventory-item-name")
        self.item_prices = page.get_by_test_id("inventory-item-price")
        self.checkout_button = page.get_by_test_id("checkout")

    def prices(self) -> list[float]:
        self.item_prices.first.wait_for()  # all_inner_texts() does not auto-wait
        return [parse_price(text) for text in self.item_prices.all_inner_texts()]

    def remove(self, name: str) -> None:
        self.items.filter(has=self.page.get_by_text(name, exact=True)).get_by_role(
            "button", name="Remove"
        ).click()

    def checkout(self) -> None:
        self.checkout_button.click()
