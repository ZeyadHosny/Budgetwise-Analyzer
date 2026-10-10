"""Compare monthly recorded expenses and budgets for matching users."""

from datetime import date
from math import fsum

from budgetwise.models.implementation.budget import Budget

from .monthly_comparison import compare_user_month


def compare_group_month(
    records,
    config,
    year,
    month,
    category,
    requested_users=None,
):
    """Compare a selected group or all users with monthly records.

    Users without dated records in the selected month are excluded
    and reported separately.
    """

    if (
        isinstance(year, bool)
        or isinstance(month, bool)
        or not isinstance(year, int)
        or not isinstance(month, int)
    ):
        raise ValueError("Year and month must be integers.")

    date(year, month, 1)

    if not isinstance(category, str) or not category.strip():
        raise ValueError("Category must be a non-empty string.")

    category = category.strip()
    records = list(records)
    monthly_records = []

    for record in records:
        if record["date"] is None:
            continue

        transaction_date = date.fromisoformat(record["date"])

        if (
            transaction_date.year == year
            and transaction_date.month == month
        ):
            monthly_records.append(record)

    observed_users = {
        record["user_id"] for record in monthly_records
    }

    if requested_users is None:
        # Automatic group: users with any dated transaction
        # in the selected month, including Income transactions.
        selected_users = observed_users
    else:
        if isinstance(requested_users, str):
            raise ValueError("Provide users as a collection of IDs.")

        selected_users = set(requested_users)

        for user_id in selected_users:
            if not isinstance(user_id, str) or not user_id.strip():
                raise ValueError("Each user ID must be a non-empty string.")

    included_users = selected_users & observed_users
    excluded_users = selected_users - observed_users

    details = {}

    for user_id in sorted(included_users):
        details[user_id] = compare_user_month(
            monthly_records,
            config,
            user_id,
            year,
            month,
            category,
        )

    actual = fsum(
        result["recorded_actual"]
        for result in details.values()
    )

    missing_budget_users = [
        user_id
        for user_id, result in details.items()
        if result["limit"] is None
    ]

    limit = None
    difference = None

    if not included_users:
        status = "no_data"

    elif missing_budget_users:
        # Do not compare the whole group's spending with
        # a budget that covers only some group members.
        status = (
            "unbudgeted"
            if len(missing_budget_users) == len(included_users)
            else "incomplete_budget"
        )

    else:
        limit = fsum(
            result["limit"]
            for result in details.values()
        )

        status, difference = Budget(
            category, limit
        ).status(actual)

    return {
        "year": year,
        "month": month,
        "category": category,
        "included_users": sorted(included_users),
        "excluded_no_month_records": sorted(excluded_users),
        "missing_budget_users": missing_budget_users,
        "users_without_category_expenses": [
            user_id
            for user_id, result in details.items()
            if not result["has_category_expense_record"]
        ],
        "users": details,
        "group": {
            "user_count": len(included_users),
            "recorded_actual": actual,
            "limit": limit,
            "status": status,
            "difference": difference,
        },
    }
