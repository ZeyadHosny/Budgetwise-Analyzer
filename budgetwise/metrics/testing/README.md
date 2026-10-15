# Tests

`test_counters.py` checks that:

- new metrics start at zero
- each `record_*` method updates the right count
- invalid counts are rejected
- `reconciles()` is true only when every row is accounted for
- `timed()` records time, including when the block raises an error
- load, clean and analysis times are kept separate
- `from_pipeline()` copies all counts and timings
- `report()` and `format_report()` include all seven measurements

## Run

```bash
python -m unittest budgetwise.metrics.testing.test_counters -v
```

Expected: 17 tests, all passing.