"""
A twenty-row hand-checked fixture for the aggregation tests.

Each row is a cleaned record in the shape budgetwise.pipeline.clean_file()
returns. Totals below were summed by hand, row by row, and are the expected
values the tests assert against.

 #  type     date        category        amount
 1  Expense  2023-01-05  Food              100
 2  Expense  2023-01-12  Food              250
 3  Expense  2023-01-20  Rent             1000
 4  Income   2023-01-31  Salary           5000
 5  Expense  2023-02-03  Food              150
 6  Expense  2023-02-10  Transportation    300
 7  Expense  2023-02-15  Rent             1000
 8  Income   2023-02-28  Salary           5000
 9  Expense  None        Food              400   <- undated
10  Expense  2023-03-01  Utilities         200
11  Expense  2023-03-08  Entertainment     120
12  Income   2023-03-15  Freelance         800
13  Expense  2023-03-22  Food              180
14  Expense  None        Rent              950   <- undated
15  Income   None        Bonus             600   <- undated
16  Expense  2022-12-30  Healthcare        220
17  Expense  2022-12-31  Food               80
18  Income   2022-12-31  Investment        300
19  Expense  2023-03-30  Uncategorized      50
20  Expense  2023-02-20  Utilities         210

Expense by category (undated rows INCLUDED):
  Food           100 + 250 + 150 + 400 + 180 + 80 = 1160
  Rent           1000 + 1000 + 950                = 2950
  Transportation 300
  Utilities      200 + 210                        = 410
  Entertainment  120
  Healthcare     220
  Uncategorized  50
  total                                           = 5210

Income by category:
  Salary 10000 · Freelance 800 · Bonus 600 · Investment 300 · total 11700

Expense by month (undated rows EXCLUDED: 400 + 950 = 1350 left out):
  2022-12  220 + 80                  = 300
  2023-01  100 + 250 + 1000          = 1350
  2023-02  150 + 300 + 1000 + 210    = 1660
  2023-03  200 + 120 + 180 + 50      = 550
  total                              = 3860   (5210 - 1350)

Income by month (undated Bonus 600 EXCLUDED):
  2022-12 300 · 2023-01 5000 · 2023-02 5000 · 2023-03 800 · total 11100
"""

_ROWS = [
    ("Expense", "2023-01-05", "Food", 100),
    ("Expense", "2023-01-12", "Food", 250),
    ("Expense", "2023-01-20", "Rent", 1000),
    ("Income", "2023-01-31", "Salary", 5000),
    ("Expense", "2023-02-03", "Food", 150),
    ("Expense", "2023-02-10", "Transportation", 300),
    ("Expense", "2023-02-15", "Rent", 1000),
    ("Income", "2023-02-28", "Salary", 5000),
    ("Expense", None, "Food", 400),
    ("Expense", "2023-03-01", "Utilities", 200),
    ("Expense", "2023-03-08", "Entertainment", 120),
    ("Income", "2023-03-15", "Freelance", 800),
    ("Expense", "2023-03-22", "Food", 180),
    ("Expense", None, "Rent", 950),
    ("Income", None, "Bonus", 600),
    ("Expense", "2022-12-30", "Healthcare", 220),
    ("Expense", "2022-12-31", "Food", 80),
    ("Income", "2022-12-31", "Investment", 300),
    ("Expense", "2023-03-30", "Uncategorized", 50),
    ("Expense", "2023-02-20", "Utilities", 210),
]


def records():
    """Return a fresh list of the twenty fixture rows as cleaned record dicts."""
    return [
        {
            "line_number": number,
            "transaction_id": f"T{number:03d}",
            "user_id": "U001",
            "transaction_type": kind,
            "date": date,
            "category": category,
            "amount": float(amount),
        }
        for number, (kind, date, category, amount) in enumerate(_ROWS, start=2)
    ]


class FakeTransaction:
    """Stands in for a budgetwise.models Transaction: same getters, nothing else."""

    def __init__(self, record):
        self._record = record

    def get_category(self):
        return self._record["category"]

    def get_amount(self):
        return self._record["amount"]

    def get_transaction_type(self):
        return self._record["transaction_type"]

    def get_month(self):
        date = self._record["date"]
        return None if date is None else (date[0:4], date[5:7])


def objects():
    """Return the same twenty rows as Transaction-like objects."""
    return [FakeTransaction(record) for record in records()]


EXPENSE_BY_CATEGORY = {
    "Food": 1160.0, "Rent": 2950.0, "Transportation": 300.0, "Utilities": 410.0,
    "Entertainment": 120.0, "Healthcare": 220.0, "Uncategorized": 50.0,
}
INCOME_BY_CATEGORY = {
    "Salary": 10000.0, "Freelance": 800.0, "Bonus": 600.0, "Investment": 300.0,
}
EXPENSE_BY_MONTH = {
    ("2022", "12"): 300.0, ("2023", "01"): 1350.0,
    ("2023", "02"): 1660.0, ("2023", "03"): 550.0,
}
INCOME_BY_MONTH = {
    ("2022", "12"): 300.0, ("2023", "01"): 5000.0,
    ("2023", "02"): 5000.0, ("2023", "03"): 800.0,
}
