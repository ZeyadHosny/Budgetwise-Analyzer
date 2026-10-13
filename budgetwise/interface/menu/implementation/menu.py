# The interactive text menu.   Task P3.5 - Zeyad
# Project-1.pdf section 4.1: "build a simple interactive text menu (not a
# one-shot script) ... a while loop reading from input()".
# Project-1.pdf section 2: text-based menu, no GUI.
# This module is the only place print() and input() appear.
# Standard library only - Project-1.pdf section 2.

import sys
from datetime import datetime
from pathlib import Path
from budgetwise.analysis.summaries import (
    net_balance,
    top_categories,
    total_expenses,
    total_income,
)
from budgetwise.interface.export import export_cleaned, export_summary
from budgetwise.pipeline import run

# The heading printed above the options on every pass of the loop.
BANNER = "=== BudgetWise Finance Analyzer ==="
# The five options section 4.1 requires, in the order it lists them.
OPTIONS = (
    "1. Load full dataset",
    "2. Load transactions by date range",
    "3. Load transactions by category",
    "4. View error log",
    "5. Exit",
)
# The choices prompt_choice will accept. Anything else reprompts.
VALID_CHOICES = ("1", "2", "3", "4", "5")
# The dataset path, relative to the repository root.
DATASET = "data/raw/budgetwise_finance_dataset.csv"
# Where task P2.8 writes the error log that option 4 displays.
ERROR_LOG = Path("output/logs/errors.log")
# The date format section 4.5 standardizes every date to.
DATE_FORMAT = "%Y-%m-%d"
# The 14 canonical categories agreed at G1. Task P2.2 produces these from
# the 47 raw spellings in the dataset.
CATEGORIES = (
    "Bonus", "Education", "Entertainment", "Food", "Freelance",
    "Healthcare", "Investment", "Other", "Rent", "Salary", "Savings",
    "Transportation", "Uncategorized", "Utilities",
)
# How many category names to print per line when listing the options.
CATEGORIES_PER_LINE = 4
# Earliest transaction date in the dataset, measured over all 15,414 dated
# rows. Shown as a hint so the user does not pick a range that matches
# nothing. It is NOT a validation rule: a wider range is legitimate.
DATASET_FIRST_DATE = "2019-01-01"
# Latest transaction date in the dataset, measured the same way.
DATASET_LAST_DATE = "2024-12-31"


# Function to read a menu choice
def prompt_choice():
    """
    Description:
    - Read one menu choice from the user.
    - Reprompts instead of raising, which is the robustness section 7 asks
      for: a typo must not end the program.

    Input arguments:
       None (reads from input())

    Return:
        str: One of '1' through '5'.
    """
    while True:
        raw = input("Choose an option: ").strip()
        if raw in VALID_CHOICES:
            return raw
        print("  Please choose 1 to 5.")


# Function to read one date
def read_date(label):
    """
    Description:
    - Read one YYYY-MM-DD date, reprompting until it parses.
    - Helper for prompt_date_range, which calls it twice: once for the
      start date and once for the end date.

    Input arguments:
       label (str): The prompt shown to the user, e.g. 'Start date'.

    Return:
        str: The date as 'YYYY-MM-DD'.
    """
    while True:
        raw = input(f"{label} (YYYY-MM-DD): ").strip()
        try:
            return datetime.strptime(raw, DATE_FORMAT).strftime(DATE_FORMAT)
        except ValueError:
            print("  Not a valid date. Use YYYY-MM-DD, "
                  "for example 2023-07-14.")


# Function to read a start and end date
def prompt_date_range():
    """
    Description:
    - Read a start and end date for menu option 2.
    - Section 4.1: "asks for a start/end date and only loads/filters
      transactions within that range".
    - States the format AND the span the data actually covers, so the user
      is not left to discover an empty result by trial and error.
    - A range outside the span is accepted, not refused. Asking for
      2019-2030 is a legitimate query whose answer happens to be every
      row, and section 4.1 does not authorize refusing it. The user is told
      when a range falls outside the data so an empty result is explained
      rather than mysterious.
    - Reprompts only when the end date is before the start date, which is
      the one case that can never be what the user meant.

    Input arguments:
       None (reads from input())

    Return:
        tuple: (start, end) as 'YYYY-MM-DD', with end on or after start.
    """
    print(f"  Transactions run from {DATASET_FIRST_DATE} to "
          f"{DATASET_LAST_DATE}.")
    print("  Rows with no date are excluded from a date range "
          "- section 4.5.")
    while True:
        start = read_date("Start date")
        end = read_date("End date  ")
        if end < start:
            print(f"  The end date ({end}) is before the start date "
                  f"({start}). Enter the earlier date first.")
            continue
        if end < DATASET_FIRST_DATE or start > DATASET_LAST_DATE:
            print(f"  Note: {start} to {end} falls outside "
                  f"{DATASET_FIRST_DATE}-{DATASET_LAST_DATE}, "
                  f"so this will match no transactions.")
        return start, end


# Function to print the categories the user may choose from
def show_categories():
    """
    Description:
    - Print the 14 canonical categories, a few per line.
    - Shown BEFORE the first prompt, not only after a mistake, so the user
      never has to guess and fail in order to learn what is valid.

    Input arguments:
       None

    Return:
        None (prints to the screen)
    """
    for start in range(0, len(CATEGORIES), CATEGORIES_PER_LINE):
        print("    " + ", ".join(
            CATEGORIES[start:start + CATEGORIES_PER_LINE]))


# Function to read a category name
def prompt_category():
    """
    Description:
    - Read a category name for menu option 3.
    - Lists the valid categories up front, so the expected input is stated
      before it is asked for rather than after it is got wrong.
    - Matches case-insensitively, so 'food' and 'FOOD' both work.
    - Reprompts on an unrecognized name rather than failing - section 4.1
      requires the program not to crash on bad input.

    Input arguments:
       None (reads from input())

    Return:
        str: A canonical category name, e.g. 'Food'.
    """
    lookup = {name.lower(): name for name in CATEGORIES}
    print("  Categories:")
    show_categories()
    while True:
        raw = input("Category (one of the above): ").strip().lower()
        if raw in lookup:
            return lookup[raw]
        print(f"  '{raw}' is not one of the 14 categories. Choose from:")
        show_categories()


# Function to show the error log for menu option 4
def view_error_log(path=ERROR_LOG):
    """
    Description:
    - Show the error log on screen for menu option 4.
    - PLACEHOLDER, not this task. Task P2.8 (Patrick) owns the error log:
      its format, its reason codes, and what belongs in it. This prints the
      file if it is there and says so if it is not, which is all the menu
      needs in order to be tested. Replace the body once P2.8 is merged.

    Input arguments:
       path (Path): The log file to show. Defaults to
           output/logs/errors.log, which task P2.8 writes.

    Return:
        None (prints to the screen)
    """
    if path.exists():
        print(path.read_text(encoding="utf-8").rstrip())
    else:
        print(f"  No error log at {path} yet - task P2.8 writes it.")


# Function to format the block printed after a load
def format_summary(result):
    """
    Description:
    - Turn a pipeline result into the block printed after a load.
    - Points the user at the error log whenever rows were skipped or
      removed as duplicates, so the counts are never unexplained.

    Input arguments:
       result (dict): Task P2.10's result, holding 'transactions' and a
           'counts' mapping with input, valid, duplicates and skipped.

    Return:
        str: The formatted block, ready to print.
    """
    counts = result.get("counts", {})
    lines = [
        "",
        f"  Loaded {len(result.get('transactions', [])):,} transactions",
        f"    input      {counts.get('input', 0):>8,}",
        f"    valid      {counts.get('valid', 0):>8,}",
        f"    duplicates {counts.get('duplicates', 0):>8,}",
        f"    skipped    {counts.get('skipped', 0):>8,}",
    ]
    if counts.get("skipped") or counts.get("duplicates"):
        lines.append(f"    see {ERROR_LOG} for the reasons")
    return "\n".join(lines)


def export_run(result, dataset, selection=None):
    """Export the transactions selected by this menu load."""
    records = result.get("records")
    if records is None or (result.get("error") and not records):
        return
    transactions = result.get("transactions")
    if transactions is None or (result.get("error") and not transactions):
        return

    counts = result.get("counts", {})
    cleaning_count_keys = (
        "input", "valid", "duplicates", "skipped", "corrected", "flagged",
        "categories_normalized", "repeated_ids", "by_reason",
    )
    summary = {
        "scope": "transactions selected by menu query",
        "selection": selection or {"type": "all"},
        "selected_transactions": len(transactions),
        "counts": {
            key: counts[key] for key in cleaning_count_keys if key in counts
        },
        "timings": result.get("timings", {}),
        "totals": {
            "income": total_income(transactions),
            "expenses": total_expenses(transactions),
            "net": net_balance(transactions),
        },
        "top_categories": top_categories(transactions, n=5),
    }
    generated_at = datetime.now()
    cleaned_path = export_cleaned(transactions, dataset, when=generated_at)
    summary_path = export_summary(summary, dataset, when=generated_at)
    print(f"  Cleaned CSV: {cleaned_path}")
    print(f"  JSON summary: {summary_path}")


# Function to raise when the pipeline is not available
def missing_pipeline(*args, **kwargs):
    """
    Description:
    - Stand in for task P2.10's run() until it is merged.
    - Raising NotImplementedError rather than crashing lets run_menu catch
      it and print a clear message, so the menu stays usable.

    Input arguments:
       Any. All arguments are ignored.

    Return:
        None (always raises NotImplementedError)
    """
    raise NotImplementedError("pipeline.run() - task P2.10, Sarah")


# Function holding the while loop section 4.1 requires
def run_menu(pipeline_run=run, dataset=DATASET):
    """
    Description:
    - Run the menu loop section 4.1 requires. Prints the options, reads a
      choice, acts on it, and repeats until the user chooses 5.
    - pipeline_run is injected rather than imported so this module can be
      tested on its own and does not depend on a file that is not merged
      yet. The menu knows nothing about how loading works.
    - Catches EOFError and KeyboardInterrupt so a closed pipe or Ctrl+C
      exits cleanly instead of printing a traceback.

    Input arguments:
       pipeline_run (callable): Task P2.10's run(). Defaults to a stand-in
           that reports the task is not available yet.
       dataset (str): The dataset path passed through to pipeline_run.

    Return:
        None (returns when the user chooses 5)
    """
    if pipeline_run is None:
        pipeline_run = missing_pipeline

    while True:
        print()
        print(BANNER)
        for line in OPTIONS:
            print(line)

        try:
            choice = prompt_choice()
        except (EOFError, KeyboardInterrupt):
            print("\n  Exiting.")
            return

        try:
            if choice == "1":
                result = pipeline_run(dataset)
                print(format_summary(result))
                export_run(result, dataset, {"type": "all"})

            elif choice == "2":
                start, end = prompt_date_range()
                result = pipeline_run(dataset, start=start, end=end)
                print(format_summary(result))
                export_run(result, dataset, {
                    "type": "date_range", "start": start, "end": end,
                })
                print(f"  Range {start} to {end}. Rows with no date are "
                      f"excluded from a date range - section 4.5.")

            elif choice == "3":
                category = prompt_category()
                result = pipeline_run(dataset, category=category)
                print(format_summary(result))
                export_run(result, dataset, {
                    "type": "category", "category": category,
                })
                print(f"  Category {category}. The filter runs after "
                      f"normalization, so 'Fod' and 'Foodd' match too.")

            elif choice == "4":
                print()
                view_error_log()

            elif choice == "5":
                print("  Goodbye.")
                return

        except (EOFError, KeyboardInterrupt):
            print("\n  Exiting.")
            return
        except FileNotFoundError as exc:
            print(f"  Could not open the dataset: {exc}")
        except NotImplementedError as exc:
            print(f"  Not available yet: {exc}")


# Function standing in for the pipeline during a demo
def demo_run(dataset_path, start=None, end=None, category=None):
    """
    Description:
    - Stand in for task P2.10 using six real rows from the dataset, so the
      menu can be exercised end to end before P2.10 is merged.
    - Applies the same two filters the real pipeline applies, including
      dropping the undated row from a date range, as section 4.5 requires.
    - Remove this function once P2.10 merges.

    Input arguments:
       dataset_path (str): Ignored. Present so this signature matches
           task P2.10's run(), which does read it.
       start (str): Range start as 'YYYY-MM-DD', or None.
       end (str): Range end as 'YYYY-MM-DD', or None.
       category (str): A canonical category name, or None.

    Return:
        dict: The same shape task P2.10's run() returns.
    """
    rows = [
        ("T4999", "2023-04-25", "Education", 3888.0),
        ("T1044", "2021-05-06", "Food", 1810.0),
        ("T3133", "2024-07-17", "Rent", 9567.0),
        ("T12350", None, "Food", 6299.0),
        ("T9824", "2024-12-12", "Salary", 62061.0),
        ("T2699", "2023-02-25", "Transportation", 2553.0),
    ]
    kept = rows
    if start and end:
        kept = [row for row in kept if row[1] and start <= row[1] <= end]
    if category:
        kept = [row for row in kept if row[2] == category]
    return {
        "transactions": kept,
        "accounts": {},
        "counts": {"input": len(rows), "valid": len(kept),
                   "duplicates": 0, "skipped": 0},
        "timings": {},
    }


if __name__ == "__main__":
    if "--demo" in sys.argv:
        print("  (demo mode - six sample rows, task P2.10 not yet available)")
        run_menu(pipeline_run=demo_run)
    else:
        run_menu()
