"""End-to-end checks for menu inputs and outputs."""

import io
import re
import sys
sys.dont_write_bytecode = True
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from budgetwise.interface.menu.implementation import menu
from budgetwise.pipeline import run
# Import the shared harness from the other test file (no support files needed).
HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))
from budget_wise_analyzer_e2e_tests import WorkflowCase, row

CATEGORIES = ('Bonus', 'Education', 'Entertainment', 'Food', 'Freelance',
              'Healthcare', 'Investment', 'Other', 'Rent', 'Salary', 'Savings',
              'Transportation', 'Uncategorized', 'Utilities')
OPTIONS = ('1. Load full dataset', '2. Load transactions by date range',
           '3. Load transactions by category', '4. View error log', '5. Exit')


class PromptTests(unittest.TestCase):
    """Check both the parsed answer and feedback from each input prompt."""

    def prompt(self, function, answers, *args):
        remaining = iter(answers)
        prompts = []
        stream = io.StringIO()

        def answer(label):
            prompts.append(label)
            try:
                return next(remaining)
            except StopIteration:
                self.fail('Unexpected additional prompt: ' + label)

        with redirect_stdout(stream), patch('builtins.input', side_effect=answer):
            value = function(*args)
        self.assertIsNone(next(remaining, None), 'Prompt accepted an invalid input or exited early')
        self.assertNotIn('Traceback', stream.getvalue())
        return value, stream.getvalue(), prompts


def choice_check(raw, expected, invalid=False):
    def check(self):
        answers = [raw, expected] if invalid else [raw]
        value, output, prompts = self.prompt(menu.prompt_choice, answers)
        self.assertEqual(value, expected)
        self.assertEqual(prompts, ['Choose an option: '] * len(answers))
        self.assertEqual(output.count('Please choose 1 to 5.'), int(invalid))
    check.__doc__ = f'Main choice {raw!r}: ' + ('reject and recover' if invalid else f'accept as {expected}')
    return check


for choice in '12345':
    for variant, raw in [('plain', choice), ('whitespace', ' \t' + choice + '  ')]:
        setattr(PromptTests, f'test_choice_accept_{choice}_{variant}', choice_check(raw, choice))
for index, raw in enumerate(['', '   ', '0', '6', '-1', '99', '1.0', '+1', '01', 'one',
                             'exit', '1 2', '1\n2', '１', '١', 'None', 'x'*1000], 1):
    setattr(PromptTests, f'test_choice_reject_{index:02d}', choice_check(raw, '5', True))


def date_check(raw, expected=None, label='Start date'):
    def check(self):
        invalid = expected is None
        answers = [raw, '2024-02-29'] if invalid else [raw]
        value, output, prompts = self.prompt(menu.read_date, answers, label)
        self.assertEqual(value, '2024-02-29' if invalid else expected)
        self.assertEqual(prompts, [f'{label} (YYYY-MM-DD): '] * len(answers))
        self.assertEqual(output.count('Not a valid date.'), int(invalid))
        if invalid:
            self.assertIn('Use YYYY-MM-DD', output)
    check.__doc__ = f'{label} {raw!r}: ' + ('reject and recover' if expected is None else f'normalize to {expected}')
    return check


VALID_DATES = [('2024-02-29', '2024-02-29'), ('2000-02-29', '2000-02-29'),
               ('2023-12-31', '2023-12-31'), ('2024-01-01', '2024-01-01'),
               (' 2024-06-15\t', '2024-06-15'), ('2024-2-9', '2024-02-09'),
               ('1900-02-28', '1900-02-28'), ('9999-12-31', '9999-12-31')]
INVALID_DATES = ['', ' ', 'not-a-date', '2023-02-29', '1900-02-29', '2024-02-30',
                 '2024-04-31', '2024-13-01', '2024-00-01', '2024-01-00', '2024-01-32',
                 '2024/01/01', '01/31/2024', '31-01-24', '24-01-01',
                 '2024-01-01T12:00:00', '2024-01-01junk', '2024 -01-01',
                 '0000-01-01', '10000-01-01', '2024-01', 'x'*1000]
for label in ('Start date', 'End date'):
    prefix = label.split()[0].lower()
    for index, (raw, expected) in enumerate(VALID_DATES, 1):
        setattr(PromptTests, f'test_{prefix}_date_accept_{index:02d}', date_check(raw, expected, label))
    for index, raw in enumerate(INVALID_DATES, 1):
        setattr(PromptTests, f'test_{prefix}_date_reject_{index:02d}', date_check(raw, label=label))


def category_check(raw, expected, invalid=False):
    def check(self):
        answers = [raw, expected] if invalid else [raw]
        value, output, prompts = self.prompt(menu.prompt_category, answers)
        self.assertEqual(value, expected)
        self.assertEqual(prompts, ['Category (one of the above): '] * len(answers))
        for category in CATEGORIES:
            self.assertIn(category, output)
        self.assertEqual(output.count('is not one of the 14 categories'), int(invalid))
    check.__doc__ = f'Category {raw!r}: ' + ('reject and recover' if invalid else f'accept as {expected}')
    return check


for category in CATEGORIES:
    for variant, raw in [('canonical', category), ('lower', category.lower()),
                         ('upper', category.upper()), ('mixed_space', ' \t' + category.swapcase() + ' ' )]:
        setattr(PromptTests, f'test_category_accept_{category.lower()}_{variant}', category_check(raw, category))
for index, raw in enumerate(['', ' ', 'Unknown', 'Shopping', 'Fod', 'Foodd', 'Travel',
                             '1', 'Food,Rent', 'Food Rent', 'Fo od', 'food!', 'x'*1000], 1):
    setattr(PromptTests, f'test_category_reject_{index:02d}', category_check(raw, 'Food', True))


# A separate class sharing the helper, without inheriting the generated tests.
class DateRangeTests(unittest.TestCase):
    prompt = PromptTests.prompt

    def test_reversed_range_recovers_without_accepting_reversed_values(self):
        value, output, prompts = self.prompt(menu.prompt_date_range,
            ['2024-03-31', '2024-03-01', '2024-03-01', '2024-03-31'])
        self.assertEqual(value, ('2024-03-01', '2024-03-31'))
        self.assertEqual(len(prompts), 4)
        self.assertIn('end date (2024-03-01) is before the start date (2024-03-31)', output)


def range_check(start, end, outside):
    def check(self):
        value, output, prompts = self.prompt(menu.prompt_date_range, [start, end])
        self.assertEqual(value, (start, end))
        self.assertEqual(len(prompts), 2)
        self.assertIn('Rows with no date are excluded', output)
        self.assertEqual('falls outside' in output, outside)
    check.__doc__ = f'Accept range {start} to {end}; outside-hint warning={outside}'
    return check


for name, start, end, outside in [
    ('same_day', '2024-02-29', '2024-02-29', False),
    ('first_day', '2019-01-01', '2019-01-01', False),
    ('last_day', '2024-12-31', '2024-12-31', False),
    ('cross_year', '2023-12-31', '2024-01-01', False),
    ('full_span', '2019-01-01', '2024-12-31', False),
    ('overlap_left', '2018-12-01', '2019-01-01', False),
    ('overlap_right', '2024-12-31', '2025-01-31', False),
    ('enclosing', '2018-01-01', '2025-01-01', False),
    ('before', '2018-01-01', '2018-12-31', True),
    ('after', '2025-01-01', '2025-12-31', True),
]:
    setattr(DateRangeTests, f'test_range_{name}', range_check(start, end, outside))


class MenuWorkflowTests(WorkflowCase):
    """Assert visible messages alongside actual pipeline results and artifacts."""

    def counts_output(self, loaded, input_count, valid, duplicates, skipped):
        self.assertIn('Dataset cleaning:', self.last_stdout)
        self.assertIn('Selected results:', self.last_stdout)
        self.assertLess(self.last_stdout.index('Dataset cleaning:'),
                        self.last_stdout.index('Selected results:'))
        self.assertIn(f'Matching transactions: {loaded:,}', self.last_stdout)
        for label, expected in [('Rows read:', input_count), ('Valid rows:', valid),
                                ('Duplicates removed:', duplicates), ('Invalid rows skipped:', skipped)]:
            self.assertRegex(self.last_stdout, rf'(?m)^\s+{label}\s+{expected:,}\s*$')

    def test_startup_options_and_exit_output(self):
        self.session(self.dataset([]), ['5'])
        self.assertEqual(self.last_stdout.count('=== BudgetWise Finance Analyzer ==='), 1)
        positions = [self.last_stdout.index(option) for option in OPTIONS]
        self.assertEqual(positions, sorted(positions))
        self.assertIn('Choose an option:', self.last_stdout)
        self.assertTrue(self.last_stdout.rstrip().endswith('Goodbye.'))
        self.assertNotIn('Matching transactions:', self.last_stdout)

    def test_invalid_choice_then_load_and_exit(self):
        result, = self.session(self.dataset([row(25, date='2024-06-15')]), ['', '99', '1', '5'])
        self.totals(result, expenses=25)
        self.assertEqual(self.last_stdout.count('Please choose 1 to 5.'), 2)
        self.counts_output(1, 1, 1, 0, 0)

    def test_summary_counts_and_log_reference(self):
        valid = row(25, id='T0001', date='2024-06-15')
        result = self.load([valid, valid, row('BAD')])
        self.totals(result, expenses=25)
        self.counts_output(1, 3, 1, 1, 1)
        self.assertIn('for cleaning reasons.', self.last_stdout)
        self.assertIn(str(Path('output/logs/errors.log')), self.last_stdout)

    def test_clean_load_does_not_claim_skipped_or_duplicate_rows(self):
        self.load([row(10), row(20)])
        self.counts_output(2, 2, 2, 0, 0)
        self.assertNotIn('for cleaning reasons.', self.last_stdout)

    def test_empty_dataset_output(self):
        self.load([])
        self.counts_output(0, 0, 0, 0, 0)

    def test_empty_category_output(self):
        self.load([row(10)], category='Rent')
        self.counts_output(0, 1, 1, 0, 0)
        self.assertIn('Category Rent.', self.last_stdout)

    def test_empty_date_selection_output(self):
        self.load([row(10, date='2024-06-15')], start='2024-07-01', end='2024-07-31')
        self.counts_output(0, 1, 1, 0, 0)
        self.assertIn('Range 2024-07-01 to 2024-07-31.', self.last_stdout)

    def test_large_counts_are_formatted_without_rounding(self):
        # Presentation-only fixture, not a simulated pipeline calculation.
        output = menu.format_summary({'transactions': [None] * 1234,
                                      'counts': {'input': 1500, 'valid': 1234,
                                                 'duplicates': 200, 'skipped': 66}})
        self.assertIn('Matching transactions: 1,234', output)
        for label, expected in [('Rows read:', '1,500'), ('Valid rows:', '1,234'),
                                ('Duplicates removed:', '200'), ('Invalid rows skipped:', '66')]:
            self.assertRegex(output, rf'(?m)^\s+{label}\s+{expected}\s*$')

    def test_unavailable_pipeline_message_and_recovery(self):
        captured = io.StringIO()
        with redirect_stdout(captured), patch('builtins.input', side_effect=['1', '5']):
            menu.run_menu(pipeline_run=None, dataset=str(self.dataset([])))
        output = captured.getvalue()
        self.assertIn('Not available yet:', output)
        self.assertIn('Goodbye.', output)
        self.assertNotIn('Matching transactions:', output)
        self.assertNotIn('Traceback', output)

    def test_date_input_recovery_and_filter_description(self):
        path = self.dataset([row(10, date='2024-06-15'), row(20, date='2024-07-01')])
        result, = self.session(path, ['2', 'bad', '2024-06-01', 'bad', '2024-06-30', '5'])
        self.assertEqual(self.last_stdout.count('Not a valid date.'), 2)
        self.assertIn('Range 2024-06-01 to 2024-06-30.', self.last_stdout)
        self.counts_output(1, 2, 2, 0, 0)
        self.totals(result, expenses=10)

    def test_invalid_category_recovery_and_normalized_description(self):
        result, = self.session(self.dataset([row(25)]), ['3', 'Fod', ' fOoD ', '5'])
        self.assertIn("'fod' is not one of the 14 categories", self.last_stdout)
        self.assertIn('Category Food. The filter runs after normalization', self.last_stdout)
        self.totals(result, expenses=25)

    def test_missing_log_output_and_return_to_menu(self):
        self.session(self.dataset([]), ['4', '5'])
        self.assertIn('No error log at', self.last_stdout)
        self.assertEqual(self.last_stdout.count('=== BudgetWise Finance Analyzer ==='), 2)

    def test_existing_log_output_matches_file(self):
        path = self.output_root / 'logs/errors.log'
        path.parent.mkdir(parents=True)
        text = 'line=2 field=amount reason=unrecognized_amount_format raw=BAD\n'
        path.write_text(text, encoding='utf-8')
        self.session(self.dataset([]), ['4', '5'])
        self.assertIn(text.rstrip(), self.last_stdout)
        self.assertNotIn('No error log', self.last_stdout)

    def test_empty_log_does_not_invent_entries(self):
        path = self.output_root / 'logs/errors.log'
        path.parent.mkdir(parents=True)
        path.write_text('', encoding='utf-8')
        self.session(self.dataset([]), ['4', '5'])
        self.assertNotIn('reason=', self.last_stdout)
        self.assertNotIn('No error log', self.last_stdout)

    def test_missing_dataset_failure_message(self):
        self.session(self.directory / 'missing.csv', ['1', '5'])
        self.assertIn('Could not open the dataset: CSV is missing', self.last_stdout)
        self.assertNotIn('Matching transactions:', self.last_stdout)
        self.assertNotIn('JSON summary:', self.last_stdout)

    def test_export_success_messages_point_to_readable_artifacts(self):
        self.load([row(25)])
        for label, path in [('Cleaned CSV', self.csv_path), ('JSON summary', self.json_path), ('Charts', self.chart_path)]:
            self.assertIn(f'{label}: {path}', self.last_stdout)
            self.assertTrue(path.is_file())
        self.assertNotIn('Export failed', self.last_stdout)

    def test_export_failure_message_without_false_export_success(self):
        self.output_root.mkdir()
        (self.output_root / 'cleaned').write_text('blocked', encoding='utf-8')
        result, = self.session(self.dataset([row(25)]), ['1', '5'])
        self.assertIn('Export failed:', self.last_stdout)
        for label in ('Cleaned CSV:', 'JSON summary:', 'Charts:'):
            self.assertNotIn(label, self.last_stdout)
        self.totals(result, expenses=25)
        self.counts_output(1, 1, 1, 0, 0)

    def test_multiple_actions_print_separate_counts_and_filter_labels(self):
        results = self.session(self.dataset([row(10), row(20, category='Rent')]),
                               ['1', '3', 'Food', '3', 'Rent', '4', '5'])
        self.assertEqual(re.findall(r'Matching transactions: (\d+)', self.last_stdout), ['2', '1', '1'])
        self.assertIn('Category Food.', self.last_stdout)
        self.assertIn('Category Rent.', self.last_stdout)
        self.assertEqual(len(results), 3)

    def test_range_warning_must_not_contradict_actual_matching_data(self):
        result = self.load([row(25, date='2026-10-01')], start='2026-10-01', end='2026-10-31')
        self.totals(result, expenses=25)
        self.counts_output(1, 1, 1, 0, 0)
        self.assertNotIn('will match no transactions', self.last_stdout,
                         'The menu predicts zero matches even though the selected dataset has a matching transaction')
        self.assertIn('Reference dataset date range:', self.last_stdout)
        self.assertIn('Results depend on the selected dataset.', self.last_stdout)


def interrupt_check(prefix, exception):
    def check(self):
        answers = iter([*prefix, exception()])
        prompts = []
        output = io.StringIO()
        def answer(label):
            prompts.append(label)
            value = next(answers)
            if isinstance(value, BaseException):
                raise value
            return value
        with redirect_stdout(output), patch('builtins.input', side_effect=answer), patch.object(menu, 'run', wraps=run) as pipeline:
            menu.run_menu(pipeline_run=pipeline, dataset=str(self.dataset([row(25)])))
        pipeline.assert_not_called()
        self.assertEqual(len(prompts), len(prefix)+1)
        self.assertIn('Exiting.', output.getvalue())
        self.assertNotIn('Traceback', output.getvalue())
        self.assertNotIn('Matching transactions:', output.getvalue())
    check.__doc__ = f'{exception.__name__} after inputs {prefix!r}: clean exit without loading incomplete selection'
    return check


for position, prefix in [('choice', []), ('start', ['2']), ('end', ['2', '2024-01-01']),
                         ('category', ['3']), ('choice_retry', ['99']),
                         ('date_retry', ['2', 'bad']), ('category_retry', ['3', 'unknown']),
                         ('reversed_retry', ['2', '2024-02-01', '2024-01-01'])]:
    for exception in (EOFError, KeyboardInterrupt):
        setattr(MenuWorkflowTests, f'test_interrupt_{position}_{exception.__name__}', interrupt_check(prefix, exception))


if __name__ == '__main__':
    unittest.main(verbosity=2)
