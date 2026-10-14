# metrics/testing

Henrietta · domain reviewer Patrick

## Cases covered

- [x] New metrics start at zero
- [x] Each `record_*` method adds to the right count
- [x] Negative, fractional, text and boolean counts are refused
- [x] `reconciles()` is true only when input = valid + skipped + duplicates
- [x] Corrected rows are not double counted in the reconciliation
- [x] A failed reconciliation shows a warning in the text report
- [x] `timed()` records elapsed time, even when the block raises
- [x] Load, clean and analysis times are kept separate; unknown phases and negative times are refused
- [x] `from_pipeline()` copies all six counts and both pipeline timings; missing keys default to zero
- [x] `report()` holds all seven measurements; `format_report()` lists them in §5 order

## Run

From the project root:

```bash
python -m unittest budgetwise.metrics.testing.test_counters -v
```

Expected result: `Ran 17 tests ... OK`.
