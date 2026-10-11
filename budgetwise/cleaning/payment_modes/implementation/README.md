# cleaning/payment_modes/implementation

Henrietta · `P2.5` · domain reviewer Sarah

## What this does

`parser.py` provides one public function:

```python
normalize_payment_mode(raw: str | None) -> tuple[str, str | None]
```

| Situation | Returns |
|---|---|
| Already the standard name | `("Card", None)` |
| Changed: case, abbreviation, spelling, separator, or extra spaces | `("Card", "PAYMENT_MODE_NORMALIZED")` |
| Missing: `None`, `""`, or whitespace only | `("Unknown", "PAYMENT_MODE_UNKNOWN")` |
| Unknown: not in the mapping | `("Unknown", "PAYMENT_MODE_UNKNOWN")` |

It always returns a usable name and never drops a row.

## Mapping

The mapping is a dictionary inside `parser.py`. Keys are lowercase:

| Lookup key | Standard name |
|---|---|
| `upi` | UPI |
| `card`, `crd` | Card |
| `cash`, `csh` | Cash |
| `bank transfer`, `banktransfer`, `bank_transfer`, `bank transfr` | Bank Transfer |

Because lookups ignore case, these 9 keys cover all 19 nonblank variants in the data.

## How it works

1. `None`, `""`, or whitespace only → `Unknown` + `PAYMENT_MODE_UNKNOWN`.
2. Strip spaces and lowercase the value, then look it up.
3. Found → return the standard name. If the raw value differs from it in any way, including extra spaces, also return `PAYMENT_MODE_NORMALIZED`. If it is identical, the reason is `None`.
4. Not found → `Unknown` + `PAYMENT_MODE_UNKNOWN`, so the log shows what was missed.

Step 3 compares the **original** value (`raw != normalized`), not the stripped one. That is what makes whitespace-only corrections get logged.

