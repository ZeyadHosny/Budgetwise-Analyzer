# cleaning/payment_modes

Maps raw payment-mode strings onto a fixed set of names.

## 1. What this folder does

Raw payment modes vary in case and spacing (`upi`, `UPI`, ` cash `). This
module maps each one to a canonical name and returns a reason code whenever
it changed the value.

Canonical names: `UPI`, `Card`, `Cash`, `Bank Transfer`, plus `Unknown` for
anything missing or unrecognized.

## 2. How other modules use it

```python
from budgetwise.cleaning.payment_modes import normalize_payment_mode

mode, reason = normalize_payment_mode("UPI")     # ("UPI", None)
mode, reason = normalize_payment_mode("upi")     # ("UPI", "PAYMENT_MODE_NORMALIZED")
mode, reason = normalize_payment_mode("")        # ("Unknown", "PAYMENT_MODE_UNKNOWN")
```

## 3. What it produces

| Input | Returns | Reason |
|---|---|---|
| `UPI` | `"UPI"` | — |
| `upi` | `"UPI"` | `PAYMENT_MODE_NORMALIZED` |
| `bank transfer` | `"Bank Transfer"` | `PAYMENT_MODE_NORMALIZED` |
| `""` / `None` | `"Unknown"` | `PAYMENT_MODE_UNKNOWN` |
| `Cheque` | `"Unknown"` | `PAYMENT_MODE_UNKNOWN` |

## 4. Folders

| Folder | Contents |
|---|---|
| `implementation/` | `parser.py` |
| `testing/` | `test_parser.py` |
| `supplementary/` | profiling notes |
