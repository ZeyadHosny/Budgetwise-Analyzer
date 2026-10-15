"""Largest expense ranking and monthly budget comparisons."""

from typing import NamedTuple

from budgetwise.analysis.aggregation import totals_by_month_and_category
from budgetwise.analysis.summaries import top_expenses
from budgetwise.models import Budget
from budgetwise.models.implementation.account import Account

from .limits import load_limits


class BudgetResult(NamedTuple):
    category: str
    limit: float | None
    actual: float
    status: str
    difference: float | None


def largest_expenses(transactions, n=5):
    """Return up to n expenses, largest first; ties preserve input order."""
    return top_expenses(transactions, n=n)


def compare_to_budget(accounts: list[Account], year, month):
    """Compare a month's category expenses against configured limits.

    Configured categories with no spend are returned with actual 0.0 when
    that month contains any expenses. Spending categories without a limit are
    returned with status ``unbudgeted``. A month without expenses returns [].
    """
    month_key = _month_key(year, month)
    monthly_totals = totals_by_month_and_category(
        accounts,
        kind="expense"
    ).get(month_key, {})
    if not monthly_totals:
        return []

    limits = load_limits()
    results = []
    for category in sorted(set(limits) | set(monthly_totals)):
        actual = monthly_totals.get(category, 0.0)
        if category in limits:
            status, difference = Budget(category, limits[category]).status(actual)
            results.append(
                BudgetResult(category, limits[category], actual, status, difference)
            )
        else:
            results.append(BudgetResult(category, None, actual, "unbudgeted", None))
    return results


def _month_key(year, month):
    if not isinstance(year, str) or not isinstance(month, str):
        raise TypeError("year and month must be strings")
    if len(year) != 4 or not year.isdigit():
        raise ValueError("year must be four digits")
    if len(month) != 2 or not month.isdigit() or not 1 <= int(month) <= 12:
        raise ValueError("month must be a two-digit month from 01 to 12")
    return year, month