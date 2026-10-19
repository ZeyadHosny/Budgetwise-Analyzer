"""Tests for row checks: required columns, duplicates, malformed rows
and repeated IDs.

Run from the repository root:
    python3 -m unittest budgetwise.cleaning.rows.testing.test_raw_rows -v
"""
import csv
import io
import os
import unittest
from collections import Counter

from budgetwise.errorlog import Reason
from budgetwise.cleaning.rows import (
    EXPECTED_COLUMNS,
    find_repeated_ids,
    has_required_fields,
    is_duplicate,
    raw_duplicate_key,
    split_exact_duplicates,
    validate_raw_row,
)

# Internal helpers, imported directly for testing.
from budgetwise.cleaning.rows.implementation.raw_rows import (
    check_transaction_id,
    check_transaction_type,
    check_user_id,
)

# The raw dataset, if present, is in data/raw/ at the repository root.
REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), *[os.pardir] * 4))
DATASET_PATH = os.path.join(REPO_ROOT, "data", "raw", "budgetwise_synthetic_dirty.csv")
if not os.path.exists(DATASET_PATH):
    DATASET_PATH = None


def make_row(**changes):
    """A valid raw row. Keyword arguments replace individual fields."""
    row = {
        "transaction_id": "T4999", "user_id": "U018", "date": "2023-04-25",
        "transaction_type": "Expense", "category": "Educaton", "amount": "3888",
        "payment_mode": "card", "location": "Ahmedabad", "notes": "Movie tickets",
    }
    row.update(changes)
    return row


def numbered(*rows):
    """Number rows like the loader does: the first data row is row 2."""
    return list(enumerate(rows, start=2))


def read_csv_text(*lines):
    """Parse CSV text with csv.DictReader, exactly as the loader does."""
    text = "\n".join((",".join(EXPECTED_COLUMNS),) + lines) + "\n"
    return list(csv.DictReader(io.StringIO(text)))


class TransactionIdTests(unittest.TestCase):
    def test_valid_id_is_kept_exactly(self):
        for raw in ("T4999", "T12828", "T0001"):       # 4 and 5 digits both exist
            with self.subTest(raw=raw):
                self.assertEqual(check_transaction_id(raw), (raw, []))

    def test_outer_spaces_are_removed(self):
        self.assertEqual(check_transaction_id(" T4999 "), ("T4999", []))

    def test_missing_id_makes_the_row_unusable(self):
        for raw in ("", "   ", None, 4999, ["T4999"]):
            with self.subTest(raw=raw):
                self.assertEqual(check_transaction_id(raw), (None, [Reason.MALFORMED_ROW]))

    def test_unexpected_format_is_kept_but_reported(self):
        for raw in ("4999", "t4999", "T12", "T123456", "TX999", "U018"):
            with self.subTest(raw=raw):
                self.assertEqual(check_transaction_id(raw), (raw, [Reason.MALFORMED_ROW]))


class UserIdTests(unittest.TestCase):
    def test_valid_id_is_kept_exactly(self):
        for raw in ("U018", "U133", "U001"):
            with self.subTest(raw=raw):
                self.assertEqual(check_user_id(raw), (raw, []))

    def test_outer_spaces_are_removed(self):
        self.assertEqual(check_user_id(" U018 "), ("U018", []))

    def test_missing_id_makes_the_row_unusable(self):
        for raw in ("", "   ", None, 18, {}):
            with self.subTest(raw=raw):
                self.assertEqual(check_user_id(raw), (None, [Reason.MALFORMED_ROW]))

    def test_unexpected_format_is_kept_but_reported(self):
        for raw in ("018", "u018", "U18", "U0180", "T4999"):
            with self.subTest(raw=raw):
                self.assertEqual(check_user_id(raw), (raw, [Reason.MALFORMED_ROW]))


class TransactionTypeTests(unittest.TestCase):
    def test_standard_values(self):
        self.assertEqual(check_transaction_type("Expense"), ("Expense", []))
        self.assertEqual(check_transaction_type("Income"), ("Income", []))

    def test_capitalization_and_outer_spaces_do_not_matter(self):
        cases = {"expense": "Expense", "INCOME": "Income", " Income ": "Income"}
        for raw, expected in cases.items():
            with self.subTest(raw=raw):
                self.assertEqual(check_transaction_type(raw), (expected, []))

    def test_missing_type_makes_the_row_unusable(self):
        for raw in ("", "   ", None, 1, ["Expense"]):
            with self.subTest(raw=raw):
                self.assertEqual(check_transaction_type(raw), (None, [Reason.MALFORMED_ROW]))

    def test_unrecognized_type_is_not_guessed(self):
        # "-500": a sign is never read as a direction.
        for raw in ("Refund", "Expenses", "Inc", "Debit", "N/A", "-500"):
            with self.subTest(raw=raw):
                self.assertEqual(check_transaction_type(raw), (None, [Reason.MALFORMED_ROW]))


class DuplicateKeyTests(unittest.TestCase):
    def test_key_is_a_tuple_of_all_nine_raw_values(self):
        key = raw_duplicate_key(make_row())
        self.assertIsInstance(key, tuple)      # immutable, so it can go in a set
        self.assertEqual(len(key), 9)
        self.assertEqual((key[0], key[-1]), ("T4999", "Movie tickets"))

    def test_key_does_not_depend_on_dictionary_order(self):
        row = make_row()
        self.assertEqual(raw_duplicate_key(row), raw_duplicate_key(dict(reversed(list(row.items())))))


class IsDuplicateTests(unittest.TestCase):
    def test_first_time_false_then_true(self):
        seen_keys = set()
        self.assertFalse(is_duplicate(make_row(), seen_keys))   # first time
        self.assertTrue(is_duplicate(make_row(), seen_keys))    # identical copy
        self.assertEqual(len(seen_keys), 1)

    def test_same_id_with_a_different_field_is_not_a_duplicate(self):
        seen_keys = set()
        is_duplicate(make_row(), seen_keys)
        self.assertFalse(is_duplicate(make_row(amount="9999"), seen_keys))

    def test_raw_text_is_compared_exactly(self):
        seen_keys = set()
        is_duplicate(make_row(category="Food"), seen_keys)
        self.assertFalse(is_duplicate(make_row(category="food"), seen_keys))


class HasRequiredFieldsTests(unittest.TestCase):
    def test_true_for_a_usable_row_even_with_blank_optional_fields(self):
        self.assertTrue(has_required_fields(make_row()))
        self.assertTrue(has_required_fields(make_row(date="", category="", amount="", notes="")))

    def test_false_when_a_required_field_is_missing_or_invalid(self):
        for change in ({"transaction_id": ""}, {"user_id": ""}, {"transaction_type": ""},
                       {"transaction_type": "Refund"}):
            with self.subTest(change=change):
                self.assertFalse(has_required_fields(make_row(**change)))

    def test_false_for_things_that_are_not_rows(self):
        for bad in (None, 42, "text", {}):
            with self.subTest(bad=bad):
                self.assertFalse(has_required_fields(bad))


class ExactDuplicateTests(unittest.TestCase):
    def test_first_copy_is_kept_and_later_copies_are_duplicates(self):
        unique, duplicates = split_exact_duplicates(numbered(make_row(), make_row(), make_row()))
        self.assertEqual([number for number, _ in unique], [2])
        self.assertEqual([number for number, _ in duplicates], [3, 4])

    def test_same_id_but_one_different_field_is_not_a_duplicate(self):
        # Change each other column in turn.
        for column in EXPECTED_COLUMNS[1:]:
            with self.subTest(column=column):
                rows = numbered(make_row(), make_row(**{column: "different"}))
                unique, duplicates = split_exact_duplicates(rows)
                self.assertEqual((len(unique), duplicates), (2, []))

    def test_comparison_uses_raw_text_before_any_cleaning(self):
        # All four clean to the same values, but the raw rows differ.
        rows = numbered(
            make_row(category="Food"),
            make_row(category="food"),
            make_row(category="Food "),
            make_row(category="Food", amount="₹3888"),
        )
        unique, duplicates = split_exact_duplicates(rows)
        self.assertEqual((len(unique), duplicates), (4, []))

    def test_rows_with_blank_fields_can_be_duplicates(self):
        rows = numbered(make_row(date="", notes=""), make_row(date="", notes=""))
        self.assertEqual(len(split_exact_duplicates(rows)[1]), 1)

    def test_raw_rows_are_not_changed(self):
        rows = [make_row(), make_row()]
        before = [dict(row) for row in rows]
        split_exact_duplicates(numbered(*rows))
        self.assertEqual(rows, before)

    def test_empty_input(self):
        self.assertEqual(split_exact_duplicates([]), ([], []))


class ValidateRawRowTests(unittest.TestCase):
    def test_good_row_is_usable_with_no_problems(self):
        self.assertEqual(validate_raw_row(make_row()), (True, []))

    def test_blank_optional_fields_are_allowed(self):
        # All six optional columns blank.
        row = read_csv_text("T0001,U001,,Income,,,,,")[0]
        self.assertEqual(validate_raw_row(row), (True, []))

    def test_too_few_fields(self):
        row = read_csv_text("T0001,U001,2023-04-25,Expense")[0]
        self.assertEqual(validate_raw_row(row), (False, [("row", "too few fields")]))

    def test_too_many_fields(self):
        row = read_csv_text("T0001,U001,2023-04-25,Expense,Food,10,Cash,Pune,Lunch,extra")[0]
        self.assertEqual(validate_raw_row(row), (False, [("row", "too many fields")]))

    def test_missing_required_values_make_the_row_unusable(self):
        for column in ("transaction_id", "user_id", "transaction_type"):
            with self.subTest(column=column):
                usable, problems = validate_raw_row(make_row(**{column: ""}))
                self.assertFalse(usable)
                self.assertEqual([name for name, _ in problems], [column])

    def test_unrecognized_transaction_type_makes_the_row_unusable(self):
        usable, problems = validate_raw_row(make_row(transaction_type="Refund"))
        self.assertFalse(usable)
        self.assertEqual(problems[0][0], "transaction_type")

    def test_oddly_formatted_id_is_usable_but_reported(self):
        usable, problems = validate_raw_row(make_row(transaction_id="X99"))
        self.assertTrue(usable)
        self.assertEqual([name for name, _ in problems], ["transaction_id"])

    def test_things_that_are_not_rows_do_not_crash(self):
        for bad in (None, 42, "text", ["a", "b"], {}):
            with self.subTest(bad=bad):
                usable, problems = validate_raw_row(bad)
                self.assertFalse(usable)
                self.assertEqual(problems[0][0], "row")

    def test_row_is_not_changed(self):
        row = make_row()
        before = dict(row)
        validate_raw_row(row)
        self.assertEqual(row, before)


class RepeatedIdTests(unittest.TestCase):
    def test_counts_ids_seen_more_than_once(self):
        rows = numbered(make_row(), make_row(amount="1"), make_row(amount="2"),
                        make_row(transaction_id="T1"))
        self.assertEqual(find_repeated_ids(rows), {"T4999": 3})

    def test_rows_without_an_id_are_never_repeated_ids(self):
        # Rows with no ID never share an ID.
        rows = numbered(
            make_row(transaction_id=""), make_row(transaction_id="", amount="1"),
            make_row(transaction_id="   "), make_row(transaction_id="   ", amount="2"),
            make_row(transaction_id=None), make_row(transaction_id=None, amount="3"),
            make_row(transaction_id=7), make_row(transaction_id=7, amount="4"),
        )
        self.assertEqual(find_repeated_ids(rows), {})

    def test_eligible_repeated_id_is_still_counted_beside_missing_ids(self):
        rows = numbered(
            make_row(), make_row(amount="1"),                     # T4999 twice
            make_row(transaction_id=""), make_row(transaction_id="", amount="2"),
        )
        self.assertEqual(find_repeated_ids(rows), {"T4999": 2})

    def test_spaces_around_an_id_do_not_make_it_a_different_id(self):
        rows = numbered(make_row(transaction_id="T4999"), make_row(transaction_id=" T4999 ", amount="1"))
        self.assertEqual(find_repeated_ids(rows), {"T4999": 2})

    def test_rows_that_are_not_records_are_ignored(self):
        rows = [(2, "junk"), (3, None), (4, make_row()), (5, make_row(amount="1"))]
        self.assertEqual(find_repeated_ids(rows), {"T4999": 2})


@unittest.skipUnless(DATASET_PATH, "raw dataset not found in data/raw/")
class FullDatasetTests(unittest.TestCase):
    """Dirty dataset: 15,836 rows, 804 exact duplicates, 959 repeated IDs."""

    @classmethod
    def setUpClass(cls):
        with open(DATASET_PATH, encoding="utf-8", newline="") as csv_file:
            cls.rows = list(enumerate(csv.DictReader(csv_file), start=2))
        cls.unique, cls.duplicates = split_exact_duplicates(cls.rows)

    def test_duplicate_and_unique_counts(self):
        self.assertEqual(len(self.rows), 15836)
        self.assertEqual(len(self.duplicates), 804)
        self.assertEqual(len(self.unique), 15032)

    def test_no_row_is_malformed(self):
        self.assertTrue(all(validate_raw_row(row) == (True, []) for _, row in self.rows))

    def test_repeated_ids_in_raw_file(self):
        self.assertEqual(len(find_repeated_ids(self.rows)), 959)

    def test_repeated_ids_that_remain_after_duplicates_are_removed(self):
        # 754 of the 1,680 repeat only because of exact duplicates.
        # The other 926 are on rows that differ, and all are kept.
        self.assertEqual(len(find_repeated_ids(self.unique)), 172)
        self.assertEqual(len({row["transaction_id"] for _, row in self.unique}), 14858)

    def test_required_columns_are_all_valid_and_unchanged(self):
        for _, row in self.rows:
            self.assertEqual(check_transaction_id(row["transaction_id"]), (row["transaction_id"], []))
            self.assertEqual(check_user_id(row["user_id"]), (row["user_id"], []))
            self.assertEqual(
                check_transaction_type(row["transaction_type"]), (row["transaction_type"], [])
            )

    def test_user_and_type_counts_match_the_profile(self):
        self.assertEqual(len({row["user_id"] for _, row in self.rows}), 192)
        types = Counter(row["transaction_type"] for _, row in self.rows)
        self.assertEqual(types, {"Expense": 13442, "Income": 2394})

    def test_blank_counts_per_column_match_the_profile(self):
        expected = {"transaction_id": 0, "user_id": 0, "date": 344, "transaction_type": 0,
                    "category": 158, "amount": 178, "payment_mode": 503, "location": 722,
                    "notes": 1534}
        for column, count in expected.items():
            with self.subTest(column=column):
                self.assertEqual(sum(1 for _, row in self.rows if row[column] == ""), count)


if __name__ == "__main__":
    unittest.main()
