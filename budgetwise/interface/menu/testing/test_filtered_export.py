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
            "summary": {
                "scope": "transactions selected by menu query",
                "selection": {"type": "all"},
                "selected_transactions": 1,
                "counts": {"input": 2, "valid": 2},
                "timings": {},
                "total_breakdown": {
                    "totals": {"income": 0.0, "expenses": 50.0, "net": -50.0},
                    "top_categories": [("Food", 50.0)],
                    "largest_expenses": [self.selected],
                    "budget_by_category": [],
                    "account_breakdown": {},
                    "chart_data": [{"category": "Food", "expenses": 50.0}],
                },
                "monthly_breakdown": {
                    "months": [],
                    "chart_data": [{"month": "2026-01", "expenses": 50.0}],
                },
                "category_breakdown": [],
            },
            "error": None,
        }
        self.pipeline_filters = []

    def run_with_filters(self, inputs):
        def pipeline_run(dataset, **filters):
            self.pipeline_filters.append(filters)
            if "category" in filters:
                self.result["summary"]["selection"] = {
                    "type": "category", "category": filters["category"],
                }
            elif "start" in filters or "end" in filters:
                self.result["summary"]["selection"] = {
                    "type": "date_range", **filters,
                }
            return self.result

        with patch("builtins.input", side_effect=inputs), \
             patch.object(menu, "export_cleaned", return_value=Path("clean.csv")) as csv_export, \
             patch.object(menu, "export_summary", return_value=Path("summary.json")) as json_export:
            menu.run_menu(pipeline_run=pipeline_run, dataset="sample.csv")
        return csv_export, json_export

    def test_date_range_exports_only_selected_transactions(self):
        csv_export, json_export = self.run_with_filters(
            ["2", "2026-01-05", "2026-01-20", "5"]
        )

        self.assertEqual(self.pipeline_filters, [{
            "start": "2026-01-05", "end": "2026-01-20",
        }])
        self.assertEqual(csv_export.call_args.args[0], [self.selected])
        self.assertEqual(json_export.call_args.args[0]["selection"], {
            "type": "date_range", "start": "2026-01-05", "end": "2026-01-20",
        })
        self.assertEqual(
            json_export.call_args.args[0]["total_breakdown"]["totals"]["expenses"],
            50.0,
        )

    def test_category_exports_only_selected_transactions(self):
        csv_export, json_export = self.run_with_filters(
            ["3", "Food", "5"]
        )

        self.assertEqual(self.pipeline_filters, [{"category": "Food"}])
        self.assertEqual(csv_export.call_args.args[0], [self.selected])
        self.assertEqual(json_export.call_args.args[0]["selection"], {
            "type": "category", "category": "Food",
        })
        self.assertEqual(
            json_export.call_args.args[0]["total_breakdown"]["totals"]["expenses"],
            50.0,
        )


if __name__ == "__main__":
    unittest.main()
