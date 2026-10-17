"""Automated acceptance checks for BudgetWise Analyzer."""

import inspect
import json
import sys
sys.dont_write_bytecode = True
import unittest
from pathlib import Path

# Support both unittest discovery and direct execution from an IDE.
ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

"""Real menu/pipeline harness; only terminal input and output paths are replaced."""

import csv
import io
import json
import os
import tempfile
import unittest
from contextlib import ExitStack, redirect_stdout
from pathlib import Path
from unittest.mock import patch

from budgetwise.interface.menu.implementation.menu import run_menu
from budgetwise.interface.export.implementation import csv_export, json_export, chart_export
from budgetwise.pipeline import run

FIELDS = ('transaction_id', 'user_id', 'date', 'transaction_type', 'category',
          'amount', 'payment_mode', 'location', 'notes')


def row(amount=10, *, date='2026-10-01', category='Food', kind='Expense',
        id=None, location='Mumbai', notes=''):
    """IDs are allocated when writing, unless an exact ID is requested."""
    return dict(zip(FIELDS, (id, 'U001', date, kind, category, str(amount),
                             'Cash', location, notes)))


class WorkflowCase(unittest.TestCase):
    def setUp(self):
        self.stack = ExitStack()
        self.addCleanup(self.stack.close)
        self.directory = Path(self.stack.enter_context(tempfile.TemporaryDirectory(
            prefix='budgetwise_e2e_')))
        previous = Path.cwd()
        os.chdir(self.directory)
        self.stack.callback(os.chdir, previous)
        self.output_root = self.directory / 'output'
        for module in (csv_export, json_export, chart_export):
            self.stack.enter_context(patch.object(module, 'OUTPUT_ROOT', self.output_root))
        self.sequence = 0
        self.last_results = []
        self.last_stdout = ''

    def dataset(self, rows):
        self.sequence += 1
        path = self.directory / f'fixture_{self.sequence}.csv'
        with path.open('w', encoding='utf-8', newline='') as stream:
            writer = csv.writer(stream)
            writer.writerow(FIELDS)
            for index, record in enumerate(rows, 1):
                if isinstance(record, dict):
                    record = dict(record)
                    record['transaction_id'] = record['transaction_id'] or f'T{index:04d}'
                    writer.writerow([record[field] for field in FIELDS])
                else:
                    # A physical short/long CSV row, deliberately not repaired.
                    writer.writerow(record)
        return path

    def session(self, path, answers, before_input=None):
        """Run the real interactive loop, bounded by a finite input script."""
        answers = iter(answers)
        results = []
        captured = io.StringIO()

        def traced_run(*args, **kwargs):
            result = run(*args, **kwargs)
            results.append(result)
            return result

        def answer(prompt):
            print(prompt, end='')
            if before_input:
                before_input(results, captured.getvalue())
            try:
                return next(answers)
            except StopIteration:
                self.fail('Menu requested unexpected additional input: ' + prompt)

        try:
            with redirect_stdout(captured), patch('builtins.input', side_effect=answer):
                run_menu(pipeline_run=traced_run, dataset=str(path))
        finally:
            self.last_results = results
            self.last_stdout = captured.getvalue()
        self.assertIsNone(next(answers, None), 'Menu exited before consuming the scripted interaction')
        self.assertIn('Goodbye', self.last_stdout)
        self.assertNotIn('Traceback', self.last_stdout)
        return results

    def load(self, rows, *, start=None, end=None, category=None):
        path = self.dataset(rows)
        if start is not None:
            answers = ['2', start, end, '5']
        elif category is not None:
            answers = ['3', category, '5']
        else:
            answers = ['1', '5']
        results = self.session(path, answers)
        self.assertEqual(len(results), 1)
        result = results[0]
        self.assertIsNone(result['error'])
        counts = result['counts']
        self.assertEqual(counts['input'], counts['valid'] + counts['skipped'] + counts['duplicates'])
        self.assertEqual(counts['objects_failed'], 0)
        self.assertEqual(len(result['transactions']), result['summary']['selected_transactions'])
        # Read actual newly written artifacts, not mocked exporter return values.
        self.csv_path = self.single_file('cleaned', f'cleaned_{path.stem}_*.csv')
        self.json_path = self.single_file('summaries', f'summary_{path.stem}_*.json')
        self.chart_path = self.single_file('summaries', f'charts_{path.stem}_*.txt')
        self.document = json.loads(self.json_path.read_text(encoding='utf-8'))
        exported_summary = {key: value for key, value in self.document.items()
                            if key not in ('dataset', 'generated')}
        self.assertEqual(exported_summary, json.loads(json.dumps(result['summary'])))
        self.assertEqual(self.document['dataset'], path.name)
        with self.csv_path.open(encoding='utf-8-sig', newline='') as stream:
            self.exported_rows = list(csv.DictReader(stream))
        self.assertEqual(len(self.exported_rows), len(result['transactions']))
        for record, transaction in zip(self.exported_rows, result['transactions']):
            self.assertEqual(record['transaction_id'], transaction.get_transaction_id())
            self.assertEqual(record['transaction_type'], transaction.get_transaction_type())
            self.assertEqual(record['category'], transaction.get_category())
            self.assertEqual(record['date'], transaction.get_date() or '')
            self.assertAlmostEqual(float(record['amount']), transaction.get_amount(), places=2)
        self.assertIn(str(self.json_path), self.last_stdout)
        return result

    def single_file(self, folder, pattern):
        matches = list((self.output_root / folder).glob(pattern))
        self.assertEqual(len(matches), 1, f'Expected one fresh {pattern}, found {matches}')
        return matches[0]

    def totals(self, result, *, expenses, income=0):
        actual = result['summary']['total_breakdown']['totals']
        for key, expected in dict(expenses=expenses, income=income, net=income-expenses).items():
            self.assertAlmostEqual(actual[key], expected, places=5, msg=f'Incorrect {key}')

    def months(self, result):
        return {item['month']: item['totals']['expenses']
                for item in result['summary']['monthly_breakdown']['months']}

    def top(self, result):
        return result['summary']['total_breakdown']

    def issue(self, result, line, field, reason_fragment):
        matches = [issue for issue in result['issues']
                   if issue[0] == line and issue[1] == field
                   and reason_fragment.lower() in issue[2].lower()]
        self.assertTrue(matches, f'No {field}/{reason_fragment} issue for CSV line {line}: {result["issues"]}')
        log = (self.output_root / 'logs/errors.log').read_text(encoding='utf-8')
        for issue in matches:
            self.assertTrue(any(f'line={line} ' in entry and f'field={field} ' in entry
                                and f'reason={issue[2]}' in entry for entry in log.splitlines()),
                            f'Issue not persisted in errors.log: {issue}')
        return matches

    def budget(self, result, month='2026-10', category='Food', *, actual, limit, difference):
        months = [item for item in result['budget_comparisons'] if item['month'] == month]
        self.assertEqual(len(months), 1)
        matches = [item for item in months[0]['categories'] if item['category'] == category]
        self.assertEqual(len(matches), 1, 'Category must be compared exactly once per month')
        item = matches[0]
        for key, expected in dict(actual=actual, limit=limit, difference=difference).items():
            self.assertAlmostEqual(item[key], expected, msg=f'Budget {category}: incorrect {key}')
        self.assertEqual(item['status'], 'over' if difference > 0 else 'under' if difference < 0 else 'exact')

from budgetwise.analysis.aggregation import totals_by_category, totals_by_month, unique_categories
from budgetwise.cleaning.rows import is_duplicate
from budgetwise.loader import load_rows
from budgetwise.models import Transaction, ExpenseTransaction, IncomeTransaction, Account


def load_limits():
    """Independent oracle: read configured numbers without production budget logic."""
    config = json.loads((ROOT / 'config/monthly_budgets.json').read_text(encoding='utf-8'))
    return config['limits']

MANUAL_CASE_IDS = (38, 49, 76, 86, 87)

CASE_DESCRIPTIONS = {'TC-001': '[Positive] Prepare a valid BudgetWise-compatible CSV with these illustrative fields: '
           'transaction_id,date,amount,transaction_type,category,merchant. Rows: '
           '(T01,2026-10-01,25,Expense,Food,Market) and '
           '(T02,2026-10-02,100,Income,Salary,Employer). Launch application; choose Load full '
           'dataset; generate summary.',
 'TC-002': '[Positive] Place only a valid BudgetWise CSV at the configured input path; start from '
           'the program menu and load it. Verify the analyzed transactions against its physical '
           'nonheader record count, allowing for explicitly logged invalid/duplicate rows.',
 'TC-003': '[Positive] CSV rows with equivalent valid dates in supported formats: '
           'T01,date=2026-10-15,amount=10; T02,date=10/15/2026,amount=20; '
           'T03,date=15-10-26,amount=30 (all Expense/Food). Load, filter by October 2026, and '
           'inspect cleaned output.',
 'TC-004': '[Positive] CSV with valid dates across months: (T01,09/30/2026,10,Expense,Food); '
           '(T02,2026-10-01,20,Expense,Food). Load then request a September-only report.',
 'TC-005': '[Positive] CSV Expense rows with amount strings "$125", "₹125", "Rs. 125", "125 INR", '
           'and "125" (distinct IDs, same date/category). Load and view totals.',
 'TC-006': '[Positive] CSV Expense rows amount="₹1,250" and amount="$250" (properly quoted in CSV '
           'if commas are present). Load and view cleaned amount/report.',
 'TC-007': '[Negative] Input three records: a valid Expense/Food/20 row, an otherwise valid row '
           'whose amount="not-a-number", and an otherwise valid row with date="2026-02-30". Load '
           'full dataset; open errors.log and attempt a report.',
 'TC-008': '[Negative] CSV with one row missing transaction_type and one complete row amount=35, '
           'type=Expense, category=Food, valid date. Load and produce a report.',
 'TC-009': '[Negative] Input two byte-for-byte identical transaction rows: '
           '(T01,2026-10-01,40,Expense,Food,Market). Load and request expense summary; examine '
           'errors.log.',
 'TC-010': '[Boundary] Input (T01,2026-10-01,40,Expense,Food,Market) and '
           '(T01,2026-10-01,55,Expense,Food,Market), with the SAME ID but DIFFERENT amount. Load '
           'and report.',
 'TC-011': '[Negative] Load a CSV containing a valid row plus amount="BAD", invalid '
           'date="2026-13-01", and an exact duplicate of the valid row. Open the generated '
           'errors.log.',
 'TC-012': '[Negative] Load an otherwise valid row with category missing and amount="₹50"; open '
           'errors.log after analysis.',
 'TC-013': '[Positive] Start application with a valid dataset configured. DO NOT enter a menu '
           'option. Observe startup behavior.',
 'TC-014': '[Positive] From the menu select Load full dataset, with two valid expenses in '
           'different categories: Food=20 and Utilities=30.',
 'TC-015': '[Boundary] Use date-range load: two rows (2026-10-01,15,Expense,Food) and '
           '(2026-10-31,25,Expense,Food), plus (2026-11-01,40,Expense,Food). Enter 2026-10-01 '
           'through 2026-10-31.',
 'TC-016': '[Positive] Use category load/filter with (Food,15), (Food,25), (Utilities,40), all '
           'valid expenses. Choose Food.',
 'TC-017': '[Positive] Create a CSV containing an invalid amount, load it, and choose View error '
           'log from the text menu.',
 'TC-018': '[Negative] At the main menu choose Exit. Then run again and enter an unsupported '
           'option (e.g., 99), followed by a supported option.',
 'TC-019': '[Negative] Request a date range with zero matching rows, then request a reversed date '
           'range (end before start).',
 'TC-020': '[Boundary] Input CSV: only the correct BudgetWise header row; zero data rows. Through '
           'the text menu, load the file and request a spending report.',
 'TC-021': '[Positive] Input CSV with a properly quoted comma in a text field: T01 | 2026-10-01 | '
           '35 | Expense | Food | "Market, Downtown". Load and display/export the cleaned '
           'analysis. Use the actual BudgetWise field names.',
 'TC-022': '[Negative] Input a CSV with valid T01 | 2026-10-01 | 15 | Expense | Food | Market, '
           'followed by a physically truncated row lacking required columns, then valid T03 | '
           '2026-10-02 | 25 | Expense | Food | Market. Load and inspect errors.log.',
 'TC-023': '[Negative] Temporarily point the configured input to a nonexistent CSV (or rename the '
           'expected dataset file). Start the application, select Load full dataset, then try '
           'another menu option.',
 'TC-024': '[Negative] Input valid T01 | 2026-10-01 | 20 | Expense | Food | Shop; invalid T02 | '
           '2026-10-02 | [blank amount] | Expense | Food | Shop. Load, check the log and expense '
           'report.',
 'TC-025': '[Negative] Input a valid Expense/Food/20 row plus a row with '
           'transaction_type="Mystery" and amount=70; all other fields valid. Run a financial '
           'summary and open errors.log.',
 'TC-026': '[Negative] At Load transactions by date range, enter an invalid date (e.g., '
           'start="not-a-date") and then retry with a valid range covering '
           'T01=2026-10-01/Expense/12.',
 'TC-027': '[Boundary] Load valid expenses Food=20 and Rent=30. Select a category value that has '
           'no matching transactions; then select Food.',
 'TC-028': '[Positive] Load two valid transactions: T01 in Food/20 and T02 in Utilities/30. From '
           'the interactive menu first load Food only, then reload/load Utilities only; compare '
           'each active report.',
 'TC-029': '[Negative] Input one valid Expense/15 row, one CSV row with unquoted extra '
           'delimiter(s) causing extra/misaligned fields, and a final valid Expense/25 row. Load '
           'and inspect results/log.',
 'TC-030': '[Code inspection] Load two distinct valid transactions through the menu and generate a '
           'summary. Then perform a brief source-code check of the in-memory transaction '
           'collection (E2E output alone cannot prove container type).',
 'TC-031': '[Code inspection] Input valid Expense rows: Sep Food=10; Oct Food=20; Oct '
           'Utilities=30. Load and view category/month summaries; briefly inspect aggregation '
           'storage.',
 'TC-032': '[Code inspection] Input categories Food, Food, Utilities and merchants ShopA, ShopA, '
           'ShopB, with two EXACT duplicate raw rows. Run full load, use any '
           'unique-category/merchant features, and review source.',
 'TC-033': '[Code inspection] Load valid September and October transactions; view monthly output. '
           'Then inspect the source of grouping keys after the successful E2E run.',
 'TC-034': '[Boundary] Input two valid Food expenses: T01 | 2025-10-15 | 20 and T02 | 2026-10-15 | '
           '30. Load and display monthly aggregation. Inspect grouping implementation for '
           'dictionary and fixed year-month key use.',
 'TC-035': '[Code inspection] Run the full workflow with an expense and an income (load → summary '
           '→ export). Inspect the classes used to represent/account for those transactions.',
 'TC-036': '[Code inspection] Exercise a normal transaction workflow (or specialized transaction '
           'behavior if exposed) and inspect a concrete subclass used by the application.',
 'TC-037': '[Code inspection] Load transactions and run a budget/summary workflow. Inspect one '
           'class that controls protected/private data using methods or properties.',
 'TC-039': '[Positive] Input Income rows 800 and 200 and Expense rows 150 and 50 (all valid, same '
           'October). Load and request the financial summary.',
 'TC-040': '[Positive] Input Expense rows: Sep 15 and 25; Oct 10 and 50. Load full dataset and '
           'show monthly expense report.',
 'TC-041': '[Positive] Input 6 Expense categories with one row each: Food=60, Rent=50, '
           'Utilities=40, Entertainment=30, Shopping=20, Healthcare=10. Load and request top '
           'spending categories.',
 'TC-042': '[Positive] Input 6 Expense transactions with distinct magnitudes 60,50,40,30,20,10 '
           'plus one Income=900. Load and request largest expense transactions.',
 'TC-043': '[Boundary] Input two valid expense transactions only (Food=25, Utilities=15). Request '
           'top five categories and top five largest expense transactions.',
 'TC-044': '[Positive] Set or identify October Food budget B=100 (or take any actual configured '
           'B). Input valid October Food expenses totaling 120 if B=100. View budget vs. actual by '
           'category.',
 'TC-045': '[Positive] Inspect program report/configuration for category limits, then load at '
           'least one complete month of valid transactions across five distinct spending '
           'categories.',
 'TC-046': '[Positive] For one configured category/month with budget B (e.g., B=100), load '
           'eligible expenses summing B+20 (e.g., 60+60). Show budget comparison.',
 'TC-047': '[Positive] For one configured category/month with budget B (e.g., B=100), load '
           'eligible expenses summing B−30 (e.g., 30+40). Show budget comparison.',
 'TC-048': '[Boundary] For one configured category/month with budget B (e.g., B=100), load '
           'expenses totaling exactly B.',
 'TC-050': '[Positive] Load two months of expenses (September=20, October=60). Choose any textual '
           'spending visualization shown by the application.',
 'TC-051': '[Boundary] Load all valid expense records in exactly one category/month and request '
           'visualization; then load zero matching records and retry.',
 'TC-052': '[Positive] Load two valid Expense transactions (Food=10, Rent=20); run the Export '
           'action; inspect newly created file.',
 'TC-053': '[Negative] Load one valid row, one row with amount="BAD", and a fully identical '
           'duplicate of the valid row. Export cleaned summary and open it with a standard '
           'CSV/JSON reader.',
 'TC-054': '[Positive] Load a subset through category/date filtering, generate its report, and '
           'export a cleaned summary.',
 'TC-055': '[Boundary] Load a valid CSV containing ONLY Income rows 200 and 300 in October, with '
           'no Expense rows. Request all financial summary outputs, including top spending '
           'categories/transactions.',
 'TC-056': '[Boundary] Load a valid CSV containing ONLY October Expense rows Food=15 and '
           'Utilities=25, with no Income rows. Request the full financial summary.',
 'TC-057': '[Positive] Use actual configured monthly budgets B_Food and B_Rent (or set B_Food=100, '
           'B_Rent=200 if editable). Load one month of Food expenses=B_Food+20 and Rent '
           'expenses=B_Rent-30; view both category comparisons.',
 'TC-058': '[Boundary] Use the same category with configured monthly limit B (e.g., Food B=100). '
           'Load September Food expense=B+10 and October Food expense=B-20, then inspect both '
           'months of budget comparison.',
 'TC-059': '[Negative] Load six valid expense transactions amount 75, 60, -50, 40, 30, 20; add one '
           'sentinel Expense amount=100000000, one invalid Expense amount="BAD", and one '
           'Income=2000. Request top five expense transactions.',
 'TC-060': '[Positive] Use the team\'s documented category mapping to load Food variants "Food"=35 '
           'and "food"=15 (if both mapped to Food), plus Rent=20. Display total spending and '
           'top-category ranking.',
 'TC-061': '[Boundary] Load a valid header-only CSV, then request monthly summary, net balance, '
           'and top-five categories/transactions. Repeat after a date/category filter with no '
           'matching records.',
 'TC-062': '[Negative] After loading a valid Expense/25 row, temporarily make the configured '
           'export destination unavailable or unwritable, then request CSV/JSON export.',
 'TC-063': '[Positive] Load 4 Expense rows (distinct IDs): $100, ₹100, Rs. 100, and 100 INR. '
           'Compare cleaned values and overall expense report.',
 'TC-064': '[Positive] Load one row with $35, one with ₹45, one with Rs. 55, and one with 65 INR; '
           'inspect errors.log or processing log.',
 'TC-065': '[Boundary] Load one plain-number Expense amount="75" alongside one symbol-marked '
           'amount="$25".',
 'TC-066': '[Boundary] Load Expense rows 99999999 and 100000000 (otherwise valid). Generate total '
           'expenses and inspect errors.log.',
 'TC-067': '[Negative] Load Expense rows amount=999999999 and amount=25 in October, plus an Income '
           'row of 50. View monthly/category/global summaries and the error log.',
 'TC-068': '[Boundary] Load valid rows: amount=-40, type=Expense, category=Food; amount=-100, '
           'type=Income, category=Salary.',
 'TC-069': '[Boundary] Load a positive Expense amount=30 and a negative Expense amount=-20 in the '
           'same category/month.',
 'TC-070': '[Boundary] Load a valid Income row with amount=0 and a valid Expense row amount=0.',
 'TC-071': '[Negative] Load (T01,2026-10-01,25,Expense,[blank category],Market) and '
           '(T02,2026-10-02,10,Expense,Food,Market). Report by category and open errors.log.',
 'TC-072': '[Boundary] Input valid expense row date="03/04/2026" (ambiguous slash date), '
           'amount=25. Export cleaned summary or view date-based output.',
 'TC-073': '[Boundary] Input valid expense row date="03-04-26" (ambiguous hyphen two-digit-year '
           'date), amount=25. Export cleaned summary or view date-based output.',
 'TC-074': '[Boundary] Input a valid expense date="12/11/2026" and another "12-11-26". Load and '
           'filter November vs December.',
 'TC-075': '[Negative] Input Expense rows date="2026-02-30", amount=40, category=Food and valid '
           'date="2026-02-28", amount=10. Run February summary, check errors.log.',
 'TC-077': '[Negative] Load two rows: missing date + Expense/Food/25; valid 2026-10-01 + '
           'Expense/Food/10. Inspect category totals, October/monthly totals, and errors.log.',
 'TC-078': '[Negative] Load two FULLY identical raw rows (including id, date, amount, type, '
           'category, merchant): (T01,2026-10-01,20,Expense,Food,Shop).',
 'TC-079': '[Boundary] Load rows with transaction_id="T01" for both, but merchant ShopA vs ShopB; '
           'all other fields identical. Generate report.',
 'TC-080': '[Boundary] Load TWO raw rows that become the same after cleaning: '
           '(T01,2026-10-01,"$20",Expense,Food,Shop) and (T01,2026-10-01,"₹20",Expense,Food,Shop).',
 'TC-081': '[Boundary] Load rows (T01,2026-10-01,20,Expense,"food",Shop) and '
           '(T01,2026-10-01,20,Expense,"Food",Shop) with no other difference. Ensure category '
           'mapping treats both as Food.',
 'TC-082': '[Negative] Load otherwise valid Expense row date="nonsense-date", amount=25, plus '
           'valid dated Expense row amount=10. Check errors.log and monthly summary.',
 'TC-083': '[Negative] Load otherwise valid Expense row date="2026-10-01", amount="12foo", plus '
           'valid Expense row amount=10. Check errors.log and report.',
 'TC-084': '[Positive] Select two raw category strings that the team’s documented mapping '
           'explicitly maps to the SAME canonical category (e.g., "food" and "Food" IF both are '
           'defined). Input expenses 10 and 20, respectively.',
 'TC-085': '[Boundary] Load one row with no category and one with a documented misspelling variant '
           '(e.g., "Foood" ONLY IF the mapping includes it). Export summary and compare mapping '
           'table.',
 'TC-088': '[Boundary] Load Expense rows amount=-99999999 and amount=-100000000 on valid October '
           'dates. Inspect October totals and errors.log.',
 'TC-089': '[Boundary] Load Expense rows amount="99999999.99" and "100000000.01" on distinct valid '
           'dates with other fields valid.',
 'TC-090': '[Positive] Load distinct valid Expense rows with quoted amount strings "$12.50", '
           '"₹12.50", "Rs. 12.50" and "12.50 INR"; calculate summary and inspect errors.log.',
 'TC-091': '[Boundary] Load T01 with whitespace-only category (e.g., three spaces) and amount=15, '
           'plus valid T02 Food/25 in the same month. Inspect category and overall expense totals.',
 'TC-092': '[Boundary] Load Expense T01 date="2024-02-29" amount=20 and T02 date="2025-02-28" '
           'amount=10. Request February 2024 and February 2025 reports, then inspect cleaned '
           'dates.',
 'TC-093': '[Negative] Load invalid Expense T01 date="2025-02-29" amount=60 and valid T02 '
           'date="2025-02-28" amount=10. Request February 2025 summary and inspect errors.log.',
 'TC-094': '[Negative] Load one valid Expense/10 row and one Expense row with amount="$12x" (all '
           'other fields valid). Open errors.log and request all expense reports.',
 'TC-095': "[Negative] Choose a category string ABSENT from the team's documented "
           'raw-to-normalized mapping (e.g., "UnexpectedCategoryXYZ") and load a valid Expense/35 '
           'row. View categories and log; consult mapping documentation.',
 'TC-096': '[Boundary] Load THREE completely identical raw Expense rows (all columns identical), '
           'each amount=15. Run analysis and inspect duplicate indications/log.',
 'TC-097': '[Boundary] Load two transactions with the SAME transaction_id and identical '
           'amount=30/date/category/merchant, but transaction_type differs: one Income and one '
           'Expense.',
 'TC-098': '[Negative] Input T01 with date="bad-date" AND amount="invalid", then a second valid '
           'Expense/10 row. Load and inspect errors.log and financial totals.',
 'TC-099': '[Positive] For a category with two documented raw variants (for example Food/"food"), '
           'load each as an October expense=20 and 30. Select normalized category and view monthly '
           'budget comparison.'}


class WorkbookTests(WorkflowCase):
    def test_TC_001(self):
        result = self.load([row(25), row(100, kind='Income', category='Salary')])
        self.totals(result, expenses=25, income=100)
        self.assertEqual(len(result['transactions']), 2)

    def test_TC_002(self):
        rows = [row(11), row(22), row(33, kind='Income', category='Salary')]
        path = self.dataset(rows)
        with path.open(encoding='utf-8') as stream:
            physical_records = sum(1 for _ in stream) - 1
        result, = self.session(path, ['1', '5'])
        self.assertEqual(physical_records, 3)
        self.assertEqual(result['counts']['input'], physical_records)
        self.assertEqual(len(result['transactions']), physical_records)
        self.totals(result, expenses=33, income=33)

    def test_TC_003(self):
        result = self.load([row(10, date='2026-10-15'), row(20, date='10/15/2026'),
                            row(30, date='15-10-26')], start='2026-10-01', end='2026-10-31')
        self.totals(result, expenses=60)
        self.assertEqual([r['date'] for r in self.exported_rows], ['2026-10-15'] * 3)

    def test_TC_004(self):
        result = self.load([row(10, date='09/30/2026'), row(20)],
                           start='2026-09-01', end='2026-09-30')
        self.totals(result, expenses=10)
        self.assertEqual(self.months(result), {'2026-09': 10})

    def currency_case(self, amounts, values, labels):
        result = self.load([row(amount) for amount in amounts])
        self.totals(result, expenses=sum(values))
        self.assertEqual([t.get_amount() for t in result['transactions']], values)
        self.assertEqual([t.get_original_currency() for t in result['transactions']], labels)
        self.assertEqual([r['original_currency'] for r in self.exported_rows], labels)
        for line, (raw, label) in enumerate(zip(amounts, labels), 2):
            if label != 'plain':
                matches = self.issue(result, line, 'amount', 'currency')
                self.assertTrue(any(label in str(issue[3]) for issue in matches))
                self.assertIn(raw, (self.output_root / 'logs/errors.log').read_text(encoding='utf-8'))
        return result

    def test_TC_005(self):
        self.currency_case(['$125', '₹125', 'Rs. 125', '125 INR', '125'],
                           [125] * 5, ['$', '₹', 'Rs.', 'INR', 'plain'])

    def test_TC_006(self):
        self.currency_case(['₹1,250', '$250'], [1250, 250], ['₹', '$'])

    def test_TC_007(self):
        rows = [row(20), row('not-a-number'), row(40, date='2026-02-30')]
        result = self.load(rows)
        self.totals(result, expenses=60)  # Repo keeps undated rows for category analysis.
        self.issue(result, 3, 'amount', 'unrecognized')
        self.issue(result, 4, 'date', 'date')
        result = self.load(rows, start='2026-01-01', end='2026-12-31')
        self.totals(result, expenses=20)

    def test_TC_008(self):
        result = self.load([row(70, kind=''), row(35)])
        self.totals(result, expenses=35)
        self.issue(result, 2, 'transaction_type', 'missing_required')

    def duplicate_case(self, amount, copies):
        original = row(amount, id='T0001')
        result = self.load([original] * copies)
        self.totals(result, expenses=amount)
        self.assertEqual(result['counts']['duplicates'], copies-1)
        for line in range(3, copies+2):
            self.issue(result, line, 'row', 'duplicate')

    def test_TC_009(self):
        self.duplicate_case(40, 2)

    def test_TC_010(self):
        result = self.load([row(40, id='T0001'), row(55, id='T0001')])
        self.totals(result, expenses=95)
        self.assertEqual(len(result['transactions']), 2)
        self.assertEqual(result['counts']['duplicates'], 0)

    def test_TC_011(self):
        valid = row(10, id='T0001')
        result = self.load([valid, row('BAD'), row(20, date='2026-13-01'), valid])
        self.issue(result, 3, 'amount', 'unrecognized')
        self.issue(result, 4, 'date', 'date')
        self.issue(result, 5, 'row', 'duplicate')

    def test_TC_012(self):
        result = self.load([row('₹50', category='')])
        self.totals(result, expenses=50)
        self.assertEqual(self.top(result)['top_categories'], [('Uncategorized', 50)])
        self.issue(result, 2, 'category', 'uncategorized')
        self.issue(result, 2, 'amount', 'currency')
        self.assertIn('₹', (self.output_root / 'logs/errors.log').read_text(encoding='utf-8'))

    def test_TC_013(self):
        def before_input(results, output):
            self.assertEqual(results, [], 'Dataset loaded before a user chose an action')
            for label in ('Load full dataset', 'Load transactions by date range',
                          'Load transactions by category', 'View error log', 'Exit'):
                self.assertIn(label, output)
            self.assertFalse((self.output_root / 'cleaned').exists())
        self.assertEqual(self.session(self.dataset([row(10)]), ['5'], before_input), [])

    def test_TC_014(self):
        self.totals(self.load([row(20), row(30, category='Utilities')]), expenses=50)
        self.assertIn('Matching transactions: 2', self.last_stdout)

    def test_TC_015(self):
        result = self.load([row(15), row(25, date='2026-10-31'), row(40, date='2026-11-01')],
                           start='2026-10-01', end='2026-10-31')
        self.totals(result, expenses=40)
        self.assertEqual([t.get_date() for t in result['transactions']], ['2026-10-01', '2026-10-31'])

    def test_TC_016(self):
        result = self.load([row(15), row(25), row(40, category='Utilities')], category='Food')
        self.totals(result, expenses=40)
        self.assertEqual(self.top(result)['top_categories'], [('Food', 40)])

    def test_TC_017(self):
        result, = self.session(self.dataset([row('BAD'), row(20)]), ['1', '4', '5'])
        matches = self.issue(result, 2, 'amount', 'unrecognized')
        self.assertIn(matches[0][2], self.last_stdout)
        self.assertIn('BAD', self.last_stdout)
        self.assertIn('line=2', self.last_stdout)

    def test_TC_018(self):
        path = self.dataset([row(20)])
        self.assertEqual(self.session(path, ['5']), [])
        result, = self.session(path, ['99', '1', '5'])
        self.assertIn('Please choose', self.last_stdout)
        self.totals(result, expenses=20)

    def test_TC_019(self):
        results = self.session(self.dataset([row(20)]),
                               ['2', '2026-09-01', '2026-09-30',
                                '2', '2026-10-31', '2026-10-01',
                                '2026-10-01', '2026-10-31', '5'])
        self.assertEqual(len(results), 2)
        self.totals(results[0], expenses=0)
        self.totals(results[1], expenses=20)
        self.assertIn('Matching transactions: 0', self.last_stdout)
        self.assertIn('before the start', self.last_stdout)

    def test_TC_020(self):
        result = self.load([])
        self.totals(result, expenses=0)
        self.assertEqual(result['transactions'], [])
        self.assertIn('Matching transactions: 0', self.last_stdout)

    def test_TC_021(self):
        record = row(35, notes='Market, Downtown')
        path = self.dataset([record])
        loaded = list(load_rows(path))
        self.assertEqual(len(loaded), 1)
        self.assertEqual(loaded[0][1]['notes'], 'Market, Downtown')
        result = self.load([record])
        self.totals(result, expenses=35)
        self.assertEqual(result['records'][0]['notes'], 'Market, Downtown')

    def test_TC_022(self):
        result = self.load([row(15), ['T0002', 'U001'], row(25, date='2026-10-02')])
        self.totals(result, expenses=40)
        self.assertEqual(result['counts']['skipped'], 1)
        self.issue(result, 3, 'transaction_type', 'missing_required')

    def test_TC_023(self):
        result, = self.session(self.directory / 'does_not_exist.csv', ['1', '4', '5'])
        self.assertIsInstance(result['error'], FileNotFoundError)
        self.assertIn('Could not open the dataset', self.last_stdout)
        self.assertNotIn('Matching transactions:', self.last_stdout)
        self.assertFalse((self.output_root / 'cleaned').exists())

    def test_TC_024(self):
        result = self.load([row(20), row('')])
        self.totals(result, expenses=20)
        self.issue(result, 3, 'amount', 'missing')

    def test_TC_025(self):
        result = self.load([row(20), row(70, kind='Mystery')])
        self.totals(result, expenses=20)
        self.issue(result, 3, 'transaction_type', 'missing_required')

    def test_TC_026(self):
        result, = self.session(self.dataset([row(12)]),
                                ['2', 'not-a-date', '2026-10-01', '2026-10-31', '5'])
        self.totals(result, expenses=12)
        self.assertIn('Not a valid date', self.last_stdout)

    def test_TC_027(self):
        results = self.session(self.dataset([row(20), row(30, category='Rent')]),
                               ['3', 'Entertainment', '3', 'Food', '5'])
        self.assertEqual(len(results), 2)
        self.totals(results[0], expenses=0)
        self.totals(results[1], expenses=20)
        self.assertIn('Matching transactions: 0', self.last_stdout)

    def test_TC_028(self):
        results = self.session(self.dataset([row(20), row(30, category='Utilities')]),
                               ['3', 'Food', '3', 'Utilities', '5'])
        self.assertEqual(len(results), 2)
        self.totals(results[0], expenses=20)
        self.totals(results[1], expenses=30)
        self.assertEqual([len(r['transactions']) for r in results], [1, 1])

    def test_TC_029(self):
        malformed = row(90, id='T0002')
        malformed = [malformed[field] for field in FIELDS] + ['unquoted surplus']
        result = self.load([row(15), malformed, row(25)])
        self.totals(result, expenses=40)
        self.assertTrue(any(i[0] == 3 and 'malformed' in i[2] for i in result['issues']),
                        'Surplus CSV fields must not disappear without a log entry')

    def test_TC_030(self):
        result = self.load([row(10), row(20)])
        self.totals(result, expenses=30)
        self.assertIsInstance(result['transactions'], list)
        self.assertEqual(len(result['transactions']), 2)
        self.assertTrue(all(isinstance(t, Transaction) for t in result['transactions']))

    def test_TC_031(self):
        result = self.load([row(10, date='2026-09-01'), row(20), row(30, category='Utilities')])
        categories = totals_by_category(result['transactions'], kind='expense')
        months = totals_by_month(result['transactions'], kind='expense')
        self.assertIsInstance(categories, dict)
        self.assertIsInstance(months, dict)
        self.assertEqual(categories, {'Food': 30, 'Utilities': 30})
        self.assertEqual(months, {('2026', '09'): 10, ('2026', '10'): 50})
        self.assertEqual(self.months(result), {'2026-09': 10, '2026-10': 50})

    def test_TC_032(self):
        original = row(10, id='T0001', location='Mumbai')
        observed_sets = []
        def trace(frame, event, arg):
            if frame.f_code is is_duplicate.__code__ and event == 'call':
                observed_sets.append(isinstance(frame.f_locals.get('seen_keys'), set))
            return trace
        previous = sys.gettrace()
        try:
            sys.settrace(trace)
            result = self.load([original, original, row(20, category='Utilities', location='Delhi')])
        finally:
            sys.settrace(previous)
        self.totals(result, expenses=30)
        self.assertEqual(result['counts']['duplicates'], 1)
        self.assertEqual(unique_categories(result['transactions']), {'Food', 'Utilities'})
        self.assertIsInstance(unique_categories(result['transactions']), set)
        self.assertTrue(observed_sets and all(observed_sets), 'Pipeline must actually pass a set to duplicate detection')

    def test_TC_033(self):
        result = self.load([row(10, date='2026-09-01'), row(20)])
        months = totals_by_month(result['transactions'], kind='expense')
        self.assertEqual(months, {('2026', '09'): 10, ('2026', '10'): 20})
        self.assertTrue(all(isinstance(key, tuple) and len(key) == 2 for key in months))

    def test_TC_034(self):
        result = self.load([row(20, date='2025-10-15'), row(30, date='2026-10-15')])
        self.assertEqual(self.months(result), {'2025-10': 20, '2026-10': 30})
        self.assertEqual(totals_by_month(result['transactions'], kind='expense'),
                         {('2025', '10'): 20, ('2026', '10'): 30})

    def oop_workflow(self):
        result = self.load([row(25), row(100, kind='Income', category='Salary')])
        self.totals(result, expenses=25, income=100)
        expense, income = result['transactions']
        self.assertIsInstance(expense, ExpenseTransaction)
        self.assertIsInstance(income, IncomeTransaction)
        self.assertTrue(issubclass(ExpenseTransaction, Transaction))
        self.assertTrue(issubclass(IncomeTransaction, Transaction))
        self.assertEqual([expense.get_signed_amount(), income.get_signed_amount()], [-25, 100])
        self.assertIsNot(ExpenseTransaction.get_signed_amount, Transaction.get_signed_amount)
        account = result['accounts']['cash']
        self.assertIsInstance(account, Account)
        self.assertEqual(account.get_total_spent(), 25)
        self.assertEqual(account.get_total_received(), 100)
        return result, expense, account

    def test_TC_035(self):
        _, expense, account = self.oop_workflow()
        self.assertIn('_Transaction__amount', vars(expense))
        copied = account.get_transactions()
        copied.clear()
        self.assertEqual(account.get_transaction_count(), 2)

    def test_TC_036(self):
        _, expense, _ = self.oop_workflow()
        self.assertTrue(expense.is_discretionary())
        self.assertTrue(inspect.isclass(type(expense)))

    def test_TC_037(self):
        _, expense, account = self.oop_workflow()
        self.assertIn('_Transaction__amount', vars(expense))
        with self.assertRaises(ValueError):
            expense.set_amount(-10)
        self.assertEqual(expense.get_amount(), 25)
        expense.set_amount(30)
        self.assertEqual(expense.get_amount(), 30)
        self.assertEqual(account.get_total_spent(), 30)
        account.get_transactions().clear()
        self.assertEqual(account.get_transaction_count(), 2)

    def test_TC_039(self):
        result = self.load([row(800, kind='Income'), row(200, kind='Income'), row(150), row(50)])
        self.totals(result, expenses=200, income=1000)

    def test_TC_040(self):
        result = self.load([row(15, date='2026-09-01'), row(25, date='2026-09-02'), row(10), row(50)])
        self.totals(result, expenses=100)
        self.assertEqual(self.months(result), {'2026-09': 40, '2026-10': 60})

    def test_TC_041(self):
        # Shopping is illustrative: this repo's closed map uses Education instead.
        pairs = [('Food', 60), ('Rent', 50), ('Utilities', 40),
                 ('Entertainment', 30), ('Education', 20), ('Health', 10)]
        result = self.load([row(amount, category=category) for category, amount in pairs]
                           + [row(900, kind='Income', category='Salary')])
        self.assertEqual(self.top(result)['top_categories'], pairs[:5])
        self.totals(result, expenses=210, income=900)

    def test_TC_042(self):
        result = self.load([row(v) for v in [60, 50, 40, 30, 20, 10]] + [row(900, kind='Income')])
        self.assertEqual([r['amount'] for r in self.top(result)['largest_expenses']], [60, 50, 40, 30, 20])
        self.assertTrue(all(r['transaction_type'] == 'Expense' for r in self.top(result)['largest_expenses']))

    def test_TC_043(self):
        result = self.load([row(25), row(15, category='Utilities')])
        self.totals(result, expenses=40)
        self.assertEqual(self.top(result)['top_categories'], [('Food', 25), ('Utilities', 15)])
        self.assertEqual([r['amount'] for r in self.top(result)['largest_expenses']], [25, 15])

    def budget_case(self, difference):
        limit = load_limits()['Food']
        self.assertGreaterEqual(limit+difference, 0)
        result = self.load([row((limit+difference)/2), row((limit+difference)/2)])
        self.totals(result, expenses=limit+difference)
        self.budget(result, actual=limit+difference, limit=limit, difference=difference)

    def test_TC_044(self):
        self.budget_case(20)

    def test_TC_045(self):
        limits = load_limits()
        self.assertGreaterEqual(len(limits), 5)
        # Use a documented raw spelling for each configured canonical category.
        # Transportation's CSV spelling is Travel in this repository's closed map.
        raw_names = {'Transportation': 'Travel'}
        result = self.load([row(10, category=raw_names.get(category, category)) for category in limits])
        for category, limit in limits.items():
            with self.subTest(category=category):
                self.budget(result, category=category, actual=10, limit=limit, difference=10-limit)

    def test_TC_046(self):
        self.budget_case(20)

    def test_TC_047(self):
        self.budget_case(-30)

    def test_TC_048(self):
        self.budget_case(0)

    def test_TC_050(self):
        self.load([row(20, date='2026-09-01'), row(60)])
        chart = self.chart_path.read_text(encoding='utf-8')
        lines = {line.split()[0]: line for line in chart.splitlines() if line.startswith('2026-')}
        self.assertEqual(set(lines), {'2026-09', '2026-10'})
        # ASCII chart uses #; accept its actual bar glyph without inspecting production logic.
        bars = {month: line.split()[1] for month, line in lines.items()}
        self.assertGreater(len(bars['2026-10']), len(bars['2026-09']))
        self.assertAlmostEqual(len(bars['2026-09']) / len(bars['2026-10']), 1/3, delta=0.04)
        self.assertEqual(float(lines['2026-09'].split()[-1]), 20)
        self.assertEqual(float(lines['2026-10'].split()[-1]), 60)

    def test_TC_051(self):
        self.load([row(25)])
        chart = self.chart_path.read_text(encoding='utf-8')
        self.assertIn('Food', chart)
        self.assertIn('2026-10', chart)
        result = self.load([row(25)], category='Rent')
        self.totals(result, expenses=0)
        chart = self.chart_path.read_text(encoding='utf-8')
        self.assertNotIn('Food', chart)
        self.assertNotIn('2026-10 ', chart)

    def test_TC_052(self):
        self.assertFalse(self.output_root.exists())
        result = self.load([row(10), row(20, category='Rent')])
        self.totals(result, expenses=30)
        self.assertEqual(self.document['total_breakdown']['totals']['expenses'], 30)
        self.assertEqual(sum(float(r['amount']) for r in self.exported_rows), 30)

    def test_TC_053(self):
        valid = row(25, id='T0001')
        result = self.load([valid, row('BAD'), valid])
        self.totals(result, expenses=25)
        self.assertEqual(len(self.exported_rows), 1)
        self.assertEqual(self.document['selected_transactions'], 1)

    def test_TC_054(self):
        rows = [row(10), row(20, category='Rent'), row(30, date='2026-09-01')]
        for selection, expected, label in [({'category': 'Food'}, 40, 'category'),
                                          ({'start': '2026-10-01', 'end': '2026-10-31'}, 30, 'date_range')]:
            with self.subTest(selection=selection):
                result = self.load(rows, **selection)
                self.totals(result, expenses=expected)
                self.assertEqual(self.document['selection']['type'], label)
                self.assertEqual(self.document['total_breakdown']['totals']['expenses'], expected)
                for key, value in selection.items():
                    self.assertEqual(self.document['selection'][key], value)

    def test_TC_055(self):
        result = self.load([row(200, kind='Income'), row(300, kind='Income')])
        self.totals(result, expenses=0, income=500)
        self.assertEqual(self.months(result), {'2026-10': 0})
        self.assertEqual(self.top(result)['top_categories'], [])
        self.assertEqual(self.top(result)['largest_expenses'], [])

    def test_TC_056(self):
        result = self.load([row(15), row(25, category='Utilities')])
        self.totals(result, expenses=40)
        self.assertEqual(self.months(result), {'2026-10': 40})

    def test_TC_057(self):
        limits = load_limits()
        result = self.load([row(limits['Food']+20), row(limits['Rent']-30, category='Rent'),
                            row(500, kind='Income', category='Salary')])
        for category, difference in [('Food', 20), ('Rent', -30)]:
            self.budget(result, category=category, actual=limits[category]+difference,
                        limit=limits[category], difference=difference)

    def test_TC_058(self):
        limit = load_limits()['Food']
        result = self.load([row(limit+10, date='2026-09-01'), row(limit-20)])
        self.budget(result, month='2026-09', actual=limit+10, limit=limit, difference=10)
        self.budget(result, actual=limit-20, limit=limit, difference=-20)

    def test_TC_059(self):
        result = self.load([row(v) for v in [75, 60, -50, 40, 30, 20, 100000000, 'BAD']]
                           + [row(2000, kind='Income')])
        self.assertEqual([r['amount'] for r in self.top(result)['largest_expenses']], [75, 60, 50, 40, 30])
        self.totals(result, expenses=275, income=2000)
        self.issue(result, 8, 'amount', 'sentinel')
        self.issue(result, 9, 'amount', 'unrecognized')

    def test_TC_060(self):
        result = self.load([row(35), row(15, category='food'), row(20, category='Rent')])
        self.totals(result, expenses=70)
        self.assertEqual(self.top(result)['top_categories'], [('Food', 50), ('Rent', 20)])

    def test_TC_061(self):
        for rows, selection in [([], {}), ([row(20)], {'category': 'Rent'}),
                                ([row(20)], {'start': '2026-09-01', 'end': '2026-09-30'})]:
            with self.subTest(selection=selection):
                result = self.load(rows, **selection)
                self.totals(result, expenses=0)
                self.assertEqual(self.months(result), {})
                self.assertEqual(self.top(result)['top_categories'], [])
                self.assertEqual(self.top(result)['largest_expenses'], [])
                self.assertEqual(self.exported_rows, [])

    def test_TC_062(self):
        # A real filesystem obstruction works on Windows without unreliable chmod assumptions.
        self.output_root.mkdir()
        (self.output_root / 'cleaned').write_text('This is a file, not a directory.', encoding='utf-8')
        try:
            self.session(self.dataset([row(25)]), ['1', '5'])
        except OSError as error:
            self.fail(f'Export I/O failure escaped the menu: {type(error).__name__}: {error}')
        self.assertRegex(self.last_stdout.lower(), r'fail|error|could not|cannot|unavailable')
        self.assertNotIn('Cleaned CSV:', self.last_stdout)
        self.assertFalse((self.output_root / 'summaries').exists())

    def test_TC_063(self):
        self.currency_case(['$100', '₹100', 'Rs. 100', '100 INR'], [100]*4, ['$', '₹', 'Rs.', 'INR'])

    def test_TC_064(self):
        self.currency_case(['$35', '₹45', 'Rs.55', '65 INR'], [35, 45, 55, 65], ['$', '₹', 'Rs.', 'INR'])

    def test_TC_065(self):
        self.currency_case(['75', '$25'], [75, 25], ['plain', '$'])

    def sentinel_case(self, values, expected):
        result = self.load([row(v) for v in values])
        self.totals(result, expenses=expected)
        self.assertEqual(len(result['transactions']), 1)
        self.issue(result, 3, 'amount', 'sentinel')

    def test_TC_066(self):
        self.sentinel_case([99999999, 100000000], 99999999)

    def test_TC_067(self):
        result = self.load([row(999999999), row(25), row(50, kind='Income')])
        self.totals(result, expenses=25, income=50)
        self.assertEqual(self.months(result), {'2026-10': 25})
        self.assertEqual([r['amount'] for r in self.top(result)['largest_expenses']], [25])
        self.assertEqual(self.top(result)['top_categories'], [('Food', 25)])
        self.issue(result, 2, 'amount', 'sentinel')

    def test_TC_068(self):
        result = self.load([row(-40), row(-100, kind='Income')])
        self.totals(result, expenses=40, income=100)
        self.assertEqual([t.get_signed_amount() for t in result['transactions']], [-40, 100])

    def test_TC_069(self):
        self.totals(self.load([row(30), row(-20)]), expenses=50)

    def test_TC_070(self):
        result = self.load([row(0), row(0, kind='Income')])
        self.totals(result, expenses=0)
        self.assertEqual([t.get_transaction_type() for t in result['transactions']], ['Expense', 'Income'])

    def test_TC_071(self):
        result = self.load([row(25, category=''), row(10)])
        self.totals(result, expenses=35)
        self.assertEqual(dict(self.top(result)['top_categories']), {'Uncategorized': 25, 'Food': 10})
        self.issue(result, 2, 'category', 'uncategorized')

    def test_TC_072(self):
        result = self.load([row(20, date='03/04/2026')], start='2026-03-01', end='2026-03-31')
        self.totals(result, expenses=20)
        self.assertEqual(self.exported_rows[0]['date'], '2026-03-04')

    def test_TC_073(self):
        result = self.load([row(20, date='03-04-26')], start='2026-04-01', end='2026-04-30')
        self.totals(result, expenses=20)
        self.assertEqual(self.exported_rows[0]['date'], '2026-04-03')

    def test_TC_074(self):
        rows = [row(20, date='12/11/2026'), row(30, date='12-11-26')]
        for month, expected, cleaned in [('11', 30, '2026-11-12'), ('12', 20, '2026-12-11')]:
            with self.subTest(month=month):
                result = self.load(rows, start=f'2026-{month}-01', end=f'2026-{month}-28')
                self.totals(result, expenses=expected)
                self.assertEqual(self.exported_rows[0]['date'], cleaned)

    def test_TC_075(self):
        result = self.load([row(40, date='2026-02-30'), row(10, date='2026-02-28')],
                           start='2026-02-01', end='2026-02-28')
        self.totals(result, expenses=10)
        self.issue(result, 2, 'date', 'date')

    def test_TC_077(self):
        rows = [row(25, date=''), row(10)]
        result = self.load(rows)
        self.totals(result, expenses=35)
        self.assertEqual(self.months(result), {'2026-10': 10})
        self.issue(result, 2, 'date', 'missing')
        self.totals(self.load(rows, start='2026-10-01', end='2026-10-31'), expenses=10)

    def test_TC_078(self):
        self.duplicate_case(20, 2)

    def test_TC_079(self):
        result = self.load([row(20, id='T0001', location='Mumbai'), row(20, id='T0001', location='Delhi')])
        self.totals(result, expenses=40)
        self.assertEqual(result['counts']['duplicates'], 0)
        self.assertEqual(len(result['transactions']), 2)

    def test_TC_080(self):
        result = self.load([row('$20', id='T0001'), row('₹20', id='T0001')])
        self.totals(result, expenses=40)
        self.assertEqual(result['counts']['duplicates'], 0)
        self.assertEqual([t.get_original_currency() for t in result['transactions']], ['$', '₹'])

    def test_TC_081(self):
        result = self.load([row(20, id='T0001', category='food'), row(20, id='T0001', category='Food')])
        self.totals(result, expenses=40)
        self.assertEqual(result['counts']['duplicates'], 0)
        self.assertEqual(self.top(result)['top_categories'], [('Food', 40)])

    def test_TC_082(self):
        result = self.load([row(25, date='nonsense-date'), row(10)],
                           start='2026-10-01', end='2026-10-31')
        self.totals(result, expenses=10)
        self.assertIsNone(result['records'][0]['date'])
        self.issue(result, 2, 'date', 'date')

    def test_TC_083(self):
        result = self.load([row('12foo'), row(10)])
        self.totals(result, expenses=10)
        self.issue(result, 2, 'amount', 'unrecognized')

    def test_TC_084(self):
        result = self.load([row(10), row(20, category='food')])
        self.assertEqual(self.top(result)['top_categories'], [('Food', 30)])
        self.totals(result, expenses=30)

    def test_TC_085(self):
        result = self.load([row(15, category=''), row(25, category='Fod')])
        self.assertEqual(self.top(result)['top_categories'], [('Food', 25), ('Uncategorized', 15)])
        self.issue(result, 2, 'category', 'uncategorized')
        self.issue(result, 3, 'category', 'normalized')

    def test_TC_088(self):
        self.sentinel_case([-99999999, -100000000], 99999999)

    def test_TC_089(self):
        self.sentinel_case([99999999.99, 100000000.01], 99999999.99)

    def test_TC_090(self):
        self.currency_case(['$12.50', '₹12.50', 'Rs.12.50', '12.50 INR'], [12.5]*4, ['$', '₹', 'Rs.', 'INR'])

    def test_TC_091(self):
        result = self.load([row(15, category='   '), row(25)])
        self.totals(result, expenses=40)
        self.assertEqual(self.top(result)['top_categories'], [('Food', 25), ('Uncategorized', 15)])
        self.issue(result, 2, 'category', 'uncategorized')

    def test_TC_092(self):
        result = self.load([row(20, date='2024-02-29'), row(10, date='2025-02-28')])
        self.assertEqual(self.months(result), {'2024-02': 20, '2025-02': 10})
        self.assertEqual([r['date'] for r in self.exported_rows], ['2024-02-29', '2025-02-28'])

    def test_TC_093(self):
        result = self.load([row(60, date='2025-02-29'), row(10, date='2025-02-28')],
                           start='2025-02-01', end='2025-02-28')
        self.totals(result, expenses=10)
        self.issue(result, 2, 'date', 'date')

    def test_TC_094(self):
        result = self.load([row('$12x'), row(10)])
        self.totals(result, expenses=10)
        self.issue(result, 2, 'amount', 'unrecognized')

    def test_TC_095(self):
        result = self.load([row(35, category='UnexpectedCategoryXYZ')])
        self.totals(result, expenses=35)
        self.assertEqual(self.top(result)['top_categories'], [('Uncategorized', 35)])
        self.issue(result, 2, 'category', 'unknown')

    def test_TC_096(self):
        self.duplicate_case(15, 3)

    def test_TC_097(self):
        result = self.load([row(30, id='T0001', kind='Income'), row(30, id='T0001')])
        self.totals(result, expenses=30, income=30)
        self.assertEqual(result['counts']['duplicates'], 0)
        self.assertEqual(len(result['transactions']), 2)

    def test_TC_098(self):
        result = self.load([row('invalid', date='bad-date'), row(10)])
        self.totals(result, expenses=10)
        self.assertEqual(len(result['transactions']), 1)
        self.issue(result, 2, 'amount', 'unrecognized')

    def test_TC_099(self):
        result = self.load([row(20), row(30, category='food')], category='Food')
        self.totals(result, expenses=50)
        self.assertEqual(self.top(result)['top_categories'], [('Food', 50)])
        self.assertEqual(self.months(result), {'2026-10': 50})
        limit = load_limits()['Food']
        self.budget(result, actual=50, limit=limit, difference=50-limit)


expected_ids = {f'TC_{number:03d}' for number in range(1, 100)
                if number not in MANUAL_CASE_IDS}
actual_ids = {name.removeprefix('test_') for name in dir(WorkbookTests) if name.startswith('test_TC_')}
if expected_ids != actual_ids or set(CASE_DESCRIPTIONS) != {key.replace('_', '-') for key in expected_ids}:
    raise RuntimeError(f'Workbook coverage mismatch: missing={expected_ids-actual_ids}, extra={actual_ids-expected_ids}')
for case_id, description in CASE_DESCRIPTIONS.items():
    method = getattr(WorkbookTests, 'test_' + case_id.replace('-', '_'))
    method.__doc__ = f'{case_id} | {description}'


def tearDownModule():
    print('Test cases TC-038, TC-049, TC-076, TC-086, and TC-087 should be tested manually.',
          flush=True)


if __name__ == '__main__':
    unittest.main(verbosity=2)
