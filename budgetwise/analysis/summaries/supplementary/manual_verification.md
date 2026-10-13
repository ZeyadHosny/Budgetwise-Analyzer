# P3.3 — Manual verification

**Responsible:** Bahareh  
**Domain reviewer:** Henrieta  
**Branch:** `feat/p3-3-summaries`

## 1. Sample and rules

Source: `../testing/fixture.py`

The sample contains ten cleaned dictionaries: seven expenses and three
income records. One expense and one income record have no date.

- Transaction direction comes from `transaction_type`, never the amount sign.
- Undated transactions remain in overall totals and rankings.
- Undated transactions are excluded from monthly expenses.
- Category ties use category name in ascending order.
- Individual expense ties preserve the supplied input order.

## 2. Hand calculations and actual results

Actual results were verified by the passing fixture tests.

| Output | Hand-calculated expected | Actual | Result |
|---|---|---|---|
| Total income | 1000 + 500 + 100 = 1600 | 1600.0 | PASS |
| Total expenses | 120 + 200 + 500 + 80 + 200 + 150 + 50 = 1300 | 1300.0 | PASS |
| Net balance | 1600 − 1300 = 300 | 300.0 | PASS |
| January expenses | 120 + 200 + 500 = 820 | 820.0 | PASS |
| February expenses | 80 + 200 + 150 = 430 | 430.0 | PASS |
| Undated expense difference | 1300 − (820 + 430) = 50 | 50.0 | PASS |

### Top five spending categories

| Rank | Category | Expected total | Actual total |
|---|---|---|---|
| 1 | Rent | 500.0 | 500.0 |
| 2 | Food | 250.0 | 250.0 |
| 3 | Other | 200.0 | 200.0 |
| 4 | Transportation | 200.0 | 200.0 |
| 5 | Utilities | 150.0 | 150.0 |

Food includes the undated expense: 120 + 80 + 50 = 250.
The undated income in Other is excluded from spending totals.

### Top five individual expenses

| Rank | Expected ID | Actual ID | Amount |
|---|---|---|---|
| 1 | E03 | E03 | 500.0 |
| 2 | E02 | E02 | 200.0 |
| 3 | E05 | E05 | 200.0 |
| 4 | E06 | E06 | 150.0 |
| 5 | E01 | E01 | 120.0 |

E02 precedes E05 because it appears earlier in the input.

## 3. Test execution

Executed on the extracted contents of
`Budgetwise-Analyzer-feat-p3-3-summaries.zip`.

- Execution date: October 11, 2026 (America/New_York)
- Python version: 3.12.14
- Exact commit SHA: not recorded; the supplied ZIP was the tested snapshot.

From the repository root:

```bash
python -m unittest budgetwise.analysis.summaries.testing.test_totals budgetwise.analysis.summaries.testing.test_rankings -v
```

Observed result:

```text
Ran 27 tests in 0.001s

OK
```

Coverage includes hand-calculated totals and rankings, undated records,
empty input, income-only input, expense-only totals, ranking limits,
tie rules, generators, repeated transaction IDs, and input preservation.

## 4. Repository-wide check

Command:

```bash
python -m unittest discover
```

Observed result:

```text
Ran 134 tests in 0.057s

FAILED (failures=2)
```

Both failures were structural checks outside summaries:

- Missing testing package files in cleaning/dates, cleaning/rows,
  and interface/menu.
- Missing required layout files in cleaning/dates, cleaning/notes,
  cleaning/rows, and interface/menu.

The 27 P3.3 tests passed in this run.

## 5. Remaining validation

The current tests verify cleaned dictionary inputs.

Integration with the actual Transaction model classes and reconciliation
on the full cleaned dataset remain pending. Final full-data validation
depends on G2. No full-dataset summary results are claimed here.
