"""Tests for the requested amount parser implementation."""

import unittest

from budgetwise.cleaning.categories.implementation import parse_amount
from budgetwise.errorlog.implementation.reason_codes import Reason


class TestParseAmount(unittest.TestCase):
    def test_parses_supported_currency_labels(self):
        cases = (
            ("₹5891", (5891.0, "₹", None)),
            ("$5891", (5891.0, "$", None)),
            ("Rs.5638", (5638.0, "Rs.", None)),
            ("6602 INR", (6602.0, "INR", None)),
            ("5891", (5891.0, None, None)),
        )
        for raw, expected in cases:
            with self.subTest(raw=raw):
                self.assertEqual(parse_amount(raw), expected)

    def test_removes_commas_and_negative_sign(self):
        self.assertEqual(parse_amount("₹-5,891"), (5891.0, "₹", None))

    def test_returns_missing_reason(self):
        for raw in ("", "   "):
            with self.subTest(raw=raw):
                self.assertEqual(parse_amount(raw), (None, None, Reason.MISSING_AMOUNT))

    def test_returns_unrecognized_format_reason(self):
        self.assertEqual(
            parse_amount("abc"),
            (None, None, Reason.UNRECOGNIZED_AMOUNT_FORMAT),
        )

    def test_returns_sentinel_reason(self):
        self.assertEqual(
            parse_amount("100000000"),
            (None, None, Reason.SENTINEL_AMOUNT),
        )


if __name__ == "__main__":
    unittest.main()
