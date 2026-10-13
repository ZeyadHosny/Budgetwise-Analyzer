# Summary Analysis

Calculates financial totals and spending rankings from cleaned transactions.

| Item | Details |
|---|---|
| Responsible | Bahareh |
| Task | P3.3 |
| Status | Implemented; 39 summary tests passed in a local review copy |
| Dependencies | Public aggregation interface; real models for integration tests |
| Final validation | Pending rerun on the final approved cleaning baseline |

## 1. Outputs

The public interface provides:

| Function | Result |
|---|---|
| `total_income(transactions)` | Total income |
| `total_expenses(transactions)` | Total expenses |
| `net_balance(transactions)` | Income minus expenses |
| `monthly_expenses(transactions)` | Expense totals keyed by `("YYYY", "MM")` |
| `top_categories(transactions, n=5)` | Category and expense-total pairs |
| `top_expenses(transactions, n=5)` | Original expense records or objects |

Totals, monthly expenses and category rankings use the public aggregation
interface. Individual expense rankings read transaction records directly.

## 2. Supported inputs

Functions accept cleaned dictionaries or Transaction objects providing
the agreed getters.

The caller selects which transactions to analyze. Functions do not load
files or receive an Account object directly.

After a successful `budgetwise.pipeline.run()` call:

```python
from budgetwise.analysis.summaries import (
    total_expenses,
    monthly_expenses,
    top_categories,
)

# Overall report for the selected pipeline result
overall_expenses = total_expenses(result["transactions"])

# Cash report
cash_transactions = result["accounts"]["cash"].get_transactions()
cash_expenses = total_expenses(cash_transactions)

# Bank report
bank_transactions = result["accounts"]["bank"].get_transactions()
bank_monthly = monthly_expenses(bank_transactions)

# Unknown-payment report
unknown_transactions = result["accounts"]["unknown"].get_transactions()
unknown_categories = top_categories(unknown_transactions)
```

Check pipeline errors and object-build failures before presenting a result
as complete.

Accounts hold the same transaction objects as the selected master list.
Do not add master totals to account totals: that would count records twice.

For an overall largest-expense ranking, use the ordered master list.
Concatenating account lists can change the order of equal-amount expenses.

## 3. Calculation rules

- Inputs must already be cleaned.
- Amounts are unsigned magnitudes.
- Income versus expense comes from `transaction_type`, not amount sign.
- Undated records remain in overall totals and rankings.
- Undated expenses are excluded from monthly totals.
- Months are returned in chronological order.
- Category ties use ascending category names.
- Individual expense ties preserve supplied input order.
- Input records are not modified or deduplicated.
- Repeated transaction IDs alone do not remove records.

Net balance represents income minus expenses over the selected records.
It is not an account balance including opening balances.

## 4. Limits and empty input

Ranking functions default to five results.

- Zero returns an empty list.
- Fewer available results returns all available results.
- Negative limits raise `ValueError`.
- Noninteger limits, including booleans, raise `TypeError`.

Empty input returns zero overall totals, an empty monthly dictionary,
and empty rankings.

## 5. Files

| Folder | Files |
|---|---|
| `implementation/` | `totals.py`, `rankings.py` |
| `testing/` | `fixture.py`, `test_totals.py`, `test_rankings.py`, `test_account_summaries.py` |
| `supplementary/` | `manual_verification.md` |

## 6. Tests

Run from the repository root:

```bash
python -m unittest budgetwise.analysis.summaries.testing.test_totals budgetwise.analysis.summaries.testing.test_rankings budgetwise.analysis.summaries.testing.test_account_summaries -v
```

The existing tests contain 27 dictionary-based cases. The new integration
file adds 12 tests using real ExpenseTransaction, IncomeTransaction,
CashAccount, BankAccount and UnknownAccount classes.

Integration coverage includes:
- All six outputs for overall and individual account selections.
- Hand-calculated expectations.
- Dictionary/object equivalence.
- Exactly-once fixture account coverage.
- Undated expenses and income.
- Stable ranking ties and original-object identity.
- Repeated transaction IDs.
- Empty accounts and unchanged inputs.
- Shared amount updates without cached totals.

Observed on October 13, 2026, using Python 3.12.14 in a local review copy of
`Budgetwise-Analyzer-feature-P3.7-exports.zip`, after adding the integration file:

```text
Ran 39 tests

OK
```

This result describes the review copy. Verify the actual integration branch
after committing the files.

These are fixture tests; they do not establish pipeline routing or
full-dataset correctness by themselves. Separate full-dataset review
findings are recorded in `supplementary/manual_verification.md`.

## 7. Reporting and exports

Summary functions return analysis values; formatting belongs to the menu
and export features.

- Monthly tuple keys need an explicit JSON-compatible representation.
- `top_expenses()` returns original objects or dictionaries, which an
  exporter must serialize using the agreed record fields.
- Budget comparisons belong to `analysis/budgets`.
- Account report selection belongs to the caller/menu.

## 8. Remaining validation

- Verify the committed integration branch.
- Preserve historical and current execution evidence separately.
- Record the exact revision and dataset for final validation after G2.
- Verify menu/report/export integration on the final application.
