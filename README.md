# Selenium to Playwright Migration

[![CI](https://github.com/FrancoDuperre/selenium-to-playwright-migration/actions/workflows/ci.yml/badge.svg)](https://github.com/FrancoDuperre/selenium-to-playwright-migration/actions/workflows/ci.yml)

The same end-to-end suite written twice, first in Selenium the way inherited suites often look, then migrated to Playwright, with a benchmark that measures what actually changed. Both versions use Python and Pytest and test the public [SauceDemo](https://www.saucedemo.com) practice store.

> **About the "before" suite:** `legacy_selenium/` is a baseline I wrote on purpose with patterns common in inherited Selenium suites (fixed sleeps after navigation, explicit waits around every lookup, hand-built selectors, a new browser per test, a custom screenshot hook). It is not code from a real client or employer.

## Results

Measured on 2026-10-06 on a Windows 11 laptop with Google Chrome 154, both suites driving the same installed Chrome in headless mode. Each run is a full `pytest` invocation, including startup. Variants were run alternately, so network conditions affected all of them equally.

| Metric | Selenium (legacy) | Playwright (migrated) |
| --- | --- | --- |
| Tests per run | 10 | 10 |
| Suite time, median of 10 runs | 70.4 s | 6.8 s |
| Suite time with sleeps disabled, median | 36.8 s | n/a (no sleeps) |
| Runs with at least one failure | 0 / 10 | 0 / 10 |
| Runs with a failure, sleeps disabled | 0 / 10 | n/a |
| Lines of code (pages + tests) | 186 | 172 |
| Fixed sleeps in code | 7 | 0 |
| Explicit wait calls in code | 3 | 1 |
| Setup commands from a fresh clone | 4 | 4 |

Raw data: [`results/benchmark.csv`](results/benchmark.csv) (one row per run) and [`results/code_metrics.csv`](results/code_metrics.csv).

### What the numbers say

- **About 10x faster, for two separate reasons.** Disabling the legacy sleeps alone takes the Selenium suite from 70.4 s to 36.8 s, so roughly half of the original time was fixed waiting. The remaining gap (36.8 s vs 6.8 s) was not measured separately; the main design difference left is that the legacy suite starts a new Chrome for every test, while pytest-playwright reuses one browser and opens a lightweight context per test.
- **No stability gain here.** Both suites passed 10 out of 10 runs, and so did the legacy suite with its sleeps disabled. SauceDemo is fast and predictable, so it does not expose the flakiness that sleeps usually cause on slower apps. This benchmark does not show Playwright being more stable.
- **Only slightly less code.** 172 vs 186 lines (about 8% fewer). Most of the gain is in readability: the explicit-wait helper layer disappears and assertions retry by themselves.
- **Same setup effort.** Both need `git clone`, a virtual environment, `pip install -r requirements.txt` and a `.env` file. Selenium Manager downloads the driver automatically, and the Playwright suite uses the installed Chrome (`--browser-channel=chrome`), so neither needs an extra install step. With Playwright's bundled browsers you would add `playwright install chromium`.

How each number is produced:

| Metric | How it is measured |
| --- | --- |
| Suite time | Wall-clock time of `python -m pytest <suite>`, median of 10 runs |
| Sleeps disabled | Same legacy suite with `-p benchmark.no_sleep`, a plugin that turns `time.sleep` into a no-op inside the page objects only |
| Runs with a failure | Runs whose JUnit XML report has at least one failure or error |
| Lines of code | `cloc` on `pages/` and `tests/` of each suite (code lines, no blanks or comments) |
| Sleeps and waits | Regex count of `time.sleep(` / `wait_for_timeout(` and `.until(` / `.wait_for(` in each suite |
| Setup commands | Counted by hand from the Quick start below |

## Quick start

Requires Python 3.12 and Google Chrome. The benchmark also needs [cloc](https://github.com/AlDanial/cloc).

```bash
git clone https://github.com/FrancoDuperre/selenium-to-playwright-migration.git
cd selenium-to-playwright-migration
python -m venv .venv && source .venv/bin/activate    # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env        # then fill in the demo credentials shown on saucedemo.com

pytest legacy_selenium                    # before
pytest migrated_playwright                # after
python benchmark/run_benchmark.py         # 10 runs of each variant (about 20 minutes)
```

`python benchmark/run_benchmark.py --runs 3` gives a quick sanity check.

## Project structure

```
legacy_selenium/        "Before": Selenium + Pytest
  pages/                Page objects with CSS selectors, WebDriverWait helpers and sleeps
  tests/                test_login.py, test_cart.py, test_checkout.py
  conftest.py           Chrome per test, manual screenshot on failure
migrated_playwright/    "After": Playwright + Pytest, same tests and names
  pages/                Page objects with locators (data-test ids and roles)
  tests/
  conftest.py           data-test as test id, page opened on the login screen
benchmark/
  run_benchmark.py      Runs every variant N times and writes results/
  no_sleep.py           pytest plugin that disables the legacy sleeps
results/                benchmark.csv, code_metrics.csv, summary.md
MIGRATION_GUIDE.md      Before/after mapping with code from this repo
```

## Design decisions

- **Same language, test runner and browser.** Both suites are Python + Pytest and drive the same installed Chrome, so the comparison isolates the automation library instead of mixing in language or browser differences.
- **Same tests, same names.** Each suite has the same 10 tests (login, cart and checkout, positive and negative) so the timing and code metrics compare like with like.
- **A variant without sleeps.** Comparing only "legacy" vs "migrated" would credit Playwright for removing sleeps that could also be removed in Selenium. The no-sleep variant shows how much of the gain comes from each change.
- **Results published as they came out.** The CSV in `results/` is the raw output of one benchmark run. Every row of the results table is copied unedited from `results/summary.md`, except "Setup commands", which is counted by hand.
- **No credentials in the repo.** Demo credentials come from a gitignored `.env` locally and from GitHub Actions secrets in CI.

See [MIGRATION_GUIDE.md](MIGRATION_GUIDE.md) for the step-by-step mapping from Selenium to Playwright, with before and after code.

## CI

Every push and pull request runs both suites and a short 3-run benchmark on GitHub Actions, and uploads the results as an artifact. CI numbers come from a shared Linux runner and will differ from the local results above.

## About

Franco Duperre, QA Automation Engineer. Open to freelance work: <Upwork profile link>
