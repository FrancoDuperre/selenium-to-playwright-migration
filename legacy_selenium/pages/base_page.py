from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


class BasePage:
    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(driver, 10)

    def find(self, css):
        return self.wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, css)))

    def find_all(self, css):
        return self.wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, css)))

    def click(self, css):
        self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, css))).click()

    def type(self, css, text):
        element = self.find(css)
        element.clear()
        element.send_keys(text)

    def text_of(self, css):
        return self.find(css).text

    def cart_badge_count(self):
        badges = self.driver.find_elements(By.CSS_SELECTOR, '[data-test="shopping-cart-badge"]')
        return badges[0].text if badges else ""


def parse_price(text):
    return float(text.split("$")[1])
