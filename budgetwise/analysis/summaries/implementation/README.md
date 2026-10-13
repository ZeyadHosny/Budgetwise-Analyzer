# analysis/summaries/implementation

**Task:** P3.3  
**Responsible:** Bahareh

## Modules

| Module | Functions |
|---|---|
| `totals.py` | `total_income`, `total_expenses`, `net_balance`, `monthly_expenses` |
| `rankings.py` | `top_categories`, `top_expenses` |

## Dependencies

Totals and category rankings use the public interface:

```python
from budgetwise.analysis.aggregation import (
    totals_by_category,
    totals_by_month,
)
```

No imports reach into another feature's implementation folder.

Individual expense rankings read cleaned records directly through
dictionary keys or the model getters `get_amount()` and
`get_transaction_type()`.

## Rules

- Inputs are already cleaned; amounts are unsigned.
- Transaction direction comes from `transaction_type`.
- Undated records remain in overall totals and rankings.
- Monthly expenses exclude undated records.
- Category ties use ascending category names.
- Expense ties preserve input order.
- Original records are not modified or deduplicated.

## Public access

Other features should import these functions from
`budgetwise.analysis.summaries`, not from this implementation folder.

## Validation

The 27 dictionary-based summary tests passed on the supplied branch ZIP.
Actual model integration and full-data reconciliation remain pending.

See [manual verification](../supplementary/manual_verification.md).
