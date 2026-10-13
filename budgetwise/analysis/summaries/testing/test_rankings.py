"""
test_rankings.py - spending ranking tests (task P3.3, Bahareh)

Check hand-calculated rankings, tie rules, limits, and input preservation.
These tests use cleaned dictionaries, not the actual model classes.
"""

import unittest
from copy import deepcopy

from budgetwise.analysis.summaries import (
    top_categories,
    top_expenses,
)
from .fixture import (
    make_transactions,
    EXPECTED_TOP_CATEGORIES,
    EXPECTED_TOP_EXPENSE_IDS,
)


class TestSummaryRankings(unittest.TestCase):
    """Verify category and individual expense rankings."""

    def setUp(self):
        """Create fresh records before each test."""
        self.transactions = make_transactions()

    def test_top_categories(self):
        """Default category ranking matches the hand-calculated result."""
        self.assertEqual(
            top_categories(self.transactions),
            EXPECTED_TOP_CATEGORIES,
        )

    def test_top_expenses(self):
        """Default expense ranking matches the expected transaction IDs."""
        result = top_expenses(self.transactions)
        self.assertEqual(
            [record["transaction_id"] for record in result],
            EXPECTED_TOP_EXPENSE_IDS,
        )

    def test_category_ties_use_name(self):
        """Equal category totals use alphabetical order regardless of input."""
        result = top_categories(list(reversed(self.transactions)))
        self.assertEqual(result, EXPECTED_TOP_CATEGORIES)

    def test_expense_ties_preserve_input_order(self):
        """Equal expense amounts follow their order in the supplied input."""
        result = top_expenses(list(reversed(self.transactions)))
        self.assertEqual(
            [record["transaction_id"] for record in result],
            ["E03", "E05", "E02", "E06", "E01"],
        )

    def test_custom_limit(self):
        """A limit of two returns the two highest results."""
        self.assertEqual(
            top_categories(self.transactions, n=2),
            EXPECTED_TOP_CATEGORIES[:2],
        )
        result = top_expenses(self.transactions, n=2)
        self.assertEqual(
            [record["transaction_id"] for record in result],
            EXPECTED_TOP_EXPENSE_IDS[:2],
        )

    def test_large_limit(self):
        """A large limit returns all available expense results."""
        self.assertEqual(
            top_categories(self.transactions, n=20),
            EXPECTED_TOP_CATEGORIES,
        )
        result = top_expenses(self.transactions, n=20)
        self.assertEqual(
            [record["transaction_id"] for record in result],
            ["E03", "E02", "E05", "E06", "E01", "E04", "E07"],
        )

    def test_zero_limit(self):
        """A zero limit returns empty lists."""
        self.assertEqual(top_categories(self.transactions, n=0), [])
        self.assertEqual(top_expenses(self.transactions, n=0), [])

    def test_empty_input(self):
        """Empty input returns empty lists."""
        self.assertEqual(top_categories([]), [])
        self.assertEqual(top_expenses([]), [])

    def test_income_only(self):
        """Income records do not appear in spending rankings."""
        records = self.transactions[7:]
        self.assertEqual(top_categories(records), [])
        self.assertEqual(top_expenses(records), [])

    def test_undated_expense_is_included(self):
        """An expense without a date can appear in both rankings."""
        records = [self.transactions[6]]
        self.assertEqual(top_categories(records), [("Food", 50.0)])
        result = top_expenses(records)
        self.assertEqual(
            [record["transaction_id"] for record in result],
            ["E07"],
        )

    def test_negative_limit(self):
        """Both functions reject negative result limits."""
        for function in (top_categories, top_expenses):
            with self.subTest(function=function.__name__):
                with self.assertRaises(ValueError):
                    function(self.transactions, n=-1)

    def test_invalid_limit_types(self):
        """Both functions reject nonintegers and booleans."""
        for function in (top_categories, top_expenses):
            for invalid in (2.5, "5", None, True, False):
                with self.subTest(
                    function=function.__name__,
                    n=invalid,
                ):
                    with self.assertRaises(TypeError):
                        function(self.transactions, n=invalid)

    def test_input_is_not_modified(self):
        """Rankings leave the input records and their order unchanged."""
        original = deepcopy(self.transactions)
        top_categories(self.transactions)
        top_expenses(self.transactions)
        self.assertEqual(self.transactions, original)

    def test_expenses_return_original_records(self):
        """Expense results retain the original record objects."""
        result = top_expenses(self.transactions, n=1)
        self.assertIs(result[0], self.transactions[2])

    def test_repeated_ids_are_retained(self):
        """Distinct expenses with the same ID remain separate results."""
        first = dict(self.transactions[0])
        second = dict(first)
        second["amount"] = 90.0

        result = top_expenses([first, second])
        self.assertEqual(len(result), 2)
        self.assertIs(result[0], first)
        self.assertIs(result[1], second)

    def test_generator_input(self):
        """Both rankings accept single-use generators."""
        category_records = (record for record in self.transactions)
        self.assertEqual(
            top_categories(category_records),
            EXPECTED_TOP_CATEGORIES,
        )

        expense_records = (record for record in self.transactions)
        result = top_expenses(expense_records)
        self.assertEqual(
            [record["transaction_id"] for record in result],
            EXPECTED_TOP_EXPENSE_IDS,
        )


if __name__ == "__main__":
    unittest.main()
