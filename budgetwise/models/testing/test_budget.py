import unittest

from budgetwise.models import Budget


class TestBudget(unittest.TestCase):
    def setUp(self):
        self.budget = Budget("Food", 8000)

    def test_category_and_limit_are_read_through_getters(self):
        self.assertEqual(self.budget.get_category(), "Food")
        self.assertEqual(self.budget.get_monthly_limit(), 8000.0)

    def test_over_budget_has_positive_difference(self):
        self.assertEqual(self.budget.status(9500), ("over", 1500.0))

    def test_under_budget_has_negative_difference(self):
        self.assertEqual(self.budget.status(7800), ("under", -200.0))

    def test_exact_budget_has_zero_difference(self):
        self.assertEqual(self.budget.status(8000), ("exact", 0.0))

    def test_category_is_trimmed(self):
        self.assertEqual(Budget(" Food ", 10).get_category(), "Food")

    def test_rejects_invalid_category(self):
        for category in (None, 5):
            with self.subTest(category=category):
                with self.assertRaises(TypeError):
                    Budget(category, 10)
        with self.assertRaises(ValueError):
            Budget("  ", 10)

    def test_rejects_invalid_limit_or_actual(self):
        for value in (-1, float("nan"), float("inf")):
            with self.subTest(value=value):
                with self.assertRaises(ValueError):
                    Budget("Food", value)
                with self.assertRaises(ValueError):
                    self.budget.status(value)

    def test_rejects_boolean_amounts(self):
        with self.assertRaises(TypeError):
            Budget("Food", True)
        with self.assertRaises(TypeError):
            self.budget.status(False)


if __name__ == "__main__":
    unittest.main()