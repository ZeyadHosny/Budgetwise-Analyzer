# analysis/aggregation/testing

Henrietta · domain reviewer Bahareh

## Fixture

`fixture.py` holds twenty cleaned rows, including three undated ones, with every expected total summed by hand in its docstring. The same rows are also provided as Transaction-like objects, so every result is checked against both input shapes.

## Cases covered

- [x] Category totals match the hand-summed fixture (expense and income)
- [x] Month totals match the same fixture (expense and income)
- [x] Undated transactions appear in category totals
- [x] The same transactions are absent from every month total (difference = 1,350)
- [x] `kind="expense"` excludes income rows, and the reverse
- [x] An unknown `kind` raises `ValueError`
- [x] `unique_categories` returns a `set`
- [x] Month keys are tuples of two strings, in chronological order
- [x] Month-and-category totals add up to the month totals
- [x] An empty list returns empty containers, not an error

## Run

From the project root:

```bash
python -m unittest budgetwise.analysis.aggregation.testing.test_by_category budgetwise.analysis.aggregation.testing.test_by_month -v
```

Expected result: `Ran 27 tests ... OK`.

## Checked against the real data

On the full dataset through `clean_file()` (provisional, before `G4`): expense category total 165,749,066; expense month total 162,224,605; the 3,524,461 difference equals the undated expense transactions exactly.

After `P3.3`, the sum of `totals_by_category(kind="expense")` should equal the total-expenses figure `summaries/` reports.
