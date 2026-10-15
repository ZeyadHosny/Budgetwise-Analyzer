"""
by_month.py  -  totals by (year, month)                  
Section 4.2 data structures used here:
  tuple  the month key is ('2023', '07'): immutable, so it can be a dict key,
         and tuples of zero-padded strings sort chronologically
  dict   totals accumulate under that key

A transaction with no date is left out of every monthly total (section 4.5).
So sum(totals_by_month) can be smaller than sum(totals_by_category), and that
is correct, not a bug.
"""

from collections import defaultdict

from budgetwise.models.implementation.account import Account

from .fields import check_kind, get_amount, get_category, get_month, matches_kind


def totals_by_month(accounts: list[Account], kind=None):
    """
    Description:
    - Sum the amount of every dated transaction under its (year, month) key.
    - Undated transactions are skipped (section 4.5).
    - Keys are returned in chronological order.

    Input arguments:
       accounts (list[Account]): A list of account objects containing transactions.
       kind (str or None): 'expense', 'income', or None for both.

    Return:
        dict[tuple[str, str], float]: e.g. {('2023', '07'): 1204880.0}.
    """
    kind = check_kind(kind)
    totals = defaultdict(float)
    transactions = []
    for account in accounts:
        transactions.extend(account.get_transactions())
    for transaction in transactions:
        if not matches_kind(transaction, kind):
            continue
        month = get_month(transaction)
        if month is None:
            continue
        totals[month] += get_amount(transaction)
    return {month: totals[month] for month in sorted(totals)}


def totals_by_month_and_category(accounts: list[Account], kind=None):
    """
    Description:
    - Sum dated transactions by month, then by category within each month.
      Used for monthly budget comparisons and month-level charts.
    - Undated transactions are skipped (section 4.5).

    Input arguments:
       accounts (list[Account]): A list of account objects containing transactions.
       kind (str or None): 'expense', 'income', or None for both.

    Return:
        dict[tuple[str, str], dict[str, float]]:
            e.g. {('2023', '07'): {'Food': 98000.0, 'Rent': 120500.0}}.
    """
    kind = check_kind(kind)
    totals = defaultdict(lambda: defaultdict(float))
    transactions = []
    for account in accounts:
        transactions.extend(account.get_transactions())
    for transaction in transactions:
        if not matches_kind(transaction, kind):
            continue
        month = get_month(transaction)
        if month is None:
            continue
        totals[month][get_category(transaction)] += get_amount(transaction)
    return {month: dict(totals[month]) for month in sorted(totals)}
