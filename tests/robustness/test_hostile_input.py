"""
Robustness tests: the program must not crash on malformed input (section 4.1).

Each test cleans a small CSV with clean_file() and checks that:
  * a result is returned instead of an exception
  * every row is accounted for: input = valid + skipped + duplicates
  * every kept row follows the section 4.5 conventions

Tests marked @unittest.expectedFailure record known defects. They pass while
the defect exists. Remove the decorator once the defect is fixed.
"""

import os
import re
import shutil
import tempfile
import unittest
from pathlib import Path

from budgetwise.errorlog import ErrorLog
from budgetwise.pipeline import clean_file

REPO = Path(__file__).resolve().parents[2]
DATASET = REPO / "data" / "raw" / "budgetwise_finance_dataset.csv"

HEADER = ("transaction_id,user_id,date,transaction_type,category,amount,"
          "payment_mode,location,notes\n")
GOOD_ROW = "T1001,U001,2023-04-25,Expense,Food,100,Card,Pune,Lunch\n"

SENTINEL_LIMIT = 100_000_000
DATE_PATTERN = re.compile(r"^\d{4}-\d{2}-\d{2}$")
APPROVED_CATEGORIES = {
    "Food", "Rent", "Transportation", "Entertainment", "Utilities", "Education",
    "Healthcare", "Savings", "Other", "Freelance", "Investment", "Bonus",
    "Salary", "Uncategorized",
}


def amount_row(number, amount):
    """One otherwise-valid row with the given raw amount text."""
    return f"T{number},U001,2023-01-01,Expense,Food,{amount},Card,Pune,x\n"


def date_row(number, date):
    """One otherwise-valid row with the given raw date text."""
    return f"T{number},U001,{date},Expense,Food,100,Card,Pune,x\n"


class HostileInputCase(unittest.TestCase):
    """Writes each test's CSV and log to a temporary folder."""

    def setUp(self):
        self.folder = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.folder, ignore_errors=True)

    def clean_text(self, text, encoding="utf-8"):
        """Write text to a CSV file and clean it."""
        path = os.path.join(self.folder, "input.csv")
        with open(path, "w", encoding=encoding, newline="") as file:
            file.write(text)
        return self.clean_path(path)

    def clean_path(self, path):
        """Clean a file and check the result."""
        log = ErrorLog(os.path.join(self.folder, "errors.log"))
        try:
            result = clean_file(path, log)
        finally:
            log.close()
        self.assert_survived(result)
        return result

    def assert_survived(self, result):
        """Check the result is complete and every kept row is valid."""
        self.assertIsInstance(result, dict)
        self.assertTrue(
            result["error"] is None or isinstance(result["error"], str))
        counts = result["counts"]
        self.assertEqual(
            counts["input"],
            counts["valid"] + counts["skipped"] + counts["duplicates"],
            "input = valid + skipped + duplicates does not hold",
        )
        self.assertEqual(len(result["records"]), counts["valid"])
        for record in result["records"]:
            self.assertGreaterEqual(record["amount"], 0)
            self.assertLess(record["amount"], SENTINEL_LIMIT)
            self.assertIn(record["category"], APPROVED_CATEGORIES)
            self.assertIn(record["transaction_type"], ("Expense", "Income"))
            if record["date"] is not None:
                self.assertRegex(record["date"], DATE_PATTERN)


class TestBrokenFiles(HostileInputCase):

    def test_missing_file(self):
        result = self.clean_path(os.path.join(
            self.folder, "does_not_exist.csv"))
        self.assertIsNotNone(result["error"])
        self.assertEqual(result["records"], [])

    def test_empty_file(self):
        result = self.clean_text("")
        self.assertIsNotNone(result["error"])
        self.assertEqual(result["records"], [])

    def test_header_only(self):
        result = self.clean_text(HEADER)
        self.assertIsNone(result["error"])
        self.assertEqual(result["counts"]["input"], 0)

    def test_header_missing_a_column(self):
        header = HEADER.replace(",notes", "")
        result = self.clean_text(
            header + "T1001,U001,2023-04-25,Expense,Food,100,Card,Pune\n")
        self.assertIsNotNone(result["error"])
        self.assertEqual(result["records"], [])

    def test_duplicate_header_column(self):
        result = self.clean_text(HEADER.replace("notes", "amount") + GOOD_ROW)
        self.assertIsNotNone(result["error"])

    def test_file_with_no_valid_rows(self):
        result = self.clean_text(
            HEADER + amount_row(1001, "abc") + amount_row(1002, ""))
        self.assertIsNone(result["error"])
        self.assertEqual(result["counts"]["valid"], 0)
        self.assertEqual(result["counts"]["skipped"], 2)

    @unittest.expectedFailure
    def test_file_saved_with_byte_order_mark(self):
        # Known defect (loader): a BOM at the start of the file makes the
        # header check reject the whole file.
        result = self.clean_text(HEADER + GOOD_ROW, encoding="utf-8-sig")
        self.assertIsNone(result["error"])
        self.assertEqual(result["counts"]["valid"], 1)


class TestMalformedRows(HostileInputCase):

    def test_row_with_too_few_fields_is_skipped(self):
        result = self.clean_text(
            HEADER + "T1002,U001,2023-04-25,Expense\n" + GOOD_ROW)
        self.assertEqual(result["counts"]["skipped"], 1)
        self.assertEqual(result["counts"]["valid"], 1)

    @unittest.expectedFailure
    def test_row_with_too_many_fields_is_not_kept_as_valid(self):
        # Known defect (loader): extra fields are dropped silently, so the
        # values shift and the row is kept with amount 1.0.
        row = "T1002,U001,2023-01-01,Expense,Food,Rs. 1,200,Card,Pune,x\n"
        result = self.clean_text(HEADER + row)
        self.assertEqual(result["counts"]["valid"], 0)

    def test_every_field_blank_is_skipped(self):
        result = self.clean_text(HEADER + ",,,,,,,,\n" + GOOD_ROW)
        self.assertEqual(result["counts"]["skipped"], 1)
        self.assertEqual(result["counts"]["valid"], 1)

    def test_unknown_transaction_type_is_skipped(self):
        result = self.clean_text(
            HEADER + "T1002,U001,2023-01-01,Refund,Food,100,Card,Pune,x\n")
        self.assertEqual(result["counts"]["skipped"], 1)

    @unittest.expectedFailure
    def test_blank_lines_are_not_counted_as_records(self):
        # Known defect (loader): blank lines are counted as input rows.
        result = self.clean_text(HEADER + "\n\n" + GOOD_ROW)
        self.assertEqual(result["counts"]["input"], 1)

    def test_quoted_comma_in_amount_and_notes(self):
        result = self.clean_text(
            HEADER + 'T1002,U001,2023-01-01,Expense,Food,"1,200",Card,Pune,"hello, world"\n')
        self.assertEqual(result["records"][0]["amount"], 1200.0)

    def test_non_ascii_text_does_not_crash(self):
        result = self.clean_text(
            HEADER + "T1002,U001,2023-01-01,Expense,Fööd 🍔,100,Cärd,Pünе,ñ\n")
        record = result["records"][0]
        self.assertEqual(record["category"], "Uncategorized")
        self.assertEqual(record["payment_mode"], "Unknown")
        self.assertEqual(record["location"], "Unknown")

    def test_exact_duplicate_rows_are_counted_once(self):
        result = self.clean_text(HEADER + GOOD_ROW + GOOD_ROW + GOOD_ROW)
        self.assertEqual(result["counts"]["valid"], 1)
        self.assertEqual(result["counts"]["duplicates"], 2)


class TestHostileDates(HostileInputCase):

    def test_impossible_and_unreadable_dates_keep_the_row_without_a_date(self):
        dates = ["31/02/2023", "99-99-99", "14th July", "2023-13-45", ""]
        result = self.clean_text(HEADER + "".join(
            date_row(1001 + i, d) for i, d in enumerate(dates)))
        self.assertEqual(result["counts"]["valid"], len(dates))
        self.assertTrue(
            all(record["date"] is None for record in result["records"]))


class TestHostileAmounts(HostileInputCase):

    def test_unreadable_amounts_are_skipped(self):
        for amount in ("abc", "₹₹5", "", "Rs.", "1.2.3"):
            with self.subTest(amount=amount):
                result = self.clean_text(HEADER + amount_row(1001, amount))
                self.assertEqual(result["counts"]["valid"], 0)
                self.assertEqual(result["counts"]["skipped"], 1)

    def test_sentinel_amount_never_reaches_the_records(self):
        result = self.clean_text(
            HEADER + amount_row(1001, "999999999") + GOOD_ROW)
        self.assertEqual(result["counts"]["valid"], 1)
        self.assertEqual(result["records"][0]["amount"], 100.0)

    def test_negative_amount_becomes_its_magnitude(self):
        result = self.clean_text(HEADER + amount_row(1001, "-50"))
        self.assertEqual(result["records"][0]["amount"], 50.0)

    @unittest.expectedFailure
    def test_double_minus_amount_is_rejected(self):
        # Known defect (amounts): '--5' is accepted as 5.0.
        result = self.clean_text(HEADER + amount_row(1001, "--5"))
        self.assertEqual(result["counts"]["valid"], 0)


@unittest.skipUnless(DATASET.exists(), "raw dataset not found")
class TestFullDataset(HostileInputCase):
    """The full dataset is cleaned without errors."""

    def test_full_dataset_survives_and_reconciles(self):
        result = self.clean_path(str(DATASET))
        self.assertIsNone(result["error"])
        self.assertEqual(result["counts"]["input"], 15900)


if __name__ == "__main__":
    unittest.main()
