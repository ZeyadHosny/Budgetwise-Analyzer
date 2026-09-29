# analysis/summaries/testing

Bahareh · domain reviewer Henrieta

## Required cases

- [ ] `total_income` counts only income rows
- [ ] `total_expenses` counts only expense rows
- [ ] A negative raw amount still contributes its positive magnitude
- [ ] `net_balance` equals income minus expenses
- [ ] `monthly_expenses` keys are `(year, month)` tuples
- [ ] `top_categories` returns exactly `n`, ordered descending
- [ ] Fewer than `n` categories returns all of them, not an error
- [ ] A tie is broken by the documented rule, the same way twice
- [ ] Totals equal `aggregation`'s totals for the same fixture

## Hand verification — required by P3.2

The workbook note says *"Cross-check totals manually on small sample."* Take
twenty rows, add them up on paper, and assert those exact numbers. Record the
working in `supplementary/manual_verification.md`.

This is the only check that catches a plausible-looking wrong answer. A test
that compares your code to your code proves nothing.

## Run

```bash
python -m unittest discover
```

Check how many tests ran, not just that it said `OK`.
