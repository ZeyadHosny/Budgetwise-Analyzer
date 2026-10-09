import csv
import os
import tempfile
import unittest

from budgetwise.loader import load_rows, validate_header


HEADER = [
    "transaction_id",
    "user_id",
    "date",
    "transaction_type",
    "category",
    "amount",
    "payment_mode",
    "location",
    "notes"
]


class TestHeaderValidation(unittest.TestCase):

    def test_valid_header_is_accepted(self):
        self.assertIsNone(validate_header(HEADER))

    def test_duplicate_column_is_rejected(self):
        header = HEADER + ["amount"]

        with self.assertRaisesRegex(
            ValueError,
            "duplicate columns"
        ):
            validate_header(header)

    def test_missing_column_is_rejected(self):
        header = [
            column for column in HEADER
            if column != "amount"
        ]

        with self.assertRaisesRegex(
            ValueError,
            "missing columns"
        ):
            validate_header(header)

    def test_unexpected_column_is_rejected(self):
        header = HEADER + ["merchant"]

        with self.assertRaisesRegex(
            ValueError,
            "unexpected columns"
        ):
            validate_header(header)

    def test_missing_header_is_rejected(self):
        with self.assertRaises(ValueError):
            validate_header(None)

    def test_loader_rejects_duplicate_header(self):
        with tempfile.TemporaryDirectory() as directory:
            filename = os.path.join(directory, "duplicate.csv")

            with open(
                filename,
                "w",
                newline="",
                encoding="utf-8"
            ) as file:
                writer = csv.writer(file)
                writer.writerow(HEADER + ["amount"])
                writer.writerow([
                    "T001", "U001", "2023-01-01", "Expense",
                    "Food", "25", "Cash", "Pune", "Lunch", "99"
                ])

            with self.assertRaisesRegex(
                ValueError,
                "duplicate columns"
            ):
                list(load_rows(filename))


if __name__ == "__main__":
    unittest.main()
