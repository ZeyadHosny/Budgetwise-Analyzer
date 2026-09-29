# metrics/implementation

Zeyad · `P3.5` · domain reviewer Patrick

## Write these

```python
class RunMetrics:
    record_input()                  one raw row read
    record_valid()                  one transaction built
    record_corrected(field)         a cleaner changed a value
    record_skipped(reason)          a row was dropped
    record_duplicate()
    record_category_normalized()
    report() -> dict

@contextmanager
def timed(metrics, phase)           times a block, stores seconds
```

## Count while you go

Counting during the single pass the pipeline already makes costs nothing. A
second pass afterwards to work out what happened is slower and can disagree with
what was actually done.

## Make the numbers reconcile

```
input = valid + skipped + duplicates
```

If that does not hold, some rows are being counted twice or not at all. Assert it
at the end of a run — a report whose own totals do not add up invites exactly the
question you do not want in Q&A.

## Corrected versus skipped

- **Corrected** — the row survived, but a value changed. `Foodd` → `Food`, a date
  reformatted, a `₹` stripped.
- **Skipped** — the row did not survive. No amount, unparseable beyond recovery,
  or an exact duplicate.

A row can be corrected more than once — different fields. Decide at `G1` whether
that counts once or several times, and write it in `measured_results.md`. Both
are defensible; only silence is not.

## Timing

`time.perf_counter()` from the standard library. Time the three phases §5 names
separately — one total is not what the assignment asks for.

## Do not

- Estimate. §5 says measured values.
- Print — `interface/` does that.
- Import pandas or numpy — violates §2.
