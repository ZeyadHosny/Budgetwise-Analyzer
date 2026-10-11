import unittest

from budgetwise.analysis.aggregation import (
    count_by_category,
    totals_by_category,
    unique_categories,
)

from . import fixture


class TestTotalsByCategory(unittest.TestCase):

    def test_expense_totals_match_hand_sums(self):
        self.assertEqual(
            totals_by_category(fixture.records(), kind="expense"),
            fixture.EXPENSE_BY_CATEGORY,
        )

    def test_income_totals_match_hand_sums(self):
        self.assertEqual(
            totals_by_category(fixture.records(), kind="income"),
            fixture.INCOME_BY_CATEGORY,
        )

    def test_no_kind_combines_both(self):
        totals = totals_by_category(fixture.records())
        self.assertEqual(sum(totals.values()), 5210.0 + 11700.0)

    def test_expense_filter_excludes_income_categories(self):
        totals = totals_by_category(fixture.records(), kind="expense")
        self.assertNotIn("Salary", totals)

    def test_income_filter_excludes_expense_categories(self):
        totals = totals_by_category(fixture.records(), kind="income")
        self.assertNotIn("Food", totals)

    def test_undated_rows_still_count(self):
        # Food includes the undated 400; Rent includes the undated 950.
        totals = totals_by_category(fixture.records(), kind="expense")
        self.assertEqual(totals["Food"], 1160.0)
        self.assertEqual(totals["Rent"], 2950.0)

    def test_kind_is_case_insensitive(self):
        self.assertEqual(
            totals_by_category(fixture.records(), kind="Expense"),
            fixture.EXPENSE_BY_CATEGORY,
        )

    def test_unknown_kind_raises(self):
        with self.assertRaises(ValueError):
            totals_by_category(fixture.records(), kind="expenses")

    def test_transaction_objects_give_same_totals(self):
        self.assertEqual(
            totals_by_category(fixture.objects(), kind="expense"),
            fixture.EXPENSE_BY_CATEGORY,
        )

    def test_returns_plain_dict(self):
        self.assertIs(type(totals_by_category(fixture.records())), dict)

    def test_empty_list_returns_empty_dict(self):
        self.assertEqual(totals_by_category([]), {})


class TestCountByCategory(unittest.TestCase):

    def test_expense_counts(self):
        self.assertEqual(
            count_by_category(fixture.records(), kind="expense"),
            {"Food": 6, "Rent": 3, "Transportation": 1, "Utilities": 2,
             "Entertainment": 1, "Healthcare": 1, "Uncategorized": 1},
        )

    def test_counts_add_up_to_twenty(self):
        self.assertEqual(sum(count_by_category(fixture.records()).values()), 20)

    def test_empty_list_returns_empty_dict(self):
        self.assertEqual(count_by_category([]), {})


class TestUniqueCategories(unittest.TestCase):

    def test_returns_a_set(self):
        self.assertIsInstance(unique_categories(fixture.records()), set)

    def test_contains_each_category_once(self):
        self.assertEqual(
            unique_categories(fixture.records()),
            set(fixture.EXPENSE_BY_CATEGORY) | set(fixture.INCOME_BY_CATEGORY),
        )

    def test_empty_list_returns_empty_set(self):
        self.assertEqual(unique_categories([]), set())


if __name__ == "__main__":
    unittest.main()
