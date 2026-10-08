import unittest

from budgetwise.cleaning.categories import normalize_category


class TestCategoryParser(unittest.TestCase):

    def test_exact_food(self):
        self.assertEqual(
            normalize_category("Food"),
            ("Food", None)
        )

    def test_uppercase_food(self):
        self.assertEqual(
            normalize_category("FOOD"),
            ("Food", "CATEGORY_NORMALIZED")
        )

    def test_food_typo(self):
        self.assertEqual(
            normalize_category("Fod"),
            ("Food", "CATEGORY_NORMALIZED")
        )

    def test_food_with_spaces(self):
        self.assertEqual(
            normalize_category("  Food  "),
            ("Food", None)
        )

    def test_rent_typo(self):
        self.assertEqual(
            normalize_category("Rentt"),
            ("Rent", "CATEGORY_NORMALIZED")
        )

    def test_travel_typo(self):
        self.assertEqual(
            normalize_category("Traval"),
            ("Transportation", "CATEGORY_NORMALIZED")
        )

    def test_entertainment_typo(self):
        self.assertEqual(
            normalize_category("Entrtnmnt"),
            ("Entertainment", "CATEGORY_NORMALIZED")
        )

    def test_utilities_typo(self):
        self.assertEqual(
            normalize_category("Utilties"),
            ("Utilities", "CATEGORY_NORMALIZED")
        )

    def test_education_typo(self):
        self.assertEqual(
            normalize_category("Educaton"),
            ("Education", "CATEGORY_NORMALIZED")
        )

    def test_healthcare_mapping(self):
        self.assertEqual(
            normalize_category("Helth"),
            ("Healthcare", "CATEGORY_NORMALIZED")
        )

    def test_savings_mapping(self):
        self.assertEqual(
            normalize_category("Saving"),
            ("Savings", "CATEGORY_NORMALIZED")
        )

    def test_other_mapping(self):
        self.assertEqual(
            normalize_category("Misc"),
            ("Other", "CATEGORY_NORMALIZED")
        )

    def test_freelance(self):
        self.assertEqual(
            normalize_category("Freelance"),
            ("Freelance", None)
        )

    def test_bonus(self):
        self.assertEqual(
            normalize_category("Bonus"),
            ("Bonus", None)
        )

    def test_missing_empty_string(self):
        self.assertEqual(
            normalize_category(""),
            ("Uncategorized", "CATEGORY_UNCATEGORIZED")
        )

    def test_missing_spaces(self):
        self.assertEqual(
            normalize_category("   "),
            ("Uncategorized", "CATEGORY_UNCATEGORIZED")
        )

    def test_missing_none(self):
        self.assertEqual(
            normalize_category(None),
            ("Uncategorized", "CATEGORY_UNCATEGORIZED")
        )

    def test_unknown_category(self):
        self.assertEqual(
            normalize_category("CarPayment"),
            ("Uncategorized", "UNKNOWN_CATEGORY")
        )


if __name__ == "__main__":
    unittest.main()
