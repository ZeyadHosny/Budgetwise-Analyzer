# Interactive text menu — original menu task: Zeyad.
# Standard library only.
# Budget prompts and display are in budget_menu.py.

import sys
from datetime import datetime
from pathlib import Path


BANNER = "=== BudgetWise Finance Analyzer ==="

OPTIONS = (
    "1. Load full dataset",
    "2. Load transactions by date range",
    "3. Load transactions by category",
    "4. View error log",
    "5. Exit",
    "6. Compare monthly budgets",
)

VALID_CHOICES = ("1", "2", "3", "4", "5", "6")

DATASET = "data/raw/budgetwise_finance_dataset.csv"
ERROR_LOG = Path("output/logs/errors.log")
DATE_FORMAT = "%Y-%m-%d"

# Names match the current category cleaner.
CATEGORIES = (
    "Bonus", "Education", "Entertainment", "Food", "Freelance",
    "Healthcare", "Investment", "Other", "Rent", "Salary",
    "Savings", "Transportation", "Uncategorized", "Utilities",
)

CATEGORIES_PER_LINE = 4

# Dataset date coverage is a hint, not a validation restriction.
DATASET_FIRST_DATE = "2021-01-01"
DATASET_LAST_DATE = "2024-12-31"


def prompt_choice():
    """Read a menu choice, reprompting on invalid input."""

    while True:
        raw = input("Choose an option: ").strip()

        if raw in VALID_CHOICES:
            return raw

        print("  Please choose 1 to 6.")


def read_date(label):
    """Read a date and return it as YYYY-MM-DD."""

    while True:
        raw = input(f"{label} (YYYY-MM-DD): ").strip()

        try:
            return datetime.strptime(
                raw, DATE_FORMAT
            ).strftime(DATE_FORMAT)
        except ValueError:
            print(
                "  Not a valid date. Use YYYY-MM-DD, "
                "for example 2023-07-14."
            )


def prompt_date_range():
    """Read a date range with the end on or after the start."""

    print(
        f"  Transactions run from {DATASET_FIRST_DATE} "
        f"to {DATASET_LAST_DATE}."
    )
    print(
        "  Rows with no date are excluded from a date range "
        "- section 4.5."
    )

    while True:
        start = read_date("Start date")
        end = read_date("End date  ")

        if end < start:
            print(
                f"  The end date ({end}) is before the start date "
                f"({start}). Enter the earlier date first."
            )
            continue

        if end < DATASET_FIRST_DATE or start > DATASET_LAST_DATE:
            print(
                f"  Note: {start} to {end} falls outside "
                f"{DATASET_FIRST_DATE}-{DATASET_LAST_DATE}, "
                "so this will match no transactions."
            )

        return start, end


def show_categories():
    """Display the canonical categories."""

    for start in range(0, len(CATEGORIES), CATEGORIES_PER_LINE):
        print(
            "    "
            + ", ".join(
                CATEGORIES[start:start + CATEGORIES_PER_LINE]
            )
        )


def prompt_category():
    """Read a canonical category, ignoring capitalization."""

    lookup = {name.lower(): name for name in CATEGORIES}

    print("  Categories:")
    show_categories()

    while True:
        raw = input(
            "Category (one of the above): "
        ).strip().lower()

        if raw in lookup:
            return lookup[raw]

        print(
            f"  '{raw}' is not one of the 14 categories. "
            "Choose from:"
        )
        show_categories()


def view_error_log(path=ERROR_LOG):
    """Display the existing error log if available."""

    path = Path(path)

    if path.exists():
        print(path.read_text(encoding="utf-8").rstrip())
    else:
        print(f"  No error log at {path} yet.")


def format_summary(result):
    """Display cleaning counts separately from selection counts."""

    counts = result.get("counts", {})

    lines = [
        "",
        f"  Loaded {len(result.get('transactions', [])):,} transactions",
        f"    input      {counts.get('input', 0):>8,}",
        f"    valid      {counts.get('valid', 0):>8,}",
        f"    duplicates {counts.get('duplicates', 0):>8,}",
        f"    skipped    {counts.get('skipped', 0):>8,}",
    ]

    if "selected_count" in result:
        lines.append(
            f"    selected   {result['selected_count']:>8,}"
        )
        lines.append(
            "    Cleaning counts cover the full dataset; "
            "selected is the count after filtering."
        )

    if counts.get("skipped") or counts.get("duplicates"):
        lines.append(f"    see {ERROR_LOG} for the reasons")

    return "\n".join(lines)


def missing_pipeline(*args, **kwargs):
    """Retain the original placeholder for compatibility."""

    raise NotImplementedError(
        "pipeline.run() - task P2.10, Sarah"
    )


def run_menu(pipeline_run=None, dataset=DATASET):
    """Run the menu with cleaning and monthly budget comparison.

    A pipeline callable may still be injected for tests or demos.
    Normal execution uses the adapter for the current cleaner.
    """

    from budgetwise.interface.menu.implementation.budget_menu import (
        run_budget_menu,
    )

    if pipeline_run is None:
        from budgetwise.interface.menu.implementation.pipeline_adapter import (
            run_for_menu,
        )
        pipeline_run = run_for_menu

    all_records = None

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
                all_records = result.get("all_records")

            elif choice == "2":
                start, end = prompt_date_range()

                result = pipeline_run(
                    dataset,
                    start=start,
                    end=end,
                )

                print(format_summary(result))
                print(
                    f"  Range {start} to {end}. "
                    "Rows with no date are excluded from "
                    "a date range - section 4.5."
                )

                all_records = result.get("all_records")

            elif choice == "3":
                category = prompt_category()

                result = pipeline_run(
                    dataset,
                    category=category,
                )

                print(format_summary(result))
                print(
                    f"  Category {category}. "
                    "The filter runs after normalization."
                )

                all_records = result.get("all_records")

            elif choice == "4":
                print()
                view_error_log()

            elif choice == "5":
                print("  Goodbye.")
                return

            elif choice == "6":
                if all_records is None:
                    print(
                        "  Load the dataset using option 1, 2, or 3 "
                        "before comparing budgets."
                    )
                    print(
                        "  Budget comparison requires complete "
                        "cleaned records from the current pipeline."
                    )
                    continue

                run_budget_menu(all_records)

        except (EOFError, KeyboardInterrupt):
            print("\n  Exiting.")
            return

        except FileNotFoundError as exc:
            print(f"  Could not open a required file: {exc}")

        except OSError as exc:
            print(
                f"  Could not read or write a required file: {exc}"
            )

        except ValueError as exc:
            print(f"  Could not complete the selection: {exc}")

        except NotImplementedError as exc:
            print(f"  Not available yet: {exc}")


def demo_run(dataset_path, start=None, end=None, category=None):
    """Retain the original six-row loading and filtering demo.

    Demo tuples do not provide the full fields needed for budgets.
    Use the real cleaning pipeline for budget comparison.
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
        kept = [
            row
            for row in kept
            if row[1] and start <= row[1] <= end
        ]

    if category:
        kept = [
            row
            for row in kept
            if row[2] == category
        ]

    return {
        "transactions": kept,
        "accounts": {},
        "counts": {
            "input": len(rows),
            "valid": len(kept),
            "duplicates": 0,
            "skipped": 0,
        },
        "timings": {},
    }


if __name__ == "__main__":
    if "--demo" in sys.argv:
        print("  (demo mode - six sample rows; loading and filtering only)")
        run_menu(pipeline_run=demo_run)
    else:
        run_menu()
