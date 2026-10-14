# metrics/implementation

Henrietta · `P3.8` · domain reviewer Patrick

## Files

| File | Contents |
|---|---|
| `counters.py` | `RunMetrics`: the six counts and three timings §5 asks for |
| `timers.py` | `timed(metrics, phase)`: a context manager that times one phase |

## RunMetrics

```python
metrics = RunMetrics()                       # or RunMetrics.from_pipeline(result)
metrics.record_input(n=1)                    # also record_valid, record_corrected,
                                             # record_skipped, record_duplicate,
                                             # record_category_normalized
metrics.add_time("load", seconds)            # phases: load, clean, analysis
metrics.reconciles() -> bool                 # input == valid + skipped + duplicates
metrics.report() -> dict                     # counts, timings_seconds (+ total), reconciles
metrics.format_report() -> str               # aligned text; never prints
```

Counts are private and only grow: negative or fractional counts raise `ValueError`.

## Counting once, not twice

The pipeline already counts every category of row during its single pass.
`RunMetrics.from_pipeline(result)` copies those counts and the pipeline's
`load` and `clean` timings rather than walking the records a second time, so
the metrics can never disagree with what the pipeline actually did. Only the
analysis phase is timed separately:

```python
metrics = RunMetrics.from_pipeline(result)
with timed(metrics, "analysis"):
    ...  # aggregation and summaries
```

## Rules followed

- Timing uses `time.perf_counter()`, and each phase is timed separately (§5).
- Measured, never estimated.
- Returns values; the menu and report decide what to print.
- Standard library only; no pandas or numpy (§2).
