# analysis/aggregation/testing

Henrieta · domain reviewer Zeyad

## Required cases

- [ ] Category totals match a hand-summed twenty-row fixture exactly
- [ ] Month totals match the same fixture
- [ ] A transaction with no date appears in the category total
- [ ] That same transaction is **absent** from every month total
- [ ] `kind="expense"` excludes income rows, and the reverse
- [ ] `unique_categories` returns a `set`, not a list
- [ ] Month keys are tuples of two strings, not a string like `"2023-07"`
- [ ] An empty transaction list returns empty containers, not an error

## Verify against the real data

After running the full dataset, the sum of `totals_by_category(kind="expense")`
should equal the total-expenses figure `summaries/` reports. If they differ, one
of you is filtering differently — find out which before either result is used in
the report.

## Run

```bash
python -m unittest discover
```

Check how many tests ran, not just that it said `OK`.
