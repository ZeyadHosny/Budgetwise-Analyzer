# Pipeline evidence

`clean_file()` run on all 15,900 rows of `budgetwise_finance_dataset.csv`.

| Count | Value |
|---|---|
| Input rows | 15,900 |
| Exact duplicate raw rows removed | 900 |
| Skipped rows | 349 |
| of which blank amount | 271 |
| of which sentinel amount (100,000,000 or more) | 78 |
| Valid rows | 14,651 |
| Input = valid + skipped + duplicates | True |
| Valid rows kept with no date | 454 |
| Transaction IDs shared by different rows (all kept) | 888 |
| Total income | 144,624,974 |
| Total expenses | 165,749,066 |

The valid count and both totals match the figures in the architecture file.

## Order of the steps

1. `load_rows()` reads every raw row with its line number.
2. `is_duplicate()` is checked on the untouched raw row, before any cleaning
   (Project-1.pdf section 4.5).
3. `has_required_fields()` skips rows that cannot be used.
4. `parse_amount()`: a row with no usable amount is skipped.
5. The other columns are cleaned. A missing date does not remove the row.
6. `Transaction.create()` builds the object (needs `budgetwise.models`).
7. The menu's date-range and category filters are applied.

## Known issues found while integrating

- The payment-mode mapping sends 5,271 rows to "Unknown" (`Crd`, `CRD`, `Csh`,
  `csh`, `BankTransfer`, `Bank_Transfer`, `Bank Transfr`).
- `ErrorLog` opens `errors.log` in append mode, so the file grows on every load.
- `parse_amount` returns no reason when it strips a currency label or a minus
  sign, so the pipeline logs those two cases itself.
- 15 pipeline tests are skipped until `budgetwise.models` has its classes.
