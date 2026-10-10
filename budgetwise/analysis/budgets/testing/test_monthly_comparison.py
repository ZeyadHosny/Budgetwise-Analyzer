import copy
import json
import tempfile
import unittest
from pathlib import Path

from budgetwise.analysis.budgets.implementation.monthly_comparison import (
    compare_user_month,
    load_budget_config,
    resolve_limit,
)


class TestMonthlyComparison(unittest.TestCase):

    def setUp(self):
        self.config = {
            "limits": {
                "Food": 3900,
                "Transportation": 5600,
            },
            "user_overrides": {},
        }

    def record(
        self,
        amount,
        user_id="U001",
        transaction_date="2024-07-10",
        category="Food",
        transaction_type="Expense",
        source_line=2,
        currency_label=None,
        payment_mode="Cash",
    ):
        return {
            "user_id": user_id,
            "date": transaction_date,
            "category": category,
            "transaction_type": transaction_type,
            "amount": amount,
            "source_line": source_line,
            "currency_label": currency_label,
            "payment_mode": payment_mode,
        }

    def compare(self, records, category="Food"):
        return compare_user_month(
            records,
            self.config,
            "U001",
            2024,
            7,
            category,
        )

    def test_over_under_and_equal(self):
        cases = (
            (4200, "over", 300.0),
            (3500, "under", 400.0),
            (3900, "equal", 0.0),
        )

        for amount, status, difference in cases:
            with self.subTest(amount=amount):
                result = self.compare([self.record(amount)])

                self.assertEqual(result["status"], status)
                self.assertEqual(result["difference"], difference)

    def test_only_matching_user_month_category_expenses(self):
        records = [
            self.record(1000, source_line=2),
            self.record(2000, source_line=3),
            self.record(9000, user_id="U002"),
            self.record(9000, transaction_date="2024-06-10"),
            self.record(9000, transaction_date="2023-07-10"),
            self.record(9000, category="Transportation"),
            self.record(9000, transaction_type="Income"),
            self.record(9000, transaction_date=None),
        ]

        result = self.compare(records)

        self.assertEqual(result["recorded_actual"], 3000.0)
        self.assertEqual(result["expense_record_count"], 2)
        self.assertEqual(result["source_lines"], [2, 3])

    def test_currency_labels_do_not_split_totals(self):
        records = [
            self.record(2000, currency_label="$"),
            self.record(2200, currency_label="₹"),
        ]

        result = self.compare(records)

        self.assertEqual(result["recorded_actual"], 4200.0)
        self.assertEqual(result["status"], "over")

    def test_unknown_payment_mode_is_retained(self):
        result = self.compare([
            self.record(4200, payment_mode="Unknown")
        ])

        self.assertEqual(result["recorded_actual"], 4200.0)

    def test_no_month_records(self):
        result = self.compare([
            self.record(4200, transaction_date="2024-06-10")
        ])

        self.assertEqual(result["status"], "no_data")
        self.assertIsNone(result["difference"])
        self.assertFalse(result["has_month_records"])

    def test_month_records_without_category_expenses(self):
        result = self.compare([
            self.record(1000, transaction_type="Income")
        ])

        self.assertEqual(result["recorded_actual"], 0.0)
        self.assertEqual(result["status"], "under")
        self.assertTrue(result["has_month_records"])
        self.assertFalse(result["has_category_expense_record"])

    def test_explicit_zero_expense_has_evidence(self):
        result = self.compare([self.record(0)])

        self.assertEqual(result["recorded_actual"], 0.0)
        self.assertTrue(result["has_category_expense_record"])

    def test_missing_budget_is_unbudgeted(self):
        result = self.compare(
            [self.record(1000, category="Education")],
            category="Education",
        )

        self.assertEqual(result["status"], "unbudgeted")
        self.assertIsNone(result["limit"])
        self.assertIsNone(result["difference"])

    def test_default_limit(self):
        self.assertEqual(
            resolve_limit(self.config, "U001", "Food"),
            3900.0,
        )

    def test_override_limit(self):
        self.config["user_overrides"] = {
            "U001": {"Food": 4500}
        }

        result = self.compare([self.record(4200)])

        self.assertEqual(result["limit"], 4500.0)
        self.assertEqual(result["status"], "under")
        self.assertEqual(result["difference"], 300.0)

    def test_zero_override_is_valid(self):
        self.config["user_overrides"] = {
            "U001": {"Food": 0}
        }

        result = self.compare([self.record(100)])

        self.assertEqual(result["limit"], 0.0)
        self.assertEqual(result["status"], "over")

    def test_override_for_one_category_keeps_other_defaults(self):
        self.config["user_overrides"] = {
            "U001": {"Food": 4500}
        }

        self.assertEqual(
            resolve_limit(self.config, "U001", "Transportation"),
            5600.0,
        )

    def test_invalid_configured_limit_is_rejected(self):
        for value in (-1, None, True, "3900", float("nan")):
            with self.subTest(value=value):
                config = {
                    "limits": {"Food": value},
                    "user_overrides": {},
                }

                with self.assertRaises(ValueError):
                    resolve_limit(config, "U001", "Food")

    def test_baseline_year_can_be_compared(self):
        result = compare_user_month(
            [self.record(4200, transaction_date="2021-07-10")],
            self.config,
            "U001",
            2021,
            7,
            "Food",
        )

        self.assertEqual(result["status"], "over")

    def test_invalid_selection_is_rejected(self):
        cases = (
            ("", 2024, 7, "Food"),
            ("U001", 2024, 7, ""),
            ("U001", 2024, 13, "Food"),
            ("U001", 2024, 0, "Food"),
            ("U001", "2024", 7, "Food"),
            ("U001", 2024, True, "Food"),
        )

        for user_id, year, month, category in cases:
            with self.subTest(
                user_id=user_id,
                year=year,
                month=month,
                category=category,
            ):
                with self.assertRaises(ValueError):
                    compare_user_month(
                        [],
                        self.config,
                        user_id,
                        year,
                        month,
                        category,
                    )

    def test_records_and_config_are_not_modified(self):
        records = [self.record(4200)]
        original_records = copy.deepcopy(records)
        original_config = copy.deepcopy(self.config)

        self.compare(records)

        self.assertEqual(records, original_records)
        self.assertEqual(self.config, original_config)

    def test_load_config_from_file(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "budgets.json"
            path.write_text(
                json.dumps(self.config),
                encoding="utf-8",
            )

            self.assertEqual(
                load_budget_config(path),
                self.config,
            )


if __name__ == "__main__":
    unittest.main()
