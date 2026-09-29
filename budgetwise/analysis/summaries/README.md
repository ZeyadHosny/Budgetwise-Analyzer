# analysis/summaries

The headline numbers: income, expenses, balance, monthly spend, top five.

| | |
|---|---|
| **Responsible** | Bahareh |
| **Domain reviewer** | Henrieta (`P3.2`) |
| **PR approval** | Zeyad or Patrick — see `CONTRIBUTING.md` |
| **Tasks** | `P3.2` |
| **Status** | Not started |

## 1. What this folder does

Five of the seven outputs §4.4 names explicitly are produced here. They are
the figures the report leads with and the presentation opens on.

Everything here is built from `analysis/aggregation`. Do not re-walk the
transaction list — if a total disagrees with Henrieta's, the report contains two
different answers to the same question.

The main dataset holds **13,517 expense** and **2,383 income** rows before
cleaning.

## 2. How other modules use it

```python
from budgetwise.analysis.summaries import (
    total_income, total_expenses, net_balance,
    monthly_expenses, top_categories,
)

top_categories(transactions, n=5)   # [("Food", 8210400.0), ("Rent", ...), ...]
```

`interface/` displays these. `analysis/budgets` uses the monthly figures.

## 3. What it produces

| Call | Returns | §4.4 item |
|---|---|---|
| `total_income(txns)` | `14_082_330.0` | total income |
| `total_expenses(txns)` | `79_441_210.0` | total expenses |
| `net_balance(txns)` | `-65_358_880.0` | net balance |
| `monthly_expenses(txns)` | `{("2023","07"): 1_204_880.0, ...}` | monthly expenses |
| `top_categories(txns, n=5)` | five `(name, total)` pairs, descending | top 5 spending categories |

Figures above are illustrative of the shape, not real results — the real ones
come from a run and go in the report.

## 4. Requirements and tasks covered

| Requirement | Source | Task |
|---|---|---|
| Total income | §4.4 | `P3.2` |
| Total expenses | §4.4 | `P3.2` |
| Net balance | §4.4 | `P3.2` |
| Monthly expenses | §4.4 | `P3.2` |
| Top 5 spending categories | §4.4 | `P3.2` |
| Produce spending summaries and trends | §2 | `P3.2` `P4.4` |
| Direction from `transaction_type`, never the sign | §4.5 | `P3.2` |

## 5. Folders

| Folder | Contents |
|---|---|
| `implementation/` | `totals.py`, `rankings.py` |
| `testing/` | `test_totals.py`, `test_rankings.py` |
| `supplementary/` | `manual_verification.md` |

## 6. Done when

- [ ] All five figures produced
- [ ] Every one cross-checked by hand on a small sample — `P3.2`'s own note
- [ ] Ties in the top five broken by a documented, stable rule
- [ ] Totals agree with `aggregation`'s, to the cent
- [ ] `manual_verification.md` written — report evidence
