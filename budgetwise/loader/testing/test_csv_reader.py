import os
import unittest

from budgetwise.loader.implementation.csv_reader import load_rows


FIXTURES_DIR = os.path.join(os.path.dirname(__file__), "fixtures")


class TestCSVReader(unittest.TestCase):

    def test_reads_valid_rows(self):
        filename = os.path.join(FIXTURES_DIR, "valid.csv")

        rows = list(load_rows(filename))

        self.assertEqual(len(rows), 3)

        # Check line numbers
        self.assertEqual(rows[0][0], 2)
        self.assertEqual(rows[1][0], 3)
        self.assertEqual(rows[2][0], 4)

        # Check first row
        first_row = rows[0][1]

        self.assertEqual(first_row["transaction_id"], "T001")
        self.assertEqual(first_row["user_id"], "U001")
        self.assertEqual(first_row["date"], "2023-01-01")
        self.assertEqual(first_row["transaction_type"], "Expense")
        self.assertEqual(first_row["category"], "Food")
        self.assertEqual(first_row["amount"], "25.50")
        self.assertEqual(first_row["payment_mode"], "card")
        self.assertEqual(first_row["location"], "Bowling Green")
        self.assertEqual(first_row["notes"], "Lunch")

    def test_short_row_is_still_yielded(self):
        filename = os.path.join(FIXTURES_DIR, "malformed_rows.csv")

        rows = list(load_rows(filename))

        self.assertEqual(len(rows), 1)

        line_no, row = rows[0]

        self.assertEqual(line_no, 2)

        self.assertEqual(row["transaction_id"], "T100")
        self.assertEqual(row["user_id"], "U100")
        self.assertEqual(row["date"], "2023-01-01")
        self.assertEqual(row["transaction_type"], "Expense")

        # Missing fields should become empty strings
        self.assertEqual(row["category"], "")
        self.assertEqual(row["amount"], "")
        self.assertEqual(row["payment_mode"], "")
        self.assertEqual(row["location"], "")
        self.assertEqual(row["notes"], "")

    def test_bad_header_raises_value_error(self):
        filename = os.path.join(FIXTURES_DIR, "bad_header.csv")

        with self.assertRaises(ValueError):
            list(load_rows(filename))

    def test_missing_file_raises_file_not_found_error(self):
        filename = os.path.join(FIXTURES_DIR, "does_not_exist.csv")

        with self.assertRaises(FileNotFoundError):
            list(load_rows(filename))


if __name__ == "__main__":
    unittest.main()