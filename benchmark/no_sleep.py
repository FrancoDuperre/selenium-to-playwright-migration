"""pytest plugin used only by the benchmark (`-p benchmark.no_sleep`).

Replaces `time.sleep` with a no-op inside the legacy page objects, so the benchmark can
separate the cost of fixed sleeps from everything else. Selenium's own polling in
WebDriverWait is left untouched.
"""

import importlib
import pkgutil
import types

import legacy_selenium.pages as legacy_pages

_NO_SLEEP_TIME = types.SimpleNamespace(sleep=lambda seconds: None)


def pytest_configure(config):
    for module_info in pkgutil.iter_modules(legacy_pages.__path__):
        module = importlib.import_module(f"{legacy_pages.__name__}.{module_info.name}")
        if hasattr(module, "time"):
            module.time = _NO_SLEEP_TIME
