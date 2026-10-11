# analysis/aggregation

Groups cleaned transactions into totals by category and by month.

| | |
|---|---|
| **Responsible** | Henrietta |
| **Domain reviewer** | Bahareh (`P3.2`) |
| **PR approval** | Zeyad or Patrick — see `CONTRIBUTING.md` |
| **Tasks** | `P3.2` |
| **Status** | Implemented and under review |

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
| `unique_categories(txns)` | `{"Food", "Rent", "Transportation", ...}` — a set |
| `count_by_category(txns, kind="expense")` | `{"Food": 3120, ...}` |
| `totals_by_month_and_category(txns, kind="expense")` | `{("2023", "07"): {"Food": 98000.0, ...}, ...}` |

Month keys are tuples, not strings, so they sort chronologically without any
date parsing. Transactions with no date are absent from `totals_by_month` but
still present in `totals_by_category` — §4.5 requires exactly that.

## 4. Requirements and tasks covered

| Requirement | Source | Task |
|---|---|---|
| Use dictionaries to aggregate totals by category and by month | §4.2 | `P3.2` |
| Use sets to identify unique categories | §4.2 | `P3.2` |
| Use tuples for fixed keys such as `(year, month)` | §4.2 | `P3.2` |
| Store transactions as a list of objects | §4.2 | `P3.2` |
| Missing date excluded from date analysis, still counts to category totals | §4.5 | `P3.2` |
| Organize and aggregate using appropriate data structures | §2 | `P3.2` |

