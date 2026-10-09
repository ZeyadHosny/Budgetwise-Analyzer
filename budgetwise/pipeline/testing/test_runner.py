"""
Tests for runner.py   (the cleaning pipeline, task P2.10)

Run from the repository root:
    python -m unittest budgetwise.pipeline.testing.test_runner -v

HOW THESE TESTS WORK
  * Each test writes a small CSV file to a temporary folder and runs the
    pipeline on it, so the real loader and the real cleaners are exercised
    together.
  * Each test gives the pipeline its own ErrorLog in the temporary folder,
    so the tests never write to the real output/logs/errors.log.
  * Tests that need transaction objects are skipped until budgetwise.models
    has its classes. The cleaning tests run without them.
  * FullDatasetTests check the counts on all 15,900 rows. They are skipped
    if the dataset is not in data/raw/.
"""

import os
import tempfile
import unittest
from unittest import mock

from budgetwise.errorlog import ErrorLog
from budgetwise.pipeline import clean_file, run

try:
    from budgetwise.models import ExpenseTransaction, IncomeTransaction
    HAVE_MODELS = True
except ImportError:
    HAVE_MODELS = False
NEEDS_MODELS = unittest.skipUnless(HAVE_MODELS, "budgetwise.models has no classes yet")

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), *[os.pardir] * 3))
DATASET_PATH = os.path.join(REPO_ROOT, "data", "raw", "budgetwise_finance_dataset.csv")

HEADER = "transaction_id,user_id,date,transaction_type,category,amount,payment_mode,location,notes"

# One row of every kind the pipeline has to deal with. The number in each
# comment is the row's line number in the file (the header is line 1).
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


# ==========================================================================
# CLEANING  (clean_file) - these run without the model classes
# ==========================================================================
class CleaningTests(PipelineTestCase):
    def setUp(self):
        super().setUp()
        self.result = clean_file(self.write_csv(SMALL_FILE), self.error_log)
        self.counts = self.result["counts"]
        self.by_line = {record["line_number"]: record for record in self.result["records"]}

    # ---- counts ---------------------------------------------------------
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

    # ---- cleaned values -------------------------------------------------
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

    def test_stripped_label_and_sign_are_logged(self):
        reasons = self.reasons_on_line(self.result, 2)
        self.assertIn("currency_label_stripped", reasons)
        self.assertIn("negative_amount_magnitude", reasons)

    # ---- the mandatory conventions (section 4.5) ------------------------
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
        self.assertEqual(self.reasons_on_line(self.result, 10), ["missing_required_field"])

    def test_missing_category_becomes_uncategorized(self):
        self.assertEqual(self.by_line[9]["category"], "Uncategorized")
        self.assertEqual(self.by_line[9]["payment_mode"], "Unknown")

    def test_placeholder_note_is_flagged_and_text_kept(self):
        self.assertEqual(self.by_line[4]["notes"], "...")
        self.assertIn("notes_low_information", self.reasons_on_line(self.result, 4))

    # ---- the error log --------------------------------------------------
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
        # 'Fod' and 'Food' clean to the same category, but the RAW rows
        # differ, so neither is a duplicate.
        path = self.write_csv([
            "T0001,U001,2023-01-01,Expense,Fod,10,Cash,Pune,Lunch",
            "T0001,U001,2023-01-01,Expense,Food,10,Cash,Pune,Lunch",
        ])
        result = clean_file(path, self.error_log)
        self.assertEqual(result["counts"]["duplicates"], 0)
        self.assertEqual([r["category"] for r in result["records"]], ["Food", "Food"])

    def test_loading_twice_gives_the_same_answer(self):
        # The menu can load more than once in a session. Rows seen in the
        # first load must not be treated as duplicates in the second.
        path = self.write_csv(SMALL_FILE)
        first = clean_file(path, self.error_log)
        second = clean_file(path, self.error_log)
        self.assertEqual(first["counts"], second["counts"])
        self.assertEqual(len(second["records"]), 4)


class BadInputTests(PipelineTestCase):
    def test_missing_file_gives_an_error_message_not_a_crash(self):
        result = clean_file(os.path.join(self.folder, "no_such_file.csv"), self.error_log)
        self.assertIn("could not load", result["error"])
        self.assertEqual(result["records"], [])
        self.assertEqual(result["counts"]["input"], 0)

    def test_wrong_header_does_not_crash(self):
        result = clean_file(self.write_csv(["1,2"], header="first,second"), self.error_log)
        self.assertIn("could not load", result["error"])

    def test_empty_file_does_not_crash(self):
        path = os.path.join(self.folder, "empty.csv")
        open(path, "w", encoding="utf-8").close()
        self.assertIn("could not load", clean_file(path, self.error_log)["error"])

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


# ==========================================================================
# BUILDING OBJECTS  (run) - these need budgetwise.models
# ==========================================================================
@NEEDS_MODELS
class ObjectTests(PipelineTestCase):
    def setUp(self):
        super().setUp()
        self.result = run(self.write_csv(SMALL_FILE), error_log=self.error_log)
        self.by_id = {}
        for transaction in self.result["transactions"]:
            self.by_id.setdefault(transaction.transaction_id, []).append(transaction)

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
        self.assertEqual(transaction.date, "2022-08-05")
        self.assertEqual(transaction.category, "Food")
        self.assertEqual(transaction.amount, 3888.0)

    def test_amount_is_unsigned_and_direction_comes_from_type(self):
        transaction = self.by_id["T0001"][0]          # raw amount was negative
        self.assertGreater(transaction.amount, 0)
        self.assertLess(transaction.signed_amount(), 0)       # it is an Expense
        self.assertGreater(self.by_id["T0002"][0].signed_amount(), 0)

    def test_row_with_no_date_becomes_an_object_without_a_date(self):
        self.assertIsNone(self.by_id["T0002"][0].date)

    def test_repeated_id_rows_are_both_objects(self):
        self.assertEqual(len(self.by_id["T0001"]), 2)

    def test_skipped_rows_are_not_objects(self):
        for transaction_id in ("T0003", "T0004", "T0005", "T0007"):
            self.assertNotIn(transaction_id, self.by_id)


@NEEDS_MODELS
class FilterTests(PipelineTestCase):
    def setUp(self):
        super().setUp()
        self.path = self.write_csv(SMALL_FILE)

    def ids(self, **filters):
        result = run(self.path, error_log=self.error_log, **filters)
        return [t.transaction_id for t in result["transactions"]]

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


# ==========================================================================
# THE FULL DATASET
# ==========================================================================
@unittest.skipUnless(os.path.exists(DATASET_PATH), "raw dataset not found in data/raw/")
class FullDatasetTests(unittest.TestCase):
    """The G2 reconciliation on all 15,900 rows."""

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
        self.assertEqual(self.counts["input"], 15900)
        self.assertEqual(self.counts["duplicates"], 900)
        self.assertEqual(self.counts["skipped"], 349)
        self.assertEqual(self.counts["valid"], 14651)
        self.assertEqual(15900, 14651 + 349 + 900)

    def test_skipped_rows_are_blank_amounts_and_sentinels(self):
        self.assertEqual(self.reasons["missing_amount"], 271)
        self.assertEqual(self.reasons["sentinel_amount"], 78)

    def test_rows_with_no_date_are_kept(self):
        undated = sum(1 for record in self.result["records"] if record["date"] is None)
        self.assertEqual(undated, 454)
        self.assertEqual(self.reasons["missing_date"], 454)

    def test_no_sentinel_or_negative_amount_survives(self):
        for record in self.result["records"]:
            self.assertTrue(0 <= record["amount"] < 100_000_000)

    def test_every_date_is_iso(self):
        for record in self.result["records"]:
            if record["date"] is not None:
                self.assertRegex(record["date"], r"^\d{4}-\d{2}-\d{2}$")

    def test_income_and_expense_totals(self):
        totals = {"Income": 0.0, "Expense": 0.0}
        for record in self.result["records"]:
            totals[record["transaction_type"]] += record["amount"]
        self.assertEqual(totals, {"Income": 144_624_974.0, "Expense": 165_749_066.0})

    def test_repeated_ids_are_all_kept(self):
        self.assertEqual(self.counts["repeated_ids"], 888)
        self.assertEqual(self.reasons["repeated_transaction_id"], 1846)


if __name__ == "__main__":
    unittest.main()
