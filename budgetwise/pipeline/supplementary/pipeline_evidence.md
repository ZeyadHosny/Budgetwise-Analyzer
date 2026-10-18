# Pipeline evidence

Results after integrating with Zeyad's model classes (#16) and Henrietta's
payment-mode fix (#19), and applying Bahareh's follow-up review of
October 11, 2026.

## How these figures were produced

- Command: `python3 -m unittest budgetwise.pipeline.testing.test_runner -v`
- Dataset: `data/raw/budgetwise_synthetic_dirty.csv`, 15,836 data rows
  (the D01 dataset; **re-measured 2026-10-17**, Python 3.12.10, Windows 11,
  branch `feature/P3.7-exports`)
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
| Input rows | 15,836 |
| Exact duplicate raw rows removed | 804 |
| Skipped rows | 170 |
| of which blank amount | 170 |
| of which sentinel amount (100,000,000 or more) | 0 - none in this dataset |
| Valid rows (cleaned records) | 14,862 |
| Input = valid + skipped + duplicates | 15,836 = 14,862 + 170 + 804 |
| Valid rows with a value corrected | 11,469 |
| Valid rows flagged with a concern | 5,112 |
| Valid rows whose category text changed | 3,969 |
| Valid rows kept with no date | **2,581** |
| Total income | 134,553,045 |
| Total expenses | 53,348,034 |

Two rows deserve a sentence each in the report.

**Sentinel amounts are zero.** Section 4.5 names `999999999` as its worked
example of an invalid amount. This dataset contains none, so that rule runs and
never fires. It is still implemented and still tested with hand-written input.

**2,581 valid rows have no date, 17% of them.** On the earlier dataset the
figure was 454, or 3%. Only 322 are blank; the other 2,259 carry a date in a
shape `parse_date()` does not implement and are rejected as `invalid_date`.
Those rows are kept and count toward category totals, but every monthly figure
excludes them.

A row is counted at most once as corrected and at most once as flagged,
however many reasons it carries. A row can be both.

## Repeated transaction IDs: distinct IDs versus affected rows

| Population | Distinct repeated IDs |
|---|---:|
| Raw file (15,836 rows) | 959 |
| After exact duplicates are removed (15,032 rows) | 172 |
| Final cleaned records (14,862 rows) | 163 |

The 163 IDs sit on 328 rows. All 328 rows are kept, and each one has a
`repeated_transaction_id` entry in the log, so 328 is a count of log events,
not of IDs.

The drop from 959 to 172 is much steeper than on the earlier dataset, where
1,680 fell to 926: here 787 of the 959 repeat only because of exact
duplicates, and stop repeating once those 804 rows are removed.

## Objects and accounts (run() only)

| Count | Value |
|---|---|
| Objects built | 14,862 |
| of which `ExpenseTransaction` | 12,612 |
| of which `IncomeTransaction` | 2,250 |
| Objects the classes refused | 0 |
| In the `CashAccount` | 3,563 |
| In the `BankAccount` | 10,591 |
| In the `UnknownAccount` (unknown payment mode) | 708 |
| Total across the three accounts | 14,862 |

Every object is in the list and in exactly one account. The sum of
`get_signed_amount()` over all objects is 81,205,011, which equals total income
minus total expenses (134,553,045 - 53,348,034). The sign is positive on this
dataset, where the earlier one gave -21,124,092.

Two income categories in the approved set, `Freelance` and `Investment`, have
no rows here, so `IncomeTransaction.is_passive_income()` never returns True.
See `budgetwise/cleaning/categories/README.md`.

## Payment mode "Unknown"

With Henrietta's fix (#19) the seven misspellings now map to Cash, Card or
Bank Transfer. Only blank payment modes remain `Unknown`.

| Population | Blank | Unrecognized | Total `Unknown` |
|---|---:|---:|---:|
| Raw file (15,836 rows) | 503 | 239 | 742 |
| After exact duplicates are removed (15,032 rows) | 484 | - | - |
| Final cleaned records (14,862 rows) | - | - | 708 |

So `Unknown` no longer means "the row had no payment mode". Quote the two
components separately where the distinction matters. The
`payment_mode_normalized` count falls to 12, from 10,944, because almost
nothing here is a recognised variant needing a rewrite.

## Reasons logged on the full dataset

| Reason | Events | Action |
|---|---|---|
| duplicate_row | 804 | skipped |
| missing_amount | 170 | skipped |
| sentinel_amount | 78 | skipped |
| date_normalized | 8,126 | corrected |
| **invalid_date** | **2,259** | date dropped, row kept |
| category_normalized | 2,275 | corrected |
| category_uncategorized | 154 | corrected |
| **unknown_category** | **1,540** | corrected to `Uncategorized` |
| payment_mode_normalized | 12 | corrected |
| payment_mode_unknown | 708 | corrected |
| location_normalized | 1,251 | corrected |
| location_unknown | 2,134 | corrected |
| currency_label_stripped | 2,628 | corrected |
| negative_amount_magnitude | 60 | corrected |
| missing_date | 322 | flagged |
| notes_missing | 1,435 | flagged |
| notes_low_information | 0 | flagged |
| repeated_transaction_id | 328 | flagged |

`invalid_date` and `unknown_category` are both zero on
`budgetwise_finance_dataset.csv` and are the two reason codes this dataset
introduces. `notes_low_information` is the reverse: 2,765 events there, none
here, because this dataset has no placeholder notes.

`sentinel_amount` is absent from the table because it fires zero times here.

This dataset carries the two symbols the other file shares, but no `Rs.` and
no trailing `INR` at all, so two of the four section 4.5 strip rules never fire
on it.

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
