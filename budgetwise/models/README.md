# models

The object model — transaction classes and the budget class.

| | |
|---|---|
| **Responsible** | Zeyad |
| **Domain reviewer** | Patrick (`P2.5`) |
| **PR approval** | Zeyad or Patrick — see `CONTRIBUTING.md` |
| **Tasks** | `P2.5` |
| **Status** | Not started |

## 1. What this folder does

The classes every other module passes around. This folder is where §4.3 is
satisfied, and §4.3 is graded directly: inheritance, encapsulation, and a Budget
class are all named requirements.

**The data does not support an Account hierarchy.** The nine columns include
`user_id` and `payment_mode` but nothing describing an account type. The
assignment marks the `Account` hierarchy as *suggested, not required*, and warns
against "artificial subclasses solely to satisfy the requirement". Design classes
the data actually supports and record the reasoning — that decision belongs to
`G1`.

## 2. How other modules use it

```python
from budgetwise.models import Transaction, ExpenseTransaction, Budget

t = ExpenseTransaction(
    transaction_id="T4999", user_id="U018",
    date="2023-07-14", category="Food", amount=5891.0,
)
t.signed_amount        # -5891.0 — direction from the subclass, not the sign
t.month                # ("2023", "07") — the tuple key analysis groups by
```

Every module uses these. They depend on nothing else in the package.

## 3. What it produces

| Expression | Returns | Why |
|---|---|---|
| `ExpenseTransaction(...).signed_amount` | `-5891.0` | Direction comes from `transaction_type`, never the raw sign (§4.5) |
| `IncomeTransaction(...).signed_amount` | `+5891.0` | Same rule, opposite sign |
| `t.month` | `("2023", "07")` | The tuple key §4.2 requires |
| `t.amount = -5` | `ValueError` | Amount is stored as an unsigned magnitude |
| `Budget("Food", 8000).status(9500)` | `("over", 1500.0)` | §4.4 over/under indicator |

## 4. Requirements and tasks covered

| Requirement | Source | Task |
|---|---|---|
| At least one clear example of inheritance, meaningful "is-a" | §4.3 | `P2.5` |
| Encapsulation — private/protected attributes with controlled access | §4.3 | `P2.5` |
| A `Budget` class comparing spending to limits and flagging overages | §4.3 | `P2.5` |
| Store transactions as a list of objects | §4.2 | `P2.5` |
| Use tuples for fixed keys such as `(year, month)` | §4.2 | `P2.5` |
| Direction from `transaction_type`, not the sign of the amount | §4.5 | `P2.5` |
| Justify the class design in the report | §4.3 | `P4.4` |

## 5. Folders

| Folder | Contents |
|---|---|
| `implementation/` | `transaction.py`, `budget.py` |
| `testing/` | `test_transaction.py`, `test_budget.py` |
| `supplementary/` | `class_diagram.md`, `design_justification.md` |

## 6. Done when

- [ ] One base class with at least one subclass, a real "is-a" relationship
- [ ] At least one protected or private attribute with a property controlling access
- [ ] A test proves the attribute cannot be set to an invalid value
- [ ] `Budget` returns over/under plus the difference
- [ ] `class_diagram.md` and `design_justification.md` written — both are report material
