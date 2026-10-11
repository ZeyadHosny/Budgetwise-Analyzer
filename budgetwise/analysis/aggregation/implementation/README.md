# analysis/aggregation/implementation

Henrietta · `P3.2` · domain reviewer Bahareh

## Files

| File | Contents |
|---|---|
| `by_category.py` | `totals_by_category`, `count_by_category`, `unique_categories` |
| `by_month.py` | `totals_by_month`, `totals_by_month_and_category` |
| `fields.py` | Reads one value from a transaction, whichever shape it arrives in |

## Functions

```python
totals_by_category(transactions, kind=None)           -> dict[str, float]
count_by_category(transactions, kind=None)            -> dict[str, int]
unique_categories(transactions)                       -> set[str]
totals_by_month(transactions, kind=None)              -> dict[tuple[str, str], float]
totals_by_month_and_category(transactions, kind=None) -> dict[tuple[str, str], dict[str, float]]
```

- `kind` is `"expense"`, `"income"` or `None` for both. Case is ignored. Anything else raises `ValueError`, so a typo fails loudly instead of returning empty totals.
- `transactions` is a list of `Transaction` objects (`budgetwise.models`) or cleaned record dicts (`budgetwise.pipeline.clean_file()`).
- Monthly results come back in chronological order.

## The rule that is easy to get wrong

§4.5: a missing date is excluded from date analysis but still counts toward category totals. So `totals_by_category` includes undated rows and `totals_by_month` skips them, and their sums differ. See `../supplementary/data_structure_choices.md`.

## Rules followed

- Amounts are summed as unsigned magnitudes; direction comes from `transaction_type`.
- No file reading: the functions receive transactions from the pipeline.
- Standard library only (`collections.defaultdict`); no pandas or numpy (§2).
