# Aggregation

Groups cleaned transactions into totals by category and by month. Summaries,
budgets and charts all build on these functions instead of re-walking the
transactions.

| | |
|---|---|
| **Responsible** | Henrietta |
| **Domain reviewer** | Bahareh |
| **PR approval** | Zeyad or Patrick (see `CONTRIBUTING.md`) |
| **Task** | `P3.2` |
| **Status** | Implemented |

## Interface

```python
from budgetwise.analysis.aggregation import (
    totals_by_category, count_by_category, unique_categories,
    totals_by_month, totals_by_month_and_category,
)
```

| Function | Returns |
|---|---|
| `totals_by_category(txns, kind=None)` | `{"Food": 16187376.0, ...}` |
| `count_by_category(txns, kind=None)` | `{"Food": 3734, ...}` |
| `unique_categories(txns)` | a `set` of category names |
| `totals_by_month(txns, kind=None)` | `{("2022", "06"): 215224.0, ...}` in date order |
| `totals_by_month_and_category(txns, kind=None)` | `{("2022", "06"): {"Food": 66285.0, ...}, ...}` |

- `kind` is `"expense"`, `"income"` or `None` for both. Any other value raises
  `ValueError`, so a typo fails instead of returning empty totals.
- `txns` can be `Transaction` objects or the cleaned records from
  `clean_file()`. `implementation/fields.py` reads both.
- Amounts are summed as magnitudes; direction comes from `transaction_type`.

## Data structures (§4.2)

| Structure | Used for | Why |
|---|---|---|
| `list` | the transactions | ordered and walked once per total |
| `dict` | totals by category and by month | keyed accumulation in one step |
| `set` | unique categories | membership without duplicates |
| `tuple` | the `(year, month)` key | immutable, so it can be a key, and sorts by date |

## Undated transactions (§4.5)

A row with no usable date counts in category totals but not in monthly totals,
so the two sums differ. On the synthetic dirty dataset:

| Expense total | Amount |
|---|---:|
| By category | 53,348,034 |
| By month | 53,104,693 |
| Difference: undated expenses | 243,341 |

This is expected. `supplementary/data_structure_choices.md` explains each
choice in more detail for the report.

## Files

| Folder | Contents |
|---|---|
| `implementation/` | `by_category.py`, `by_month.py`, `fields.py` |
| `testing/` | `test_by_category.py`, `test_by_month.py`, `fixture.py` |
| `supplementary/` | `data_structure_choices.md` |

## Tests

27 tests check every total against a 20-row fixture summed by hand, using both
input shapes, including undated rows, the `kind` filter, set and tuple types,
date order and empty input.

```bash
python -m unittest budgetwise.analysis.aggregation.testing.test_by_category budgetwise.analysis.aggregation.testing.test_by_month -v
```
