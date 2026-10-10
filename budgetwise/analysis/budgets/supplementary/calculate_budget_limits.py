"""Calculate proposed budget limits from cleaned historical expenses.

Run from the project root:
python -m budgetwise.analysis.budgets.supplementary.calculate_budget_limits
"""

from collections import defaultdict
from datetime import date
from math import ceil
from pathlib import Path
from statistics import median

from budgetwise.pipeline import run_cleaning


CATEGORIES = (
    "Food",
    "Rent",
    "Transportation",
    "Utilities",
    "Entertainment",
    "Education",
    "Healthcare",
)

BASELINE_START = date(2021, 1, 1)
BASELINE_END = date(2023, 12, 31)
ROUND_UP_TO = 100


def calculate_limits(records):
    """Return evidence and proposed limits for each category."""

    monthly_totals = defaultdict(float)
    row_counts = defaultdict(int)
    users = defaultdict(set)

    for record in records:
        # Direction comes only from transaction_type.
        if record["transaction_type"] != "Expense":
            continue

        category = record["category"]

        if category not in CATEGORIES:
            continue

        # Undated records remain in cleaning results,
        # but cannot participate in monthly calculations.
        if record["date"] is None:
            continue

        transaction_date = date.fromisoformat(record["date"])

        if not BASELINE_START <= transaction_date <= BASELINE_END:
            continue

        user_id = record["user_id"]

        key = (
            user_id,
            transaction_date.year,
            transaction_date.month,
            category,
        )

        # Preserve recorded zero amounts.
        # Do not create groups for absent months.
        monthly_totals[key] += record["amount"]
        row_counts[category] += 1
        users[category].add(user_id)

    category_totals = defaultdict(list)

    for key, total in monthly_totals.items():
        category = key[3]
        category_totals[category].append(total)

    results = {}

    for category in CATEGORIES:
        observed_totals = category_totals[category]

        if observed_totals:
            median_total = median(observed_totals)
            proposed_limit = (
                ceil(median_total / ROUND_UP_TO) * ROUND_UP_TO
            )
        else:
            median_total = None
            proposed_limit = None

        results[category] = {
            "expense_rows": row_counts[category],
            "observed_user_months": len(observed_totals),
            "users": len(users[category]),
            "median": median_total,
            "proposed_limit": proposed_limit,
        }

    return results


def main():
    project_root = Path(__file__).resolve().parents[4]

    dataset_path = (
        project_root
        / "data"
        / "raw"
        / "budgetwise_finance_dataset.csv"
    )

    # Keep this evidence run's log separate from normal runs.
    log_path = (
        project_root
        / "output"
        / "logs"
        / "budget_baseline_errors.log"
    )
    log_path.parent.mkdir(parents=True, exist_ok=True)

    cleaning_result = run_cleaning(
        dataset_path,
        log_path=str(log_path),
    )

    results = calculate_limits(cleaning_result.records)

    print("PROPOSED BUDGET BENCHMARKS — FOR TEAM REVIEW")
    print("Baseline: 2021-01-01 through 2023-12-31")
    print("Method: median observed user-month category total")
    print("Rounding: upward to the nearest 100 dataset units")
    print("Absent months are not assumed to have zero spending.")
    print()
    print("Cleaning counts:", cleaning_result.counts)
    print()

    print(
        "| Category | Expense rows | Observed user-months | "
        "Users | Median | Proposed limit |"
    )
    print("|---|---:|---:|---:|---:|---:|")

    for category, evidence in results.items():
        median_value = evidence["median"]
        limit = evidence["proposed_limit"]

        median_text = (
            "No data"
            if median_value is None
            else f"{median_value:.2f}"
        )
        limit_text = (
            "Undefined"
            if limit is None
            else str(limit)
        )

        print(
            f"| {category} "
            f"| {evidence['expense_rows']} "
            f"| {evidence['observed_user_months']} "
            f"| {evidence['users']} "
            f"| {median_text} "
            f"| {limit_text} |"
        )


if __name__ == "__main__":
    main()
