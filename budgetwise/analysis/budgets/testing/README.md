# analysis/budgets/testing

Patrick · domain reviewer Sarah

## Required cases

- [ ] `largest_expenses` returns exactly `n`, largest first
- [ ] Income transactions never appear, however large
- [ ] Fewer than `n` expenses returns all of them, not an error
- [ ] Spending above the limit → `"over"` with a positive difference
- [ ] Spending below the limit → `"under"` with a negative difference
- [ ] Spending equal to the limit → `"exact"` with zero
- [ ] A category with no spending in that month → actual is `0.00`, not missing
- [ ] A category with no configured limit follows the agreed rule
- [ ] A month with no transactions returns empty results, not an error
- [ ] No transaction at or above `100_000_000` ever appears

That last one is a cross-check on Patrick's own cleaning module. If it fails,
the bug is in `cleaning/amounts`, not here.

## Run

```bash
python -m unittest discover
```

Check how many tests ran, not just that it said `OK`.
