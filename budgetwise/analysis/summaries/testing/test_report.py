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
                "period": {
                    "start": "2024-01-01",
                    "end": "2024-01-31",
                    "full_month": True,
                },
                "categories": [
                    {
                        "category": "Food",
                        "limit": 200.0,
                        "actual": 150.0,
                        "status": "under",
                        "difference": -50.0,
                    },
                    {
                        "category": "Rent",
                        "limit": 300.0,
                        "actual": 0.0,
                        "status": "under",
                        "difference": -300.0,
                    },
                ],
            },
            {
                "month": "2024-02",
                "period": {
                    "start": "2024-02-01",
                    "end": "2024-02-29",
                    "full_month": True,
                },
                "categories": [
                    {
                        "category": "Food",
                        "limit": 200.0,
                        "actual": 60.0,
                        "status": "under",
                        "difference": -140.0,
                    },
                    {
                        "category": "Rent",
                        "limit": 300.0,
                        "actual": 200.0,
                        "status": "under",
                        "difference": -100.0,
                    },
                ],
            },
        ]

    def test_builds_total_monthly_and_chart_sections(self):
        result, chart_data = build_summary(
            self.accounts,
            {"input": 4, "valid": 4},
            {"load": 0.1, "clean": 0.2},
            self.budget_comparisons,
            {"type": "all"},
            n=2,
        )

        # Verify the top-level summary format.
        self.assertEqual(
            set(result),
            {
                "scope",
                "selection",
                "selected_transactions",
                "counts",
                "timings",
                "total_breakdown",
                "monthly_breakdown",
            },
        )

        self.assertEqual(
            result["scope"],
            "transactions selected by menu query",
        )
        self.assertEqual(result["selection"], {"type": "all"})
        self.assertEqual(result["selected_transactions"], 5)
        self.assertEqual(result["counts"], {"input": 4, "valid": 4})
        self.assertEqual(
            result["timings"],
            {"load": 0.1, "clean": 0.2},
        )

        # Verify the total breakdown.
        total = result["total_breakdown"]

        self.assertEqual(
            total["totals"],
            {
                "income": 300.0,
                "expenses": 410.0,
                "net": -110.0,
            },
        )

        self.assertEqual(
            total["top_categories"],
            [("Food", 210.0), ("Rent", 200.0)],
        )

        self.assertEqual(
            [item["transaction_id"] for item in total["largest_expenses"]],
            ["E3", "E1"],
        )

        food_budget = next(
            item
            for item in total["budget_by_category"]
            if item["category"] == "Food"
        )

        self.assertEqual(
            (
                food_budget["limit"],
                food_budget["actual"],
                food_budget["status"],
                food_budget["difference"],
            ),
            (400.0, 210.0, "under", -190.0),
        )

        # Verify account breakdown using each account's getters.
        self.assertEqual(
            set(total["account_breakdown"]),
            set(result["total_breakdown"]["account_breakdown"]),
        )

        expected_account_counts = {
            "cash": 3,
            "bank": 1,
            "unknown": 1,
        }

        for kind, account in self.accounts.items():
            with self.subTest(account=kind):
                breakdown = total["account_breakdown"][kind]

                self.assertEqual(
                    breakdown["transaction_count"],
                    account.get_transaction_count(),
                )
                self.assertEqual(
                    breakdown["total_spent"],
                    account.get_total_spent(),
                )
                self.assertEqual(
                    breakdown["transaction_count"],
                    expected_account_counts[kind],
                )

        # Verify the monthly breakdown.
        monthly = result["monthly_breakdown"]

        self.assertEqual(
            [item["month"] for item in monthly["months"]],
            ["2024-01", "2024-02"],
        )

        self.assertEqual(
            monthly["months"][0]["totals"],
            {
                "income": 300.0,
                "expenses": 150.0,
                "net": 150.0,
            },
        )

        # Chart data is now stored separately.
        self.assertEqual(
            chart_data["monthly_breakdown"],
            [
                {"month": "2024-01", "expenses": 150.0},
                {"month": "2024-02", "expenses": 260.0},
            ],
        )

        # Verify total chart data.
        self.assertEqual(
            chart_data["total_breakdown"],
            [
                {"category": "Food", "expenses": 210.0},
                {"category": "Rent", "expenses": 200.0},
            ],
        )

        # Ensure chart data was removed from the summary sections.
        self.assertNotIn("chart_data", total)
        self.assertNotIn("chart_data", monthly)

        # The old category_breakdown section is no longer part
        # of the summary structure.
        self.assertNotIn("category_breakdown", result)


if __name__ == "__main__":
    unittest.main()