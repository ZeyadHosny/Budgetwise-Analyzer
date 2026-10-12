# Pipeline evidence

Results after the Phase 2 review corrections (Bahareh, October 10, 2026).

## How these figures were produced

- Command: `python -m unittest budgetwise.pipeline.testing.test_runner -v`
- Dataset: `data/raw/budgetwise_finance_dataset.csv`, 15,900 data rows
- Run in a test copy of the repository with the model classes taken from
  `budgetwise_architecture.py`. **Re-run on the real branch and replace the
  Python version, branch and commit below before submitting.**
- Python version: (fill in from `python --version`)
- Branch and commit: (fill in from `git log -1 --oneline`)

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

## Object counts (run() only)

| Count | Value |
|---|---|
| Objects built | 14,651 |
| Objects the classes refused | 0 |
| In the cash account | 2,105 |
| In the bank account | 6,960 |
| In neither account (payment mode Unknown) | 5,586 |

## Payment mode "Unknown": which population each figure describes

| Population | Unknown | of which blank | of which a known spelling |
|---|---|---|---|
| Raw file (15,900 rows) | 6,079 | 808 | 5,271 |
| After exact duplicates are removed | 5,731 | 748 | 4,983 |
| Final cleaned records | 5,586 | 724 | 4,862 |

The spellings are `Crd`, `CRD`, `Csh`, `csh`, `BankTransfer`, `Bank_Transfer`
and `Bank Transfr`. The earlier figure of 5,271 is the raw-file count.

## Reasons logged on the full dataset

| Reason | Events | Action |
|---|---|---|
| duplicate_row | 900 | skipped |
| missing_amount | 271 | skipped |
| sentinel_amount | 78 | skipped |
| date_normalized | 8,605 | corrected |
| category_normalized | 10,689 | corrected |
| category_uncategorized | 266 | corrected |
| payment_mode_normalized | 6,082 | corrected |
| payment_mode_unknown | 5,586 | corrected |
| location_normalized | 10,182 | corrected |
| location_unknown | 1,158 | corrected |
| currency_label_stripped | 2,981 | corrected |
| negative_amount_magnitude | 147 | corrected |
| missing_date | 454 | flagged |
| notes_missing | 2,590 | flagged |
| notes_low_information | 2,765 | flagged |
| repeated_transaction_id | 1,846 | flagged |

## Representative log entries

```
line=275 field=row reason=duplicate_row raw='T2217'
line=168 field=amount reason=missing_amount raw=''
line=12 field=amount reason=sentinel_amount raw='999999999'
line=3 field=date reason=date_normalized raw='08/05/2022'
line=8 field=amount reason=currency_label_stripped raw='Rs.828'
line=2 field=category reason=category_normalized raw='Educaton'
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
7. `Transaction.create()` builds an `ExpenseTransaction` or `IncomeTransaction`.
8. The menu's date-range and category filters are applied.
9. Each returned object is added to the `CashAccount` or `BankAccount`.

## Test results in the test copy

| Suite | Tests | Result |
|---|---|---|
| Dates | 24 | all pass |
| Rows | 47 | all pass |
| Notes | 12 | all pass |
| Pipeline | 86 | 82 pass, 4 skipped |

The 4 skipped pipeline tests wait for fixes owned by Patrick (review items
S05 and S09) and start running by themselves once those are merged. On a
branch without the model classes, a further 33 pipeline tests are skipped.

## Open items owned by others

- Loader pads short rows with blanks and drops surplus fields; header check
  accepts a repeated column name (S05, Patrick).
- `parse_amount` removes every minus sign, so `1-2` becomes 12 (S09, Patrick).
- Payment-mode spellings above map to "Unknown" (S10, Henrieta).
- Model classes are not yet in `budgetwise/models` (S10, Zeyad).
- Reason-code vocabulary and casing are not yet approved by the team (S08).
  The pipeline keeps every code it creates in one block at the top of
  `runner.py`, so the change is in one place.
- `ErrorLog` appends, so `errors.log` holds every load (S12, Patrick).
