import time

from legacy_selenium.pages.base_page import BasePage, parse_price


class CheckoutPage(BasePage):
    FIRST_NAME = '[data-test="firstName"]'
    LAST_NAME = '[data-test="lastName"]'
    POSTAL_CODE = '[data-test="postalCode"]'
    CONTINUE = '[data-test="continue"]'
    FINISH = '[data-test="finish"]'
    ERROR = '[data-test="error"]'
    SUBTOTAL = '[data-test="subtotal-label"]'
    TAX = '[data-test="tax-label"]'
    TOTAL = '[data-test="total-label"]'
    COMPLETE_HEADER = '[data-test="complete-header"]'

    def fill_information(self, first_name="", last_name="", postal_code=""):
        if first_name:
            self.type(self.FIRST_NAME, first_name)
        if last_name:
            self.type(self.LAST_NAME, last_name)
        if postal_code:
            self.type(self.POSTAL_CODE, postal_code)

    def continue_checkout(self):
        self.click(self.CONTINUE)
        time.sleep(1)

    def finish(self):
        self.click(self.FINISH)
        time.sleep(1)

    def error_message(self):
        return self.text_of(self.ERROR)

    def subtotal(self):
        return parse_price(self.text_of(self.SUBTOTAL))

    def tax(self):
        return parse_price(self.text_of(self.TAX))

    def total(self):
        return parse_price(self.text_of(self.TOTAL))

    def complete_header(self):
        return self.text_of(self.COMPLETE_HEADER)
