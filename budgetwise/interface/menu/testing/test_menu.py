# Tests for the menu.   Task P3.5 - Zeyad
# Run with:  python -m unittest discover -p "test_*.py"
# input() is replaced with unittest.mock.patch, which is standard library,
# so the menu can be driven without anyone typing at it.
# Standard library only - Project-1.pdf section 2.

import io
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest.mock import patch

# The implementation lives in the sibling folder, so it has to be added to
# the import path before the module can be imported.
IMPLEMENTATION_PATH = Path(__file__).resolve().parent.parent / "implementation"
sys.path.insert(0, str(IMPLEMENTATION_PATH))

import menu                                                  # noqa: E402

# A path that cannot exist, used to test the missing-log message.
MISSING_LOG_PATH = Path("does/not/exist.log")
# One real line from the error log task P2.8 writes.
SAMPLE_LOG_LINE = "line 275 | row | duplicate_row | T2217"


class TestPromptChoice(unittest.TestCase):
    """
    Description:
    - Reading a menu choice. Section 7 requires the program to survive bad
      input, so every invalid entry must reprompt rather than raise.
    """

    # Test that each of the five options is accepted
    def test_accepts_each_option(self):
        """
        Description:
        - All five options section 4.1 lists must be reachable.
        """
        for option in "12345":
            with patch("builtins.input", side_effect=[option]):
                self.assertEqual(menu.prompt_choice(), option)

    # Test that a number outside the range reprompts
    def test_rejects_out_of_range(self):
        """
        Description:
        - '9' is a number but not an option. The second value proves the
          loop came back and asked again rather than ending.
        """
        with patch("builtins.input", side_effect=["9", "1"]):
            self.assertEqual(menu.prompt_choice(), "1")

    # Test that text reprompts
    def test_rejects_text(self):
        """
        Description:
        - Text where a number was expected must not raise, which is the
          most likely thing a user actually types.
        """
        with patch("builtins.input", side_effect=["banana", "3"]):
            self.assertEqual(menu.prompt_choice(), "3")

    # Test that pressing enter on its own reprompts
    def test_rejects_empty(self):
        """
        Description:
        - An empty line is the easiest input to produce by accident.
        """
        with patch("builtins.input", side_effect=["", "5"]):
            self.assertEqual(menu.prompt_choice(), "5")


class TestDateRange(unittest.TestCase):
    """
    Description:
    - Menu option 2. Section 4.1: "asks for a start/end date and only
      loads/filters transactions within that range".
    """

    # Test that a valid range is returned unchanged
    def test_valid_range(self):
        """
        Description:
        - Two well-formed dates in the right order are returned as a tuple.
        """
        with patch("builtins.input",
                   side_effect=["2023-01-01", "2023-12-31"]):
            self.assertEqual(menu.prompt_date_range(),
                             ("2023-01-01", "2023-12-31"))

    # Test that a date that cannot exist reprompts
    def test_rejects_impossible_date(self):
        """
        Description:
        - '2023-13-45' has the right shape but names no real day. strptime
          catches it, and the prompt comes back.
        """
        with patch("builtins.input",
                   side_effect=["2023-13-45", "2023-01-01", "2023-12-31"]):
            self.assertEqual(menu.prompt_date_range(),
                             ("2023-01-01", "2023-12-31"))

    # Test that a different date format reprompts
    def test_rejects_wrong_format(self):
        """
        Description:
        - '01/01/2023' is a real date written the wrong way. Section 4.5
          standardizes on YYYY-MM-DD, so it is refused rather than guessed
          at.
        """
        with patch("builtins.input",
                   side_effect=["01/01/2023", "2023-01-01", "2023-12-31"]):
            self.assertEqual(menu.prompt_date_range()[0], "2023-01-01")

    # Test that a backwards range reprompts
    def test_rejects_end_before_start(self):
        """
        Description:
        - Both dates are valid but the range is backwards, so it could
          never match a row. Caught at the prompt rather than returning an
          empty result the user cannot explain.
        """
        with patch("builtins.input",
                   side_effect=["2023-06-01", "2022-01-01",
                                "2023-01-01", "2023-12-31"]):
            start, end = menu.prompt_date_range()
            self.assertLessEqual(start, end)

    # Test that a single-day range is allowed
    def test_same_day_range_is_allowed(self):
        """
        Description:
        - The boundary case. Start equal to end is a legitimate one-day
          range, not a backwards one.
        """
        with patch("builtins.input",
                   side_effect=["2023-07-14", "2023-07-14"]):
            self.assertEqual(menu.prompt_date_range(),
                             ("2023-07-14", "2023-07-14"))


class TestCategory(unittest.TestCase):
    """
    Description:
    - Menu option 3, matching against the 14 canonical categories.
    """

    def test_choices_match_normalized_category_names(self):
      self.assertEqual(menu.CATEGORIES, (
        "Bonus", "Education", "Entertainment", "Food", "Freelance",
        "Healthcare", "Investment", "Other", "Rent", "Salary",
        "Savings", "Transportation", "Uncategorized", "Utilities",
      ))

    # Test that an exact category name is accepted
    def test_exact_match(self):
        """
        Description:
        - The straightforward case.
        """
        with patch("builtins.input", side_effect=["Food"]):
            self.assertEqual(menu.prompt_category(), "Food")

    # Test that capitalization does not matter
    def test_case_insensitive(self):
        """
        Description:
        - The canonical name is returned whatever the user typed, so the
          filter downstream always receives the same spelling.
        """
        with patch("builtins.input", side_effect=["food"]):
            self.assertEqual(menu.prompt_category(), "Food")

    # Test that an unknown category reprompts
    def test_rejects_unknown_then_accepts(self):
        """
        Description:
        - An unrecognized name lists the available categories and asks
          again, rather than returning nothing and leaving the user to
          guess what went wrong.
        """
        with patch("builtins.input", side_effect=["Wobble", "Rent"]):
            self.assertEqual(menu.prompt_category(), "Rent")

    # Test that the placeholder category can be selected
    def test_uncategorized_is_selectable(self):
        """
        Description:
        - 285 rows have a blank category and become Uncategorized during
          cleaning, so the user must be able to ask for them.
        """
        with patch("builtins.input", side_effect=["uncategorized"]):
            self.assertEqual(menu.prompt_category(), "Uncategorized")


class TestErrorLog(unittest.TestCase):
    """
    Description:
    - Menu option 4. view_error_log is a placeholder for task P2.8, so
      these cases check only that option 4 shows something sensible rather
      than testing a log format this task does not own.
    - The function prints rather than returning, so stdout is captured with
      contextlib.redirect_stdout, which is standard library.
    """

    # Method to run view_error_log and capture what it printed
    @staticmethod
    def shown(path):
        """
        Description:
        - Call view_error_log and return what it printed, so a test can
          assert on screen output.

        Input arguments:
           path (Path): The log file to show.

        Return:
            str: Everything the function printed.
        """
        captured = io.StringIO()
        with redirect_stdout(captured):
            menu.view_error_log(path)
        return captured.getvalue()

    # Test the message shown before the log exists
    def test_missing_file_says_so(self):
        """
        Description:
        - No log yet means no load has run, or task P2.8 is not merged.
          Saying so is more useful than printing nothing.
        """
        self.assertIn("No error log", self.shown(MISSING_LOG_PATH))

    # Test that an existing log is shown
    def test_shows_an_existing_log(self):
        """
        Description:
        - When the file is there, its contents reach the screen. The line
          format belongs to task P2.8; this only checks it is displayed.
        """
        with tempfile.TemporaryDirectory() as directory:
            log_path = Path(directory) / "errors.log"
            log_path.write_text(SAMPLE_LOG_LINE, encoding="utf-8")
            self.assertIn("duplicate_row", self.shown(log_path))

    # Test that showing the log never raises
    def test_never_raises(self):
        """
        Description:
        - Section 4.1: the program must not crash on bad input. Option 4
          must survive a missing file, since that is the normal state
          before the first load.
        """
        self.shown(MISSING_LOG_PATH)
        self.shown(Path("output/logs/errors.log"))


class TestLoop(unittest.TestCase):
    """
    Description:
    - Section 4.1 requires a while loop rather than a one-shot script.
      Every case here would hang forever if the loop were wrong, so
      finishing at all is most of the assertion.
    """

    # Test that option 5 ends the loop
    def test_option_5_exits(self):
        """
        Description:
        - The loop must return on option 5. If it did not, this test would
          hang rather than fail.
        """
        with patch("builtins.input", side_effect=["5"]):
            menu.run_menu(pipeline_run=menu.demo_run)

    # Test a full load followed by an exit
    def test_option_1_then_exit(self):
        """
        Description:
        - The loop must come back and ask again after doing work, which is
          what makes it a menu rather than a script.
        """
        with patch("builtins.input", side_effect=["1", "5"]):
            menu.run_menu(pipeline_run=menu.demo_run)

    def test_successful_load_exports_cleaned_records_and_summary(self):
        record = {
            "transaction_id": "E1",
            "user_id": "U1",
            "date": "2026-01-05",
            "transaction_type": "Expense",
            "category": "Food",
            "amount": 50.0,
            "original_currency": "plain",
        }
        unselected_record = {
            "transaction_id": "I1",
            "user_id": "U1",
            "date": "2026-01-06",
            "transaction_type": "Income",
            "category": "Salary",
            "amount": 500.0,
            "original_currency": "plain",
        }
        result = {
            "records": [record, unselected_record],
            "transactions": [record],
            "counts": {"input": 2, "valid": 2, "returned": 1},
            "timings": {"load": 0.1, "clean": 0.2},
            "error": None,
        }
        with patch("builtins.input", side_effect=["1", "5"]), \
             patch.object(menu, "export_cleaned", return_value=Path("clean.csv")) as csv_export, \
             patch.object(menu, "export_summary", return_value=Path("summary.json")) as json_export:
            menu.run_menu(pipeline_run=lambda dataset: result, dataset="sample.csv")

        csv_export.assert_called_once()
        self.assertEqual(csv_export.call_args.args, ([record], "sample.csv"))
        self.assertEqual(json_export.call_args.args[1], "sample.csv")
        self.assertIs(csv_export.call_args.kwargs["when"],
                      json_export.call_args.kwargs["when"])
        summary = json_export.call_args.args[0]
        self.assertEqual(summary["counts"], {"input": 2, "valid": 2})
        self.assertEqual(summary["selection"], {"type": "all"})
        self.assertEqual(summary["selected_transactions"], 1)
        self.assertEqual(summary["totals"], {
            "income": 0.0, "expenses": 50.0, "net": -50.0,
        })
        self.assertEqual(summary["top_categories"], [("Food", 50.0)])

    # Test that bad input does not end the program
    def test_invalid_then_exit(self):
        """
        Description:
        - Section 7 robustness, at the loop level rather than the prompt
          level.
        """
        with patch("builtins.input", side_effect=["9", "banana", "5"]):
            menu.run_menu(pipeline_run=menu.demo_run)

    # Test that Ctrl+C exits without a traceback
    def test_ctrl_c_exits_cleanly(self):
        """
        Description:
        - A user interrupting the program should see a message, not a
          traceback. The same handler covers a closed input stream.
        """
        with patch("builtins.input", side_effect=KeyboardInterrupt):
            menu.run_menu(pipeline_run=menu.demo_run)

    # Test that the menu survives the pipeline being absent
    def test_missing_pipeline_does_not_crash(self):
        """
        Description:
        - Before task P2.10 is merged, option 1 must report that the
          feature is not available yet and return to the menu. This is what
          lets the menu be built and demonstrated independently.
        """
        with patch("builtins.input", side_effect=["1", "5"]):
            menu.run_menu(pipeline_run=None)


class TestSummary(unittest.TestCase):
    """
    Description:
    - The block printed after a load.
    """

    # Test that the summary shows the four counts
    def test_format_summary_shows_counts(self):
        """
        Description:
        - The real dataset figures: 15,900 rows in, 14,651 valid, 900
          duplicates removed and 349 skipped. All four must appear, with
          thousands separators, or the user cannot tell what happened to
          the missing rows.
        """
        output = menu.format_summary({
            "transactions": [1, 2, 3],
            "counts": {"input": 15900, "valid": 14651,
                       "duplicates": 900, "skipped": 349},
        })
        self.assertIn("15,900", output)
        self.assertIn("14,651", output)
        self.assertIn("900", output)


if __name__ == "__main__":
    unittest.main(verbosity=2)
