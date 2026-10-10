"""Compare a user's recorded monthly expenses with a budget."""

import json
from datetime import date
from math import fsum
from pathlib import Path

from budgetwise.models.implementation.budget import Budget


def load_budget_config(path=None):
    """Read budget configuration without changing it."""

    if path is None:
        project_root = Path(__file__).resolve().parents[4]
        path = project_root / "config" / "monthly_budgets.json"

    with Path(path).open("r", encoding="utf-8") as file:
        return json.load(file)


def resolve_limit(config, user_id, category):
    """Use a user override if present; otherwise use the default."""

    overrides = config.get("user_overrides", {}).get(user_id, {})

    if category in overrides:
        limit = overrides[category]
    elif category in config["limits"]:
        limit = config["limits"][category]
    else:
        return None

    # Validate configured limits, including explicit zero limits.
    return Budget(category, limit).get_monthly_limit()


def compare_user_month(
    records,
    config,
    user_id,
    year,
    month,
    category,
):
    """Compare matching expenses in cleaned record dictionaries.

    Records must come from the cleaning pipeline.
    The function does not change records or cleaning counts.
    """

    if not isinstance(user_id, str) or not user_id.strip():
        raise ValueError("User ID must be a non-empty string.")

    if not isinstance(category, str) or not category.strip():
        raise ValueError("Category must be a non-empty string.")

    if (
        isinstance(year, bool)
        or isinstance(month, bool)
        or not isinstance(year, int)
        or not isinstance(month, int)
    ):
        raise ValueError("Year and month must be integers.")

    # Reject impossible year/month selections.
    date(year, month, 1)

    category = category.strip()
    monthly_records = []

    for record in records:
        if record["user_id"] != user_id:
            continue

        if record["date"] is None:
            continue

        transaction_date = date.fromisoformat(record["date"])

        if (
            transaction_date.year == year
            and transaction_date.month == month
        ):
            monthly_records.append(record)

    expenses = [
        record
        for record in monthly_records
        if (
            record["transaction_type"] == "Expense"
            and record["category"] == category
        )
    ]

    actual = fsum(record["amount"] for record in expenses)
    limit = resolve_limit(config, user_id, category)

    result = {
        "user_id": user_id,
        "year": year,
        "month": month,
        "category": category,
        "recorded_actual": actual,
        "limit": limit,
        "has_month_records": bool(monthly_records),
        "has_category_expense_record": bool(expenses),
        "expense_record_count": len(expenses),
        "source_lines": [
            record["source_line"] for record in expenses
        ],
        "status": None,
        "difference": None,
    }

    if not monthly_records:
        result["status"] = "no_data"
        return result

    if limit is None:
        result["status"] = "unbudgeted"
        return result

    budget = Budget(category, limit)
    status, difference = budget.status(actual)

    result["status"] = status
    result["difference"] = difference

    return result
