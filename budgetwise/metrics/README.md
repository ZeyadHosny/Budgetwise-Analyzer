# Metrics

Counts and times each run of the program for the report.

| | |
|---|---|
| **Responsible** | Henrietta |
| **Reviewer** | Patrick |
| **PR approval** | Zeyad or Patrick (see `CONTRIBUTING.md`) |
| **Task** | `P3.8` |
| **Status** | Implemented, under review |

## What it measures

Section 5 requires seven measured values:

| Measurement | Source |
|---|---|
| Input records | Rows read from the CSV |
| Valid records | Rows kept after cleaning |
| Corrected records | Kept rows with at least one value standardized |
| Skipped records | Rows that could not be cleaned |
| Duplicates detected | Exact copies removed before cleaning |
| Categories normalized | Rows whose category was changed |
| Execution time | Loading, cleaning and analysis, timed separately |

The counts must satisfy: input = valid + skipped + duplicates.

## Usage

```python
from budgetwise.metrics import RunMetrics, timed

result = clean_file(path)
metrics = RunMetrics.from_pipeline(result)

with timed(metrics, "analysis"):
    ...  # aggregation and summaries

print(metrics.format_report())
```

`from_pipeline` takes the counts and the load and clean times from the cleaning
pipeline. `timed` adds the analysis time.

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
| `implementation/` | `counters.py`, `timers.py` |
| `testing/` | `test_counters.py` |
| `supplementary/` | `measured_results.md` |

## Tests

```bash
python -m unittest budgetwise.metrics.testing.test_counters -v
```

## Status

- [x] All seven measurements produced
- [x] Loading, cleaning and analysis timed separately
- [x] Counts reconcile
- [ ] Corrected and skipped definitions agreed by the team (`D08`)
- [ ] Final results recorded from the G4 run