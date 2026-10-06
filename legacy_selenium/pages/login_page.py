import time

from legacy_selenium.pages.base_page import BasePage


class LoginPage(BasePage):
    USERNAME = '[data-test="username"]'
    PASSWORD = '[data-test="password"]'
    LOGIN_BUTTON = '[data-test="login-button"]'
    ERROR = '[data-test="error"]'

    def login(self, username, password):
        self.type(self.USERNAME, username)
        self.type(self.PASSWORD, password)
        self.click(self.LOGIN_BUTTON)
        time.sleep(1)  # give the inventory page time to load

    def error_message(self):
        return self.text_of(self.ERROR)
