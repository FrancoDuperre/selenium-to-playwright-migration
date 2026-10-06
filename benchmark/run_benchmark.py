"""Benchmark the legacy Selenium suite against the migrated Playwright suite.

Runs every variant N times, alternating between them so network drift affects all of
them equally, and writes:
  results/benchmark.csv      one row per run (raw data)
  results/code_metrics.csv   lines of code and waits per suite
  results/summary.md         the results table used in the README

Usage: python benchmark/run_benchmark.py [--runs 10]
"""

import argparse
import csv
import json
import re
import shutil
import statistics
import subprocess
import sys
import time
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RESULTS = ROOT / "results"

VARIANTS = {
    "selenium": ["legacy_selenium"],
    "selenium-no-sleeps": ["legacy_selenium", "-p", "benchmark.no_sleep"],
    "playwright": ["migrated_playwright"],
}
SUITES = {"selenium": "legacy_selenium", "playwright": "migrated_playwright"}


def run_once(args: list[str], junit: Path) -> tuple[float, int, int]:
    """Returns (seconds, tests, failed tests). A run that crashes counts as failed."""
    junit.unlink(missing_ok=True)
    command = [sys.executable, "-m", "pytest", *args, "-q", "-p", "no:cacheprovider", f"--junitxml={junit}"]
    start = time.perf_counter()
    subprocess.run(command, cwd=ROOT, capture_output=True, text=True)
    seconds = time.perf_counter() - start
    if not junit.exists():
        return seconds, 0, 1
    suite = ET.parse(junit).getroot()
    if suite.tag == "testsuites":
        suite = suite[0]
    failed = int(suite.get("failures", 0)) + int(suite.get("errors", 0))
    return seconds, int(suite.get("tests", 0)), failed


def lines_of_code(path: Path) -> int:
    if not shutil.which("cloc"):
        sys.exit("cloc is not installed: https://github.com/AlDanial/cloc#install-via-package-manager")
    output = subprocess.run(
        ["cloc", "--json", "--quiet", str(path / "pages"), str(path / "tests")],
        capture_output=True, text=True, check=True,
    ).stdout
    return json.loads(output)["Python"]["code"]


def count_matches(path: Path, pattern: str) -> int:
    return sum(len(re.findall(pattern, file.read_text())) for file in path.rglob("*.py"))


def code_metrics() -> dict[str, dict[str, int]]:
    metrics = {}
    for name, folder in SUITES.items():
        path = ROOT / folder
        metrics[name] = {
            "lines_of_code": lines_of_code(path),
            "fixed_sleeps": count_matches(path, r"time\.sleep\(|wait_for_timeout\("),
            "explicit_waits": count_matches(path, r"\.until\(|\.wait_for\("),
        }
    return metrics


def write_summary(rows: list[dict], metrics: dict, runs: int) -> str:
    def stats(variant: str) -> tuple[float, int, int]:
        mine = [r for r in rows if r["variant"] == variant]
        median = statistics.median(float(r["seconds"]) for r in mine)
        failing_runs = sum(1 for r in mine if int(r["failed_tests"]) > 0)
        tests = max(int(r["tests"]) for r in mine)
        return median, failing_runs, tests

    sel, sel_ns, pw = (stats(v) for v in VARIANTS)
    m_sel, m_pw = metrics["selenium"], metrics["playwright"]
    lines = [
        "| Metric | Selenium (legacy) | Playwright (migrated) |",
        "| --- | --- | --- |",
        f"| Tests per run | {sel[2]} | {pw[2]} |",
        f"| Suite time, median of {runs} runs | {sel[0]:.1f} s | {pw[0]:.1f} s |",
        f"| Suite time with sleeps disabled, median | {sel_ns[0]:.1f} s | n/a (no sleeps) |",
        f"| Runs with at least one failure | {sel[1]} / {runs} | {pw[1]} / {runs} |",
        f"| Runs with a failure, sleeps disabled | {sel_ns[1]} / {runs} | n/a |",
        f"| Lines of code (pages + tests) | {m_sel['lines_of_code']} | {m_pw['lines_of_code']} |",
        f"| Fixed sleeps in code | {m_sel['fixed_sleeps']} | {m_pw['fixed_sleeps']} |",
        f"| Explicit wait calls in code | {m_sel['explicit_waits']} | {m_pw['explicit_waits']} |",
    ]
    return "\n".join(lines) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--runs", type=int, default=10)
    runs = parser.parse_args().runs

    RESULTS.mkdir(exist_ok=True)
    junit = RESULTS / ".last-run.xml"
    rows = []
    for run in range(1, runs + 1):
        for variant, args in VARIANTS.items():
            seconds, tests, failed = run_once(args, junit)
            rows.append({"run": run, "variant": variant, "seconds": f"{seconds:.2f}",
                         "tests": tests, "failed_tests": failed})
            print(f"run {run:>2}/{runs}  {variant:<19} {seconds:6.1f} s  {tests} tests  {failed} failed", flush=True)
    junit.unlink(missing_ok=True)

    with open(RESULTS / "benchmark.csv", "w", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)

    metrics = code_metrics()
    with open(RESULTS / "code_metrics.csv", "w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["suite", *metrics["selenium"]])
        for suite, values in metrics.items():
            writer.writerow([suite, *values.values()])

    summary = write_summary(rows, metrics, runs)
    (RESULTS / "summary.md").write_text(summary)
    print("\n" + summary)


if __name__ == "__main__":
    main()
