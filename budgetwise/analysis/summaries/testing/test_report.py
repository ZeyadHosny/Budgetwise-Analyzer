import unittest

from budgetwise.analysis.summaries import build_summary
from budgetwise.models import (
    BankAccount,
    CashAccount,
    ExpenseTransaction,
    IncomeTransaction,
    UnknownAccount,
)


class TestBuildSummary(unittest.TestCase):
    def setUp(self):
        self.cash = CashAccount()
        self.cash.add_transaction(
            ExpenseTransaction("E1", "U1", "2024-01-05", "Food", 100.0)
        )
        self.cash.add_transaction(
            ExpenseTransaction("E2", "U1", "2024-01-20", "Food", 50.0)
        )
        self.cash.add_transaction(
            IncomeTransaction("I1", "U1", "2024-01-10", "Salary", 300.0)
        )
        self.bank = BankAccount()
        self.bank.add_transaction(
            ExpenseTransaction("E3", "U1", "2024-02-03", "Rent", 200.0)
        )
        self.unknown = UnknownAccount()
        self.unknown.add_transaction(
            ExpenseTransaction("E4", "U1", "2024-02-07", "Food", 60.0)
        )
        self.accounts = {
            "cash": self.cash,
            "bank": self.bank,
            "unknown": self.unknown,
        }
        self.budget_comparisons = [
            {
                "month": "2024-01",
                "period": {"start": "2024-01-01", "end": "2024-01-31",
                           "full_month": True},
                "categories": [
                    {"category": "Food", "limit": 200.0, "actual": 150.0,
                     "status": "under", "difference": -50.0},
                    {"category": "Rent", "limit": 300.0, "actual": 0.0,
                     "status": "under", "difference": -300.0},
                ],
            },
            {
                "month": "2024-02",
                "period": {"start": "2024-02-01", "end": "2024-02-29",
                           "full_month": True},
                "categories": [
                    {"category": "Food", "limit": 200.0, "actual": 60.0,
                     "status": "under", "difference": -140.0},
                    {"category": "Rent", "limit": 300.0, "actual": 200.0,
                     "status": "under", "difference": -100.0},
                ],
            },
        ]

    def test_builds_total_monthly_and_category_sections(self):
        summary = build_summary(
            self.accounts,
            {"input": 4, "valid": 4},
            {"load": 0.1, "clean": 0.2},
            self.budget_comparisons,
            {"type": "all"},
            n=2,
        )

        self.assertEqual(
            set(summary) - {"scope", "selection", "selected_transactions",
                            "counts", "timings"},
            {"total_breakdown", "monthly_breakdown", "category_breakdown"},
        )
        total = summary["total_breakdown"]
        self.assertEqual(total["totals"], {
            "income": 300.0, "expenses": 410.0, "net": -110.0,
        })
        self.assertEqual(total["top_categories"], [("Food", 210.0), ("Rent", 200.0)])
        self.assertEqual(
            [item["transaction_id"] for item in total["largest_expenses"]],
            ["E3", "E1"],
        )
        food_budget = next(
            item for item in total["budget_by_category"]
            if item["category"] == "Food"
        )
        self.assertEqual(
            (food_budget["limit"], food_budget["actual"],
             food_budget["status"], food_budget["difference"]),
            (400.0, 210.0, "under", -190.0),
        )
        self.assertEqual(total["account_breakdown"]["cash"]["transaction_count"], 3)

        monthly = summary["monthly_breakdown"]
        self.assertEqual([item["month"] for item in monthly["months"]],
                         ["2024-01", "2024-02"])
        self.assertEqual(monthly["months"][0]["totals"], {
            "income": 300.0, "expenses": 150.0, "net": 150.0,
        })
        self.assertEqual(monthly["chart_data"], [
            {"month": "2024-01", "expenses": 150.0},
            {"month": "2024-02", "expenses": 260.0},
        ])
        food = next(item for item in summary["category_breakdown"]
                    if item["category"] == "Food")
        self.assertEqual(food["transaction_count"], 3)
        self.assertEqual(food["totals"]["expenses"], 210.0)


if __name__ == "__main__":
    unittest.main()
