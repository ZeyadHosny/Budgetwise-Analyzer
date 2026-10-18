# analysis/budgets/implementation

Patrick · `P3.3` · domain reviewer Sarah

## Write these

```python
largest_expenses(transactions, n=5) -> list[Transaction]
compare_to_budget(transactions, year, month) -> list[BudgetResult]

BudgetResult: category · limit · actual · status · difference
    status is "over", "under", "exact", or "unbudgeted"
    limit and difference are None for an unbudgeted category
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

**Categories with no limit.** Report categories with spending and no configured
limit as `unbudgeted`. Configured categories are included with actual zero when
another expense exists in that month. If the month has no expenses, return an
empty list.

## Watch for

Sentinel rows at `999999999` should already be excluded by `cleaning/amounts`.
If one shows up in `largest_expenses`, that rule has failed. This function is the
most likely place to spot it, so treat a suspiciously large figure as a bug
report for Patrick's own cleaning module rather than a real transaction.

## Do not

- Hard-code limits in Python — they belong in `config/`
- Reimplement the over/under logic — `models.Budget` owns it
- Import pandas or numpy — violates §2

To regenerate the historical limits and justification from the configured
category list, run from the repository root:

```bash
python -m budgetwise.analysis.budgets.implementation.generate_budget_evidence
```

The script uses the median monthly expense, rounded upward to the next 500
dataset units. Use `--increment`, `--dataset`, `--config`, and
`--justification` to override its defaults.
