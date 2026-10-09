import unittest

from budgetwise.cleaning.amounts import clean_amount
from budgetwise.errorlog import Reason


class TestCleanAmount(unittest.TestCase):

    def test_plain_amount_has_no_issues(self):
        self.assertEqual(
            clean_amount("1000"),
            (1000.0, None, [])
        )

    def test_negative_amount_has_correction_reason(self):
        self.assertEqual(
            clean_amount("-1000"),
            (
                1000.0,
                None,
                [Reason.AMOUNT_NEGATIVE_TO_MAGNITUDE]
            )
        )

    def test_formatting_has_correction_reason(self):
        cases = [
            ("$1000", 1000.0, "$"),
            ("₹1000", 1000.0, "₹"),
            ("Rs.1000", 1000.0, "Rs."),
            ("1000 INR", 1000.0, "INR"),
            ("1,000", 1000.0, None),
            (" 1000 ", 1000.0, None),
            ("+1000", 1000.0, None)
        ]

        for raw, amount, symbol in cases:
            with self.subTest(raw_input=raw):
                self.assertEqual(
                    clean_amount(raw),
                    (
                        amount,
                        symbol,
                        [Reason.AMOUNT_FORMAT_NORMALIZED]
                    )
                )

    def test_multiple_corrections_are_preserved(self):
        self.assertEqual(
            clean_amount("-$1,000"),
            (
                1000.0,
                "$",
                [
                    Reason.AMOUNT_NEGATIVE_TO_MAGNITUDE,
                    Reason.AMOUNT_FORMAT_NORMALIZED
                ]
            )
        )

    def test_missing_amount_keeps_error_reason(self):
        for raw in [None, "", "   "]:
            with self.subTest(raw_input=raw):
                self.assertEqual(
                    clean_amount(raw),
                    (None, None, [Reason.MISSING_AMOUNT])
                )

    def test_invalid_amount_keeps_error_reason(self):
        for raw in ["1-2", "NaN", "inf", "abc", 100]:
            with self.subTest(raw_input=raw):
                self.assertEqual(
                    clean_amount(raw),
                    (
                        None,
                        None,
                        [Reason.UNRECOGNIZED_AMOUNT_FORMAT]
                    )
                )

    def test_sentinel_keeps_only_exclusion_reason(self):
        self.assertEqual(
            clean_amount("-$100,000,000"),
            (None, None, [Reason.SENTINEL_AMOUNT])
        )


if __name__ == "__main__":
    unittest.main()
