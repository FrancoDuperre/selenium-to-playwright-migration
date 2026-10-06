from playwright.sync_api import Locator, Page

from migrated_playwright.pages.base_page import BasePage


class InventoryPage(BasePage):
    def __init__(self, page: Page):
        super().__init__(page)
        self.items = page.get_by_test_id("inventory-item")

    def item(self, name: str) -> Locator:
        return self.items.filter(has=self.page.get_by_text(name, exact=True))

    def add_to_cart(self, name: str) -> None:
        self.item(name).get_by_role("button", name="Add to cart").click()

    def open_cart(self) -> None:
        self.cart_link.click()
