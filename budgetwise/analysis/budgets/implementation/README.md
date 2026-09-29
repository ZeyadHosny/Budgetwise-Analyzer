# analysis/budgets/implementation

Patrick · `P3.3` · domain reviewer Sarah

## Write these

```python
largest_expenses(transactions, n=5) -> list[Transaction]
compare_to_budget(transactions, year, month) -> list[BudgetResult]

BudgetResult: category · limit · actual · status · difference
    status is "over", "under", or "exact"
```

## The limits live in config, not in code

`config/monthly_budgets.json`. Keeping them as data means changing a limit does
not require changing code, and the file itself can go in the report as evidence.

Use the `Budget` class from `models/` for the comparison — §4.3 requires that
class to exist and do exactly this. Do not write a second comparison here.

## Three decisions to settle at G1

**Which five categories.** Must be at least five, and they should be the ones
that matter — the highest-spending categories are the defensible choice.

**What the limits are, and why.** "Justify them" is the graded part. A defensible
method: take the median monthly spend per category from the cleaned data and set
the limit near it, then say so. An arbitrary round number with no reasoning
behind it is worth less than a slightly awkward number you can explain.

**Categories with no limit.** Skip them, or report them as unbudgeted? Either is
fine. Deciding silently is not — pick one and write it down.

## Watch for

Sentinel rows at `999999999` should already be excluded by `cleaning/amounts`.
If one shows up in `largest_expenses`, that rule has failed. This function is the
most likely place to spot it, so treat a suspiciously large figure as a bug
report for Patrick's own cleaning module rather than a real transaction.

## Do not

- Hard-code limits in Python — they belong in `config/`
- Reimplement the over/under logic — `models.Budget` owns it
- Import pandas or numpy — violates §2
