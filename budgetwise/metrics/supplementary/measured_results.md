# Measured Results

Run measurements required by §5, recorded for the report.

## Provisional run (before G4)

Source: `feature/P3.7-exports`, 2026-10-17, on the D01 dataset
`data/raw/budgetwise_synthetic_dirty.csv`. Python 3.12.10, Windows 11.
Replace with the frozen G4 run before reporting.

| Measurement | Value | finance (old) |
|---|---:|---:|
| Input records | 15,836 | 15,900 |
| Valid records | 14,862 | 14,651 |
| Corrected records | 11,469 | 14,587 |
| Skipped records | 170 | 349 |
| Duplicates detected | 804 | 900 |
| Categories normalized | 3,969 | 10,955 |
| Loading time | 0.0331 s | 0.0429 s |
| Cleaning time | 0.5455 s | 0.6500 s |
| Analysis time | 0.0224 s | 0.0595 s |
| Total time | 0.6010 s | 0.7524 s |

Check: 14,862 valid + 170 skipped + 804 duplicates = 15,836 input.

**Read the two count columns with care.** The D01 dataset produces *fewer*
corrections and *fewer* normalizations, which looks like a cleaner file and is
not. Those counts measure dirt the cleaners recognise and repair. This dataset
holds more dirt they cannot interpret: 2,259 unreadable dates and 1,540
unmapped category strings, against zero of each on the earlier file. §5 asks
for effectiveness, so quote those two alongside the table or the figures read
backwards.

### Per-stage timings

Median of 7 runs, same machine and date, from
`python budgetwise/metrics/supplementary/run_timings.py`:

| Workload | Median ms | Min-max ms |
|---|---:|---|
| Loading | 35.4 | 33.0-40.9 |
| Cleaning and issue logging | 561.9 | 527.5-636.9 |
| Object building and selection | 18.4 | 16.6-23.6 |
| Budget comparisons | 675.9 | 607.4-754.6 |
| Summary building | 76.5 | 68.8-77.8 |
| Preparing cleaning statistics | 18.0 | 17.1-19.0 |
| Export of cleaned CSV, summary and charts | 70.7 | 68.6-76.2 |
| **Pipeline total** | **1,474.2** | 1,363.8-1,569.0 |
| Financial analysis (separate) | 41.6 | 35.4-121.8 |

Budget comparisons are the largest single stage at 676 ms, ahead of cleaning
at 562 ms. The pipeline total exceeds the 0.60 s figure above because it also
builds objects, compares budgets, builds the summary and writes three output
files; the table above times `clean_file()` and the aggregation calls only.

## Definitions

| Count | Meaning |
|---|---|
| Duplicates | Exact copies of an earlier raw row, removed before cleaning |
| Skipped | Rows that could not be cleaned, such as a missing amount |
| Valid | All remaining rows |
| Corrected | Valid rows with at least one value standardized, counted once per row |
| Categories normalized | Valid rows whose category changed, including 154 blanks set to `Uncategorized` and 1,540 unmapped strings routed there |

Corrected rows are a subset of valid rows and are not part of the check above.

## Reproduce

```python
from budgetwise.errorlog import ErrorLog
from budgetwise.pipeline import clean_file
from budgetwise.analysis.aggregation import totals_by_category, totals_by_month
from budgetwise.metrics import RunMetrics, timed

log = ErrorLog("output/logs/errors.log")
result = clean_file("data/raw/budgetwise_synthetic_dirty.csv", log)
log.close()

metrics = RunMetrics.from_pipeline(result)
with timed(metrics, "analysis"):
    for kind in ("expense", "income"):
        totals_by_category(result["records"], kind=kind)
        totals_by_month(result["records"], kind=kind)

print(metrics.format_report())
```