import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from budgetwise.analysis.budgets import compare_to_budget, largest_expenses
from budgetwise.analysis.budgets.implementation.limits import load_limits
from budgetwise.models import ExpenseTransaction, IncomeTransaction


def make_record(transaction_id, date, category, amount, transaction_type="Expense"):
    return {
        "transaction_id": transaction_id,
        "date": date,
        "category": category,
        "amount": amount,
        "transaction_type": transaction_type,
    }


class TestLargestExpenses(unittest.TestCase):
    def test_returns_only_expenses_largest_first(self):
        income = make_record("I1", "2024-03-01", "Salary", 10000, "Income")
        first = make_record("E1", "2024-03-01", "Food", 200)
        second = make_record("E2", "2024-03-02", "Rent", 500)
        result = largest_expenses([income, first, second], n=2)
        self.assertEqual(result, [second, first])

    def test_equal_amounts_preserve_input_order(self):
        first = make_record("E1", "2024-03-01", "Food", 100)
        second = make_record("E2", "2024-03-02", "Food", 100)
        self.assertEqual(largest_expenses([first, second]), [first, second])

    def test_rejects_invalid_result_limit(self):
        with self.assertRaises(ValueError):
            largest_expenses([], n=-1)
        with self.assertRaises(TypeError):
            largest_expenses([], n=True)


class TestBudgetComparison(unittest.TestCase):
    def setUp(self):
        self.transactions = [
            make_record("E1", "2024-03-01", "Food", 80),
            make_record("E2", "2024-03-02", "Food", 40),
            make_record("E3", "2024-03-03", "Travel", 30),
            make_record("E4", "2024-02-03", "Food", 900),
            make_record("I1", "2024-03-04", "Salary", 5000, "Income"),
        ]
        self.limits = {"Food": 100, "Rent": 50}

    @patch("budgetwise.analysis.budgets.implementation.comparison.load_limits")
    def test_compares_month_expenses_and_reports_unbudgeted_categories(self, load):
        load.return_value = self.limits
        results = compare_to_budget(self.transactions, "2024", "03")
        self.assertEqual(
            [(r.category, r.limit, r.actual, r.status, r.difference) for r in results],
            [
                ("Food", 100, 120.0, "over", 20.0),
                ("Rent", 50, 0.0, "under", -50.0),
                ("Travel", None, 30.0, "unbudgeted", None),
            ],
        )

    @patch("budgetwise.analysis.budgets.implementation.comparison.load_limits")
    def test_exact_limit_is_reported(self, load):
        load.return_value = {"Food": 120}
        result = compare_to_budget(self.transactions, "2024", "03")
        self.assertEqual(result[0].status, "exact")
        self.assertEqual(result[0].difference, 0.0)

    @patch("budgetwise.analysis.budgets.implementation.comparison.load_limits")
    def test_month_without_expenses_returns_empty(self, load):
        load.return_value = self.limits
        self.assertEqual(compare_to_budget(self.transactions, "2024", "04"), [])

    @patch("budgetwise.analysis.budgets.implementation.comparison.load_limits")
    def test_model_transactions_are_supported(self, load):
        load.return_value = {"Food": 100}
        transactions = [
            ExpenseTransaction("E1", "U1", "2024-03-01", "Food", 120),
            IncomeTransaction("I1", "U1", "2024-03-02", "Salary", 900),
        ]
        result = compare_to_budget(transactions, "2024", "03")
        self.assertEqual(result[0].actual, 120.0)
        self.assertEqual(result[0].status, "over")

    def test_rejects_invalid_month(self):
        for month in ("00", "13", "3"):
            with self.subTest(month=month):
                with self.assertRaises(ValueError):
                    compare_to_budget([], "2024", month)


class TestLoadLimits(unittest.TestCase):
    def test_reads_configured_limits(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "budgets.json"
            path.write_text(json.dumps({"limits": {" Food ": 8000}}), encoding="utf-8")
            self.assertEqual(load_limits(path), {"Food": 8000.0})

    def test_duplicate_trimmed_categories_are_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "budgets.json"
            path.write_text(
                json.dumps({"limits": {"Food": 8000, " Food ": 9000}}),
                encoding="utf-8",
            )
            with self.assertRaises(ValueError):
                load_limits(path)


if __name__ == "__main__":
    unittest.main()