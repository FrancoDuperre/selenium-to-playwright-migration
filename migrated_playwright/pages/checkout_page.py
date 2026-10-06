from playwright.sync_api import Page

from migrated_playwright.pages.base_page import BasePage, parse_price


class CheckoutPage(BasePage):
    def __init__(self, page: Page):
        super().__init__(page)
        self.first_name = page.get_by_test_id("firstName")
        self.last_name = page.get_by_test_id("lastName")
        self.postal_code = page.get_by_test_id("postalCode")
        self.continue_button = page.get_by_test_id("continue")
        self.finish_button = page.get_by_test_id("finish")
        self.error = page.get_by_test_id("error")
        self.subtotal_label = page.get_by_test_id("subtotal-label")
        self.tax_label = page.get_by_test_id("tax-label")
        self.total_label = page.get_by_test_id("total-label")
        self.complete_header = page.get_by_test_id("complete-header")

    def fill_information(self, first_name: str = "", last_name: str = "", postal_code: str = "") -> None:
        if first_name:
            self.first_name.fill(first_name)
        if last_name:
            self.last_name.fill(last_name)
        if postal_code:
            self.postal_code.fill(postal_code)

    def continue_checkout(self) -> None:
        self.continue_button.click()

    def finish(self) -> None:
        self.finish_button.click()

    def subtotal(self) -> float:
        return parse_price(self.subtotal_label.inner_text())

    def tax(self) -> float:
        return parse_price(self.tax_label.inner_text())

    def total(self) -> float:
        return parse_price(self.total_label.inner_text())
