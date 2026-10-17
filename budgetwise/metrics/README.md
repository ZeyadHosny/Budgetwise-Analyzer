# Metrics

Records the counts and phase timings of each run for the report (§5).

| | |
|---|---|
| **Responsible** | Henrietta |
| **Reviewer** | Patrick |
| **PR approval** | Zeyad or Patrick (see `CONTRIBUTING.md`) |
| **Task** | `P3.8` |
| **Status** | Implemented, under review |

## Measurements

Section 5 requires the following values:

| Measurement | Definition |
|---|---|
| Input records | Rows read from the CSV |
| Valid records | Rows kept after cleaning |
| Corrected records | Valid rows with at least one value standardized, counted once per row |
| Skipped records | Rows that could not be cleaned |
| Duplicates detected | Exact copies of an earlier raw row, removed before cleaning |
| Categories normalized | Valid rows whose category was changed |
| Execution time | Loading, cleaning and analysis, timed separately |

The counts reconcile as: input = valid + skipped + duplicates.
Corrected records are a subset of valid records and are not part of this check.

## Usage

```python
from budgetwise.metrics import RunMetrics, timed

result = clean_file(path)
metrics = RunMetrics.from_pipeline(result)

with timed(metrics, "analysis"):
    ...  # aggregation and summaries

print(metrics.format_report())
```

`RunMetrics.from_pipeline` copies the counts and the loading and cleaning times
from the pipeline result. `timed` measures any further phase, such as analysis.
`reconciles()` returns `True` when the counts add up.

## Execution time for the report

`supplementary/run_timings.py` runs the pipeline on the primary dataset seven
times, each in a new Python process, and prints each run's stage times with the
median and range per stage. Run it from the repository root:

```bash
python budgetwise/metrics/supplementary/run_timings.py
```

## Example output

Provisional run on the full dataset, 2026-10-13:

```
Input records                  15,900
Valid records                  14,651
Corrected records              14,587
Invalid / skipped records         349
Duplicates detected               900
Categories normalized          10,955

Loading                      0.0429 s
Cleaning                     0.6500 s
Analysis                     0.0595 s
Total                        0.7524 s
```

Final figures will come from the G4 frozen run. See
`supplementary/measured_results.md`.

## Files

| Folder | Contents |
|---|---|
| `implementation/` | `counters.py` (run counts), `timers.py` (phase timer) |
| `testing/` | `test_counters.py` |
| `supplementary/` | `measured_results.md`, `run_timings.py` |

## Tests

```bash
python -m unittest budgetwise.metrics.testing.test_counters -v
```

## Status

- [x] All required measurements produced
- [x] Loading, cleaning and analysis timed separately
- [x] Counts reconcile
- [x] Repeated timing script for the report
- [ ] Corrected and skipped definitions agreed by the team (`D08`)
- [ ] Final results recorded from the G4 run