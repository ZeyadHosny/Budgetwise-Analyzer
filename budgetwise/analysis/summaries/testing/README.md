# analysis/summaries/testing

**Task:** P3.3  
**Responsible:** Bahareh  
**Domain reviewer:** Henrieta

## Fixture

`fixture.py` provides ten cleaned dictionaries with hand-calculated
expected results: seven expenses and three income records.

One expense and one income record have no date. Equal expense amounts
and equal category totals allow the ranking tie rules to be checked.

## Tests

| File | Test count | Coverage |
|---|---|---|
| `test_totals.py` | 11 | Income, expenses, net balance, monthly expenses, undated reconciliation, empty input, income-only and expense-only input, generators, transaction direction, input preservation |
| `test_rankings.py` | 16 | Category and expense rankings, tie rules, result limits, empty input, income exclusion, undated expenses, invalid limits, input preservation, original record identity, repeated IDs, generators |

These tests use cleaned dictionaries. They do not verify integration
with the actual Transaction model classes.

## Run

From the repository root:

```bash
python -m unittest budgetwise.analysis.summaries.testing.test_totals budgetwise.analysis.summaries.testing.test_rankings -v
```

Observed on the supplied branch ZIP using Python 3.12.14:

```text
Ran 27 tests

OK
```

## Evidence and remaining validation

See [manual verification](../supplementary/manual_verification.md)
for hand-calculated versus actual results and execution details.

Model integration and full-dataset reconciliation remain pending.
The sample totals must not be presented as full-dataset results.
