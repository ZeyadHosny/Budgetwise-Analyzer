# models

Transaction, account, and budget classes used by the rest of the package. This folder does not import from any other feature.

## Classes

| Class | Parent | Purpose |
|---|---|---|
| `Transaction` | - | Base class for one cleaned transaction. |
| `ExpenseTransaction` | `Transaction` | Money going out. Signed amount is negative. Adds `is_discretionary()`. |
| `IncomeTransaction` | `Transaction` | Money coming in. Signed amount is positive. Adds `is_earned()` and `get_source_type()`. |
| `Account` | - | Base class for a group of transactions by payment mode. |
| `CashAccount` | `Account` | Cash payments. Not reconcilable. |
| `BankAccount` | `Account` | Card, UPI, and Bank Transfer payments. Reconcilable. |
| `UnknownAccount` | `Account` | Rows with no payment mode. Not reconcilable. |
| `Budget` | - | A category's monthly limit and its over/under comparison. |

`Transaction.get_transaction_type()`, `Transaction.get_signed_amount()`, `Account.is_reconcilable()`, and `Account.describe()` raise `NotImplementedError`; the subclasses provide them.

## Encapsulation

Attributes are private (for example `__amount`, `__kind`, `__transactions`) and read through `get_` methods. `set_amount()` rejects negative, missing, and non-numeric values. `Account.get_transactions()` returns a copy, so the stored list cannot be changed from outside. `Budget` rejects an empty category and negative limits.

## Usage

```python
from budgetwise.models import ExpenseTransaction, Budget

t = ExpenseTransaction("T4999", "U018", "2023-07-14", "Food", 5891.0)
t.get_signed_amount()   # -5891.0
t.get_month()           # ('2023', '07')
t.is_discretionary()    # True
t.set_amount(-5)        # ValueError

Budget("Food", 67000).status(52014)   # ('under', -14986.0)
```

`Budget.status()` returns `over`, `under`, or `exact` with the difference (actual minus limit).

## Files

| Path | Contents |
|---|---|
| `implementation/transaction.py` | `Transaction`, `ExpenseTransaction`, `IncomeTransaction`, category groups |
| `implementation/account.py` | `Account`, `CashAccount`, `BankAccount`, `UnknownAccount` |
| `implementation/budget.py` | `Budget` |
| `testing/` | Unit tests for each module |
