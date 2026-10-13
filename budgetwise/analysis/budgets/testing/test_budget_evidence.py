import unittest

from budgetwise.analysis.budgets.implementation.generate_budget_evidence import (
    calculate_evidence,
)


class TestBudgetEvidence(unittest.TestCase):
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