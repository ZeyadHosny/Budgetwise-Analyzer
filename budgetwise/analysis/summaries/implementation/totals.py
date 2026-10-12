"""P3.3: Summary totals calculated from the aggregation public interface."""

from budgetwise.analysis.aggregation import (
    totals_by_category,
    totals_by_month,
)


def total_income(transactions):
    """Return total income, including transactions without a date."""
    category_totals = totals_by_category(transactions, kind="income")
    return sum(category_totals.values(), 0.0)


def total_expenses(transactions):
    """Return total expenses, including transactions without a date."""
    category_totals = totals_by_category(transactions, kind="expense")
    return sum(category_totals.values(), 0.0)


def net_balance(transactions):
    """Return total income minus total expenses."""
    # Materialize once so both calculations receive the same records,
    # even when the input is a generator.
    records = list(transactions)
    return total_income(records) - total_expenses(records)


def monthly_expenses(transactions):
    """Return expense totals by month, excluding undated transactions.

    Month keys follow the aggregation contract: ("YYYY", "MM").
    """
    return totals_by_month(transactions, kind="expense")
