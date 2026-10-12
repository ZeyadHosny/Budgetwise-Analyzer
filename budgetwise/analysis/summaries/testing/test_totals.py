"""
test_totals.py - summary totals tests (task P3.3, Bahareh)

Compare public summary functions with hand-calculated expectations.
These tests use cleaned dictionaries, not the actual model classes.
"""

import unittest
from copy import deepcopy

from budgetwise.analysis.summaries import (
    total_income,
    total_expenses,
    net_balance,
    monthly_expenses,
)
from .fixture import (
    make_transactions,
    EXPECTED_INCOME,
    EXPECTED_EXPENSES,
    EXPECTED_NET,
    EXPECTED_MONTHLY_EXPENSES,
)


class TestSummaryTotals(unittest.TestCase):
    """Verify totals, date handling, empty input, and input preservation."""

    def setUp(self):
        """Create fresh records before each test."""
        self.transactions = make_transactions()

    def test_total_income(self):
        """Income matches the hand-calculated total, including undated income."""
        self.assertAlmostEqual(
            total_income(self.transactions),
            EXPECTED_INCOME,
            places=2,
        )

    def test_total_expenses(self):
        """Expenses match the hand-calculated total, including undated costs."""
        self.assertAlmostEqual(
            total_expenses(self.transactions),
            EXPECTED_EXPENSES,
            places=2,
        )

    def test_net_balance(self):
        """Net balance equals the hand-calculated income minus expenses."""
        self.assertAlmostEqual(
            net_balance(self.transactions),
            EXPECTED_NET,
            places=2,
        )

    def test_monthly_expenses(self):
        """Monthly totals match the expected year-and-month mapping."""
        self.assertEqual(
            monthly_expenses(self.transactions),
            EXPECTED_MONTHLY_EXPENSES,
        )

    def test_undated_expense_reconciliation(self):
        """The difference between overall and monthly expenses is exactly 50."""
        monthly_total = sum(
            monthly_expenses(self.transactions).values()
        )
        difference = total_expenses(self.transactions) - monthly_total
        self.assertAlmostEqual(difference, 50.0, places=2)

    def test_only_income(self):
        """Income-only input has zero expenses and a positive net balance."""
        records = self.transactions[7:]
        self.assertAlmostEqual(total_income(records), 1600.0, places=2)
        self.assertEqual(total_expenses(records), 0.0)
        self.assertAlmostEqual(net_balance(records), 1600.0, places=2)
        self.assertEqual(monthly_expenses(records), {})

    def test_only_expenses(self):
        """Expense-only input has zero income and a negative net balance."""
        records = self.transactions[:7]
        self.assertEqual(total_income(records), 0.0)
        self.assertAlmostEqual(total_expenses(records), 1300.0, places=2)
        self.assertAlmostEqual(net_balance(records), -1300.0, places=2)

    def test_empty_input(self):
        """Empty input returns zero totals and an empty monthly mapping."""
        self.assertEqual(total_income([]), 0.0)
        self.assertEqual(total_expenses([]), 0.0)
        self.assertEqual(net_balance([]), 0.0)
        self.assertEqual(monthly_expenses([]), {})

    def test_net_balance_accepts_generator(self):
        """A single-use generator produces the same expected net balance."""
        records = (record for record in self.transactions)
        self.assertAlmostEqual(
            net_balance(records),
            EXPECTED_NET,
            places=2,
        )

    def test_transaction_type_controls_direction(self):
        """A positive amount classified as Expense is counted as an expense."""
        records = [
            {
                "transaction_id": "T01",
                "date": None,
                "category": "Food",
                "amount": 25.0,
                "transaction_type": "Expense",
            }
        ]
        self.assertEqual(total_income(records), 0.0)
        self.assertEqual(total_expenses(records), 25.0)
        self.assertEqual(net_balance(records), -25.0)

    def test_input_is_not_modified(self):
        """Calling all total functions leaves records and list order intact."""
        original = deepcopy(self.transactions)

        total_income(self.transactions)
        total_expenses(self.transactions)
        net_balance(self.transactions)
        monthly_expenses(self.transactions)

        self.assertEqual(self.transactions, original)


if __name__ == "__main__":
    unittest.main()
