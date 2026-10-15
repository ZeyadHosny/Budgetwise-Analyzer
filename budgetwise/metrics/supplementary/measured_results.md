# Measured Results

Run measurements required by §5, recorded for the report.

## Provisional run (before G4)

Source: `main` at commit `6055967`, 2026-10-13, on
`data/raw/budgetwise_finance_dataset.csv`. Python 3.10.12, Linux.
Replace with the frozen G4 run before reporting.

| Measurement | Value |
|---|---|
| Input records | 15,900 |
| Valid records | 14,651 |
| Corrected records | 14,587 |
| Skipped records | 349 |
| Duplicates detected | 900 |
| Categories normalized | 10,955 |
| Loading time | 0.0429 s |
| Cleaning time | 0.6500 s |
| Analysis time | 0.0595 s |
| Total time | 0.7524 s |

Check: 14,651 valid + 349 skipped + 900 duplicates = 15,900 input.

## Definitions

| Count | Meaning |
|---|---|
| Duplicates | Exact copies of an earlier raw row, removed before cleaning |
| Skipped | Rows that could not be cleaned, such as a missing amount |
| Valid | All remaining rows |
| Corrected | Valid rows with at least one value standardized, counted once per row |
| Categories normalized | Valid rows whose category changed, including 266 blanks set to `Uncategorized` |

Corrected rows are a subset of valid rows and are not part of the check above.

## Reproduce

```python
from budgetwise.errorlog import ErrorLog
from budgetwise.pipeline import clean_file
from budgetwise.analysis.aggregation import totals_by_category, totals_by_month
from budgetwise.metrics import RunMetrics, timed

log = ErrorLog("output/logs/errors.log")
result = clean_file("data/raw/budgetwise_finance_dataset.csv", log)
log.close()

metrics = RunMetrics.from_pipeline(result)
with timed(metrics, "analysis"):
    for kind in ("expense", "income"):
        totals_by_category(result["records"], kind=kind)
        totals_by_month(result["records"], kind=kind)

print(metrics.format_report())
```