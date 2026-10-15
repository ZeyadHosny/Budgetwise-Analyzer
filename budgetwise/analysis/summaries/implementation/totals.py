"""P3.3: Summary totals calculated from the aggregation public interface."""

from budgetwise.analysis.aggregation import (
    totals_by_category,
    totals_by_month,
)
from budgetwise.models import Account


def total_income(accounts: list[Account]):
    """Return total income, including transactions without a date."""
    category_totals = totals_by_category(accounts, kind="income")
    return sum(category_totals.values(), 0.0)


def total_expenses(accounts: list[Account]):
    """Return total expenses, including transactions without a date."""
    category_totals = totals_by_category(accounts, kind="expense")
    return sum(category_totals.values(), 0.0)


def net_balance(accounts: list[Account]):
    """Return total income minus total expenses."""
    # Materialize once so both calculations receive the same records,
    # even when the input is a generator.
    records = list(accounts)
    return total_income(records) - total_expenses(records)


def monthly_expenses(accounts: list[Account]):
    """Return expense totals by month, excluding undated transactions.

    Month keys follow the aggregation contract: ("YYYY", "MM").
    """
    return totals_by_month(accounts, kind="expense")
