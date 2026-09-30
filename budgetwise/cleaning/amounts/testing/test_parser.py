import csv
import unittest
from pathlib import Path

from budgetwise.cleaning.amounts import parse_amount


class TestParseAmount(unittest.TestCase):
    def test_required_cases(self):
        fixture_path = Path(__file__).with_name("fixtures") / "amount_cases.csv"
        with fixture_path.open("r", newline="", encoding="utf-8") as fixture_file:
            reader = csv.DictReader(fixture_file)
            for row in reader:
                raw = row["raw_input"]
                expected_value = row["expected_value"]
                expected_symbol = row["expected_symbol"]
                expected_reason = row["expected_reason"]

                if expected_value == "":
                    expected_value = None
                else:
                    expected_value = float(expected_value)

                if expected_symbol == "":
                    expected_symbol = None

                if expected_reason == "":
                    expected_reason = None

                actual = parse_amount(raw)
                self.assertEqual(actual, (expected_value, expected_symbol, expected_reason))

    def test_never_raises(self):
        samples = [
            "",
            "abc",
            "-5891",
            "₹-5891",
            "999999999",
            "100000000",
            "Rs.5638",
            "6602 INR",
            "5891",
        ]

        for sample in samples:
            try:
                parse_amount(sample)
            except Exception as exc:  # pragma: no cover - this is intentionally defensive
                self.fail(f"parse_amount raised on {sample!r}: {exc}")


if __name__ == "__main__":
    unittest.main()
