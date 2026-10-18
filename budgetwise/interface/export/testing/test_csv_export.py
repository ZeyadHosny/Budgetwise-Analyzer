import csv
import tempfile
import unittest
from datetime import datetime
from pathlib import Path
from unittest.mock import patch

from budgetwise.interface.export import export_cleaned
from budgetwise.models import ExpenseTransaction


class TestExportCleaned(unittest.TestCase):
    def setUp(self):
        self.temporary_directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary_directory.cleanup)
        self.output_root = Path(self.temporary_directory.name)
        self.when = datetime(2026, 10, 12, 14, 22, 5)

    def test_writes_dated_excel_compatible_csv(self):
        record = {
            "transaction_id": "T4999",
            "user_id": "U018",
            "date": "2023-07-14",
            "transaction_type": "Expense",
            "category": "Food",
            "amount": 5891,
            "original_currency": "₹",
            "payment_mode": "Card",
        }
        with patch("budgetwise.interface.export.implementation.csv_export.OUTPUT_ROOT",
                   self.output_root):
            output_path = export_cleaned(
                [record], "data/raw/budgetwise_finance_dataset.csv", self.when
            )

        self.assertEqual(
            output_path,
            self.output_root / "cleaned" /
            "cleaned_budgetwise_finance_dataset_2026-10-12.csv",
        )
        self.assertTrue(output_path.read_bytes().startswith(b"\xef\xbb\xbf"))
        with output_path.open(encoding="utf-8-sig", newline="") as csv_file:
            rows = list(csv.DictReader(csv_file))
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["amount"], "5891.00")
        self.assertEqual(rows[0]["original_currency"], "₹")

    def test_accepts_transaction_objects(self):
        transaction = ExpenseTransaction(
            "T1", "U1", "2024-01-02", "Food", 12.5,
            original_currency="₹",
        )
        with patch("budgetwise.interface.export.implementation.csv_export.OUTPUT_ROOT",
                   self.output_root):
            output_path = export_cleaned([transaction], "sample", self.when)
        with output_path.open(encoding="utf-8-sig", newline="") as csv_file:
            row = next(csv.DictReader(csv_file))
        self.assertEqual(row["amount"], "12.50")
        self.assertEqual(row["original_currency"], "₹")

    def test_empty_input_writes_header_only(self):
        with patch("budgetwise.interface.export.implementation.csv_export.OUTPUT_ROOT",
                   self.output_root):
            output_path = export_cleaned([], "sample", self.when)
        with output_path.open(encoding="utf-8-sig", newline="") as csv_file:
            reader = csv.DictReader(csv_file)
            self.assertEqual(reader.fieldnames, [
                "transaction_id", "user_id", "date", "transaction_type",
                "category", "amount", "original_currency",
            ])
            self.assertEqual(list(reader), [])


if __name__ == "__main__":
    unittest.main()