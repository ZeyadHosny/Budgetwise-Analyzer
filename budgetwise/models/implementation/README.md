# models/implementation

Zeyad · `P2.5` · domain reviewer Patrick

## Write these

```python
class Transaction:
    _amount        protected — unsigned magnitude
    @property amount        getter
    @amount.setter amount   rejects negatives with ValueError
    @property month         returns (year, month) as a tuple of strings
    @property signed_amount NotImplemented in the base

class ExpenseTransaction(Transaction):   signed_amount → negative
class IncomeTransaction(Transaction):    signed_amount → positive

class Budget:
    __limit        private
    status(actual) → ("over" | "under" | "exact", difference)
```

## Why this shape satisfies §4.3

| Requirement | Satisfied by |
|---|---|
| Meaningful inheritance | Expense and Income genuinely *are* transactions and differ in one real behaviour — direction |
| Encapsulation | `_amount` is protected, reached only through a property that rejects negatives |
| Private attribute | `Budget.__limit` cannot be reassigned after construction |
| Tuple keys | `month` returns `("2023", "07")` for `analysis/aggregation` |

## The Account question

The workbook's `P2.5` says to build an `Account` hierarchy. The data has no
account-type column — only `user_id` and `payment_mode`, whose values are `UPI`,
`Card`, `Cash`, and `Bank Transfer`. Inventing `CheckingAccount` and
`CreditAccount` would be exactly the artificial subclassing §4.3 warns against.

Raise this at `G1`, decide as a team, and record the outcome in
`supplementary/design_justification.md`. Do not decide it alone in code.

## Do not

- Store a signed amount. §4.5 requires an unsigned magnitude with direction taken
  from `transaction_type`.
- Put parsing here — the cleaners hand over values already clean.
- Import pandas or numpy — violates §2.
