# Payment Mode Cleaning

Cleans raw payment-mode values and maps each one to a single standard name.

## Responsibility

| Item | Details |
|---|---|
| Responsible | Henrietta |
| Domain reviewer | Sarah |
| PR approval | Zeyad or Patrick |
| Tasks | `P1` payment-mode profiling (Bahareh) and `P2.5` implementation |
| Status | Implemented and under review |

## Purpose

The raw dataset's `payment_mode` column has 20 distinct values. They vary in:

- capitalization: `upi`, `UPi`, `CARD`
- abbreviations: `Crd`, `Csh`
- spacing and separators: `BankTransfer`, `Bank_Transfer`
- spelling: `Bank Transfr`
- missing values: blank

Values can also carry extra spaces, such as `" Card "`.

This module maps every variant to one standard name and returns a reason code whenever the value was changed or could not be identified.

Standard names: `UPI`, `Card`, `Cash`, `Bank Transfer`, plus `Unknown` for anything missing or unrecognized.

## Public Function

```python
from budgetwise.cleaning.payment_modes import normalize_payment_mode

normalize_payment_mode(raw: str | None) -> tuple[str, str | None]
```

### Returns

A tuple `(normalized_payment_mode, reason_code)`:

| Situation | Returns |
|---|---|
| Value is already the standard name (`"Card"`) | `("Card", None)` |
| Value was changed: case, abbreviation, spelling, separator, or extra spaces | `("Card", "PAYMENT_MODE_NORMALIZED")` |
| Value is `None`, `""`, or whitespace only | `("Unknown", "PAYMENT_MODE_UNKNOWN")` |
| Value is not recognized | `("Unknown", "PAYMENT_MODE_UNKNOWN")` |

The function always returns a usable name and never causes a row to be dropped.

### How it works

1. `None`, `""`, or whitespace only returns `Unknown`.
2. The value is stripped of surrounding spaces and lowercased for lookup.
3. Recognized values return the standard name. If the original value differs from the standard name in any way, including extra spaces, the reason is `PAYMENT_MODE_NORMALIZED`.
4. Anything else returns `Unknown` with `PAYMENT_MODE_UNKNOWN`, so it shows up in the error log instead of passing through silently.

## Mapping

Unrecognized values are never passed through unchanged: anything the mapping
does not know becomes `Unknown`, so no raw string reaches analysis.

Re-measured 2026-10-17 for decision `D01` on
`data/raw/budgetwise_synthetic_dirty.csv`, before the pipeline removes
duplicates:

| Standard name | Raw variants present | Rows | finance (old) |
|---|---|---:|---:|
| UPI | `UPI` | 3,736 | 3,660 |
| Card | `Card`, `Crd` | 3,727 | 3,854 |
| Cash | `Cash`, `Csh` | 3,791 | 3,799 |
| Bank Transfer | `Bank Transfer`, `Bank Transfr`, `BankTransfer` | 3,840 | 3,779 |
| Unknown — blank | blank | 503 | 808 |
| Unknown — **unrecognized**, 54 variants | `CCash`, `Caard`, `aCrd`, `Cadr`, `UIP`, `PI`, `Csah`, `Bank Trasnfer`, `aBnk Transfer`, … | **239** | 0 |
| **Total** | 63 distinct values | **15,836** | **15,900** |

**The mapping is not closed against this dataset.** It covers 9 of the 63
distinct values. The other 54 are character scrambles over 239 rows, and they
all land in `Unknown` alongside the 503 genuinely blank values.

That matters for the report in one specific way: `Unknown` no longer means
"the row had no payment mode". It now means "blank **or** unreadable", and the
two are 503 and 239 rows respectively. Where the distinction matters, cite
them separately rather than quoting a single `Unknown` figure.

The pipeline's `payment_mode_normalized` count drops to 12 as a result,
against 10,944 on the earlier dataset: almost nothing in this file matches a
known variant that needs rewriting, because the dirt is scrambling rather than
capitalization.

### Reference

The 20-variant list the mapping implements comes from the Phase 1
payment-mode profiling of `budgetwise_finance_dataset.csv` in Bahareh's
Phase 1 report: **[insert report title / file path]**. The table above is a
fresh measurement against the D01 dataset and is not from that report.

## Reason Codes

| Reason code | Meaning |
|---|---|
| `PAYMENT_MODE_NORMALIZED` | A recognized payment mode was changed to its standard name (capitalization, abbreviation, spelling, missing space, underscore, or surrounding spaces) |
| `PAYMENT_MODE_UNKNOWN` | The payment mode was missing, blank, or not recognized; set to `Unknown` |
| `None` | The value was already the standard name; nothing to log |

The cleaning pipeline (`budgetwise/pipeline/implementation/runner.py`) writes these codes to `output/logs/errors.log` in lowercase (`payment_mode_normalized`, `payment_mode_unknown`).
|

## Testing

Tests are in `testing/test_parser.py`:

- `test_all_profiled_payment_mode_variants`: all 20 profiled values, checked with `subTest` and an assertion that exactly 20 cases are listed
- `test_card_with_spaces` and `test_bank_transfer_with_spaces`: surrounding spaces → `PAYMENT_MODE_NORMALIZED`
- `test_missing_spaces`: whitespace only → `Unknown`
- `test_missing_none`: `None` → `Unknown`
- `test_unknown_payment_mode`: unrecognized value → `Unknown`

Run from the project root:

```bash
python -m unittest budgetwise.cleaning.payment_modes.testing.test_parser -v
```

Expected result: 6 tests (covering the 20 profiled cases plus 5 edge cases), all passing.

