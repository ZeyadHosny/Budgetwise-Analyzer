# Pipeline evidence

Results after integrating with Zeyad's model classes (#16) and Henrietta's
payment-mode fix (#19), and applying Bahareh's follow-up review of
October 11, 2026.

## How these figures were produced

- Command: `python3 -m unittest budgetwise.pipeline.testing.test_runner -v`
- Dataset: `data/raw/budgetwise_finance_dataset.csv`, 15,900 data rows
- Produced in a test copy of the repository built from the files on `main` on
  2026-10-12: the model classes (#16), the category, payment-mode and
  location cleaners (#18, #19, #20), `config/category_mapping.csv`, the error
  log, the loader and the amount parser. All 173 tests in the project passed
  there (`python3 -m unittest discover`: OK, 4 expected failures).
- Re-run on the real repository: `main` at commit `78c9233`, 2026-10-16,
  Python 3.14.7. `python3 -m unittest discover` ran 442 tests; every pipeline
  test passed apart from the 4 expected failures. The figures below are
  unchanged.

## Cleaning counts (the same for every menu filter)

| Count | Value |
|---|---|
| Input rows | 15,900 |
| Exact duplicate raw rows removed | 900 |
| Skipped rows | 349 |
| of which blank amount | 271 |
| of which sentinel amount (100,000,000 or more) | 78 |
| Valid rows (cleaned records) | 14,651 |
| Input = valid + skipped + duplicates | 15,900 = 14,651 + 349 + 900 |
| Valid rows with a value corrected | 14,587 |
| Valid rows flagged with a concern | 6,768 |
| Valid rows whose category text changed | 10,955 |
| Valid rows kept with no date | 454 |
| Total income | 144,624,974 |
| Total expenses | 165,749,066 |

A row is counted at most once as corrected and at most once as flagged,
however many reasons it carries. A row can be both.

## Repeated transaction IDs: distinct IDs versus affected rows

| Population | Distinct repeated IDs |
|---|---|
| Raw file (15,900 rows) | 1,680 |
| After exact duplicates are removed (15,000 rows) | 926 |
| Final cleaned records (14,651 rows) | 888 |

The 888 IDs sit on 1,846 rows. All 1,846 rows are kept, and each one has a
`repeated_transaction_id` entry in the log, so 1,846 is a count of log
events, not of IDs.

## Objects and accounts (run() only)

| Count | Value |
|---|---|
| Objects built | 14,651 |
| of which `ExpenseTransaction` | 12,454 |
| of which `IncomeTransaction` | 2,197 |
| Objects the classes refused | 0 |
| In the `CashAccount` | 3,502 |
| In the `BankAccount` | 10,425 |
| In the `UnknownAccount` (blank payment mode) | 724 |
| Total across the three accounts | 14,651 |

Every object is in the list and in exactly one account. The sum of
`get_signed_amount()` over all objects is -21,124,092, which equals total
income minus total expenses.

## Payment mode "Unknown"

With Henrietta's fix (#19) the seven misspellings now map to Cash, Card or
Bank Transfer. Only blank payment modes remain `Unknown`.

| Population | Unknown before #19 | Unknown after #19 (blank only) |
|---|---|---|
| Raw file (15,900 rows) | 6,079 | 808 |
| After exact duplicates are removed | 5,731 | 748 |
| Final cleaned records | 5,586 | 724 |

## Reasons logged on the full dataset

| Reason | Events | Action |
|---|---|---|
| duplicate_row | 900 | skipped |
| missing_amount | 271 | skipped |
| sentinel_amount | 78 | skipped |
| date_normalized | 8,605 | corrected |
| category_normalized | 10,689 | corrected |
| category_uncategorized | 266 | corrected |
| payment_mode_normalized | 10,944 | corrected |
| payment_mode_unknown | 724 | corrected |
| location_normalized | 10,182 | corrected |
| location_unknown | 1,158 | corrected |
| currency_label_stripped | 2,981 | corrected |
| negative_amount_magnitude | 147 | corrected |
| missing_date | 454 | flagged |
| notes_missing | 2,590 | flagged |
| notes_low_information | 2,765 | flagged |
| repeated_transaction_id | 1,846 | flagged |

`currency_label_stripped` counts only rows that carried `₹`, `$`, `Rs.` or
`INR`. A plain amount is never logged as stripped: the merged amount parser
returns no symbol for it, and the pipeline also ignores a `"plain"` label if a
later parser returns one.

## Log entries from the run above

Captured from the test-copy run.

```
line=275 field=row reason=duplicate_row raw='T2217'
line=168 field=amount reason=missing_amount raw=''
line=12 field=amount reason=sentinel_amount raw='999999999'
line=3 field=date reason=date_normalized raw='08/05/2022'
line=8 field=amount reason=currency_label_stripped raw='Rs.828'
line=2 field=payment_mode reason=payment_mode_normalized raw='card'
line=3 field=payment_mode reason=payment_mode_unknown raw=''
line=5 field=date reason=missing_date raw=''
line=16 field=transaction_id reason=repeated_transaction_id raw='T11564'
```

## Order of the steps

1. `load_rows()` reads every raw row with its line number.
2. `is_duplicate()` is checked on the untouched raw row, before any cleaning
   (Project-1.pdf section 4.5).
3. `validate_raw_row()` returns `(usable, problems)`. Every problem is logged
   against its own column. Unusable rows are skipped. Usable rows with an
   unusual ID are kept and flagged.
4. `parse_amount()`: a row with no usable amount is skipped.
5. The other columns are cleaned. A missing date does not remove the row.
6. `find_repeated_ids()` flags repeated IDs. The rows are kept.
7. An `ExpenseTransaction` or `IncomeTransaction` is built, chosen by
   `transaction_type`. `Transaction` has no factory.
8. The menu's date-range and category filters are applied.
9. Each returned object is added with `add_transaction()` to the
   `CashAccount`, `BankAccount` or `UnknownAccount`.

## Test results

| Suite | Tests | Result |
|---|---|---|
| Dates | 24 | all pass |
| Rows | 47 | all pass |
| Notes | 12 | all pass |
| Pipeline | 90 | 86 pass, 4 expected failures |

The 4 expected failures are checks on Patrick's code (review items S05 and
S09). They run and fail on purpose while those defects exist, so they are
reported rather than skipped, and they pass once the fixes are merged. No
pipeline test is skipped when the dataset is present.

## Open items owned by others

- Loader pads short rows with blanks and drops surplus fields; header check
  accepts a repeated column name (S05, Patrick).
- `parse_amount` removes every minus sign, so `1-2` becomes 12 (S09, Patrick).
- Whether an object-build failure should count as flagged (D08). It does now.
- `ErrorLog` appends, so `errors.log` holds every load (S12, Patrick).
