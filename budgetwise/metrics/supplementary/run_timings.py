"""Time the pipeline on the primary dataset for the report's execution time table.

Runs the pipeline seven times, each in a new Python process, and prints
each run's stage times and the median and min-max per stage.

Run from the repository root:

    python budgetwise/metrics/supplementary/run_timings.py
"""

import json
import os
import platform
import statistics
import subprocess
import sys
import tempfile
import time
from pathlib import Path

RUNS = 7
REPO = Path(__file__).resolve().parents[3]
DATASET = "data/raw/budgetwise_finance_dataset.csv"

COLUMNS = [
    ("loading", "Loading"),
    ("cleaning", "Cleaning and issue logging"),
    ("objects", "Object building and selection"),
    ("summary", "Cleaning count summary"),
    ("total", "Pipeline total"),
    ("analysis", "Financial analysis"),
]


def one_run():
    """Time one run. Imports happen before any timer starts."""
    sys.path.insert(0, str(REPO))
    os.chdir(REPO)
    from budgetwise.errorlog import ErrorLog
    from budgetwise.pipeline.implementation import runner
    from budgetwise.analysis.aggregation import totals_by_category
    from budgetwise.analysis.summaries.implementation.totals import (
        monthly_expenses, net_balance, total_expenses, total_income)

    times = {}

    def timed(name, function):
        def wrapper(*args, **kwargs):
            start = time.perf_counter()
            result = function(*args, **kwargs)
            times[name] = times.get(name, 0.0) + time.perf_counter() - start
            return result
        return wrapper

    load_rows = runner.load_rows
    runner.load_rows = timed("loading", lambda path: list(load_rows(path)))
    runner._clean_rows = timed("clean_rows", runner._clean_rows)
    runner._build_objects = timed("objects", runner._build_objects)
    runner._summarise = timed("summary", runner._summarise)

    # A fresh log file for every run, outside the repository.
    log_path = os.path.join(tempfile.mkdtemp(), "errors.log")
    start = time.perf_counter()
    log = ErrorLog(log_path)
    result = runner.run(DATASET, error_log=log)
    log.close()
    times["total"] = time.perf_counter() - start

    transactions = result["transactions"]
    start = time.perf_counter()
    totals_by_category(transactions, kind="expense")
    monthly_expenses(transactions)
    total_income(transactions)
    total_expenses(transactions)
    net_balance(transactions)
    times["analysis"] = time.perf_counter() - start

    # _clean_rows includes loading, so loading is taken out.
    times["cleaning"] = times.pop("clean_rows") - times["loading"]

    counts = result["counts"]
    output = {name: round(seconds * 1000, 1)
              for name, seconds in times.items()}
    output.update(input=counts["input"], valid=counts["valid"],
                  built=counts.get("objects_built"))
    print(json.dumps(output))


def main():
    runs = []
    for _ in range(RUNS):
        process = subprocess.run([sys.executable, __file__, "--one"],
                                 capture_output=True, text=True)
        if process.returncode:
            print(process.stderr)
            return
        runs.append(json.loads(process.stdout.strip().splitlines()[-1]))

    print("Python", platform.python_version(), "|", platform.platform(),
          "|", platform.processor())
    print("Records:", runs[0]["input"], "input,", runs[0]["valid"], "valid,",
          runs[0]["built"], "objects")

    print("\nRun | " + " | ".join(label for _, label in COLUMNS))
    for number, run in enumerate(runs, 1):
        print(number, "|", " | ".join(
            f"{run[key]:,.1f}" for key, _ in COLUMNS))

    print("\nWorkload | Median ms | Min-max ms")
    for key, label in COLUMNS:
        values = [run[key] for run in runs]
        print(f"{label} | {statistics.median(values):,.1f} | "
              f"{min(values):,.1f}-{max(values):,.1f}")


if __name__ == "__main__":
    if "--one" in sys.argv:
        one_run()
    else:
        main()
