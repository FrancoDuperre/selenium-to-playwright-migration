import re

from playwright.sync_api import expect

from migrated_playwright.data import ERRORS
from migrated_playwright.pages.login_page import LoginPage


def test_valid_login(page, credentials):
    login_page = LoginPage(page)
    login_page.login(credentials["standard"], credentials["password"])

    expect(page).to_have_url(re.compile(r"inventory\.html"))
    expect(login_page.title).to_have_text("Products")


def test_wrong_password(page, credentials):
    login_page = LoginPage(page)
    login_page.login(credentials["standard"], "wrong-password")

    expect(login_page.error).to_have_text(ERRORS["invalid_credentials"])


def test_locked_out_user(page, credentials):
    login_page = LoginPage(page)
    login_page.login(credentials["locked_out"], credentials["password"])

    expect(login_page.error).to_have_text(ERRORS["locked_out"])
