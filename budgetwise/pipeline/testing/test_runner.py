"""Tests for the cleaning pipeline (P2.10).

Each test writes a small CSV to a temporary folder with its own ErrorLog, so
the real loader and cleaners run together and output/logs/errors.log is never
touched. Checks on teammates' open defects are expected failures.

Run from the repository root:
    python -m unittest budgetwise.pipeline.testing.test_runner -v
"""

import os
import tempfile
import unittest
from unittest import mock

from budgetwise.errorlog import ErrorLog
from budgetwise.pipeline import clean_file, run

# Zeyad's model classes (#16).
from budgetwise.models import (Account, BankAccount, CashAccount, ExpenseTransaction,
                               IncomeTransaction, Transaction, UnknownAccount)

RUNNER = "budgetwise.pipeline.implementation.runner"


# Checks on teammates' open defects. Each test is an expected failure until
# the fix is merged, then it passes. It is never skipped.
def _amount_syntax_is_validated():
    """True once parse_amount() rejects '1-2' (review item S09, Patrick)."""
    from budgetwise.cleaning.amounts import parse_amount
    try:
        return parse_amount("1-2")[0] is None
    except Exception:
        return False


def _loader_keeps_row_structure():
    """True once load_rows() no longer pads a short row with blanks or drops
    surplus fields (review item S05, Patrick)."""
    from budgetwise.loader import load_rows
    folder = tempfile.TemporaryDirectory()
    try:
        path = os.path.join(folder.name, "probe.csv")
        with open(path, "w", encoding="utf-8", newline="") as handle:
            handle.write(HEADER + "\nT0001,U001\n")
        rows = [row for _, row in load_rows(path)]
        return rows[0].get("notes") != ""
    except Exception:
        return False
    finally:
        folder.cleanup()


def until_fixed(is_fixed):
    """Run the test normally once the fix exists; until then, expect it to fail."""
    return (lambda test: test) if is_fixed else unittest.expectedFailure


def _loader_rejects_duplicate_headers():
    """True once a header naming a column twice is refused (S05, Patrick)."""
    from budgetwise.loader import load_rows
    folder = tempfile.TemporaryDirectory()
    try:
        path = os.path.join(folder.name, "probe.csv")
        with open(path, "w", encoding="utf-8", newline="") as handle:
            handle.write(HEADER + ",amount\n")
        list(load_rows(path))
        return False
    except Exception:
        return True
    finally:
        folder.cleanup()

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), *[os.pardir] * 3))
DATASET_PATH = os.path.join(REPO_ROOT, "data", "raw", "budgetwise_synthetic_dirty.csv")

HEADER = "transaction_id,user_id,date,transaction_type,category,amount,payment_mode,location,notes"

# One row of each kind. Comments give the line number (header is line 1).
SMALL_FILE = [
    "T0001,U001,08/05/2022,Expense,Fod,₹-3888,cash,PUN,Lunch",    # 2  kept
    "T0001,U001,08/05/2022,Expense,Fod,₹-3888,cash,PUN,Lunch",    # 3  exact duplicate
    "T0002,U002,,Income,Salary,500,UPI,Delhi,...",                # 4  kept, no date
    "T0003,U003,2023-01-05,Refund,Food,100,Card,Pune,Lunch",      # 5  skipped: type
    "T0004,U004,2023-01-06,Expense,Food,999999999,Card,Pune,x",   # 6  skipped: sentinel
    "T0005,U005,2023-01-07,Expense,Food,,Card,Pune,Lunch",        # 7  skipped: no amount
    "T0001,U009,2023-03-09,Expense,FOOD,12,Card,Pune,Coffee",     # 8  kept, repeated id
    "T0006,U006,2023-02-01,Expense,,40,,Mumbai,Lunch",            # 9  kept, blanks
    "T0007,U007",                                                 # 10 skipped: short row
]


class PipelineTestCase(unittest.TestCase):
    """Shared set-up: a temporary folder holding the CSV and the error log."""

    def setUp(self):
        folder = tempfile.TemporaryDirectory()
        self.addCleanup(folder.cleanup)
        self.folder = folder.name
        self.log_path = os.path.join(self.folder, "logs", "errors.log")
        self.error_log = ErrorLog(self.log_path)
        self.addCleanup(self.error_log.close)

    def write_csv(self, lines, name="test.csv", header=HEADER):
        path = os.path.join(self.folder, name)
        with open(path, "w", encoding="utf-8", newline="") as handle:
            handle.write("\n".join([header] + list(lines)) + "\n")
        return path

    @staticmethod
    def reasons_on_line(result, line_number):
        """Every reason logged for one line."""
        return [reason for line, _, reason, _ in result["issues"] if line == line_number]


# Cleaning (clean_file): no model classes needed

class CleaningTests(PipelineTestCase):
    def setUp(self):
        super().setUp()
        self.result = clean_file(self.write_csv(SMALL_FILE), self.error_log)
        self.counts = self.result["counts"]
        self.by_line = {record["line_number"]: record for record in self.result["records"]}

    # Counts
    def test_every_input_row_is_accounted_for(self):
        self.assertIsNone(self.result["error"])
        self.assertEqual(self.counts["input"], 9)
        self.assertEqual(self.counts["duplicates"], 1)
        self.assertEqual(self.counts["skipped"], 4)
        self.assertEqual(self.counts["valid"], 4)
        self.assertEqual(
            self.counts["input"],
            self.counts["valid"] + self.counts["skipped"] + self.counts["duplicates"],
        )

    def test_only_valid_rows_become_records(self):
        self.assertEqual(sorted(self.by_line), [2, 4, 8, 9])

    def test_timings_are_reported(self):
        self.assertGreaterEqual(self.result["timings"]["load"], 0)
        self.assertGreaterEqual(self.result["timings"]["clean"], 0)

    # Cleaned values
    def test_every_column_is_cleaned(self):
        self.assertEqual(self.by_line[2], {
            "line_number": 2, "transaction_id": "T0001", "user_id": "U001",
            "transaction_type": "Expense",
            "date": "2022-08-05",           # slash date read as MM/DD/YYYY
            "category": "Food",             # 'Fod' normalized
            "amount": 3888.0,               # label and sign removed, no conversion
            "original_currency": "₹",       # label kept (4.5)
            "payment_mode": "Cash", "location": "Pune",
            "notes": "Lunch", "notes_quality": "meaningful",
        })

    def test_a_plain_amount_is_not_logged_as_a_stripped_label(self):
        # Row 4 has the plain amount "500": nothing was stripped.
        self.assertNotIn("currency_label_stripped", self.reasons_on_line(self.result, 4))
        self.assertEqual(self.by_line[4]["original_currency"], "plain")

    def test_stripped_label_and_sign_are_logged(self):
        reasons = self.reasons_on_line(self.result, 2)
        self.assertIn("currency_label_stripped", reasons)
        self.assertIn("negative_amount_magnitude", reasons)

    # Required conventions (section 4.5)
    def test_exact_duplicate_is_removed_and_logged(self):
        self.assertEqual(self.reasons_on_line(self.result, 3), ["duplicate_row"])

    def test_repeated_id_on_a_different_row_is_kept(self):
        self.assertEqual(self.by_line[8]["transaction_id"], "T0001")
        self.assertEqual(self.counts["repeated_ids"], 1)
        self.assertIn("repeated_transaction_id", self.reasons_on_line(self.result, 8))

    def test_row_with_no_date_is_kept_without_a_date(self):
        record = self.by_line[4]
        self.assertIsNone(record["date"])
        self.assertEqual(record["category"], "Salary")        # still counts by category
        self.assertIn("missing_date", self.reasons_on_line(self.result, 4))

    def test_sentinel_amount_is_not_a_transaction(self):
        self.assertEqual(self.reasons_on_line(self.result, 6), ["sentinel_amount"])

    def test_row_with_no_amount_is_skipped_and_logged(self):
        self.assertEqual(self.reasons_on_line(self.result, 7), ["missing_amount"])

    def test_unknown_transaction_type_is_skipped(self):
        self.assertEqual(self.reasons_on_line(self.result, 5), ["missing_required_field"])

    def test_short_row_is_skipped_without_crashing(self):
        # Reported as missing transaction_type now, or malformed once S05 is
        # fixed. Either way it is skipped, logged once, and nothing crashes.
        reasons = self.reasons_on_line(self.result, 10)
        self.assertEqual(len(reasons), 1)
        self.assertIn(reasons[0], ("missing_required_field", "malformed_row"))

    def test_missing_category_becomes_uncategorized(self):
        self.assertEqual(self.by_line[9]["category"], "Uncategorized")
        self.assertEqual(self.by_line[9]["payment_mode"], "Unknown")

    def test_placeholder_note_is_flagged_and_text_kept(self):
        self.assertEqual(self.by_line[4]["notes"], "...")
        self.assertIn("notes_low_information", self.reasons_on_line(self.result, 4))

    # Error log
    def test_every_issue_is_written_to_the_error_log(self):
        lines = self.error_log.read()
        self.assertEqual(len(lines), len(self.result["issues"]))
        self.assertEqual(sum(self.counts["by_reason"].values()), len(lines))
        self.assertTrue(any("line=3 field=row reason=duplicate_row" in line for line in lines))

    def test_reason_codes_are_all_lowercase(self):
        for reason in self.counts["by_reason"]:
            self.assertEqual(reason, reason.lower())


class OrderTests(PipelineTestCase):
    def test_duplicates_are_judged_on_raw_rows_before_normalizing(self):
        # 'Fod' and 'Food' clean the same, but the raw rows differ: no duplicate.
        path = self.write_csv([
            "T0001,U001,2023-01-01,Expense,Fod,10,Cash,Pune,Lunch",
            "T0001,U001,2023-01-01,Expense,Food,10,Cash,Pune,Lunch",
        ])
        result = clean_file(path, self.error_log)
        self.assertEqual(result["counts"]["duplicates"], 0)
        self.assertEqual([r["category"] for r in result["records"]], ["Food", "Food"])

    def test_loading_twice_gives_the_same_answer(self):
        # A second load in the same session must not see duplicates from the first.
        path = self.write_csv(SMALL_FILE)
        first = clean_file(path, self.error_log)
        second = clean_file(path, self.error_log)
        self.assertEqual(first["counts"], second["counts"])
        self.assertEqual(len(second["records"]), 4)


class BadInputTests(PipelineTestCase):
    def test_missing_file_raises_file_not_found(self):
        result = clean_file(os.path.join(self.folder, "no_such_file.csv"), self.error_log)
        self.assertEqual(type(result["error"]), FileNotFoundError)
        self.assertEqual(result["records"], [])
        self.assertEqual(result["counts"]["input"], 0)

    def test_wrong_header_raises_value_error(self):
        result = clean_file(self.write_csv(["1,2"], header="first,second"), self.error_log)
        self.assertEqual(type(result["error"]), ValueError)

    def test_empty_file_raises_value_error(self):
        path = os.path.join(self.folder, "empty.csv")
        open(path, "w", encoding="utf-8").close()
        self.assertEqual(type(clean_file(path, self.error_log)["error"]), ValueError)

    def test_header_only_file(self):
        result = clean_file(self.write_csv([]), self.error_log)
        self.assertEqual((result["records"], result["counts"]["input"]), ([], 0))
        self.assertIsNone(result["error"])

    def test_file_with_no_valid_rows(self):
        lines = ["T0001,U001", ",,,,,,,,", "a,b,c,d,e,f,g,h,i,j,k"]
        result = clean_file(self.write_csv(lines), self.error_log)
        self.assertEqual(result["records"], [])
        self.assertEqual(result["counts"]["skipped"], 3)

    def test_bad_date_keeps_the_row_and_bad_amount_skips_it(self):
        result = clean_file(self.write_csv([
            "T0001,U001,31-02-23,Expense,Food,10,Cash,Pune,Lunch",       # impossible date
            "T0002,U002,2023-01-01,Expense,Food,abc,Cash,Pune,Lunch",    # unreadable amount
            "T0003,U003,2023-01-01,Expense,Food,nan,Cash,Pune,Lunch",    # not a number
        ]), self.error_log)
        self.assertEqual(len(result["records"]), 1)
        self.assertIsNone(result["records"][0]["date"])
        self.assertEqual(result["counts"]["skipped"], 2)

    def test_run_reports_missing_model_classes_instead_of_crashing(self):
        with mock.patch("budgetwise.pipeline.implementation.runner.Transaction", None):
            result = run(self.write_csv(SMALL_FILE), error_log=self.error_log)
        self.assertEqual(result["transactions"], [])
        self.assertIn("no Transaction class", result["error"])
        self.assertEqual(result["counts"]["valid"], 4)        # cleaning still happened


# Building objects (run): needs budgetwise.models

class ObjectTests(PipelineTestCase):
    def setUp(self):
        super().setUp()
        self.result = run(self.write_csv(SMALL_FILE), error_log=self.error_log)
        self.by_id = {}
        for transaction in self.result["transactions"]:
            self.by_id.setdefault(transaction.get_transaction_id(), []).append(transaction)

    def test_transactions_are_a_list_of_objects(self):
        self.assertIsNone(self.result["error"])
        self.assertIsInstance(self.result["transactions"], list)
        self.assertEqual(len(self.result["transactions"]), 4)
        self.assertEqual(self.result["counts"]["returned"], 4)

    def test_class_is_chosen_from_transaction_type(self):
        self.assertIsInstance(self.by_id["T0001"][0], ExpenseTransaction)
        self.assertIsInstance(self.by_id["T0002"][0], IncomeTransaction)

    def test_cleaned_values_reach_the_object(self):
        transaction = self.by_id["T0001"][0]
        self.assertEqual(transaction.get_date(), "2022-08-05")
        self.assertEqual(transaction.get_category(), "Food")
        self.assertEqual(transaction.get_amount(), 3888.0)
        self.assertEqual(transaction.get_original_currency(), "₹")

    def test_amount_is_unsigned_and_direction_comes_from_type(self):
        transaction = self.by_id["T0001"][0]          # raw amount was negative
        self.assertGreater(transaction.get_amount(), 0)
        self.assertLess(transaction.get_signed_amount(), 0)       # it is an Expense
        self.assertGreater(self.by_id["T0002"][0].get_signed_amount(), 0)

    def test_row_with_no_date_becomes_an_object_without_a_date(self):
        self.assertIsNone(self.by_id["T0002"][0].get_date())
        self.assertFalse(self.by_id["T0002"][0].has_date())

    def test_repeated_id_rows_are_both_objects(self):
        self.assertEqual(len(self.by_id["T0001"]), 2)

    def test_skipped_rows_are_not_objects(self):
        for transaction_id in ("T0003", "T0004", "T0005", "T0007"):
            self.assertNotIn(transaction_id, self.by_id)


class NoFactoryTests(unittest.TestCase):
    """Both paths: picking the subclass, and using create() if one is added."""

    def setUp(self):
        from budgetwise.pipeline.implementation import runner
        self.runner = runner
        self.record = {"transaction_type": "Expense", "transaction_id": "T1",
                       "user_id": "U1", "date": "2023-01-05", "category": "Food",
                       "amount": 10.0, "payment_mode": "Cash",
                       "original_currency": "plain"}

    def build(self, kind):
        self.record["transaction_type"] = kind
        return self.runner._build_transaction(self.record)

    def test_the_real_transaction_class_has_no_factory(self):
        self.assertFalse(callable(getattr(Transaction, "create", None)))

    def test_expense_becomes_expense_object(self):
        self.assertIsInstance(self.build("Expense"), ExpenseTransaction)

    def test_income_becomes_income_object(self):
        self.assertIsInstance(self.build("Income"), IncomeTransaction)

    def test_other_type_is_refused_not_treated_as_income(self):
        with self.assertRaises(ValueError):
            self.build("Transfer")

    def test_a_factory_is_used_if_one_is_added_later(self):
        made = ExpenseTransaction("T9", "U9", None, "Food", 1.0)
        with mock.patch.object(Transaction, "create", create=True,
                               new=mock.Mock(return_value=made)):
            self.assertIs(self.build("Expense"), made)


class AccountTests(unittest.TestCase):
    """Each returned transaction goes into the cash or the bank account."""

    @classmethod
    def setUpClass(cls):
        cls.folder = tempfile.TemporaryDirectory()
        log = ErrorLog(os.path.join(cls.folder.name, "errors.log"))
        cls.result = run(DATASET_PATH, error_log=log)
        log.close()

    @classmethod
    def tearDownClass(cls):
        cls.folder.cleanup()

    def test_both_accounts_are_returned(self):
        self.assertEqual(sorted(self.result["accounts"]), ["bank", "cash", "unknown"])

    def test_cash_account_holds_only_cash(self):
        modes = {t.get_payment_mode() for t in self.result["accounts"]["cash"].get_transactions()}
        self.assertEqual(modes, {"Cash"})

    def test_bank_account_never_holds_cash_or_unknown(self):
        modes = {t.get_payment_mode() for t in self.result["accounts"]["bank"].get_transactions()}
        self.assertEqual(modes, {"Card", "UPI", "Bank Transfer"})

    def test_unknown_account_holds_only_unknown_payment_modes(self):
        modes = {t.get_payment_mode() for t in self.result["accounts"]["unknown"].get_transactions()}
        self.assertEqual(modes, {"Unknown"})

    def test_every_transaction_is_in_exactly_one_account(self):
        placed = sum(account.get_transaction_count()
                     for account in self.result["accounts"].values())
        self.assertEqual(placed, len(self.result["transactions"]))

    def test_account_breakdown_uses_each_accounts_getters(self):
        self.assertEqual(
            set(self.result["account_breakdown"]),
            set(self.result["accounts"]),
        )
        for kind, account in self.result["accounts"].items():
            with self.subTest(kind=kind):
                self.assertEqual(self.result["account_breakdown"][kind], {
                    "transaction_count": account.get_transaction_count(),
                    "total_spent": account.get_total_spent(),
                    "total_received": account.get_total_received(),
                })

    def test_run_builds_three_section_summary_from_accounts(self):
        result = self.result
        summary = result["summary"]
        self.assertEqual(
            set(summary) - {"scope", "selection", "selected_transactions",
                            "metrics"},
            {"total_breakdown", "monthly_breakdown"},
        )
        self.assertEqual(
            summary["selected_transactions"],
            sum(account.get_transaction_count()
                for account in result["accounts"].values()),
        )
        self.assertEqual(
            summary["total_breakdown"]["totals"]["expenses"],
            sum(account.get_total_spent()
                for account in result["accounts"].values()),
        )
        self.assertTrue(summary["monthly_breakdown"]["months"])

    def test_accounts_hold_the_same_objects_as_the_list(self):
        listed = {id(t) for t in self.result["transactions"]}
        for account in self.result["accounts"].values():
            for transaction in account.get_transactions():
                self.assertIn(id(transaction), listed)


class FilterTests(PipelineTestCase):
    def setUp(self):
        super().setUp()
        self.path = self.write_csv(SMALL_FILE)

    def ids(self, **filters):
        result = run(self.path, error_log=self.error_log, **filters)
        return [t.get_transaction_id() for t in result["transactions"]]

    def test_date_range_keeps_only_rows_inside_it(self):
        self.assertEqual(self.ids(start="2023-01-01", end="2023-12-31"), ["T0001", "T0006"])

    def test_date_range_includes_its_first_and_last_day(self):
        self.assertEqual(self.ids(start="2023-02-01", end="2023-03-09"), ["T0001", "T0006"])

    def test_rows_with_no_date_are_left_out_of_a_date_range(self):
        self.assertNotIn("T0002", self.ids(start="2000-01-01", end="2099-12-31"))

    def test_only_a_start_or_only_an_end(self):
        self.assertEqual(self.ids(start="2023-03-01"), ["T0001"])
        self.assertEqual(self.ids(end="2022-12-31"), ["T0001"])

    def test_category_filter_is_applied_after_normalizing(self):
        # 'Fod' and 'FOOD' in the file both match 'food' typed by the user.
        self.assertEqual(self.ids(category="food"), ["T0001", "T0001"])

    def test_uncategorized_can_be_selected(self):
        self.assertEqual(self.ids(category="Uncategorized"), ["T0006"])

    def test_nothing_matching_is_an_empty_list_not_an_error(self):
        result = run(self.path, start="1999-01-01", end="1999-12-31", error_log=self.error_log)
        self.assertEqual(result["transactions"], [])
        self.assertIsNone(result["error"])

    def test_filters_do_not_change_the_cleaning_counts(self):
        counts = run(self.path, category="Food", error_log=self.error_log)["counts"]
        self.assertEqual((counts["input"], counts["valid"], counts["returned"]), (9, 4, 2))

    def test_filtering_leaves_every_cleaning_count_and_record_unchanged(self):
        # Review item S07: only "returned" and the accounts may differ.
        everything = run(self.path, error_log=self.error_log)
        filtered = run(self.path, category="Food", error_log=self.error_log)
        self.assertEqual(filtered["records"], everything["records"])
        for name in ("input", "duplicates", "skipped", "valid", "corrected",
                     "flagged", "repeated_ids", "by_reason", "objects_built"):
            self.assertEqual(filtered["counts"][name], everything["counts"][name], name)

    def test_budget_comparisons_are_built_from_account_transactions(self):
        result = run(self.path, error_log=self.error_log)
        comparisons = {
            item["month"]: item["categories"]
            for item in result["budget_comparisons"]
        }

        food_august = next(
            item for item in comparisons["2022-08"]
            if item["category"] == "Food"
        )
        self.assertEqual(food_august["actual"], 3888.0)
        self.assertEqual(food_august["status"], "under")
        self.assertIsNone(next(
            item for item in comparisons["2023-02"]
            if item["category"] == "Uncategorized"
        )["limit"])

    def test_partial_date_filter_is_recorded_in_budget_comparison(self):
        result = run(
            self.path,
            start="2022-08-05",
            end="2022-08-05",
            error_log=self.error_log,
        )
        comparison = result["budget_comparisons"][0]
        self.assertEqual(comparison["month"], "2022-08")
        self.assertEqual(comparison["period"], {
            "start": "2022-08-05",
            "end": "2022-08-05",
            "full_month": False,
        })

    def test_category_filter_limits_budget_results_to_selected_category(self):
        result = run(self.path, category="Food", error_log=self.error_log)
        self.assertTrue(result["budget_comparisons"])
        self.assertTrue(all(
            item["category"] == "Food"
            for month in result["budget_comparisons"]
            for item in month["categories"]
        ))


# Regression tests for Phase 2 review items S04, S06, S07, S12

CLEAN_ROW = "{id},U001,2023-01-0{day},Expense,Food,{amount},Cash,Pune,{note}"


class RowValidationTests(PipelineTestCase):
    """S04: every problem validate_raw_row() finds reaches the log."""

    def setUp(self):
        super().setUp()
        self.result = clean_file(self.write_csv([
            "X99,U001,2023-01-01,Expense,Food,10,Cash,Pune,Lunch",     # 2 odd id: KEPT
            ",U002,2023-01-02,Expense,Food,10,Cash,Pune,Lunch",        # 3 no id: skipped
            "T0003,,2023-01-03,Refund,Food,10,Cash,Pune,Lunch",        # 4 two problems
            "T0004,U004,2023-01-04,Expense,Food,10,Cash,Pune,Lunch",   # 5 clean
        ]), self.error_log)
        self.issues = [(line, field, reason) for line, field, reason, _ in self.result["issues"]]

    def test_unusual_id_is_kept_and_flagged(self):
        self.assertEqual([r["transaction_id"] for r in self.result["records"]], ["X99", "T0004"])
        self.assertIn((2, "transaction_id", "malformed_row"), self.issues)
        self.assertEqual(self.result["counts"]["flagged"], 1)

    def test_missing_id_is_skipped_and_the_field_is_recorded(self):
        self.assertIn((3, "transaction_id", "missing_required_field"), self.issues)
        self.assertEqual(self.result["counts"]["skipped"], 2)

    def test_every_problem_on_a_row_is_logged_not_just_the_first(self):
        on_line_4 = [(field, reason) for line, field, reason in self.issues if line == 4]
        self.assertEqual(on_line_4, [("user_id", "missing_required_field"),
                                     ("transaction_type", "missing_required_field")])

    def test_the_log_file_itself_holds_the_field_and_the_detail(self):
        lines = self.error_log.read()
        odd = [line for line in lines if line.startswith("line=2 ")]
        self.assertEqual(len(odd), 1)
        self.assertIn("field=transaction_id reason=malformed_row", odd[0])
        self.assertIn("X99", odd[0])                       # the raw value
        missing = [line for line in lines if line.startswith("line=3 ")]
        self.assertEqual(len(missing), 1)
        self.assertIn("field=transaction_id reason=missing_required_field", missing[0])

    def test_clean_row_has_no_issues(self):
        self.assertEqual([issue for issue in self.issues if issue[0] == 5], [])


class FlaggedCountTests(PipelineTestCase):
    """S06: repeated-ID flags are included in the flagged row count."""

    def clean(self, *lines):
        return clean_file(self.write_csv(lines), self.error_log)["counts"]

    def test_two_clean_rows_sharing_an_id_are_both_flagged(self):
        counts = self.clean(
            CLEAN_ROW.format(id="T0001", day=1, amount=10, note="Lunch"),
            CLEAN_ROW.format(id="T0001", day=2, amount=20, note="Dinner"),
        )
        self.assertEqual(counts["repeated_ids"], 1)                     # one distinct ID
        self.assertEqual(counts["by_reason"]["repeated_transaction_id"], 2)   # two rows
        self.assertEqual(counts["flagged"], 2)
        self.assertEqual(counts["corrected"], 0)

    def test_a_second_concern_on_a_row_does_not_count_it_twice(self):
        counts = self.clean(
            CLEAN_ROW.format(id="T0001", day=1, amount=10, note="..."),   # + note concern
            CLEAN_ROW.format(id="T0001", day=2, amount=20, note="Dinner"),
        )
        self.assertEqual(counts["flagged"], 2)

    def test_a_row_can_be_both_corrected_and_flagged_once_each(self):
        counts = self.clean(
            "T0001,U001,01/02/2023,Expense,Fod,₹10,cash,Pune,...",       # corrected + flagged
            CLEAN_ROW.format(id="T0002", day=2, amount=20, note="Dinner"),  # neither
        )
        self.assertEqual((counts["corrected"], counts["flagged"]), (1, 1))

    def test_rows_with_no_issue_are_in_neither_count(self):
        counts = self.clean(CLEAN_ROW.format(id="T0001", day=1, amount=10, note="Lunch"))
        self.assertEqual((counts["corrected"], counts["flagged"], counts["by_reason"]), (0, 0, {}))


class FailureBoundaryTests(PipelineTestCase):
    """S12: an unexpected failure on one row never stops the later rows."""

    LINES = [
        CLEAN_ROW.format(id="T0001", day=1, amount=10, note="Lunch"),
        CLEAN_ROW.format(id="T0002", day=2, amount=20, note="Dinner"),
        CLEAN_ROW.format(id="T0003", day=3, amount=30, note="Tea"),
    ]

    def test_failure_inside_the_duplicate_check_is_contained(self):
        calls = {"n": 0}

        def failing_once(raw, seen):
            calls["n"] += 1
            if calls["n"] == 2:
                raise TypeError("unhashable type: 'list'")
            return False

        with mock.patch(RUNNER + ".is_duplicate", failing_once):
            result = clean_file(self.write_csv(self.LINES), self.error_log)
        self.assertIsNone(result["error"])
        self.assertEqual([r["transaction_id"] for r in result["records"]], ["T0001", "T0003"])
        counts = result["counts"]
        self.assertEqual((counts["input"], counts["valid"], counts["skipped"]), (3, 2, 1))

    def test_the_diagnostic_names_the_real_error_not_a_missing_field(self):
        with mock.patch(RUNNER + ".parse_date", side_effect=RuntimeError("boom")):
            result = clean_file(self.write_csv(self.LINES[:1]), self.error_log)
        self.assertEqual(result["counts"]["by_reason"], {"malformed_row": 1})
        self.assertIn("RuntimeError: boom", result["issues"][0][3])
        self.assertIn("RuntimeError: boom", self.error_log.read()[0])

    def test_two_loads_keep_independent_counts(self):
        path = self.write_csv(SMALL_FILE)
        first = clean_file(path, self.error_log)
        second = clean_file(path, self.error_log)
        self.assertEqual(first["counts"], second["counts"])
        self.assertEqual(len(first["issues"]), len(second["issues"]))
        # The log file is in append mode (Patrick's choice), so it holds both.
        self.assertEqual(len(self.error_log.read()), 2 * len(first["issues"]))


class ObjectFailureTests(PipelineTestCase):
    """S07: a record the classes refuse is counted consistently everywhere."""

    def setUp(self):
        super().setUp()
        path = self.write_csv([
            CLEAN_ROW.format(id="T0001", day=1, amount=10, note="Lunch"),
            CLEAN_ROW.format(id="T0002", day=2, amount=20, note="Dinner"),
            CLEAN_ROW.format(id="T0003", day=3, amount=30, note="Tea"),
        ])
        real_build = __import__(RUNNER, fromlist=["x"])._build_transaction

        def refuse_one(record):
            if record["transaction_id"] == "T0002":
                raise ValueError("refused by the model")
            return real_build(record)

        with mock.patch(RUNNER + "._build_transaction", refuse_one):
            self.result = run(path, error_log=self.error_log)
        self.counts = self.result["counts"]

    def test_cleaning_counts_are_not_changed_by_an_object_failure(self):
        self.assertEqual((self.counts["input"], self.counts["valid"],
                          self.counts["skipped"], self.counts["duplicates"]), (3, 3, 0, 0))
        self.assertEqual(len(self.result["records"]), 3)       # unfiltered cleaned records

    def test_object_counts_reconcile_with_the_cleaned_records(self):
        self.assertEqual((self.counts["objects_built"], self.counts["objects_failed"]), (2, 1))
        self.assertEqual(self.counts["objects_built"] + self.counts["objects_failed"],
                         self.counts["valid"])
        self.assertEqual(self.counts["returned"], 2)
        self.assertEqual([t.get_transaction_id() for t in self.result["transactions"]],
                         ["T0001", "T0003"])

    def test_the_failure_is_in_by_reason_the_issues_and_the_log(self):
        self.assertEqual(self.counts["by_reason"], {"transaction_not_built": 1})
        self.assertEqual(sum(self.counts["by_reason"].values()), len(self.result["issues"]))
        lines = self.error_log.read()
        self.assertEqual(len(lines), 1)
        self.assertIn("line=3 field=row reason=transaction_not_built", lines[0])
        self.assertIn("refused by the model", lines[0])

    def test_the_row_that_failed_is_counted_as_flagged(self):
        self.assertEqual(self.counts["flagged"], 1)

    def test_the_failed_object_is_in_neither_account(self):
        accounts = self.result["accounts"]
        placed = sum(account.get_transaction_count() for account in accounts.values())
        self.assertEqual(placed, 2)


class ClassUseTests(PipelineTestCase):
    """Every model class the pipeline uses, and how it uses it."""

    def setUp(self):
        super().setUp()
        self.result = run(self.write_csv([
            "T0001,U001,2023-01-01,Expense,Food,10,Cash,Pune,Lunch",
            "T0002,U002,2023-01-02,Income,Salary,500,UPI,Pune,Pay",
            "T0003,U003,2023-01-03,Expense,Rent,300,Card,Pune,Rent",
            "T0004,U004,2023-01-04,Expense,Food,40,,Pune,Lunch",       # no payment mode
        ]), error_log=self.error_log)

    def test_every_object_is_a_child_class_and_also_a_transaction(self):
        kinds = [type(t) for t in self.result["transactions"]]
        self.assertEqual(kinds, [ExpenseTransaction, IncomeTransaction,
                                 ExpenseTransaction, ExpenseTransaction])
        for transaction in self.result["transactions"]:
            self.assertIsInstance(transaction, Transaction)      # inheritance
            self.assertIsNot(type(transaction), Transaction)     # never the parent

    def test_accounts_are_the_three_child_classes_of_account(self):
        accounts = self.result["accounts"]
        self.assertIs(type(accounts["cash"]), CashAccount)
        self.assertIs(type(accounts["bank"]), BankAccount)
        self.assertIs(type(accounts["unknown"]), UnknownAccount)
        for account in accounts.values():
            self.assertIsInstance(account, Account)

    def test_each_transaction_is_added_to_the_account_for_its_payment_mode(self):
        accounts = self.result["accounts"]
        self.assertEqual([t.get_transaction_id() for t in accounts["cash"].get_transactions()], ["T0001"])
        self.assertEqual([t.get_transaction_id() for t in accounts["bank"].get_transactions()],
                         ["T0002", "T0003"])
        self.assertEqual([t.get_transaction_id() for t in accounts["unknown"].get_transactions()],
                         ["T0004"])                                   # blank payment mode

    def test_account_totals_come_from_the_objects_it_holds(self):
        bank = self.result["accounts"]["bank"]
        self.assertEqual(bank.get_transaction_count(), 2)
        self.assertEqual(bank.get_total_spent(), 300.0)
        self.assertEqual(bank.get_total_received(), 500.0)
        self.assertTrue(bank.is_reconcilable())
        self.assertFalse(self.result["accounts"]["cash"].is_reconcilable())


# Checks on teammates' features (review items S05, S09)

class AmountBoundaryTests(PipelineTestCase):
    """S09: the 100,000,000 threshold and the sign rule, through the pipeline."""

    def clean(self, amount, kind="Expense"):
        line = f"T0001,U001,2023-01-01,{kind},Food,{amount},Cash,Pune,Lunch"
        return clean_file(self.write_csv([line]), self.error_log)

    def test_just_under_the_threshold_is_accepted(self):
        self.assertEqual(self.clean("99999999")["records"][0]["amount"], 99_999_999.0)

    def test_the_threshold_itself_is_rejected_and_logged(self):
        result = self.clean("100000000")
        self.assertEqual(result["records"], [])
        self.assertEqual(result["counts"]["by_reason"], {"sentinel_amount": 1})
        self.assertIn("field=amount reason=sentinel_amount", self.error_log.read()[0])

    def test_negative_expense_keeps_a_positive_amount_and_its_direction(self):
        record = self.clean("-1000")["records"][0]
        self.assertEqual((record["amount"], record["transaction_type"]), (1000.0, "Expense"))

    @until_fixed(_amount_syntax_is_validated())      # review S09, Patrick
    def test_malformed_minus_signs_are_rejected_not_silently_changed(self):
        result = self.clean("1-2")              # must never become 12
        self.assertEqual(result["records"], [])
        self.assertEqual(result["counts"]["skipped"], 1)


class LoaderStructureTests(PipelineTestCase):
    """S05: malformed CSV structure, end to end."""

    def test_explicit_blank_final_field_is_a_valid_row(self):
        result = clean_file(self.write_csv(
            ["T0001,U001,2023-01-01,Expense,Food,10,Cash,Pune,"]), self.error_log)
        self.assertEqual(len(result["records"]), 1)
        self.assertEqual(result["records"][0]["notes_quality"], "missing")

    @until_fixed(_loader_keeps_row_structure())      # review S05, Patrick
    def test_missing_final_field_is_malformed_not_a_blank_note(self):
        result = clean_file(self.write_csv(
            ["T0001,U001,2023-01-01,Expense,Food,10,Cash,Pune"]), self.error_log)
        self.assertEqual(result["records"], [])
        self.assertIn("malformed_row", result["counts"]["by_reason"])

    def test_rows_differing_only_in_a_surplus_field_are_not_duplicates(self):
        result = clean_file(self.write_csv([
            "T0001,U001,2023-01-01,Expense,Food,10,Cash,Pune,Lunch,EXTRA-A",
            "T0001,U001,2023-01-01,Expense,Food,10,Cash,Pune,Lunch,EXTRA-B",
        ]), self.error_log)
        self.assertEqual(result["counts"]["duplicates"], 0)
        self.assertEqual(result["counts"]["skipped"], 2)       # both malformed

    @until_fixed(_loader_rejects_duplicate_headers())  # review S05, Patrick
    def test_duplicate_header_name_gives_a_clear_file_error(self):
        result = clean_file(self.write_csv(
            ["T0001,U001,2023-01-01,Expense,Food,10,Cash,Pune,Lunch,99"],
            header=HEADER + ",amount"), self.error_log)
        self.assertIn("could not load", result["error"])


# Full dataset

@unittest.skipUnless(os.path.exists(DATASET_PATH), "raw dataset not found in data/raw/")
class FullDatasetTests(unittest.TestCase):
    """The G2 reconciliation on all 15,836 rows of the D01 dataset."""

    @classmethod
    def setUpClass(cls):
        cls.folder = tempfile.TemporaryDirectory()
        error_log = ErrorLog(os.path.join(cls.folder.name, "logs", "errors.log"))
        cls.result = clean_file(DATASET_PATH, error_log)
        error_log.close()
        cls.counts = cls.result["counts"]
        cls.reasons = cls.counts["by_reason"]

    @classmethod
    def tearDownClass(cls):
        cls.folder.cleanup()

    def test_input_equals_valid_plus_skipped_plus_duplicates(self):
        self.assertEqual(self.counts["input"], 15836)
        self.assertEqual(self.counts["duplicates"], 804)
        self.assertEqual(self.counts["skipped"], 170)
        self.assertEqual(self.counts["valid"], 14862)
        self.assertEqual(15836, 14862 + 170 + 804)

    def test_skipped_rows_are_blank_amounts_and_sentinels(self):
        self.assertEqual(self.reasons["missing_amount"], 170)
        # This dataset carries no 999999999 sentinels; the §4.5 rule still
        # runs, it simply never fires here. See D01.
        self.assertEqual(self.reasons.get("sentinel_amount", 0), 0)

    def test_rows_with_no_date_are_kept(self):
        undated = sum(1 for record in self.result["records"] if record["date"] is None)
        # 322 rows arrive blank; a further 2,259 hold a shape parse_date
        # cannot read, so 17% of valid rows end up with no date. Every
        # monthly figure excludes them - see D01.
        self.assertEqual(undated, 2581)
        self.assertEqual(self.reasons["missing_date"], 322)
        self.assertEqual(self.reasons["invalid_date"], 2259)
        self.assertEqual(322 + 2259, 2581)

    def test_no_sentinel_or_negative_amount_survives(self):
        for record in self.result["records"]:
            self.assertTrue(0 <= record["amount"] < 100_000_000)

    def test_every_date_is_iso(self):
        for record in self.result["records"]:
            if record["date"] is not None:
                self.assertRegex(record["date"], r"^\d{4}-\d{2}-\d{2}$")

    def test_flagged_and_corrected_counts_cover_every_reason(self):
        # S06: every repeated-ID row is flagged; no count exceeds valid rows.
        self.assertEqual(self.reasons["repeated_transaction_id"], 1846)
        self.assertGreaterEqual(self.counts["flagged"], 1846)
        self.assertLessEqual(self.counts["flagged"], self.counts["valid"])
        self.assertLessEqual(self.counts["corrected"], self.counts["valid"])
        self.assertEqual(sum(self.reasons.values()), len(self.result["issues"]))

    def test_income_and_expense_totals(self):
        totals = {"Income": 0.0, "Expense": 0.0}
        for record in self.result["records"]:
            totals[record["transaction_type"]] += record["amount"]
        self.assertEqual(totals, {"Income": 134_553_045.0, "Expense": 53_348_034.0})

    def test_repeated_ids_are_all_kept(self):
        self.assertEqual(self.counts["repeated_ids"], 163)
        self.assertEqual(self.reasons["repeated_transaction_id"], 328)


if __name__ == "__main__":
    unittest.main()
