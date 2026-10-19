# Shared definitions

**Status: complete.** Task `P0.1` · Related: [`decisions.md`](decisions.md),
[`interfaces.md`](interfaces.md)

One agreed meaning for each term, so every module and the report describe the
same thing the same way. The counts are defined in full in decision D08.

## Rows and records

| Term | Meaning |
|---|---|
| Raw row | One line of the CSV as read: a dictionary of the nine column names to text, before any cleaning |
| Cleaned record | A dictionary of cleaned values for one valid row, plus `line_number`, `original_currency` and `notes_quality` |
| Valid row | A row that could be cleaned. It becomes one cleaned record |
| Skipped row | A row that cannot be used: malformed, missing an ID, user or type, or with a blank, unreadable or too-large amount. Logged and left out |
| Corrected row | A valid row where at least one value was changed to its standard form. Counted once |
| Flagged row | A valid row kept with a concern and the value left alone. Counted once. A row can be both corrected and flagged |
| Missing value | A field that is blank or absent |

## Duplicates

| Term | Meaning |
|---|---|
| Duplicate transaction | A raw row identical in all nine fields to an earlier raw row, compared before cleaning. The first copy is kept; later copies are removed and logged |
| Repeated transaction ID | The same `transaction_id` on rows that otherwise differ. Not a duplicate: every row is kept and flagged |

## Dates

| Term | Meaning |
|---|---|
| Missing date | A blank date. The row is kept with `date = None`, logged, and left out of monthly figures |
| Invalid date | A date that matches no supported format, or matches one but does not exist (for example 31 February). Treated like a missing date |
| Standard format | `YYYY-MM-DD`. Slash dates are read month first; hyphen dates day first |

## Categories

| Term | Meaning |
|---|---|
| Raw category | The category text as it appears in the CSV |
| Normalized category | One of the 14 standard names in decision D04 |
| Category mapping | `config/category_mapping.csv`: each raw spelling and its standard name |
| Uncategorized | The category given to a blank or unrecognized raw category. Logged, never dropped |

## Amounts

| Term | Meaning |
|---|---|
| Currency label | `₹`, `$`, `Rs.` or `INR`. Removed, recorded in `original_currency`, never converted |
| Sentinel amount | `999999999`, or any amount of 100,000,000 or more. The row is skipped and logged |
| Unrecognized amount | Text that cannot be read as a number. The row is skipped and logged |

## Objects

| Term | Meaning |
|---|---|
| Transaction object | An `ExpenseTransaction` or `IncomeTransaction` built from one cleaned record |
| Expense transaction | A record whose `transaction_type` is Expense. Its signed amount is negative |
| Income transaction | A record whose `transaction_type` is Income. Its signed amount is positive |
| Account group | `CashAccount`, `BankAccount` or `UnknownAccount`: transactions grouped by payment mode, not real bank accounts |

## Analysis

| Term | Meaning |
|---|---|
| Date-based analysis | Monthly figures. Uses only records with a usable date |
| Category-based analysis | Totals by category. Includes undated records |

## Datasets and logging

| Term | Meaning |
|---|---|
| Raw dataset | `data/raw/budgetwise_synthetic_dirty.csv`, the official dataset (D01) |
| Cleaned dataset | `output/cleaned/cleaned_<dataset>_<date>.csv` |
| Error log entry | One line in `output/logs/errors.log`: row number, field, reason code and the raw value |
