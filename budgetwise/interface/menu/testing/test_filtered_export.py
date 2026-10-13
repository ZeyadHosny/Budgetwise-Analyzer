import sys
import unittest
from pathlib import Path
from unittest.mock import patch

from budgetwise.analysis.budgets import BudgetResult

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

        with patch.object(menu, "compare_to_budget", return_value=[
                 BudgetResult("Food", 100.0, 50.0, "under", -50.0)
             ]) as budget_compare, \
             patch("builtins.input", side_effect=inputs), \
             patch.object(menu, "export_cleaned", return_value=Path("clean.csv")) as csv_export, \
             patch.object(menu, "export_summary", return_value=Path("summary.json")) as json_export:
            menu.run_menu(pipeline_run=pipeline_run, dataset="sample.csv")
        return csv_export, json_export, budget_compare

    def test_date_range_exports_only_selected_transactions(self):
        csv_export, json_export, budget_compare = self.run_with_filters(
            ["2", "2026-01-05", "2026-01-20", "5"]
        )

        self.assertEqual(self.pipeline_filters, [{
            "start": "2026-01-05", "end": "2026-01-20",
        }])
        self.assertEqual(csv_export.call_args.args[0], [self.selected])
        self.assertEqual(json_export.call_args.args[0]["selection"], {
            "type": "date_range", "start": "2026-01-05", "end": "2026-01-20",
        })
        self.assertEqual(json_export.call_args.args[0]["totals"]["expenses"], 50.0)
        budget_compare.assert_called_once_with([self.selected], "2026", "01")
        comparison = json_export.call_args.args[0]["budget_comparisons"][0]
        self.assertFalse(comparison["period"]["full_month"])
        self.assertEqual(comparison["period"]["start"], "2026-01-05")
        self.assertEqual(comparison["period"]["end"], "2026-01-20")
        self.assertEqual(comparison["categories"][0]["status"], "under")

    def test_category_exports_only_selected_transactions(self):
        csv_export, json_export, budget_compare = self.run_with_filters(
            ["3", "Food", "5"]
        )

        self.assertEqual(self.pipeline_filters, [{"category": "Food"}])
        self.assertEqual(csv_export.call_args.args[0], [self.selected])
        self.assertEqual(json_export.call_args.args[0]["selection"], {
            "type": "category", "category": "Food",
        })
        self.assertEqual(json_export.call_args.args[0]["totals"]["expenses"], 50.0)
        budget_compare.assert_called_once_with([self.selected], "2026", "01")
        budget_comparisons = json_export.call_args.args[0]["budget_comparisons"]
        self.assertEqual(len(budget_comparisons[0]["categories"]), 1)
        self.assertEqual(budget_comparisons[0]["categories"][0]["category"], "Food")


if __name__ == "__main__":
    unittest.main()
