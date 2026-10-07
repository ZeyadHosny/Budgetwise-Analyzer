import unittest

from budgetwise.cleaning.locations import normalize_location


class TestLocationParser(unittest.TestCase):

    def test_exact_pune(self):
        self.assertEqual(
            normalize_location("Pune"),
            ("Pune", None)
        )

    def test_uppercase_pune(self):
        self.assertEqual(
            normalize_location("PUNE"),
            ("Pune", "LOCATION_NORMALIZED")
        )

    def test_abbreviation_pune(self):
        self.assertEqual(
            normalize_location("PUN"),
            ("Pune", "LOCATION_NORMALIZED")
        )

    def test_lowercase_bangalore(self):
        self.assertEqual(
            normalize_location("bangalore"),
            ("Bangalore", "LOCATION_NORMALIZED")
        )

    def test_abbreviation_bangalore(self):
        self.assertEqual(
            normalize_location("BAN"),
            ("Bangalore", "LOCATION_NORMALIZED")
        )

    def test_abbreviation_chennai(self):
        self.assertEqual(
            normalize_location("CHE"),
            ("Chennai", "LOCATION_NORMALIZED")
        )

    def test_abbreviation_hyderabad(self):
        self.assertEqual(
            normalize_location("HYD"),
            ("Hyderabad", "LOCATION_NORMALIZED")
        )

    def test_abbreviation_jaipur(self):
        self.assertEqual(
            normalize_location("JAI"),
            ("Jaipur", "LOCATION_NORMALIZED")
        )

    def test_abbreviation_kolkata(self):
        self.assertEqual(
            normalize_location("KOL"),
            ("Kolkata", "LOCATION_NORMALIZED")
        )

    def test_abbreviation_delhi(self):
        self.assertEqual(
            normalize_location("DEL"),
            ("Delhi", "LOCATION_NORMALIZED")
        )

    def test_abbreviation_lucknow(self):
        self.assertEqual(
            normalize_location("LUC"),
            ("Lucknow", "LOCATION_NORMALIZED")
        )

    def test_abbreviation_ahmedabad(self):
        self.assertEqual(
            normalize_location("AHM"),
            ("Ahmedabad", "LOCATION_NORMALIZED")
        )

    def test_abbreviation_mumbai(self):
        self.assertEqual(
            normalize_location("MUM"),
            ("Mumbai", "LOCATION_NORMALIZED")
        )

    def test_missing_empty_string(self):
        self.assertEqual(
            normalize_location(""),
            ("Unknown", "LOCATION_UNKNOWN")
        )

    def test_missing_spaces(self):
        self.assertEqual(
            normalize_location("   "),
            ("Unknown", "LOCATION_UNKNOWN")
        )

    def test_missing_none(self):
        self.assertEqual(
            normalize_location(None),
            ("Unknown", "LOCATION_UNKNOWN")
        )

    def test_na_location(self):
        self.assertEqual(
            normalize_location("N/A"),
            ("Unknown", "LOCATION_UNKNOWN")
        )

    def test_unknown_location(self):
        self.assertEqual(
            normalize_location("UnknownCity"),
            ("Unknown", "LOCATION_UNKNOWN")
        )


if __name__ == "__main__":
    unittest.main()
