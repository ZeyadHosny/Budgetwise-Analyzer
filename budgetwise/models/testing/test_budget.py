import unittest

from budgetwise.models.implementation.budget import Budget


class TestBudget(unittest.TestCase):

    def test_category_and_limit(self):
        budget = Budget("Food", 3900)

        self.assertEqual(budget.get_category(), "Food")
        self.assertEqual(budget.get_monthly_limit(), 3900.0)

    def test_category_surrounding_spaces(self):
        budget = Budget("  Food  ", 3900)

        self.assertEqual(budget.get_category(), "Food")

    def test_over_budget(self):
        budget = Budget("Food", 3900)

        self.assertEqual(budget.status(4200), ("over", 300.0))

    def test_under_budget(self):
        budget = Budget("Food", 3900)

        self.assertEqual(budget.status(3500), ("under", 400.0))

    def test_equal_budget(self):
        budget = Budget("Food", 3900)

        self.assertEqual(budget.status(3900), ("equal", 0.0))

    def test_zero_spending(self):
        budget = Budget("Food", 3900)

        self.assertEqual(budget.status(0), ("under", 3900.0))

    def test_zero_limit(self):
        budget = Budget("Food", 0)

        self.assertEqual(budget.status(0), ("equal", 0.0))
        self.assertEqual(budget.status(100), ("over", 100.0))

    def test_decimal_amounts(self):
        budget = Budget("Food", 100.50)

        status, difference = budget.status(120.75)

        self.assertEqual(status, "over")
        self.assertAlmostEqual(difference, 20.25)

    def test_change_limit(self):
        budget = Budget("Food", 3900)
        budget.set_monthly_limit(4500)

        self.assertEqual(budget.get_monthly_limit(), 4500.0)
        self.assertEqual(budget.status(4200), ("under", 300.0))

    def test_invalid_categories(self):
        for category in ("", "   ", None, 123):
            with self.subTest(category=category):
                with self.assertRaises(ValueError):
                    Budget(category, 3900)

    def test_invalid_initial_limits(self):
        invalid_values = (
            -1,
            None,
            "3900",
            True,
            float("nan"),
            float("inf"),
            float("-inf"),
        )

        for value in invalid_values:
            with self.subTest(value=value):
                with self.assertRaises(ValueError):
                    Budget("Food", value)

    def test_invalid_limit_change_preserves_previous_limit(self):
        budget = Budget("Food", 3900)

        for value in (-1, None, "4500", True, float("nan"), float("inf")):
            with self.subTest(value=value):
                with self.assertRaises(ValueError):
                    budget.set_monthly_limit(value)

                self.assertEqual(
                    budget.get_monthly_limit(),
                    3900.0,
                )

    def test_invalid_actual_spending(self):
        budget = Budget("Food", 3900)

        invalid_values = (
            -1,
            None,
            "4200",
            True,
            float("nan"),
            float("inf"),
            float("-inf"),
        )

        for value in invalid_values:
            with self.subTest(value=value):
                with self.assertRaises(ValueError):
                    budget.status(value)


if __name__ == "__main__":
    unittest.main()
