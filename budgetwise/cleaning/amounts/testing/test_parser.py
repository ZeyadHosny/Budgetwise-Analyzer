"""Tests for formatted amount parsing."""

import unittest

from budgetwise.cleaning.amounts import parse_amount
from budgetwise.errorlog.implementation.reason_codes import Reason


class TestParseAmount(unittest.TestCase):
    def test_parses_plain_and_formatted_amounts(self):
        cases = (
            ("5,891", (5891.0, "plain", None)),
            ("₹5891", (5891.0, "₹", None)),
            ("$5863", (5863.0, "$", None)),
            ("Rs.5638", (5638.0, "Rs.", None)),
            ("6602 INR", (6602.0, "INR", None)),
        )
        for raw, expected in cases:
            with self.subTest(raw=raw):
                self.assertEqual(parse_amount(raw), expected)

    def test_discards_negative_sign_for_magnitude(self):
        for raw, expected in (
            ("-5891", (5891.0, "plain", None)),
            ("₹-5891", (5891.0, "₹", None)),
            ("Rs.-5891", (5891.0, "Rs.", None)),
            ("-5891 INR", (5891.0, "INR", None)),
        ):
            with self.subTest(raw=raw):
                self.assertEqual(parse_amount(raw), expected)

    def test_reports_missing_amount(self):
        for raw in (None, "", "   "):
            with self.subTest(raw=raw):
                self.assertEqual(parse_amount(raw), (None, None, Reason.MISSING_AMOUNT))

    def test_reports_unrecognized_format(self):
        for raw in ("abc", "1-2", "$", "nan", "inf"):
            with self.subTest(raw=raw):
                self.assertEqual(
                    parse_amount(raw),
                    (None, None, Reason.UNRECOGNIZED_AMOUNT_FORMAT),
                )

    def test_rejects_amounts_at_or_above_sentinel_threshold(self):
        for raw in ("100000000", "999999999"):
            with self.subTest(raw=raw):
                self.assertEqual(
                    parse_amount(raw),
                    (None, None, Reason.SENTINEL_AMOUNT),
                )

    def test_accepts_amount_below_sentinel_threshold(self):
        self.assertEqual(parse_amount("99999999.99"), (99999999.99, "plain", None))


if __name__ == "__main__":
    unittest.main()
