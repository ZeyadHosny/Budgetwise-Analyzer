# Metrics

## Measurements

| Measurement | Definition |
|---|---|
| Input records | Rows read from the CSV |
| Valid records | Rows kept after cleaning |
| Corrected records | Valid rows with at least one value standardized, counted once per row |
| Skipped records | Rows that could not be cleaned, such as a missing amount |
| Duplicates detected | Exact copies of an earlier raw row, removed before cleaning |
| Categories normalized | Valid rows whose category was changed |
| Execution time | Loading, cleaning and analysis, timed separately |

The counts reconcile as input = valid + skipped + duplicates. Corrected records
are a subset of valid records and are not part of this check.

## Interface

```python
from budgetwise.metrics import RunMetrics, timed

metrics = RunMetrics.from_pipeline(result)   # counts and times from clean_file() or run()
with timed(metrics, "analysis"):
    ...                                      # any further phase
metrics.reconciles()                         # True when the counts add up
print(metrics.format_report())
```

`RunMetrics` also has `record_*` methods for each count and `add_time()` for
each phase. Counts can only increase; negative or non-whole counts raise
`ValueError`. `timed()` records the time even if the block raises an error.

Counts on the synthetic dirty dataset:

```
Input records                  15,836
Valid records                  14,862
Corrected records              12,879
Invalid / skipped records         170
Duplicates detected               804
Categories normalized           3,969
```

## Execution time for the report

`supplementary/run_timings.py` runs the pipeline seven times, each in a new
Python process, and prints every run's stage times with the median and range
per stage. It times loading, cleaning, object building, budget comparisons,
summary building, cleaning statistics and export, plus the pipeline total and a
separate financial-analysis step. Imports and process startup are not timed.

```bash
python budgetwise/metrics/supplementary/run_timings.py
python budgetwise/metrics/supplementary/run_timings.py --dataset data/raw/budgetwise_finance_dataset.csv --runs 7
```

The synthetic dirty dataset is the default. Each run exports its cleaned CSV,
summary and charts to `output/`, as the program does. Recorded results are in
`supplementary/measured_results.md`.


## Tests

17 tests cover starting values, each `record_*` method, invalid counts,
reconciliation, `timed()` (including when the block raises), separate phase
times, `from_pipeline()` and both report formats.

```bash
python -m unittest budgetwise.metrics.testing.test_counters -v
```
