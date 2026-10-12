"""
fixture.py - hand-calculated summary sample (task P3.3, Bahareh)

Ten cleaned transactions: seven expenses and three income records.
One expense and one income record have no date.

Manual calculations:
    Total income:   1000 + 500 + 100 = 1600
    Total expenses: 120 + 200 + 500 + 80 + 200 + 150 + 50 = 1300
    Net balance:    1600 - 1300 = 300

Monthly expenses:
    January 2026:  120 + 200 + 500 = 820
    February 2026: 80 + 200 + 150 = 430
    Undated expense: 50, included only in non-date summaries.
    Reconciliation: 1300 - (820 + 430) = 50

Expense categories:
    Rent:           500
    Food:           120 + 80 + 50 = 250
    Other:          200
    Transportation: 200
    Utilities:      150

Category ties: Other precedes Transportation alphabetically.
Expense ties: E02 precedes E05 because it occurs earlier in the input.
"""


def make_transactions():
    """
    Description:
    - Return a fresh list of cleaned dictionaries for each test.
    - Preserve a fixed input order for testing equal-amount ties.

    Input arguments:
        None.

    Return:
        list[dict]: ten cleaned transaction records.
    """
    rows = [
        ("E01", "2026-01-05", "Food", 120.0, "Expense"),
        ("E02", "2026-01-10", "Transportation", 200.0, "Expense"),
        ("E03", "2026-01-01", "Rent", 500.0, "Expense"),
        ("E04", "2026-02-05", "Food", 80.0, "Expense"),
        ("E05", "2026-02-10", "Other", 200.0, "Expense"),
        ("E06", "2026-02-15", "Utilities", 150.0, "Expense"),
        ("E07", None, "Food", 50.0, "Expense"),
        ("I01", "2026-01-02", "Salary", 1000.0, "Income"),
        ("I02", "2026-02-02", "Salary", 500.0, "Income"),
        ("I03", None, "Other", 100.0, "Income"),
    ]

    return [
        {
            "transaction_id": transaction_id,
            "date": date,
            "category": category,
            "amount": amount,
            "transaction_type": transaction_type,
        }
        for transaction_id, date, category, amount, transaction_type in rows
    ]


EXPECTED_INCOME = 1600.0
EXPECTED_EXPENSES = 1300.0
EXPECTED_NET = 300.0

EXPECTED_MONTHLY_EXPENSES = {
    ("2026", "01"): 820.0,
    ("2026", "02"): 430.0,
}

EXPECTED_TOP_CATEGORIES = [
    ("Rent", 500.0),
    ("Food", 250.0),
    ("Other", 200.0),
    ("Transportation", 200.0),
    ("Utilities", 150.0),
]

EXPECTED_TOP_EXPENSE_IDS = [
    "E03",
    "E02",
    "E05",
    "E06",
    "E01",
]
