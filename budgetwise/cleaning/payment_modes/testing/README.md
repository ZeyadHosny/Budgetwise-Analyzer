# cleaning/payment_modes/testing

Henrietta · `P2.5` · domain reviewer Sarah

## What is tested

`test_parser.py` checks `normalize_payment_mode()` against all 20 payment-mode values profiled in the raw dataset, plus edge cases.

| Test | Inputs | Expected result |
|---|---|---|
| `test_all_profiled_payment_mode_variants` | `UPI`, `UPi`, `Upi`, `upi` · `Card`, `CARD`, `card`, `Crd`, `CRD` · `Cash`, `CASH`, `cash`, `Csh`, `csh` · `Bank Transfer`, `bank transfer`, `BankTransfer`, `Bank_Transfer`, `Bank Transfr` · `""` | Standard name, or `Unknown` for `""` |
| `test_card_with_spaces` | `"  Card  "` | `("Card", "PAYMENT_MODE_NORMALIZED")` |
| `test_bank_transfer_with_spaces` | `"  Bank Transfer  "` | `("Bank Transfer", "PAYMENT_MODE_NORMALIZED")` |
| `test_missing_spaces` | `"   "` | `("Unknown", "PAYMENT_MODE_UNKNOWN")` |
| `test_missing_none` | `None` | `("Unknown", "PAYMENT_MODE_UNKNOWN")` |
| `test_unknown_payment_mode` | `"Cheque"` | `("Unknown", "PAYMENT_MODE_UNKNOWN")` |

The first test checks each case with `subTest`. It also asserts that exactly 20 cases are listed, so a missing case makes it fail.


## Run

From the project root:

```bash
python -m unittest budgetwise.cleaning.payment_modes.testing.test_parser -v
```

