# analysis/summaries

Summary totals and spending rankings over cleaned transactions.

| Item | Details |
|---|---|
| Responsible | Bahareh |
| Domain reviewer | Henrieta |
| PR approval | Zeyad or Patrick — see `CONTRIBUTING.md` |
| Task | P3.3 |
| Status | Implemented; 27 dictionary-based tests passed. Model integration and full-data validation pending. |
| Dependency | P3.2 aggregation; G2 for final validation |

## 1. Purpose

This module provides six outputs:

- Total income
- Total expenses
- Net balance
- Monthly expenses
- Top spending categories
- Largest individual expenses

Overall totals, monthly totals, and category rankings use the public
`budgetwise.analysis.aggregation` interface.

Individual expense rankings examine the transactions directly because
category totals cannot identify the largest individual transactions.

## 2. Public interface

```python
from budgetwise.analysis.summaries import (
    total_income,
    total_expenses,
    net_balance,
    monthly_expenses,
    top_categories,
    top_expenses,
)
```

| Call | Returns |
|---|---|
| `total_income(transactions)` | Total income as a float |
| `total_expenses(transactions)` | Total expenses as a float |
| `net_balance(transactions)` | Income minus expenses as a float |
| `monthly_expenses(transactions)` | Dictionary mapping `("YYYY", "MM")` to expense totals |
| `top_categories(transactions, n=5)` | List of `(category, expense_total)` pairs |
| `top_expenses(transactions, n=5)` | List of original expense dictionaries or objects |

The interface accepts cleaned dictionaries or model objects with the
required getters. Current summary tests verify dictionary inputs;
integration with the actual model classes remains pending.

## 3. Input and calculation rules

- Inputs must already be cleaned; this module does not repeat cleaning.
- Amounts are unsigned magnitudes.
- Income and expense classification comes from `transaction_type`.
- Undated records remain in overall totals and both rankings.
- Undated expenses are excluded from monthly totals.
- Month keys are returned in chronological order by aggregation.
- Category rankings sort by total descending, then category name ascending.
- Individual expense rankings sort by amount descending and preserve
  input order for equal amounts.
- The same ordered input produces the same ranking.
- Input records are not modified or deduplicated.

## 4. Ranking limits and empty input

Both ranking functions default to `n=5`.

- `n=0` returns an empty list.
- Fewer than `n` available results returns all available results.
- Negative `n` raises `ValueError`.
- Noninteger `n`, including booleans, raises `TypeError`.
- Income records are excluded from both spending rankings.

Empty input returns zero for overall totals and net balance,
an empty dictionary for monthly expenses, and empty lists for rankings.

## 5. Files

| Folder | Files |
|---|---|
| `implementation/` | `totals.py`, `rankings.py` |
| `testing/` | `fixture.py`, `test_totals.py`, `test_rankings.py` |
| `supplementary/` | `manual_verification.md` |

## 6. Validation

Run from the repository root:

```bash
python -m unittest budgetwise.analysis.summaries.testing.test_totals budgetwise.analysis.summaries.testing.test_rankings -v
```

Observed result on the supplied branch ZIP with Python 3.12.14:

```text
Ran 27 tests

OK
```

The ten-record fixture includes hand-calculated expectations,
undated transactions, and equal-amount ties.

See [manual verification](supplementary/manual_verification.md)
for expected versus actual results, execution details,
and the repository-wide test findings.

## 7. Remaining work

- Verify summaries with the actual Transaction model classes.
- Reconcile all summaries on the full cleaned dataset after G2.
- Record the exact commit and dataset used for final validation.

The current sample results are fixture results, not full-dataset figures.
Budget comparisons belong to `analysis/budgets`.
