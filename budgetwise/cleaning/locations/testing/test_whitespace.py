import unittest

from budgetwise.cleaning.locations import normalize_location


class TestLocationWhitespace(unittest.TestCase):

    def test_surrounding_whitespace_is_reported(self):
        cases = [
            " Pune",
            "Pune ",
            " Pune ",
            "\tPune\n"
        ]

        for raw in cases:
            with self.subTest(raw_input=raw):
                self.assertEqual(
                    normalize_location(raw),
                    ("Pune", "LOCATION_NORMALIZED")
                )

    def test_canonical_location_has_no_reason(self):
        self.assertEqual(
            normalize_location("Pune"),
            ("Pune", None)
        )

    def test_missing_location_remains_unknown(self):
        for raw in [None, "", "   ", "N/A"]:
            with self.subTest(raw_input=raw):
                self.assertEqual(
                    normalize_location(raw),
                    ("Unknown", "LOCATION_UNKNOWN")
                )


if __name__ == "__main__":
    unittest.main()
