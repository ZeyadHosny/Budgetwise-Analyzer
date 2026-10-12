"""
rankings.py - spending rankings (task P3.3, Bahareh)

Category totals come from the aggregation public interface.
Individual expenses are ranked using their cleaned amounts.
Undated transactions remain included in both rankings.
"""

from budgetwise.analysis.aggregation import totals_by_category


def _check_n(n):
    """
    Description:
    - Validate the maximum number of results.

    Input arguments:
        n (int): nonnegative result limit; bool is not accepted.

    Return:
        None.

    Raises:
        TypeError: if n is not an integer or is a bool.
        ValueError: if n is negative.
    """
    if isinstance(n, bool) or not isinstance(n, int):
        raise TypeError("n must be a nonnegative integer")
    if n < 0:
        raise ValueError("n must be a nonnegative integer")


def _get_amount(transaction):
    """
    Description:
    - Read the amount from a cleaned dictionary or model object.
    - Assume the amount is already cleaned and unsigned.

    Input arguments:
        transaction (Transaction or dict): one cleaned transaction.

    Return:
        float: the transaction amount.
    """
    if isinstance(transaction, dict):
        return float(transaction["amount"])
    return float(transaction.get_amount())


def _is_expense(transaction):
    """
    Description:
    - Identify expenses using transaction_type, never the amount sign.

    Input arguments:
        transaction (Transaction or dict): one cleaned transaction.

    Return:
        bool: True for an expense; otherwise False.
    """
    if isinstance(transaction, dict):
        kind = transaction["transaction_type"]
    else:
        kind = transaction.get_transaction_type()
    return (kind or "").strip().lower() == "expense"


def top_categories(transactions, n=5):
    """
    Description:
    - Rank categories by total expense spending.
    - Use aggregation rather than recalculate category totals.
    - Include undated expenses.
    - Break equal-total ties by category name, ascending.

    Input arguments:
        transactions (iterable): cleaned dictionaries or Transaction objects.
        n (int): maximum number of categories; defaults to 5.

    Return:
        list[tuple[str, float]]: (category, total) pairs ordered by
        total descending, then category name ascending.
        Return [] for empty input or n=0.
        Return all expense categories if fewer than n exist.

    Raises:
        TypeError: if n is not an integer or is a bool.
        ValueError: if n is negative.
    """
    _check_n(n)
    if n == 0:
        return []

    category_totals = totals_by_category(
        transactions, kind="expense"
    )
    ranked = sorted(
        category_totals.items(),
        key=lambda item: (-item[1], item[0]),
    )
    return ranked[:n]


def top_expenses(transactions, n=5):
    """
    Description:
    - Rank individual expense transactions by amount, descending.
    - Identify expenses using transaction_type.
    - Include undated expenses.
    - Preserve input order when amounts are equal.
    - Leave original records unchanged; do not deduplicate them.

    Input arguments:
        transactions (iterable): cleaned dictionaries or Transaction objects.
        n (int): maximum number of expenses; defaults to 5.

    Return:
        list: original expense dictionaries or objects, ordered by
        amount descending. Equal amounts retain their input order.
        Return [] for empty input, no expenses, or n=0.
        Return all expenses if fewer than n exist.

    Raises:
        TypeError: if n is not an integer or is a bool.
        ValueError: if n is negative.
    """
    _check_n(n)
    if n == 0:
        return []

    expenses = [
        transaction
        for transaction in transactions
        if _is_expense(transaction)
    ]
    ranked = sorted(
        expenses,
        key=_get_amount,
        reverse=True,
    )
    return ranked[:n]
