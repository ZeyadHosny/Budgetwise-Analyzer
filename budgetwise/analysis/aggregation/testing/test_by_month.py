import unittest

from budgetwise.analysis.aggregation import (
    totals_by_category,
    totals_by_month,
    totals_by_month_and_category,
)

from . import fixture


class TestTotalsByMonth(unittest.TestCase):

    def test_expense_totals_match_hand_sums(self):
        self.assertEqual(
            totals_by_month(fixture.records(), kind="expense"),
            fixture.EXPENSE_BY_MONTH,
        )

    def test_income_totals_match_hand_sums(self):
        self.assertEqual(
            totals_by_month(fixture.records(), kind="income"),
            fixture.INCOME_BY_MONTH,
        )

    def test_undated_rows_are_excluded(self):
        # Category total includes the undated 1,350; month total does not.
        by_category = sum(totals_by_category(fixture.records(), kind="expense").values())
        by_month = sum(totals_by_month(fixture.records(), kind="expense").values())
        self.assertEqual(by_category - by_month, 400.0 + 950.0)

    def test_keys_are_tuples_of_two_strings(self):
        for key in totals_by_month(fixture.records()):
            with self.subTest(key=key):
                self.assertIsInstance(key, tuple)
                self.assertEqual(len(key), 2)
                self.assertTrue(all(isinstance(part, str) for part in key))

    def test_keys_are_in_chronological_order(self):
        keys = list(totals_by_month(fixture.records()))
        self.assertEqual(keys, sorted(keys))
        self.assertEqual(keys[0], ("2022", "12"))

    def test_transaction_objects_give_same_totals(self):
        self.assertEqual(
            totals_by_month(fixture.objects(), kind="expense"),
            fixture.EXPENSE_BY_MONTH,
        )

    def test_empty_list_returns_empty_dict(self):
        self.assertEqual(totals_by_month([]), {})


class TestTotalsByMonthAndCategory(unittest.TestCase):

    def test_february_expenses(self):
        result = totals_by_month_and_category(fixture.records(), kind="expense")
        self.assertEqual(
            result[("2023", "02")],
            {"Food": 150.0, "Transportation": 300.0, "Rent": 1000.0, "Utilities": 210.0},
        )

    def test_inner_totals_match_month_totals(self):
        nested = totals_by_month_and_category(fixture.records(), kind="expense")
        flat = totals_by_month(fixture.records(), kind="expense")
        for month, by_category in nested.items():
            with self.subTest(month=month):
                self.assertEqual(sum(by_category.values()), flat[month])

    def test_empty_list_returns_empty_dict(self):
        self.assertEqual(totals_by_month_and_category([]), {})


if __name__ == "__main__":
    unittest.main()
