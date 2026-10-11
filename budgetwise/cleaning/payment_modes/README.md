# cleaning/payment_modes

Maps raw payment-mode strings onto a fixed set of names.

## 1. What this folder does

Raw payment modes vary in case, spelling, abbreviations, and spacing
(`upi`, `UPI`, `Crd`, `Csh`, `BankTransfer`, `Bank_Transfer`, `Bank Transfr`, ` cash `).

This module maps each one to a canonical name and returns a reason code whenever
it changed the value.

Canonical names: `UPI`, `Card`, `Cash`, `Bank Transfer`, plus `Unknown` for
anything missing or unrecognized.

Examples of the updated mappings:


Crd / CRD              -> Card
Csh / csh              -> Cash
BankTransfer           -> Bank Transfer
Bank_Transfer          -> Bank Transfer
Bank Transfr           -> Bank Transfer

## Reason codes
PAYMENT_MODE_NORMALIZED
Used when a recognized payment mode is changed to its approved form.
This includes:
- capitalization changes
- abbreviations
- spelling corrections
- missing spaces
- underscores
- leading or trailing spaces

## Testing
Run the payment-mode tests with:
## Bash
python -m unittest budgetwise.cleaning.payment_modes.testing.test_parser
