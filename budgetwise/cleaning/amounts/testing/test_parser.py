import csv
import os
import unittest

from budgetwise.cleaning.amounts import parse_amount
from budgetwise.errorlog import Reason


class TestParseAmount(unittest.TestCase):

    def test_amounts_from_csv(self):
        fixture_path = os.path.join(
            os.path.dirname(__file__),
            "fixtures",
            "amount_cases.csv"
        )

        with open(
            fixture_path,
            "r",
            newline="",
            encoding="utf-8"
        ) as file:
            reader = csv.DictReader(file)

            for row in reader:
                with self.subTest(raw_input=row["raw_input"]):

                    # Expected amount
                    if row["expected_value"] == "":
                        expected_value = None
                    else:
                        expected_value = float(row["expected_value"])

                    # Expected currency symbol
                    if row["expected_symbol"] == "":
                        expected_symbol = None
                    else:
                        expected_symbol = row["expected_symbol"]

                    # Expected error reason
                    if row["expected_reason"] == "":
                        expected_reason = None
                    else:
                        expected_reason = row["expected_reason"]

                    expected = (
                        expected_value,
                        expected_symbol,
                        expected_reason
                    )

                    actual = parse_amount(row["raw_input"])

                    self.assertEqual(
                        actual,
                        expected,
                        f"Failed for input: {row['raw_input']!r}"
                    )

    def test_rejects_malformed_amounts(self):
        cases = [
            "1-2",
            "--100",
            "-$-100",
            "1,2",
            "12,34",
            "$100 INR",
            "abc"
        ]

        for raw in cases:
            with self.subTest(raw_input=raw):
                self.assertEqual(
                    parse_amount(raw),
                    (
                        None,
                        None,
                        Reason.UNRECOGNIZED_AMOUNT_FORMAT
                    )
                )

    def test_rejects_nonfinite_amounts(self):
        cases = [
            "NaN",
            "nan",
            "inf",
            "-inf",
            "Infinity"
        ]

        for raw in cases:
            with self.subTest(raw_input=raw):
                self.assertEqual(
                    parse_amount(raw),
                    (
                        None,
                        None,
                        Reason.UNRECOGNIZED_AMOUNT_FORMAT
                    )
                )

    def test_negative_amounts_become_magnitudes(self):
        cases = [
            ("-1000", (1000.0, None, None)),
            ("-$1000", (1000.0, "$", None)),
            ("$-1000", (1000.0, "$", None)),
            ("-1000 INR", (1000.0, "INR", None))
        ]

        for raw, expected in cases:
            with self.subTest(raw_input=raw):
                self.assertEqual(
                    parse_amount(raw),
                    expected
                )

    def test_supported_currency_labels(self):
        cases = [
            ("₹5070", (5070.0, "₹", None)),
            ("$4262", (4262.0, "$", None)),
            ("Rs.828", (828.0, "Rs.", None)),
            ("5107 INR", (5107.0, "INR", None))
        ]

        for raw, expected in cases:
            with self.subTest(raw_input=raw):
                self.assertEqual(
                    parse_amount(raw),
                    expected
                )

    def test_valid_numeric_formats(self):
        cases = [
            ("0", (0.0, None, None)),
            ("1000.50", (1000.5, None, None)),
            ("1,000.50", (1000.5, None, None)),
            (" 1000 ", (1000.0, None, None))
        ]

        for raw, expected in cases:
            with self.subTest(raw_input=raw):
                self.assertEqual(
                    parse_amount(raw),
                    expected
                )

    def test_sentinel_boundary(self):
        self.assertEqual(
            parse_amount("99999999.99"),
            (99999999.99, None, None)
        )

        cases = [
            "100000000",
            "-100000000",
            "999999999"
        ]

        for raw in cases:
            with self.subTest(raw_input=raw):
                self.assertEqual(
                    parse_amount(raw),
                    (
                        None,
                        None,
                        Reason.SENTINEL_AMOUNT
                    )
                )

    def test_missing_amounts(self):
        cases = [
            None,
            "",
            "   "
        ]

        for raw in cases:
            with self.subTest(raw_input=raw):
                self.assertEqual(
                    parse_amount(raw),
                    (
                        None,
                        None,
                        Reason.MISSING_AMOUNT
                    )
                )

    def test_unsupported_input_types(self):
        cases = [
            100,
            10.5,
            [],
            {}
        ]

        for raw in cases:
            with self.subTest(raw_input=raw):
                self.assertEqual(
                    parse_amount(raw),
                    (
                        None,
                        None,
                        Reason.UNRECOGNIZED_AMOUNT_FORMAT
                    )
                )


if __name__ == "__main__":
    unittest.main()
