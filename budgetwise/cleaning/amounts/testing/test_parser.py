import csv
import unittest
import os
from budgetwise.cleaning.amounts import parse_amount


class TestParseAmount(unittest.TestCase):

    def test_amounts_from_csv(self):
        fixture_path = os.path.join(
        os.path.dirname(__file__),
        "fixtures",
        "amount_cases.csv"
        )
        
        with open(fixture_path, "r", newline="", encoding="utf-8") as file:
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


if __name__ == "__main__":
    unittest.main()