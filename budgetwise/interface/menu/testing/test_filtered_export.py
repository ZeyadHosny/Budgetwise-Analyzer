import sys
import unittest
from pathlib import Path
from unittest.mock import patch

IMPLEMENTATION_PATH = Path(__file__).resolve().parent.parent / "implementation"
sys.path.insert(0, str(IMPLEMENTATION_PATH))

import menu


class TestFilteredExports(unittest.TestCase):
    def setUp(self):
        self.selected = {
            "transaction_id": "E1",
            "user_id": "U1",
            "date": "2026-01-05",
            "transaction_type": "Expense",
            "category": "Food",
            "amount": 50.0,
            "original_currency": "plain",
        }
        self.other = {
            **self.selected,
            "transaction_id": "E2",
            "date": "2026-02-05",
            "category": "Rent",
            "amount": 90.0,
        }
        self.result = {
            "records": [self.selected, self.other],
            "transactions": [self.selected],
            "counts": {"input": 2, "valid": 2, "returned": 1},
            "timings": {},
            "error": None,
        }
        self.pipeline_filters = []

    def run_with_filters(self, inputs):
        def pipeline_run(dataset, **filters):
            self.pipeline_filters.append(filters)
            return self.result

        with patch("builtins.input", side_effect=inputs), \
             patch.object(menu, "export_cleaned", return_value=Path("clean.csv")) as csv_export, \
             patch.object(menu, "export_summary", return_value=Path("summary.json")) as json_export:
            menu.run_menu(pipeline_run=pipeline_run, dataset="sample.csv")
        return csv_export, json_export

    def test_date_range_exports_only_selected_transactions(self):
        csv_export, json_export = self.run_with_filters(
            ["2", "2026-01-01", "2026-01-31", "5"]
        )

        self.assertEqual(self.pipeline_filters, [{
            "start": "2026-01-01", "end": "2026-01-31",
        }])
        self.assertEqual(csv_export.call_args.args[0], [self.selected])
        self.assertEqual(json_export.call_args.args[0]["selection"], {
            "type": "date_range", "start": "2026-01-01", "end": "2026-01-31",
        })
        self.assertEqual(json_export.call_args.args[0]["totals"]["expenses"], 50.0)

    def test_category_exports_only_selected_transactions(self):
        csv_export, json_export = self.run_with_filters(["3", "Food", "5"])

        self.assertEqual(self.pipeline_filters, [{"category": "Food"}])
        self.assertEqual(csv_export.call_args.args[0], [self.selected])
        self.assertEqual(json_export.call_args.args[0]["selection"], {
            "type": "category", "category": "Food",
        })
        self.assertEqual(json_export.call_args.args[0]["totals"]["expenses"], 50.0)


if __name__ == "__main__":
    unittest.main()
