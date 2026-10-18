# Payment mode cleaning

## Interface

```python
from budgetwise.cleaning.payment_modes import normalize_payment_mode

normalize_payment_mode(raw: str | None) -> tuple[str, str | None]
```

| Input | Returns |
|---|---|
| Already a standard name, e.g. `"Card"` | `("Card", None)` |
| A known variant, e.g. `"CRD"`, `"Crad"`, `" Card "` | `("Card", "PAYMENT_MODE_NORMALIZED")` |
| `None`, `""`, whitespace only, or not recognized | `("Unknown", "PAYMENT_MODE_UNKNOWN")` |

Standard names: `UPI`, `Card`, `Cash`, `Bank Transfer`. The function always
returns a usable name and never drops a row. The pipeline writes the reason
codes to `output/logs/errors.log` in lowercase.

## Mapping

The mapping is a dictionary in `implementation/parser.py`. Lookups ignore case
and surrounding spaces.

- **Original dataset:** 9 keys cover all 19 nonblank variants (`Crd`, `Csh`,
  `BankTransfer`, `Bank_Transfer`, `Bank Transfr`, case changes).
- **Synthetic dirty dataset:** 54 new misspellings (239 raw rows). 48 of them
  (207 rows), such as `UPPI`, `Csah` and `Bank Trasnfer`, are one letter from
  exactly one standard name and are mapped.

Six values stay `Unknown` because each is one letter from both `Cash` and
`Card`: `Cah`, `Cahs`, `Cas`, `Car`, `Cad`, `Cadr` (32 raw rows).

On the synthetic dirty dataset, 510 retained rows are `Unknown`: 479 blank and
31 ambiguous. Report them separately where the difference matters.

## Files

| Folder | Contents |
|---|---|
| `implementation/` | `parser.py` |
| `testing/` | `test_parser.py` |

## Tests

8 tests cover all 20 profiled values, the new misspellings, the six ambiguous
values, whitespace, missing values and unknown values.

```bash
python -m unittest budgetwise.cleaning.payment_modes.testing.test_parser -v
```
