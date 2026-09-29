# analysis/budgets

Largest expenses, and how actual spending compares with the agreed limits.

| | |
|---|---|
| **Responsible** | Patrick |
| **Domain reviewer** | Sarah (`P3.3`) |
| **PR approval** | Zeyad or Patrick — see `CONTRIBUTING.md` |
| **Tasks** | `P3.3` |
| **Status** | Not started |

## 1. What this folder does

The remaining two of §4.4's seven required outputs: the top five largest
individual expenses, and budget versus actual by category with clear over and
under indicators.

§4.4 also requires that the team **define monthly budget limits for at least
five categories and justify them**. The justification is a graded part of the
report, not an afterthought — a limit with no reasoning behind it is an
unsupported number in a marked document.

## 2. How other modules use it

```python
from budgetwise.analysis.budgets import largest_expenses, compare_to_budget

largest_expenses(transactions, n=5)
compare_to_budget(transactions, year="2023", month="07")
```

`interface/` displays both. The limits come from `config/monthly_budgets.json`.

## 3. What it produces

`largest_expenses(txns, n=5)` — five transactions, largest first:

```
2023-07-14  Food   9,984.00  T4999
2023-03-02  Rent   9,971.00  T12828
```

`compare_to_budget(txns, "2023", "07")`:

| Category | Limit | Actual | Status | Difference |
|---|---|---|---|---|
| Food | 8,000.00 | 9,240.00 | **over** | +1,240.00 |
| Rent | 12,000.00 | 11,800.00 | under | −200.00 |
| Travel | 5,000.00 | 5,000.00 | exact | 0.00 |

Sentinel rows at `999999999` are already gone — `cleaning/amounts` excludes them.
If one appears at the top of `largest_expenses`, the sentinel rule is not
working, and this is where you would first notice.

## 4. Requirements and tasks covered

| Requirement | Source | Task |
|---|---|---|
| Top 5 largest expense transactions | §4.4 | `P3.3` |
| Budget vs. actual spending by category | §4.4 | `P3.3` |
| Clear over/under indicators | §4.4 | `P3.3` |
| Monthly budget limits for at least five categories | §4.4 | `P3.3` |
| Those limits justified | §4.4 | `P3.3` `P4.4` |
| A `Budget` class comparing spending to limits, flagging overages | §4.3 | `P2.5` |
| Produce budget comparisons | §2 | `P3.3` |

## 5. Folders

| Folder | Contents |
|---|---|
| `implementation/` | `comparison.py`, `limits.py` |
| `testing/` | `test_comparison.py` |
| `supplementary/` | `budget_justification.md` |

## 6. Done when

- [ ] Top five largest expenses correct, ties handled by a stated rule
- [ ] At least five categories have limits in `config/monthly_budgets.json`
- [ ] Every limit justified in writing
- [ ] Over, under, and exact all produce the right status and difference
- [ ] Categories with no limit are handled by an agreed rule, not ignored silently
