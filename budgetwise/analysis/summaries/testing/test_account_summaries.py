"""
P3.3: summary integration tests with real models and accounts.

Illustrative data, not full-dataset findings or approved budget limits.

Run from the repository root:
    python -m unittest budgetwise.analysis.summaries.testing.test_account_summaries -v
"""

import unittest
from collections import Counter

from budgetwise.models import (
    ExpenseTransaction,
    IncomeTransaction,
    CashAccount,
    BankAccount,
    UnknownAccount,
)
from budgetwise.analysis.summaries import (
    total_income,
    total_expenses,
    net_balance,
    monthly_expenses,
    top_categories,
    top_expenses,
)


class TestAccountSummaries(unittest.TestCase):
    """Verify all six summaries with hand-calculated expectations."""

    def setUp(self):
        """Build fresh objects and place each in one payment group."""
        rows = [
            ("T0001", "2023-01-01", "Food", 100, "Expense", "Cash"),
            ("T0002", "2023-01-02", "Rent", 200, "Expense", "Cash"),
            ("T0003", None, "Food", 50, "Expense", "Cash"),
            ("T0004", "2023-01-03", "Salary", 500, "Income", "Cash"),
            ("T0005", "2023-01-04", "Food", 100, "Expense", "Card"),
            ("T0006", "2023-02-01", "Utilities", 80, "Expense", "UPI"),
            ("T0007", "2023-01-05", "Rent", 200, "Expense", "Bank Transfer"),
            ("T0008", "2023-02-02", "Salary", 1000, "Income", "Card"),
            ("T0009", "2023-01-06", "Food", 100, "Expense", "Unknown"),
            ("T0010", None, "Other", 30, "Expense", "Unknown"),
            ("T0011", "2023-02-03", "Rent", 200, "Expense", "Unknown"),
            ("T0012", None, "Bonus", 60, "Income", "Unknown"),
        ]

        self.accounts = {
            "cash": CashAccount(),
            "bank": BankAccount(),
            "unknown": UnknownAccount(),
        }
        self.transactions = []

        for tid, date, category, amount, kind, mode in rows:
            model = (
                ExpenseTransaction if kind == "Expense"
                else IncomeTransaction
            )
            transaction = model(
                tid, "U001", date, category, amount, mode
            )
            self.transactions.append(transaction)

            if mode == "Cash":
                group = "cash"
            elif mode == "Unknown":
                group = "unknown"
            else:
                group = "bank"

            self.accounts[group].add_transaction(transaction)

    def assert_summaries(
        self, transactions, income, expenses, months, categories, ids
    ):
        """Check every output against independent expected values."""
        self.assertEqual(total_income(transactions), income)
        self.assertEqual(total_expenses(transactions), expenses)
        self.assertEqual(net_balance(transactions), income - expenses)
        self.assertEqual(monthly_expenses(transactions), months)
        self.assertEqual(top_categories(transactions), categories)
        self.assertEqual(
            [
                transaction.get_transaction_id()
                for transaction in top_expenses(transactions)
            ],
            ids,
        )

    def test_overall_real_model_summaries(self):
        """Income 1560, expenses 1060, net 500; undated expenses 80."""
        self.assert_summaries(
            self.transactions,
            1560.0,
            1060.0,
            {("2023", "01"): 700.0, ("2023", "02"): 280.0},
            [
                ("Rent", 600.0),
                ("Food", 350.0),
                ("Utilities", 80.0),
                ("Other", 30.0),
            ],
            ["T0002", "T0007", "T0011", "T0001", "T0005"],
        )

    def test_all_six_functions_for_each_account(self):
        """Each payment group's outputs match separate hand sums."""
        expected = {
            "cash": (
                500.0,
                350.0,
                {("2023", "01"): 300.0},
                [("Rent", 200.0), ("Food", 150.0)],
                ["T0002", "T0001", "T0003"],
            ),
            "bank": (
                1000.0,
                380.0,
                {("2023", "01"): 300.0, ("2023", "02"): 80.0},
                [
                    ("Rent", 200.0),
                    ("Food", 100.0),
                    ("Utilities", 80.0),
                ],
                ["T0007", "T0005", "T0006"],
            ),
            "unknown": (
                60.0,
                330.0,
                {("2023", "01"): 100.0, ("2023", "02"): 200.0},
                [
                    ("Rent", 200.0),
                    ("Food", 100.0),
                    ("Other", 30.0),
                ],
                ["T0011", "T0009", "T0010"],
            ),
        }

        for group, account in self.accounts.items():
            with self.subTest(account=group):
                self.assert_summaries(
                    account.get_transactions(), *expected[group]
                )

    def test_dictionary_and_model_inputs_match(self):
        """Both supported representations give equivalent summaries."""
        records = [
            transaction.to_dict()
            for transaction in self.transactions
        ]
        functions = (
            total_income,
            total_expenses,
            net_balance,
            monthly_expenses,
            top_categories,
        )
        for function in functions:
            with self.subTest(function=function.__name__):
                self.assertEqual(
                    function(records), function(self.transactions)
                )

        self.assertEqual(
            [record["transaction_id"] for record in top_expenses(records)],
            [
                transaction.get_transaction_id()
                for transaction in top_expenses(self.transactions)
            ],
        )

    def test_account_totals_reconcile_without_double_counting(self):
        """Disjoint account totals equal the master-list totals."""
        for function in (total_income, total_expenses, net_balance):
            with self.subTest(function=function.__name__):
                combined = sum(
                    function(account.get_transactions())
                    for account in self.accounts.values()
                )
                self.assertEqual(
                    combined, function(self.transactions)
                )

        monthly_total = sum(
            monthly_expenses(self.transactions).values()
        )
        self.assertEqual(monthly_total, 980.0)
        self.assertEqual(
            total_expenses(self.transactions) - monthly_total,
            80.0,
        )

    def test_each_object_appears_in_exactly_one_account(self):
        """Check object identities rather than transaction IDs."""
        grouped = [
            transaction
            for account in self.accounts.values()
            for transaction in account.get_transactions()
        ]
        grouped_counts = Counter(map(id, grouped))

        self.assertEqual(
            grouped_counts,
            Counter(map(id, self.transactions)),
        )
        self.assertTrue(
            all(count == 1 for count in grouped_counts.values())
        )

    def test_equal_expenses_preserve_reversed_input_order(self):
        """Equal amounts retain the supplied order of real objects."""
        ranked = top_expenses(list(reversed(self.transactions)))

        self.assertEqual(
            [
                transaction.get_transaction_id()
                for transaction in ranked
            ],
            ["T0011", "T0007", "T0002", "T0009", "T0005"],
        )
        self.assertIs(ranked[0], self.transactions[10])

    def test_category_ties_use_names(self):
        """Equal category totals use ascending category names."""
        transactions = [
            ExpenseTransaction(
                "T0101", "U001", None, "Utilities", 100, "Unknown"
            ),
            ExpenseTransaction(
                "T0102", "U001", None, "Food", 100, "Unknown"
            ),
        ]
        self.assertEqual(
            top_categories(transactions),
            [("Food", 100.0), ("Utilities", 100.0)],
        )

    def test_summaries_do_not_change_objects_or_account_order(self):
        """Calculations leave shared objects and membership unchanged."""
        before_records = [
            transaction.to_dict()
            for transaction in self.transactions
        ]
        before_order = {
            group: [
                id(transaction)
                for transaction in account.get_transactions()
            ]
            for group, account in self.accounts.items()
        }

        selections = [self.transactions] + [
            account.get_transactions()
            for account in self.accounts.values()
        ]
        for transactions in selections:
            for function in (
                total_income,
                total_expenses,
                net_balance,
                monthly_expenses,
                top_categories,
                top_expenses,
            ):
                function(transactions)

        self.assertEqual(
            [
                transaction.to_dict()
                for transaction in self.transactions
            ],
            before_records,
        )
        self.assertEqual(
            {
                group: [
                    id(transaction)
                    for transaction in account.get_transactions()
                ]
                for group, account in self.accounts.items()
            },
            before_order,
        )

    def test_empty_accounts_have_empty_summaries(self):
        """Empty account selections are valid."""
        for model in (CashAccount, BankAccount, UnknownAccount):
            with self.subTest(account=model.__name__):
                self.assert_summaries(
                    model().get_transactions(),
                    0.0, 0.0, {}, [], [],
                )

    def test_repeated_ids_retain_distinct_real_objects(self):
        """Sharing an ID does not remove a transaction."""
        first = ExpenseTransaction(
            "T0200", "U001", None, "Food", 100, "Cash"
        )
        second = ExpenseTransaction(
            "T0200", "U001", None, "Food", 90, "Cash"
        )
        account = CashAccount()
        account.add_transaction(first)
        account.add_transaction(second)

        transactions = account.get_transactions()
        ranked = top_expenses(transactions)

        self.assertEqual(total_expenses(transactions), 190.0)
        self.assertEqual(len(ranked), 2)
        self.assertIs(ranked[0], first)
        self.assertIs(ranked[1], second)

    def test_account_list_copy_does_not_remove_held_objects(self):
        """Clearing a borrowed list leaves the account intact."""
        account = self.accounts["cash"]
        borrowed = account.get_transactions()
        borrowed.clear()

        self.assertEqual(account.get_transaction_count(), 4)
        self.assertEqual(
            total_expenses(account.get_transactions()), 350.0
        )

    def test_shared_updates_are_read_without_cached_totals(self):
        """Valid amount updates appear in both account and overall totals."""
        self.transactions[0].set_amount(125.0)

        self.assertEqual(
            total_expenses(
                self.accounts["cash"].get_transactions()
            ),
            375.0,
        )
        self.assertEqual(
            total_expenses(self.transactions), 1085.0
        )
        self.assertEqual(
            monthly_expenses(self.transactions)[("2023", "01")],
            725.0,
        )


if __name__ == "__main__":
    unittest.main()
