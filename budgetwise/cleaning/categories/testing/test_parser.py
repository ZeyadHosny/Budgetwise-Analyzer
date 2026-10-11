import unittest

from budgetwise.cleaning.categories import normalize_category


class TestCategoryParser(unittest.TestCase):

    # Food
    def test_food_exact(self):
        self.assertEqual(
            normalize_category("Food"),
            ("Food", None)
        )

    def test_food_lowercase(self):
        self.assertEqual(
            normalize_category("food"),
            ("Food", "CATEGORY_NORMALIZED")
        )

    def test_food_uppercase(self):
        self.assertEqual(
            normalize_category("FOOD"),
            ("Food", "CATEGORY_NORMALIZED")
        )

    def test_food_plural(self):
        self.assertEqual(
            normalize_category("Foods"),
            ("Food", "CATEGORY_NORMALIZED")
        )

    def test_food_typo_fod(self):
        self.assertEqual(
            normalize_category("Fod"),
            ("Food", "CATEGORY_NORMALIZED")
        )

    def test_food_typo_foodd(self):
        self.assertEqual(
            normalize_category("Foodd"),
            ("Food", "CATEGORY_NORMALIZED")
        )

    def test_food_with_spaces(self):
        self.assertEqual(
            normalize_category("  Food  "),
            ("Food", "CATEGORY_NORMALIZED")
        )

    # Rent
    def test_rent_exact(self):
        self.assertEqual(
            normalize_category("Rent"),
            ("Rent", None)
        )

    def test_rent_lowercase(self):
        self.assertEqual(
            normalize_category("rent"),
            ("Rent", "CATEGORY_NORMALIZED")
        )

    def test_rent_uppercase(self):
        self.assertEqual(
            normalize_category("RENT"),
            ("Rent", "CATEGORY_NORMALIZED")
        )

    def test_rent_typo_rentt(self):
        self.assertEqual(
            normalize_category("Rentt"),
            ("Rent", "CATEGORY_NORMALIZED")
        )

    def test_rent_typo_rnt(self):
        self.assertEqual(
            normalize_category("Rnt"),
            ("Rent", "CATEGORY_NORMALIZED")
        )

    # Transportation
    def test_travel_exact(self):
        self.assertEqual(
            normalize_category("Travel"),
            ("Transportation", "CATEGORY_NORMALIZED")
        )

    def test_travel_lowercase(self):
        self.assertEqual(
            normalize_category("travel"),
            ("Transportation", "CATEGORY_NORMALIZED")
        )

    def test_travel_uppercase(self):
        self.assertEqual(
            normalize_category("TRAVEL"),
            ("Transportation", "CATEGORY_NORMALIZED")
        )

    def test_travel_typo_traval(self):
        self.assertEqual(
            normalize_category("Traval"),
            ("Transportation", "CATEGORY_NORMALIZED")
        )

    def test_travel_typo_travl(self):
        self.assertEqual(
            normalize_category("Travl"),
            ("Transportation", "CATEGORY_NORMALIZED")
        )

    # Entertainment
    def test_entertainment_exact(self):
        self.assertEqual(
            normalize_category("Entertainment"),
            ("Entertainment", None)
        )

    def test_entertainment_lowercase(self):
        self.assertEqual(
            normalize_category("entertainment"),
            ("Entertainment", "CATEGORY_NORMALIZED")
        )

    def test_entertainment_typo_enterain(self):
        self.assertEqual(
            normalize_category("Entertain"),
            ("Entertainment", "CATEGORY_NORMALIZED")
        )

    def test_entertainment_typo_entrtnmnt(self):
        self.assertEqual(
            normalize_category("Entrtnmnt"),
            ("Entertainment", "CATEGORY_NORMALIZED")
        )

    # Utilities
    def test_utilities_exact(self):
        self.assertEqual(
            normalize_category("Utilities"),
            ("Utilities", None)
        )

    def test_utilities_lowercase(self):
        self.assertEqual(
            normalize_category("utilities"),
            ("Utilities", "CATEGORY_NORMALIZED")
        )

    def test_utility_variant(self):
        self.assertEqual(
            normalize_category("Utility"),
            ("Utilities", "CATEGORY_NORMALIZED")
        )

    def test_utilities_typo_utilties(self):
        self.assertEqual(
            normalize_category("Utilties"),
            ("Utilities", "CATEGORY_NORMALIZED")
        )

    def test_utilities_typo_utlities(self):
        self.assertEqual(
            normalize_category("Utlities"),
            ("Utilities", "CATEGORY_NORMALIZED")
        )

    # Education
    def test_education_exact(self):
        self.assertEqual(
            normalize_category("Education"),
            ("Education", None)
        )

    def test_education_lowercase(self):
        self.assertEqual(
            normalize_category("education"),
            ("Education", "CATEGORY_NORMALIZED")
        )

    def test_education_typo(self):
        self.assertEqual(
            normalize_category("Educaton"),
            ("Education", "CATEGORY_NORMALIZED")
        )

    def test_education_abbreviation(self):
        self.assertEqual(
            normalize_category("EDU"),
            ("Education", "CATEGORY_NORMALIZED")
        )

    # Healthcare
    def test_health_exact(self):
        self.assertEqual(
            normalize_category("Health"),
            ("Healthcare", "CATEGORY_NORMALIZED")
        )

    def test_health_lowercase(self):
        self.assertEqual(
            normalize_category("health"),
            ("Healthcare", "CATEGORY_NORMALIZED")
        )

    def test_health_uppercase(self):
        self.assertEqual(
            normalize_category("HEALTH"),
            ("Healthcare", "CATEGORY_NORMALIZED")
        )

    def test_health_typo(self):
        self.assertEqual(
            normalize_category("Helth"),
            ("Healthcare", "CATEGORY_NORMALIZED")
        )

    # Savings
    def test_savings_exact(self):
        self.assertEqual(
            normalize_category("Savings"),
            ("Savings", None)
        )

    def test_savings_lowercase(self):
        self.assertEqual(
            normalize_category("savings"),
            ("Savings", "CATEGORY_NORMALIZED")
        )

    def test_savings_uppercase(self):
        self.assertEqual(
            normalize_category("SAVINGS"),
            ("Savings", "CATEGORY_NORMALIZED")
        )

    def test_saving_variant(self):
        self.assertEqual(
            normalize_category("Saving"),
            ("Savings", "CATEGORY_NORMALIZED")
        )

    # Other
    def test_other_exact(self):
        self.assertEqual(
            normalize_category("Other"),
            ("Other", None)
        )

    def test_others_variant(self):
        self.assertEqual(
            normalize_category("Others"),
            ("Other", "CATEGORY_NORMALIZED")
        )

    def test_others_lowercase(self):
        self.assertEqual(
            normalize_category("others"),
            ("Other", "CATEGORY_NORMALIZED")
        )

    def test_others_uppercase(self):
        self.assertEqual(
            normalize_category("OTHERS"),
            ("Other", "CATEGORY_NORMALIZED")
        )

    def test_misc_variant(self):
        self.assertEqual(
            normalize_category("Misc"),
            ("Other", "CATEGORY_NORMALIZED")
        )

    # Exact categories
    def test_freelance(self):
        self.assertEqual(
            normalize_category("Freelance"),
            ("Freelance", None)
        )

    def test_investment(self):
        self.assertEqual(
            normalize_category("Investment"),
            ("Investment", None)
        )

    def test_bonus(self):
        self.assertEqual(
            normalize_category("Bonus"),
            ("Bonus", None)
        )

    def test_salary(self):
        self.assertEqual(
            normalize_category("Salary"),
            ("Salary", None)
        )

    # Missing
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

    # Unknown
    def test_unknown_category(self):
        self.assertEqual(
            normalize_category("CarPayment"),
            ("Uncategorized", "UNKNOWN_CATEGORY")
        )


if __name__ == "__main__":
    unittest.main()
