"""
fields.py  -  read one value from a transaction          (task P3.2, Henrietta)

The aggregation functions accept two shapes of transaction:

  * a Transaction object from budgetwise.models (Zeyad, P3.1), read through
    its getters: get_category(), get_amount(), get_transaction_type(),
    get_month()
  * a cleaned record dictionary from budgetwise.pipeline.clean_file()
    (Sarah, P2.10), read by key: "category", "amount", "transaction_type",
    "date"

Accepting both means aggregation works on the pipeline's output today and on
the model objects once they are merged, without either module changing.
Standard library only.
"""

# The two values transaction_type can take after cleaning.
EXPENSE = "expense"
INCOME = "income"
VALID_KINDS = (EXPENSE, INCOME, None)

# Position of the year and month inside a 'YYYY-MM-DD' date string.
YEAR_SLICE = slice(0, 4)
MONTH_SLICE = slice(5, 7)
DATE_LENGTH = 10


def get_category(transaction):
    """
    Description:
    - Return the transaction's normalized category.

    Input arguments:
       transaction (Transaction or dict): one cleaned transaction.

    Return:
        str: e.g. 'Food'.
    """
    if isinstance(transaction, dict):
        return transaction["category"]
    return transaction.get_category()


def get_amount(transaction):
    """
    Description:
    - Return the unsigned magnitude. Direction comes from the type, never the
      sign (section 4.5).

    Input arguments:
       transaction (Transaction or dict): one cleaned transaction.

    Return:
        float: e.g. 1810.0.
    """
    if isinstance(transaction, dict):
        return float(transaction["amount"])
    return float(transaction.get_amount())


def get_kind(transaction):
    """
    Description:
    - Return 'expense' or 'income', lowercase.

    Input arguments:
       transaction (Transaction or dict): one cleaned transaction.

    Return:
        str: 'expense', 'income', or the lowercased value if it is neither.
    """
    if isinstance(transaction, dict):
        kind = transaction["transaction_type"]
    else:
        kind = transaction.get_transaction_type()
    return (kind or "").strip().lower()


def get_month(transaction):
    """
    Description:
    - Return the (year, month) tuple key, or None when the transaction has no
      usable date. Section 4.5: undated rows are left out of date analysis.

    Input arguments:
       transaction (Transaction or dict): one cleaned transaction.

    Return:
        tuple[str, str] or None: e.g. ('2023', '07').
    """
    if not isinstance(transaction, dict):
        return transaction.get_month()
    date = transaction.get("date")
    if not isinstance(date, str) or len(date) != DATE_LENGTH:
        return None
    return (date[YEAR_SLICE], date[MONTH_SLICE])


def matches_kind(transaction, kind):
    """
    Description:
    - Whether a transaction passes the kind filter.

    Input arguments:
       transaction (Transaction or dict): one cleaned transaction.
       kind (str or None): 'expense', 'income', or None for both.

    Return:
        bool: True when kind is None or the transaction is of that kind.
    """
    return kind is None or get_kind(transaction) == kind


def check_kind(kind):
    """
    Description:
    - Reject a kind filter the functions do not understand, so a typo such as
      'expenses' fails loudly instead of returning empty totals.

    Input arguments:
       kind (str or None): the filter passed in.

    Return:
        str or None: the kind, lowercased.
    """
    if kind is not None:
        kind = kind.strip().lower()
    if kind not in VALID_KINDS:
        raise ValueError(
            f"kind must be 'expense', 'income' or None, not {kind!r}")
    return kind
