import unittest

from budgetwise.cleaning.categories import normalize


class TestCategoryParser(unittest.TestCase):

    def test_exact_food(self):
        self.assertEqual(
            normalize("Food"),
            ("Food", None)
        )

    def test_uppercase_food(self):
        self.assertEqual(
            normalize("FOOD"),
            ("Food", None)
        )

    def test_food_typo(self):
        self.assertEqual(
            normalize("Fod"),
            ("Food", None)
        )

    def test_food_with_spaces(self):
        self.assertEqual(
            normalize("  Food  "),
            ("Food", None)
        )

    def test_rent_typo(self):
        self.assertEqual(
            normalize("Rentt"),
            ("Rent", None)
        )

    def test_travel_typo(self):
        self.assertEqual(
            normalize("Traval"),
            ("Travel", None)
        )

    def test_entertainment_typo(self):
        self.assertEqual(
            normalize("Entrtnmnt"),
            ("Entertainment", None)
        )

    def test_utilities_typo(self):
        self.assertEqual(
            normalize("Utilties"),
            ("Utilities", None)
        )

    def test_education_typo(self):
        self.assertEqual(
            normalize("Educaton"),
            ("Education", None)
        )

    def test_healthcare_mapping(self):
        self.assertEqual(
            normalize("Helth"),
            ("Healthcare", None)
        )

    def test_savings_mapping(self):
        self.assertEqual(
            normalize("Saving"),
            ("Savings", None)
        )

    def test_other_mapping(self):
        self.assertEqual(
            normalize("Misc"),
            ("Other", None)
        )

    def test_freelance(self):
        self.assertEqual(
            normalize("Freelance"),
            ("Freelance", None)
        )

    def test_bonus(self):
        self.assertEqual(
            normalize("Bonus"),
            ("Bonus", None)
        )

    def test_missing_empty_string(self):
        self.assertEqual(
            normalize(""),
            ("Uncategorized", "missing_category")
        )

    def test_missing_spaces(self):
        self.assertEqual(
            normalize("   "),
            ("Uncategorized", "missing_category")
        )

    def test_missing_none(self):
        self.assertEqual(
            normalize(None),
            ("Uncategorized", "missing_category")
        )

    def test_unknown_category(self):
        self.assertEqual(
            normalize("CarPayment"),
            ("Uncategorized", "unknown_category")
        )


if __name__ == "__main__":
    unittest.main()
