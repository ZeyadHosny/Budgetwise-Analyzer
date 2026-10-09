import os
import tempfile
import unittest

from budgetwise.errorlog import ErrorLog, Reason
from budgetwise.pipeline.implementation.amount_step import (
    clean_and_log_amount
)


class TestAmountStep(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp_dir.cleanup)

        self.log_path = os.path.join(
            self.temp_dir.name,
            "errors.log"
        )

        self.logger = ErrorLog(self.log_path)
        self.addCleanup(self.logger.close)

    def read_saved_log(self):
        with open(self.log_path, encoding="utf-8") as file:
            return file.readlines()

    def test_plain_amount_creates_no_log_entries(self):
        result = clean_and_log_amount(
            "1000",
            line=2,
            logger=self.logger
        )

        self.assertEqual(result, (1000.0, None, []))
        self.assertEqual(self.read_saved_log(), [])
        self.assertEqual(self.logger.counts(), {})

    def test_both_corrections_are_written_to_log(self):
        result = clean_and_log_amount(
            "-$1,000",
            line=7,
            logger=self.logger
        )

        self.assertEqual(
            result,
            (
                1000.0,
                "$",
                [
                    Reason.AMOUNT_NEGATIVE_TO_MAGNITUDE,
                    Reason.AMOUNT_FORMAT_NORMALIZED
                ]
            )
        )

        self.assertEqual(
            self.read_saved_log(),
            [
                (
                    "line=7 field=amount "
                    f"reason={Reason.AMOUNT_NEGATIVE_TO_MAGNITUDE} "
                    "raw='-$1,000'\n"
                ),
                (
                    "line=7 field=amount "
                    f"reason={Reason.AMOUNT_FORMAT_NORMALIZED} "
                    "raw='-$1,000'\n"
                )
            ]
        )

        self.assertEqual(
            self.logger.counts(),
            {
                Reason.AMOUNT_NEGATIVE_TO_MAGNITUDE: 1,
                Reason.AMOUNT_FORMAT_NORMALIZED: 1
            }
        )

    def test_invalid_amount_is_written_to_log(self):
        result = clean_and_log_amount(
            "1-2",
            line=8,
            logger=self.logger
        )

        self.assertEqual(
            result,
            (
                None,
                None,
                [Reason.UNRECOGNIZED_AMOUNT_FORMAT]
            )
        )

        self.assertEqual(
            self.read_saved_log(),
            [
                (
                    "line=8 field=amount "
                    f"reason={Reason.UNRECOGNIZED_AMOUNT_FORMAT} "
                    "raw='1-2'\n"
                )
            ]
        )

    def test_missing_amount_is_written_to_log(self):
        result = clean_and_log_amount(
            None,
            line=9,
            logger=self.logger
        )

        self.assertEqual(
            result,
            (None, None, [Reason.MISSING_AMOUNT])
        )

        self.assertEqual(
            self.read_saved_log(),
            [
                (
                    "line=9 field=amount "
                    f"reason={Reason.MISSING_AMOUNT} "
                    "raw=None\n"
                )
            ]
        )

    def test_sentinel_logs_only_exclusion_reason(self):
        result = clean_and_log_amount(
            "-$100,000,000",
            line=10,
            logger=self.logger
        )

        self.assertEqual(
            result,
            (None, None, [Reason.SENTINEL_AMOUNT])
        )

        self.assertEqual(
            self.read_saved_log(),
            [
                (
                    "line=10 field=amount "
                    f"reason={Reason.SENTINEL_AMOUNT} "
                    "raw='-$100,000,000'\n"
                )
            ]
        )


if __name__ == "__main__":
    unittest.main()
