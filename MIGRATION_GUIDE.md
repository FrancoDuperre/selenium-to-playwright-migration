# Migration guide: Selenium to Playwright (Python)

How the `legacy_selenium` suite was migrated to `migrated_playwright`. Both suites use Python and Pytest, cover the same ten tests and run on the same installed Google Chrome, so the only thing that changes is the browser automation layer. Every example below is taken from this repository.

## Mapping

| Selenium (before) | Playwright (after) | Why it matters |
| --- | --- | --- |
| `driver.find_element(By.CSS_SELECTOR, ...)` | `page.get_by_test_id(...)` / `page.locator(...)` | Locators are lazy and re-resolved on every action, so there are no stale element references |
| `WebDriverWait` + `expected_conditions` | Auto-waiting actions and `expect(...)` assertions | Clicks wait for the element to be visible, stable and enabled; assertions retry until they pass or time out |
| `time.sleep(n)` | Removed | Fixed sleeps are either too short (flaky) or too long (slow) |
| `driver.get(url)` / `driver.quit()` in a custom fixture | pytest-playwright's `page` fixture | One browser per session and a fresh context per test, instead of a new Chrome per test |
| Manual screenshot in a `pytest_runtest_makereport` hook | `--screenshot=only-on-failure --tracing=retain-on-failure` | Screenshots and full traces (DOM, network, console) on failure, with no custom code |

## 1. Locators

Selenium page objects hold CSS strings and look elements up when they are used. Selectors for product buttons are built by hand from a slug.

```python
# legacy_selenium/pages/inventory_page.py
def add_to_cart(self, product_slug):
    self.click(f'[data-test="add-to-cart-{product_slug}"]')
    time.sleep(0.5)  # wait for the badge to update
```

Playwright page objects hold locators. `data-test` is registered once as the test id attribute, and products are found by their visible name, the way a user finds them.

```python
# migrated_playwright/conftest.py
playwright.selectors.set_test_id_attribute("data-test")

# migrated_playwright/pages/inventory_page.py
def item(self, name: str) -> Locator:
    return self.items.filter(has=self.page.get_by_text(name, exact=True))

def add_to_cart(self, name: str) -> None:
    self.item(name).get_by_role("button", name="Add to cart").click()
```

## 2. Waiting

The legacy suite wraps every lookup in an explicit wait, and still adds sleeps after navigation because the next page may not be ready.

```python
# legacy_selenium/pages/base_page.py
def click(self, css):
    self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, css))).click()

# legacy_selenium/pages/login_page.py
def login(self, username, password):
    self.type(self.USERNAME, username)
    self.type(self.PASSWORD, password)
    self.click(self.LOGIN_BUTTON)
    time.sleep(1)  # give the inventory page time to load
```

In Playwright the action itself waits, so the helper layer disappears.

```python
# migrated_playwright/pages/login_page.py
def login(self, username: str, password: str) -> None:
    self.username.fill(username)
    self.password.fill(password)
    self.login_button.click()
```

One explicit wait remains: `all_inner_texts()` reads whatever is on the page right now and does not auto-wait, so the cart page waits for the first price before reading the list.

```python
# migrated_playwright/pages/cart_page.py
def prices(self) -> list[float]:
    self.item_prices.first.wait_for()  # all_inner_texts() does not auto-wait
    return [parse_price(text) for text in self.item_prices.all_inner_texts()]
```

## 3. Assertions

Selenium assertions read a value once. If the page has not updated yet, the test fails, which is why sleeps creep in.

```python
# legacy_selenium/tests/test_cart.py
assert inventory.cart_badge_count() == "2"
inventory.open_cart()
assert CartPage(driver).item_names() == ["Sauce Labs Backpack", "Sauce Labs Bike Light"]
```

`expect` retries until the condition holds or the timeout expires.

```python
# migrated_playwright/tests/test_cart.py
expect(inventory.cart_badge).to_have_text("2")
inventory.open_cart()
expect(CartPage(page).item_names).to_have_text([BACKPACK, BIKE_LIGHT])
```

## 4. Browser lifecycle

The legacy fixture starts and quits a full Chrome for every test.

```python
# legacy_selenium/conftest.py
@pytest.fixture
def driver(base_url):
    options = webdriver.ChromeOptions()
    options.add_argument("--headless=new")
    ...
    driver = webdriver.Chrome(options=options)
    driver.get(base_url)
    yield driver
    driver.quit()
```

pytest-playwright launches the browser once per session and gives each test an isolated context (its own cookies and storage), which is much cheaper than a new browser process. The suite only overrides `page` to open the login screen.

```python
# migrated_playwright/conftest.py
@pytest.fixture
def page(page):
    page.goto("/")
    return page
```

## 5. Failure artifacts

The legacy suite needs a hook to save screenshots.

```python
# legacy_selenium/conftest.py
@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    report = outcome.get_result()
    if report.when == "call" and report.failed:
        driver = item.funcargs.get("driver")
        if driver is not None:
            SCREENSHOT_DIR.mkdir(exist_ok=True)
            driver.save_screenshot(str(SCREENSHOT_DIR / f"{item.name}.png"))
```

In Playwright this is configuration, and the trace includes far more than a screenshot (open it with `playwright show-trace`).

```ini
# pytest.ini
addopts = --screenshot=only-on-failure --tracing=retain-on-failure --output=test-results
```

## Checklist for a real migration

1. Run the existing suite several times and record time and failures before touching anything.
2. Migrate one page object at a time, starting with login, and keep both suites runnable.
3. Replace each `time.sleep` with an auto-waiting action or an `expect`, never with a shorter sleep.
4. Move cross-cutting code (driver setup, screenshots) into pytest-playwright fixtures and options.
5. Re-run the benchmark and publish the numbers, including the ones that did not improve.
