# analysis/aggregation

Groups cleaned transactions into totals by category and by month.

| | |
|---|---|
| **Responsible** | Henrieta |
| **Domain reviewer** | Zeyad (`P3.1`) |
| **PR approval** | Zeyad or Patrick — see `CONTRIBUTING.md` |
| **Tasks** | `P3.1` |
| **Status** | Not started |

## 1. What this folder does

The shared counting layer. Everything in `summaries/` and `budgets/` is built
on top of these functions rather than re-walking the transaction list.

This folder is also where §4.2 is demonstrated, and §4.2 is graded directly —
the assignment names **lists, dictionaries, sets, and tuples** and expects each
to be used for the job it suits:

| Structure | Used for | Why |
|---|---|---|
| `list` | the transactions themselves | ordered, iterated repeatedly |
| `dict` | totals by category, totals by month | keyed lookup and accumulation |
| `set` | unique categories | membership and de-duplication |
| `tuple` | the `(year, month)` key | immutable, so it can be a dict key |

## 2. How other modules use it

```python
from budgetwise.analysis.aggregation import (
    totals_by_category, totals_by_month, unique_categories,
)

by_cat = totals_by_category(transactions, kind="expense")
by_month = totals_by_month(transactions, kind="expense")
```

`summaries/` and `budgets/` both use these. Neither re-implements them.

## 3. What it produces

| Call | Returns |
|---|---|
| `totals_by_category(txns, kind="expense")` | `{"Food": 8_210_400.0, "Rent": 7_980_120.0, ...}` |
| `totals_by_month(txns, kind="expense")` | `{("2023", "07"): 1_204_880.0, ...}` |
| `unique_categories(txns)` | `{"Food", "Rent", "Travel", ...}` — a set |

Month keys are tuples, not strings, so they sort chronologically without any
date parsing. Transactions with no date are absent from `totals_by_month` but
still present in `totals_by_category` — §4.5 requires exactly that.

## 4. Requirements and tasks covered

| Requirement | Source | Task |
|---|---|---|
| Use dictionaries to aggregate totals by category and by month | §4.2 | `P3.1` |
| Use sets to identify unique categories | §4.2 | `P3.1` |
| Use tuples for fixed keys such as `(year, month)` | §4.2 | `P3.1` |
| Store transactions as a list of objects | §4.2 | `P3.1` |
| Missing date excluded from date analysis, still counts to category totals | §4.5 | `P3.1` |
| Organize and aggregate using appropriate data structures | §2 | `P3.1` |

## 5. Folders

| Folder | Contents |
|---|---|
| `implementation/` | `by_category.py`, `by_month.py` |
| `testing/` | `test_by_category.py`, `test_by_month.py` |
| `supplementary/` | `data_structure_choices.md` |

## 6. Done when

- [ ] Totals cross-checked by hand against a twenty-row sample
- [ ] Dated and undated rows behave as §4.5 requires
- [ ] Month keys are tuples and sort chronologically
- [ ] `summaries/` and `budgets/` both use these rather than their own loops
- [ ] `data_structure_choices.md` written — report material
