# models/testing

Zeyad · domain reviewer Patrick

## Required cases

- [ ] `ExpenseTransaction.signed_amount` is negative, `IncomeTransaction` positive
- [ ] Both are instances of `Transaction` — inheritance actually holds
- [ ] Setting `amount` to a negative raises `ValueError`
- [ ] Setting `amount` to a valid number updates it
- [ ] `month` returns a tuple of two strings, not a string or a date
- [ ] `Budget.status` returns `"over"` with the correct difference
- [ ] `Budget.status` returns `"under"` with the correct difference
- [ ] `Budget.status` returns `"exact"` when spending equals the limit
- [ ] The private limit cannot be reassigned from outside

The encapsulation tests are not busywork. §4.3 grades controlled access, and a
test proving the setter rejects bad input is the clearest evidence there is.

## Run

```bash
python -m unittest discover
```

A run collecting 0 tests is not a pass.
