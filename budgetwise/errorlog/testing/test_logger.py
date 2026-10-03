import os
import tempfile
import unittest

from budgetwise.errorlog.implementation.logger import ErrorLog
from budgetwise.errorlog.implementation.reason_codes import Reason


class TestErrorLog(unittest.TestCase):

    def test_recorded_entry_appears_in_file(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            log_path = os.path.join(temp_dir, "errors.log")

            error_log = ErrorLog(log_path)

            error_log.record(
                line=10,
                field="amount",
                reason=Reason.MISSING_AMOUNT,
                raw=""
            )

            error_log.close()

            with open(log_path, "r", encoding="utf-8") as file:
                contents = file.read()

            self.assertIn("line=10", contents)
            self.assertIn("field=amount", contents)
            self.assertIn("reason=missing_amount", contents)
            self.assertIn("raw=''", contents)

    def test_log_folder_is_created(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            log_path = os.path.join(
                temp_dir,
                "output",
                "logs",
                "errors.log"
            )

            self.assertFalse(os.path.exists(os.path.dirname(log_path)))

            error_log = ErrorLog(log_path)

            self.assertTrue(os.path.isdir(os.path.dirname(log_path)))

            error_log.close()

    def test_counts_across_several_reasons(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            log_path = os.path.join(temp_dir, "errors.log")

            error_log = ErrorLog(log_path)

            error_log.record(
                1, "amount", Reason.MISSING_AMOUNT, ""
            )
            error_log.record(
                2, "amount", Reason.MISSING_AMOUNT, ""
            )
            error_log.record(
                3, "amount", Reason.SENTINEL_AMOUNT, "999999999"
            )
            error_log.record(
                4, "date", Reason.MISSING_DATE, ""
            )
            error_log.record(
                5, "amount", Reason.MISSING_AMOUNT, ""
            )

            counts = error_log.counts()

            self.assertEqual(counts[Reason.MISSING_AMOUNT], 3)
            self.assertEqual(counts[Reason.SENTINEL_AMOUNT], 1)
            self.assertEqual(counts[Reason.MISSING_DATE], 1)

            error_log.close()

    def test_read_returns_every_line(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            log_path = os.path.join(temp_dir, "errors.log")

            error_log = ErrorLog(log_path)

            error_log.record(
                1, "amount", Reason.MISSING_AMOUNT, ""
            )
            error_log.record(
                2, "date", Reason.MISSING_DATE, ""
            )
            error_log.record(
                3, "category", Reason.UNKNOWN_CATEGORY, "Movie"
            )

            lines = error_log.read()

            self.assertEqual(len(lines), 3)

            self.assertIn("line=1", lines[0])
            self.assertIn("line=2", lines[1])
            self.assertIn("line=3", lines[2])

            error_log.close()

    def test_raw_value_with_comma_does_not_break_format(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            log_path = os.path.join(temp_dir, "errors.log")

            error_log = ErrorLog(log_path)

            raw = "5,891"

            error_log.record(
                10,
                "amount",
                Reason.UNRECOGNIZED_AMOUNT_FORMAT,
                raw
            )

            lines = error_log.read()

            self.assertEqual(len(lines), 1)
            self.assertIn("raw='5,891'", lines[0])

            error_log.close()

    def test_raw_value_with_newline_does_not_break_format(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            log_path = os.path.join(temp_dir, "errors.log")

            error_log = ErrorLog(log_path)

            raw = "bad\namount"

            error_log.record(
                10,
                "amount",
                Reason.UNRECOGNIZED_AMOUNT_FORMAT,
                raw
            )

            lines = error_log.read()

            self.assertEqual(len(lines), 1)

            self.assertIn("raw='bad\\namount'", lines[0])

            error_log.close()

    def test_two_writes_do_not_interleave(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            log_path = os.path.join(temp_dir, "errors.log")

            error_log = ErrorLog(log_path)

            error_log.record(
                1,
                "amount",
                Reason.MISSING_AMOUNT,
                ""
            )

            error_log.record(
                2,
                "date",
                Reason.MISSING_DATE,
                ""
            )

            lines = error_log.read()

            self.assertEqual(len(lines), 2)

            self.assertTrue(lines[0].startswith("line=1"))
            self.assertTrue(lines[1].startswith("line=2"))

            error_log.close()


if __name__ == "__main__":
    unittest.main()