import unittest

from budgetwise.cleaning.categories import normalize_category


class TestCategoryWhitespace(unittest.TestCase):

    def test_surrounding_whitespace_is_reported(self):
        cases = [
            " Food",
            "Food ",
            " Food ",
            "\tFood\n"
        ]

        for raw in cases:
            with self.subTest(raw_input=raw):
                self.assertEqual(
                    normalize_category(raw),
                    ("Food", "CATEGORY_NORMALIZED")
                )

    def test_canonical_category_has_no_reason(self):
        self.assertEqual(
            normalize_category("Food"),
            ("Food", None)
        )

    def test_blank_category_remains_uncategorized(self):
        self.assertEqual(
            normalize_category("   "),
            ("Uncategorized", "CATEGORY_UNCATEGORIZED")
        )


if __name__ == "__main__":
    unittest.main()
