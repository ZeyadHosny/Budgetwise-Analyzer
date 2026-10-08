"""
Tests for parser.py   (column: date, task P2.1)
Run from the repository root:
    python -m unittest budgetwise.cleaning.dates.testing.test_parser -v
"""
import csv
import os
import unittest
from collections import Counter

from budgetwise.cleaning.dates import (
    DATE_NORMALIZED,
    INVALID_DATE,
    MISSING_DATE,
    find_date_format,
    is_ambiguous_date,
    parse_date,
)

# ---- helper: load one column of the real dataset, if the file is here ----
# The raw dataset lives in data/raw/ at the top of the repository.
REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), *[os.pardir] * 4))
DATASET_PATH = os.path.join(REPO_ROOT, "data", "raw", "budgetwise_finance_dataset.csv")
if not os.path.exists(DATASET_PATH):
    DATASET_PATH = None


def load_column(column):
    """Return every raw value of one column (all 15,900 rows)."""
    with open(DATASET_PATH, encoding="utf-8", newline="") as csv_file:
        return [row[column] for row in csv.DictReader(csv_file)]


class ValidFormatTests(unittest.TestCase):
    """The four formats found in Phase 1, with the examples from that report."""

    def test_iso_date_is_kept_with_no_reason(self):
        self.assertEqual(parse_date("2023-04-25"), ("2023-04-25", []))

    def test_slash_date_is_month_first(self):
        self.assertEqual(parse_date("08/05/2022"), ("2022-08-05", [DATE_NORMALIZED]))

    def test_hyphen_two_digit_year_is_day_first(self):
        self.assertEqual(parse_date("31-12-23"), ("2023-12-31", [DATE_NORMALIZED]))

    def test_hyphen_four_digit_year_is_day_first(self):
        self.assertEqual(parse_date("21-09-2024"), ("2024-09-21", [DATE_NORMALIZED]))

    def test_outer_spaces_are_ignored(self):
        self.assertEqual(parse_date(" 2023-04-25 "), ("2023-04-25", [DATE_NORMALIZED]))

    def test_leap_day_is_accepted(self):
        self.assertEqual(parse_date("02/29/2024")[0], "2024-02-29")
        self.assertEqual(parse_date("29-02-24")[0], "2024-02-29")

    def test_find_date_format(self):
        self.assertEqual(find_date_format("2023-04-25"), "YYYY-MM-DD")
        self.assertEqual(find_date_format("08/05/2022"), "MM/DD/YYYY")
        self.assertEqual(find_date_format("31-12-23"), "DD-MM-YY")
        self.assertEqual(find_date_format("21-09-2024"), "DD-MM-YYYY")
        self.assertIsNone(find_date_format("December 22 2021"))


class AmbiguousDateTests(unittest.TestCase):
    """Day and month both 12 or less: the mandatory convention decides."""

    def test_ambiguous_slash_date_is_month_then_day(self):
        self.assertEqual(parse_date("04/11/2024")[0], "2024-04-11")

    def test_ambiguous_hyphen_two_digit_year_is_day_then_month(self):
        self.assertEqual(parse_date("04-11-24")[0], "2024-11-04")

    def test_ambiguous_hyphen_four_digit_year_is_day_then_month(self):
        self.assertEqual(parse_date("04-11-2024")[0], "2024-11-04")

    def test_same_digits_differ_by_separator(self):
        self.assertEqual(parse_date("03/07/2022")[0], "2022-03-07")
        self.assertEqual(parse_date("03-07-22")[0], "2022-07-03")

    def test_is_ambiguous_date(self):
        for raw in ("04/11/2024", "12/12/2021", "01-02-23", "05-06-2022"):
            with self.subTest(raw=raw):
                self.assertTrue(is_ambiguous_date(raw))
        for raw in ("08/25/2022", "31-12-23", "2023-04-05", "", None, "junk"):
            with self.subTest(raw=raw):
                self.assertFalse(is_ambiguous_date(raw))


class MissingDateTests(unittest.TestCase):
    def test_missing_values(self):
        for raw in (None, "", "   ", "N/A", "n/a"):
            with self.subTest(raw=raw):
                self.assertEqual(parse_date(raw), (None, [MISSING_DATE]))


class InvalidDateTests(unittest.TestCase):
    def test_impossible_calendar_dates(self):
        for raw in ("02/30/2023", "31-02-23", "31-04-2024", "2023-02-29", "2023-13-01", "00/10/2022"):
            with self.subTest(raw=raw):
                self.assertEqual(parse_date(raw), (None, [INVALID_DATE]))

    def test_slash_date_written_day_first_is_not_silently_swapped(self):
        # 25/12/2023 is not a valid MM/DD/YYYY date. It must NOT become 25 December.
        self.assertEqual(parse_date("25/12/2023"), (None, [INVALID_DATE]))

    def test_hyphen_date_written_month_first_is_not_silently_swapped(self):
        self.assertEqual(parse_date("12-25-23"), (None, [INVALID_DATE]))

    def test_unrecognized_formats_are_never_guessed(self):
        junk = ("December 22 2021", "2022/12/09", "29/10/19", "8/5/2022", "2023-4-5",
                "20230425", "25.12.2023", "2023-04-25T10:00", "asdfgh", "!!!", "12345")
        for raw in junk:
            with self.subTest(raw=raw):
                self.assertEqual(parse_date(raw), (None, [INVALID_DATE]))

    def test_non_text_input_does_not_crash(self):
        for raw in (20230425, 3.5, ["2023-04-25"], {"date": 1}, True):
            with self.subTest(raw=raw):
                self.assertEqual(parse_date(raw), (None, [INVALID_DATE]))


@unittest.skipUnless(DATASET_PATH, "raw dataset not found in data/raw/")
class FullDatasetTests(unittest.TestCase):
    """Every count below comes from the Phase 1 date profile (15,900 rows)."""

    @classmethod
    def setUpClass(cls):
        cls.raw_values = load_column("date")
        cls.results = [parse_date(raw) for raw in cls.raw_values]

    def test_format_counts(self):
        formats = Counter(find_date_format(raw) for raw in self.raw_values)
        self.assertEqual(formats["YYYY-MM-DD"], 6091)
        self.assertEqual(formats["MM/DD/YYYY"], 4676)
        self.assertEqual(formats["DD-MM-YY"], 3044)
        self.assertEqual(formats["DD-MM-YYYY"], 1603)

    def test_reason_counts(self):
        reasons = Counter(reason for _, found in self.results for reason in found)
        self.assertEqual(reasons[MISSING_DATE], 486)
        self.assertEqual(reasons[DATE_NORMALIZED], 4676 + 3044 + 1603)
        self.assertEqual(reasons[INVALID_DATE], 0)

    def test_ambiguous_date_counts(self):
        ambiguous = Counter(
            find_date_format(raw) for raw in self.raw_values if is_ambiguous_date(raw)
        )
        self.assertEqual(ambiguous["MM/DD/YYYY"], 1865)   # the Phase 1 figure
        self.assertEqual(ambiguous["DD-MM-YY"], 1198)
        self.assertEqual(ambiguous["DD-MM-YYYY"], 650)

    def test_every_cleaned_date_is_iso_and_between_2021_and_2024(self):
        for value, _ in self.results:
            if value is not None:
                self.assertRegex(value, r"^\d{4}-\d{2}-\d{2}$")
                self.assertTrue("2021-01-01" <= value <= "2024-12-31", value)


if __name__ == "__main__":
    unittest.main()
