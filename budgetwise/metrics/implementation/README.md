# Implementation

| File | Contents |
|---|---|
| `counters.py` | `RunMetrics`, which stores the counts and timings |
| `timers.py` | `timed()`, which measures how long a block of code takes |

## RunMetrics

```python
metrics = RunMetrics()                    # empty
metrics = RunMetrics.from_pipeline(result)  # filled from the cleaning pipeline

metrics.record_input(n)                   # also record_valid, record_corrected,
                                          # record_skipped, record_duplicate,
                                          # record_category_normalized
metrics.add_time("load", seconds)         # phases: load, clean, analysis

metrics.reconciles()                      # True if input = valid + skipped + duplicates
metrics.report()                          # all values as a dictionary
metrics.format_report()                   # all values as aligned text
```

Counts can only increase. Negative or non-whole counts raise `ValueError`.

## timed

```python
with timed(metrics, "analysis"):
    ...
```

Records the elapsed time even if the block raises an error.