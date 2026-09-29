# metrics

Times the run and counts what happened, for the report.

| | |
|---|---|
| **Responsible** | Zeyad |
| **Domain reviewer** | Patrick (`P3.5`) |
| **PR approval** | Zeyad or Patrick — see `CONTRIBUTING.md` |
| **Tasks** | `P3.5` |
| **Status** | Not started |

## 1. What this folder does

§5 names seven measurements the report must contain, and requires they be
**measured, not estimated**. This module produces all seven.

| Measurement | Where it comes from |
|---|---|
| Number of input records | rows the loader yielded |
| Number of valid records | transactions built |
| Number of corrected records | rows where a cleaner changed a value |
| Number of invalid / skipped records | rows dropped |
| Number of duplicates detected | `cleaning/rows` |
| Number of categories normalized | `cleaning/categories` |
| Execution time for loading, cleaning, analysis | timers here |

"Corrected" and "skipped" are different, and the report asks for both. A row
whose category was fixed from `Foodd` to `Food` is corrected. A row dropped for
having no amount is skipped. Agree the boundary at `G1` and record it, or the
two numbers will not be comparable between runs.

## 2. How other modules use it

```python
from budgetwise.metrics import RunMetrics, timed

metrics = RunMetrics()
with timed(metrics, "load"):
    rows = list(load_rows(path))
metrics.record_corrected("category")
metrics.report()
```

`pipeline/` drives this. `interface/` displays it.

## 3. What it produces

```
Input records            15,900
Valid records            14,100
Corrected records         4,802
Invalid / skipped records   900
Duplicates detected         900
Categories normalized    12,300

Loading    0.41 s
Cleaning   1.93 s
Analysis   0.28 s
Total      2.62 s
```

Figures show the shape, not real results. Real ones come from a run and go
straight into the report.

## 4. Requirements and tasks covered

| Requirement | Source | Task |
|---|---|---|
| Number of input records | §5 | `P3.5` |
| Number of valid records | §5 | `P3.5` |
| Number of corrected records | §5 | `P3.5` |
| Number of invalid / skipped records | §5 | `P3.5` |
| Number of duplicates detected | §5 | `P3.5` |
| Number of categories normalized | §5 | `P3.5` |
| Execution time for loading, cleaning, and analysis | §5 | `P3.5` |
| Results measured, not estimated | §5 | `P4.2` |

## 5. Folders

| Folder | Contents |
|---|---|
| `implementation/` | `timers.py`, `counters.py` |
| `testing/` | `test_counters.py` |
| `supplementary/` | `measured_results.md` |

## 6. Done when

- [ ] All seven measurements produced
- [ ] The corrected-versus-skipped boundary agreed at `G1` and written down
- [ ] Timings cover load, clean, and analysis separately
- [ ] Counts reconcile: input = valid + skipped + duplicates
- [ ] `measured_results.md` holds a real frozen run from `G4`
