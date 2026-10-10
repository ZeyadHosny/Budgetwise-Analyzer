import copy
import unittest

from budgetwise.analysis.budgets.implementation.group_comparison import (
    compare_group_month,
)


class TestGroupComparison(unittest.TestCase):

    def setUp(self):
        self.config = {
            "limits": {"Food": 3900},
            "user_overrides": {},
        }

    def record(
        self,
        user_id,
        amount,
        transaction_date="2024-07-10",
        category="Food",
        transaction_type="Expense",
        source_line=2,
    ):
        return {
            "user_id": user_id,
            "date": transaction_date,
            "category": category,
            "transaction_type": transaction_type,
            "amount": amount,
            "source_line": source_line,
        }

    def compare(self, records, requested_users=None):
        return compare_group_month(
            records,
            self.config,
            2024,
            7,
            "Food",
            requested_users=requested_users,
        )

    def test_two_users_with_matching_group_budget(self):
        records = [
            self.record("U001", 4200),
            self.record("U002", 3500),
        ]

        result = self.compare(records)

        self.assertEqual(result["group"]["recorded_actual"], 7700.0)
        self.assertEqual(result["group"]["limit"], 7800.0)
        self.assertEqual(result["group"]["status"], "under")
        self.assertEqual(result["group"]["difference"], 100.0)

        # Group underspending must not hide individual overspending.
        self.assertEqual(result["users"]["U001"]["status"], "over")

    def test_selected_users_only(self):
        records = [
            self.record("U001", 4200),
            self.record("U002", 3500),
            self.record("U003", 9000),
        ]

        result = self.compare(records, ["U001", "U002"])

        self.assertEqual(result["included_users"], ["U001", "U002"])
        self.assertEqual(result["group"]["recorded_actual"], 7700.0)
        self.assertEqual(result["group"]["limit"], 7800.0)

    def test_user_without_month_records_is_excluded(self):
        records = [
            self.record("U001", 4200),
            self.record(
                "U002",
                3500,
                transaction_date="2024-06-10",
            ),
        ]

        result = self.compare(records, ["U001", "U002"])

        self.assertEqual(result["included_users"], ["U001"])
        self.assertEqual(
            result["excluded_no_month_records"],
            ["U002"],
        )
        self.assertEqual(result["group"]["limit"], 3900.0)

    def test_income_only_user_is_included_with_evidence_flag(self):
        records = [
            self.record("U001", 4200),
            self.record("U002", 10000, transaction_type="Income"),
        ]

        result = self.compare(records)

        self.assertEqual(result["included_users"], ["U001", "U002"])
        self.assertEqual(result["group"]["recorded_actual"], 4200.0)
        self.assertEqual(result["group"]["limit"], 7800.0)
        self.assertEqual(
            result["users_without_category_expenses"],
            ["U002"],
        )

    def test_other_category_user_is_included(self):
        records = [
            self.record("U001", 4200),
            self.record("U002", 1000, category="Education"),
        ]

        result = self.compare(records)

        self.assertEqual(result["group"]["recorded_actual"], 4200.0)
        self.assertEqual(result["group"]["limit"], 7800.0)
        self.assertEqual(
            result["users_without_category_expenses"],
            ["U002"],
        )

    def test_undated_records_do_not_establish_monthly_evidence(self):
        records = [
            self.record("U001", 4200),
            self.record("U002", 3500, transaction_date=None),
        ]

        result = self.compare(records, ["U001", "U002"])

        self.assertEqual(result["included_users"], ["U001"])
        self.assertEqual(
            result["excluded_no_month_records"],
            ["U002"],
        )

    def test_override_changes_matching_group_limit(self):
        self.config["user_overrides"] = {
            "U001": {"Food": 4500}
        }

        records = [
            self.record("U001", 4200),
            self.record("U002", 3500),
        ]

        result = self.compare(records)

        self.assertEqual(result["group"]["limit"], 8400.0)
        self.assertEqual(result["group"]["difference"], 700.0)

    def test_zero_override_is_included(self):
        self.config["user_overrides"] = {
            "U001": {"Food": 0}
        }

        records = [
            self.record("U001", 100),
            self.record("U002", 3500),
        ]

        result = self.compare(records)

        self.assertEqual(result["group"]["limit"], 3900.0)
        self.assertEqual(result["group"]["recorded_actual"], 3600.0)

    def test_all_users_without_budget(self):
        self.config["limits"] = {}

        result = self.compare([
            self.record("U001", 4200),
            self.record("U002", 3500),
        ])

        self.assertEqual(result["group"]["status"], "unbudgeted")
        self.assertIsNone(result["group"]["limit"])
        self.assertIsNone(result["group"]["difference"])
        self.assertEqual(
            result["missing_budget_users"],
            ["U001", "U002"],
        )

    def test_partial_budget_coverage_is_not_compared(self):
        self.config["limits"] = {}
        self.config["user_overrides"] = {
            "U001": {"Food": 3900}
        }

        result = self.compare([
            self.record("U001", 4200),
            self.record("U002", 3500),
        ])

        self.assertEqual(
            result["group"]["status"],
            "incomplete_budget",
        )
        self.assertEqual(result["group"]["recorded_actual"], 7700.0)
        self.assertIsNone(result["group"]["limit"])
        self.assertIsNone(result["group"]["difference"])
        self.assertEqual(result["missing_budget_users"], ["U002"])

    def test_empty_group_is_no_data(self):
        result = self.compare([])

        self.assertEqual(result["group"]["status"], "no_data")
        self.assertEqual(result["group"]["user_count"], 0)
        self.assertIsNone(result["group"]["limit"])

    def test_explicit_empty_selection_is_no_data(self):
        result = self.compare(
            [self.record("U001", 4200)],
            requested_users=[],
        )

        self.assertEqual(result["group"]["status"], "no_data")
        self.assertEqual(result["included_users"], [])

    def test_repeated_requested_user_is_counted_once(self):
        result = self.compare(
            [self.record("U001", 4200)],
            ["U001", "U001"],
        )

        self.assertEqual(result["group"]["user_count"], 1)
        self.assertEqual(result["group"]["limit"], 3900.0)

    def test_group_over_and_equal(self):
        for actual, status, difference in (
            (4000, "over", 100.0),
            (3900, "equal", 0.0),
        ):
            with self.subTest(actual=actual):
                result = self.compare([
                    self.record("U001", actual)
                ])

                self.assertEqual(result["group"]["status"], status)
                self.assertEqual(
                    result["group"]["difference"],
                    difference,
                )

    def test_invalid_selections_are_rejected(self):
        cases = (
            (2024, 13, "Food", None),
            ("2024", 7, "Food", None),
            (2024, True, "Food", None),
            (2024, 7, "", None),
            (2024, 7, "Food", "U001"),
            (2024, 7, "Food", [""]),
            (2024, 7, "Food", [123]),
        )

        for year, month, category, users in cases:
            with self.subTest(
                year=year,
                month=month,
                category=category,
                users=users,
            ):
                with self.assertRaises(ValueError):
                    compare_group_month(
                        [],
                        self.config,
                        year,
                        month,
                        category,
                        requested_users=users,
                    )

    def test_records_and_config_are_not_modified(self):
        records = [self.record("U001", 4200)]
        original_records = copy.deepcopy(records)
        original_config = copy.deepcopy(self.config)

        self.compare(records)

        self.assertEqual(records, original_records)
        self.assertEqual(self.config, original_config)


if __name__ == "__main__":
    unittest.main()
