"""
by_category.py  -  totals and counts by category         

Section 4.2 data structures used here:
  list   the transactions arrive as a list and are walked once
  dict   totals and counts accumulate under the category key
  set    unique_categories returns a set: membership is the whole point

A transaction with no date still counts toward its category total
(section 4.5), so nothing here looks at the date.
"""

from collections import defaultdict

from budgetwise.models.implementation.account import Account

from .fields import check_kind, get_amount, get_category, matches_kind


def totals_by_category(accounts: list[Account], kind=None):
    """
    Description:
    - Sum the amount of every transaction under its category.
    - Undated transactions are included (section 4.5).

    Input arguments:
       accounts (list[Account]): A list of account objects containing transactions.
       kind (str or None): 'expense', 'income', or None for both.

    Return:
        dict[str, float]: e.g. {'Food': 8210400.0, 'Rent': 7980120.0}.
    """
    kind = check_kind(kind)
    totals = defaultdict(float)
    transactions = []
    for account in accounts:
        transactions.extend(account.get_transactions())
    for transaction in transactions:
        if matches_kind(transaction, kind):
            totals[get_category(transaction)] += get_amount(transaction)
    return dict(totals)


def count_by_category(accounts: list[Account], kind=None):
    """
    Description:
    - Count the transactions in each category.

    Input arguments:
       accounts (list[Account]): A list of account objects containing transactions.
       kind (str or None): 'expense', 'income', or None for both.

    Return:
        dict[str, int]: e.g. {'Food': 3120, 'Rent': 2540}.
    """
    kind = check_kind(kind)
    counts = defaultdict(int)
    transactions = []
    for account in accounts:
        transactions.extend(account.get_transactions())
    for transaction in transactions:
        if matches_kind(transaction, kind):
            counts[get_category(transaction)] += 1
    return dict(counts)


def unique_categories(accounts: list[Account]):
    """
    Description:
    - The distinct categories present. A set, because the question is
      membership, not order or count.

    Input arguments:
       accounts (list[Account]): A list of account objects containing transactions.

    Return:
        set[str]: e.g. {'Food', 'Rent', 'Transportation'}.
    """
    transactions = []
    for account in accounts:
        transactions.extend(account.get_transactions())
    return {get_category(transaction) for transaction in transactions}
