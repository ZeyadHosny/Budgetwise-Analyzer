import json
import tempfile
import unittest
from datetime import date, datetime
from pathlib import Path
from unittest.mock import patch

from budgetwise.interface.export import export_summary


class TestExportSummary(unittest.TestCase):
    def setUp(self):
        self.temporary_directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary_directory.cleanup)
        self.output_root = Path(self.temporary_directory.name)
        self.when = datetime(2026, 10, 12, 14, 22, 5)

    def test_writes_dated_summary_with_dataset_and_timestamp(self):
        summary = {
            "counts": {"input": 10, "valid": 8},
            "totals": {"income": 100.0, "expenses": 50.0},
            "top_categories": [("Food", 40.0)],
            "finished": date(2026, 10, 12),
            "output_path": Path("output/cleaned.csv"),
        }
        with patch("budgetwise.interface.export.implementation.json_export.OUTPUT_ROOT",
                   self.output_root):
            output_path = export_summary(
                summary, "data/raw/budgetwise_finance_dataset.csv", self.when
            )

        self.assertEqual(
            output_path,
            self.output_root / "summaries" /
            "summary_budgetwise_finance_dataset_2026-10-12.json",
        )
        with output_path.open(encoding="utf-8") as json_file:
            document = json.load(json_file)
        self.assertEqual(document["dataset"], "budgetwise_finance_dataset.csv")
        self.assertEqual(document["generated"], "2026-10-12T14:22:05")
        self.assertEqual(document["finished"], "2026-10-12")
        self.assertEqual(document["output_path"], str(Path("output/cleaned.csv")))

    def test_rejects_non_dictionary_summary(self):
        with self.assertRaises(TypeError):
            export_summary([], "sample", self.when)


if __name__ == "__main__":
    unittest.main()