"""Tests for notes quality.

Run from the repository root:
    python3 -m unittest budgetwise.cleaning.notes.testing.test_note_quality -v
"""
import csv
import os
import unittest
from collections import Counter

from budgetwise.cleaning.notes import classify_note_quality
from budgetwise.errorlog import Reason

LOW_INFORMATION = "low_information"
MEANINGFUL = "meaningful"
MISSING = "missing"
NOT_AVAILABLE = "not_available"
PLACEHOLDER_NOTES = ("...", "!!!", "xyz123", "test", "misc", "asdfgh")

# The raw dataset, if present, is in data/raw/ at the repository root.
REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), *[os.pardir] * 4))
DATASET_PATH = os.path.join(REPO_ROOT, "data", "raw", "budgetwise_synthetic_dirty.csv")
if not os.path.exists(DATASET_PATH):
    DATASET_PATH = None


def load_column(column):
    """Return every raw value of one column (all 15,836 rows)."""
    with open(DATASET_PATH, encoding="utf-8", newline="") as csv_file:
        return [row[column] for row in csv.DictReader(csv_file)]


class MeaningfulNoteTests(unittest.TestCase):
    def test_meaningful_note_is_unchanged_and_not_flagged(self):
        for raw in ("Electricity bill", "Movie tickets", "ATM withdrawal", "EMI payment"):
            with self.subTest(raw=raw):
                self.assertEqual(classify_note_quality(raw), (raw, MEANINGFUL, []))

    def test_text_is_never_rewritten(self):
        raw = "  Paid   RENT late  "
        self.assertEqual(classify_note_quality(raw)[0], raw)

    def test_a_note_that_only_contains_a_placeholder_word_is_meaningful(self):
        for raw in ("test drive fee", "misc groceries", "Testing kit"):
            with self.subTest(raw=raw):
                self.assertEqual(classify_note_quality(raw)[1], MEANINGFUL)


class LowInformationNoteTests(unittest.TestCase):
    def test_blank_is_missing(self):
        for raw in ("", "   "):
            with self.subTest(raw=raw):
                self.assertEqual(classify_note_quality(raw), (raw, MISSING, [Reason.NOTES_MISSING]))

    def test_none_is_missing_and_gives_empty_text(self):
        self.assertEqual(classify_note_quality(None), ("", MISSING, [Reason.NOTES_MISSING]))

    def test_na_uses_the_missing_reason_with_its_own_quality_flag(self):
        for raw in ("N/A", "n/a", " N/A "):
            with self.subTest(raw=raw):
                self.assertEqual(classify_note_quality(raw),
                                 (raw, NOT_AVAILABLE, [Reason.NOTES_MISSING]))

    def test_each_known_placeholder_is_flagged_and_kept(self):
        self.assertEqual(set(PLACEHOLDER_NOTES), {"...", "!!!", "xyz123", "test", "misc", "asdfgh"})
        for raw in PLACEHOLDER_NOTES:
            with self.subTest(raw=raw):
                self.assertEqual(
                    classify_note_quality(raw),
                    (raw, LOW_INFORMATION, [Reason.NOTES_LOW_INFORMATION])
                )

    def test_placeholder_match_ignores_capitals_and_outer_spaces(self):
        for raw in ("TEST", " Misc ", "XYZ123"):
            with self.subTest(raw=raw):
                self.assertEqual(classify_note_quality(raw)[1], LOW_INFORMATION)

    def test_non_text_input_does_not_crash(self):
        for raw in (123, 4.5, ["note"]):
            with self.subTest(raw=raw):
                self.assertEqual(classify_note_quality(raw)[1], MEANINGFUL)


@unittest.skipUnless(DATASET_PATH, "raw dataset not found in data/raw/")
class FullDatasetTests(unittest.TestCase):
    """Re-profiled against budgetwise_synthetic_dirty.csv (15,836 rows).

    COVERAGE WARNING. This dataset contains no placeholder notes and no
    "N/A" values, so LOW_INFORMATION and NOT_AVAILABLE are never produced
    here. The zero assertions below record that, but the real coverage of
    those two branches now rests entirely on the hand-written cases in
    PlaceholderTests, not on this dataset.
    """

    @classmethod
    def setUpClass(cls):
        cls.raw_values = load_column("notes")
        cls.results = [classify_note_quality(raw) for raw in cls.raw_values]

    def test_quality_counts_match_profile(self):
        qualities = Counter(quality for _, quality, _ in self.results)
        self.assertEqual(qualities, {MEANINGFUL: 14302, MISSING: 1534})
        self.assertEqual(qualities[LOW_INFORMATION], 0)
        self.assertEqual(qualities[NOT_AVAILABLE], 0)

    def test_reason_counts(self):
        reasons = Counter(reason for _, _, found in self.results for reason in found)
        self.assertEqual(reasons[Reason.NOTES_MISSING], 1534)
        self.assertEqual(reasons[Reason.NOTES_LOW_INFORMATION], 0)

    def test_every_note_is_returned_unchanged(self):
        for raw, (text, _, _) in zip(self.raw_values, self.results):
            self.assertEqual(text, raw)


if __name__ == "__main__":
    unittest.main()
