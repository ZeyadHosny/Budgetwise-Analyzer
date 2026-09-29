# analysis/summaries/implementation

Bahareh · `P3.2` · domain reviewer Henrieta

## Write these

```python
total_income(transactions)        -> float
total_expenses(transactions)      -> float
net_balance(transactions)         -> float     income - expenses
monthly_expenses(transactions)    -> dict[tuple[str, str], float]
top_categories(transactions, n=5) -> list[tuple[str, float]]
```

## Build on aggregation, do not re-count

```python
from budgetwise.analysis.aggregation import totals_by_category, totals_by_month
```

`P3.2`'s collaborator is Henrieta for exactly this reason. Two independent loops
over the same data eventually disagree, and then the report has two answers to
one question with no way to tell which is right.

## Two things to get right

**Direction comes from `transaction_type`.** §4.5 is explicit: the amount is an
unsigned magnitude, and income versus expense is decided by the field, never by
a minus sign. The raw data has 153 negative amounts; every one of them is a
magnitude whose direction is set elsewhere.

**Ties in the top five need a rule.** If two categories total the same, decide
now how to order them — alphabetically is fine — and write it down. Without a
rule the ranking can change between runs on the same data, which looks like a
bug in the report.

## Trends

§2 asks for "spending summaries, budget comparisons, **and trends**", but §4.4
never defines a trend output. `monthly_expenses` is the material for it. Note
what the months actually show — growth, seasonality, a flat line — in
`manual_verification.md` so `P4.4` has something to write.

## Do not

- Re-implement grouping — use `aggregation`
- Use the sign of `amount` to classify a transaction
- Print — `interface/` does that
- Import pandas or numpy — violates §2
