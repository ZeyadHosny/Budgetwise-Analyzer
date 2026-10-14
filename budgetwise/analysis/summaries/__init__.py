"""
Public interface for summary analysis (task P3.3, Bahareh).

Expose total income, total expenses, net balance, monthly expenses,
top spending categories, and largest individual expenses.
"""

from .implementation.totals import (
    total_income,
    total_expenses,
    net_balance,
    monthly_expenses,
)
from .implementation.rankings import (
    top_categories,
    top_expenses,
)
from .implementation.report import build_summary

__all__ = [
    "total_income",
    "total_expenses",
    "net_balance",
    "monthly_expenses",
    "top_categories",
    "top_expenses",
    "build_summary",
]
