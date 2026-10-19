import csv
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from budgetwise.analysis.budgets.implementation import generate_budget_evidence as generator

from budgetwise.analysis.budgets.implementation.generate_budget_evidence import (
    calculate_evidence,
)


class TestBudgetEvidence(unittest.TestCase):
    def generate_for_window(self, start, end):
        """Real CSV and config; changing settings must change the selected history."""
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            dataset = root / 'history.csv'
            categories = ['Food', 'Rent', 'Transportation', 'Utilities', 'Entertainment']
            with dataset.open('w', newline='', encoding='utf-8') as stream:
                writer = csv.writer(stream)
                writer.writerow(['transaction_id', 'user_id', 'date', 'transaction_type',
                                 'category', 'amount', 'payment_mode', 'location', 'notes'])
                for i, category in enumerate(categories):
                    for j, (date, amount) in enumerate([
                        ('2024-01-01', 100), ('2024-03-31', 300), ('2025-01-01', 9000)
                    ]):
                        raw_category = 'Travel' if category == 'Transportation' else category
                        writer.writerow([f'T{i}{j}', 'U001', date, 'Expense', raw_category,
                                         amount, 'Cash', 'Mumbai', ''])
            config = root / 'budgets.json'
            config.write_text(json.dumps({'limits': dict.fromkeys(categories, 500)}))
            original = config.read_bytes()
            justification = root / 'justification.md'
            with patch.object(generator, 'BUDGET_BASELINE_START', start, create=True), \
                 patch.object(generator, 'BUDGET_BASELINE_END', end, create=True):
                try:
                    evidence = generator.generate(dataset, config, justification, increment=100)
                except ValueError:
                    self.assertEqual(config.read_bytes(), original)
                    self.assertFalse(justification.exists())
                    raise
            return evidence, justification.read_text(encoding='utf-8')

    def test_configured_baseline_excludes_later_spending_and_includes_zero_month(self):
        evidence, text = self.generate_for_window('2024-01-01', '2024-03-31')
        self.assertEqual([item['limit'] for item in evidence], [100] * 5)
        self.assertIn('2024-01 through 2024-03 (3 calendar months)', text)

    def test_incomplete_configured_baseline_is_rejected_without_writing(self):
        with self.assertRaisesRegex(ValueError, '2023-01-01.*2024-03-31'):
            self.generate_for_window('2023-01-01', '2024-03-31')

    def test_reversed_configured_baseline_is_rejected_without_writing(self):
        with self.assertRaisesRegex(ValueError, 'baseline start.*after'):
            self.generate_for_window('2024-04-01', '2024-03-31')

    def test_partial_month_baseline_is_rejected_without_writing(self):
        with self.assertRaisesRegex(ValueError, 'complete calendar months'):
            self.generate_for_window('2024-01-15', '2024-03-31')

    def test_monthly_statistics_include_zero_spend_months(self):
        transactions = [
            {"date": "2024-01-10", "category": "Food", "amount": 600,
             "transaction_type": "Expense"},
            {"date": "2024-01-11", "category": "Rent", "amount": 25,
             "transaction_type": "Expense"},
            {"date": "2024-01-12", "category": "Travel", "amount": 30,
             "transaction_type": "Expense"},
            {"date": "2024-01-13", "category": "Utilities", "amount": 40,
             "transaction_type": "Expense"},
            {"date": "2024-01-14", "category": "Entertainment", "amount": 50,
             "transaction_type": "Expense"},
            {"date": "2024-02-10", "category": "Salary", "amount": 1,
             "transaction_type": "Income"},
            {"date": "2024-03-10", "category": "Food", "amount": 1000,
             "transaction_type": "Expense"},
        ]

        months, evidence = calculate_evidence(
            transactions,
            ["Food", "Rent", "Travel", "Utilities", "Entertainment"],
        )

        self.assertEqual(months, [("2024", "01"), ("2024", "02"), ("2024", "03")])
        food = next(item for item in evidence if item["category"] == "Food")
        self.assertEqual(food["median"], 600)
        self.assertEqual(food["p75"], 800)
        self.assertEqual(food["maximum"], 1000.0)
        self.assertEqual(food["limit"], 1000)

    def test_rejects_fewer_than_five_budget_categories(self):
        transactions = [
            {"date": "2024-01-10", "category": "Food", "amount": 600,
             "transaction_type": "Expense"},
        ]
        with self.assertRaises(ValueError):
            calculate_evidence(transactions, ["Food"])

    def test_rejects_missing_dated_transactions(self):
        with self.assertRaises(ValueError):
            calculate_evidence([], ["Food", "Rent", "Travel", "Utilities",
                                    "Entertainment"])

    def test_rejects_category_with_no_dated_expense_spending(self):
        transactions = [
            {"date": "2024-01-10", "category": "Food", "amount": 600,
             "transaction_type": "Expense"},
            {"date": "2024-01-11", "category": "Rent", "amount": 25,
             "transaction_type": "Expense"},
            {"date": "2024-01-13", "category": "Utilities", "amount": 40,
             "transaction_type": "Expense"},
            {"date": "2024-01-14", "category": "Entertainment", "amount": 50,
             "transaction_type": "Expense"},
        ]
        with self.assertRaisesRegex(ValueError, "no dated expense spending: Travel"):
            calculate_evidence(
                transactions,
                ["Food", "Rent", "Travel", "Utilities", "Entertainment"],
            )


if __name__ == "__main__":
    unittest.main()
