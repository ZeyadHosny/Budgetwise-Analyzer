"""Build the pipeline's structured, account-backed summary report."""

from calendar import monthrange
from datetime import date

from budgetwise.analysis.aggregation import (
    totals_by_category,
    totals_by_month,
    totals_by_month_and_category,
)
from budgetwise.analysis.summaries.implementation.rankings import (
    top_categories,
    top_expenses,
)
from budgetwise.models import Budget
from budgetwise.metrics.implementation.counters import RunMetrics


def build_summary(result, selection, n=5):
    """Build total, monthly, and category sections from account mappings."""
    accounts = result["accounts"]
    budget_comparisons = result["budget_comparisons"]
    transactions = list(iter_transactions(accounts))

    expense_totals = totals_by_category(accounts.values(), kind="expense")
    income_totals = totals_by_category(accounts.values(), kind="income")
    expense_months = totals_by_month(accounts.values(), kind="expense")
    income_months = totals_by_month(accounts.values(), kind="income")
    expense_by_month_and_category = totals_by_month_and_category(
        accounts.values(), kind="expense"
    )
    months = sorted(set(expense_months) | set(income_months))

    transactions_by_month = {month: [] for month in months}
    for transaction in transactions:
        month = _get_month(transaction)
        if month in transactions_by_month:
            transactions_by_month[month].append(transaction)

    comparisons_by_month = {
        tuple(item["month"].split("-")): item
        for item in budget_comparisons
    }
    monthly_rows = []
    for month in months:
        expenses = expense_months.get(month, 0.0)
        income = income_months.get(month, 0.0)
        month_expenses = transactions_by_month[month]
        month_categories = expense_by_month_and_category.get(month, {})
        monthly_rows.append({
            "month": f"{month[0]}-{month[1]}",
            "totals": {
                "income": income,
                "expenses": expenses,
                "net": income - expenses,
            },
            "top_categories": _top_category_pairs(month_categories, n),
            "largest_expenses": [
                _transaction_dict(transaction)
                for transaction in top_expenses(month_expenses, n=n)
            ],
            "budget_comparisons": comparisons_by_month.get(month, {}).get(
                "categories", []
            ),
        })

    total_expenses = sum(expense_totals.values(), 0.0)
    total_income = sum(income_totals.values(), 0.0)
    account_breakdown = {
        kind: {
            "transaction_count": account.get_transaction_count(),
            "total_spent": account.get_total_spent(),
            "total_received": account.get_total_received(),
        }
        for kind, account in accounts.items()
    }
    expense_transactions = transactions
    metrics = RunMetrics.from_pipeline(result)

    result = {
        "scope": "transactions selected by menu query",
        "selection": selection or {"type": "all"},
        "selected_transactions": sum(
            account.get_transaction_count()
            for account in accounts.values()
        ),
        "metrics": metrics.report(),
        "total_breakdown": {
            "totals": {
                "income": total_income,
                "expenses": total_expenses,
                "net": total_income - total_expenses,
            },
            "top_categories": top_categories(accounts.values(), n=n),
            "largest_expenses": [
                _transaction_dict(transaction)
                for transaction in top_expenses(expense_transactions, n=n)
            ],
            "budget_by_category": _total_budget_comparisons(budget_comparisons),
            "account_breakdown": account_breakdown,
            "chart_data": [
                {"category": category, "expenses": expense_totals[category]}
                for category in sorted(expense_totals)
            ],
        },
        "monthly_breakdown": {
            "months": monthly_rows,
            "chart_data": [
                {"month": f"{year}-{month}", "expenses": expense_months[(year, month)]}
                for year, month in sorted(expense_months)
            ],
        },
    }

    # Extract chart data into its own object
    chart_data = {
        "total_breakdown": result["total_breakdown"].pop("chart_data"),
        "monthly_breakdown": result["monthly_breakdown"].pop("chart_data"),
    }

    return result, chart_data


def iter_transactions(accounts):
    """Yield each transaction held by the supplied account mapping."""
    for account in accounts.values():
        yield from account.get_transactions()


def _top_category_pairs(totals, n):
    return sorted(totals.items(), key=lambda item: (-item[1], item[0]))[:n]


def _get_month(transaction):
    if isinstance(transaction, dict):
        raw_date = transaction.get("date")
        if not isinstance(raw_date, str) or len(raw_date) != 10:
            return None
        return raw_date[:4], raw_date[5:7]
    return transaction.get_month()


def _transaction_dict(transaction):
    if isinstance(transaction, dict):
        return dict(transaction)
    return transaction.to_dict()


def _total_budget_comparisons(monthly_comparisons):
    accumulated = {}
    for comparison in monthly_comparisons:
        period = comparison["period"]
        start = date.fromisoformat(period["start"])
        end = date.fromisoformat(period["end"])
        days_in_month = monthrange(start.year, start.month)[1]
        fraction = (end - start).days + 1
        fraction /= days_in_month
        for item in comparison["categories"]:
            category = item["category"]
            entry = accumulated.setdefault(category, {
                "actual": 0.0, "limit": 0.0, "unbudgeted": False,
            })
            entry["actual"] += item["actual"]
            if item["limit"] is None:
                entry["unbudgeted"] = True
            else:
                entry["limit"] += item["limit"] * fraction

    totals = []
    for category in sorted(accumulated):
        entry = accumulated[category]
        if entry["unbudgeted"]:
            totals.append({
                "category": category,
                "limit": None,
                "actual": entry["actual"],
                "status": "unbudgeted",
                "difference": None,
            })
        else:
            limit = entry["limit"]
            status, difference = Budget(category, limit).status(entry["actual"])
            totals.append({
                "category": category,
                "limit": limit,
                "actual": entry["actual"],
                "status": status,
                "difference": difference,
            })
    return totals