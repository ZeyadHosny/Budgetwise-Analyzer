# cleaning/rows

Finds exact duplicate rows, checks each row is usable, and counts repeated
transaction IDs.

| | |
|---|---|
| **Responsible** | Sarah |
| **Domain reviewer** | Patrick |
| **Task** | `P2.4`. Profiling from Bahareh's Phase 1 report (`P1.1`) |

## Folder contents

| Folder | File | Holds |
|---|---|---|
| `implementation/` | `raw_rows.py` | duplicate, validation and repeated-ID functions |
| `testing/` | `test_raw_rows.py` | 47 tests |
| `supplementary/` | `row_evidence.md` | counts, timing and evidence for the report |

## Rules

Works on whole raw rows, before any column is cleaned (section 4.5).

- **Duplicates:** a row identical in all nine raw values to an earlier row.
  The first copy is kept, later copies are removed.
- **Required fields:** a row needs nine fields and a usable `transaction_id`,
  `user_id` and `transaction_type`. Otherwise it is skipped.
- **Repeated IDs:** a repeated `transaction_id` on rows that differ is not a
  duplicate. Those rows are kept and flagged, never removed.

Blank date, category, amount, payment mode, location or notes are not row
problems. Each has its own cleaner.

## Implementation

```python
from budgetwise.cleaning.rows import is_duplicate, validate_raw_row

seen_keys = set()                          # one set per load
for line, raw_row in rows:
    if is_duplicate(raw_row, seen_keys):   # on the raw row, before cleaning
        continue
    usable, problems = validate_raw_row(raw_row)
```

| Function | Returns |
|---|---|
| `raw_duplicate_key(row)` | tuple of the nine raw values, plus any extra values |
| `is_duplicate(row, seen_keys)` | `True` if the exact row is already in the set; adds new keys |
| `split_exact_duplicates(numbered_rows)` | `(unique_rows, duplicate_rows)` |
| `validate_raw_row(row)` | `(usable, problems)`; `problems` is a list of `(column, detail)` |
| `has_required_fields(row)` | `True` or `False` |
| `find_repeated_ids(numbered_rows)` | `{transaction_id: row count}` for IDs on two or more rows |
| `EXPECTED_COLUMNS` | the nine column names, in file order |

A row is a dictionary of column name to raw text. `numbered_rows` is a list of
`(line_number, row)` pairs, as the loader produces.

How it works:

- **Duplicates:** each row becomes a tuple of its raw values, unchanged, and is
  checked against a set. A set lookup takes constant time, so the file is
  checked in one pass.
- **Validation:** checks for exactly nine fields, IDs matching `T` + 4 or 5
  digits and `U` + 3 digits, and a type of Expense or Income.
- **Repeated IDs:** counted with `collections.Counter`. Rows with no ID are
  ignored; IDs are trimmed before comparing.

| Situation | Result |
|---|---|
| Identical to an earlier row | duplicate: removed |
| Same ID, any other field differs | kept and flagged |
| Missing ID, user ID or type, or type not Expense/Income | skipped |
| Unusual ID such as `X99` | kept and flagged |
| Fewer or more than nine fields | skipped |

**Faulty input.** `validate_raw_row` wraps its checks in `try/except Exception`,
so anything unexpected is reported as unusable instead of crashing.
`raw_duplicate_key` and `find_repeated_ids` catch `AttributeError` for input
that is not a dictionary.

Only `pipeline/` calls this. Reason codes come from `budgetwise.errorlog.Reason`.

## Testing

| Group | Checks |
|---|---|
| `TransactionIdTests`, `UserIdTests`, `TransactionTypeTests` | valid values kept; missing values make the row unusable; unusual formats kept and reported |
| `DuplicateKeyTests`, `IsDuplicateTests`, `ExactDuplicateTests` | only fully identical raw rows are duplicates; `Food` and `food` differ |
| `HasRequiredFieldsTests`, `ValidateRawRowTests` | wrong field counts, missing values and non-rows handled without crashing |
| `RepeatedIdTests` | repeated IDs counted; rows with no ID never counted |
| `FullDatasetTests` | on all 15,900 rows: 900 duplicates, 0 malformed, 1,680 repeated IDs |

```bash
python3 -m unittest budgetwise.cleaning.rows.testing.test_raw_rows -v
```

Run from the repository root. The 7 full-dataset tests are skipped if
`data/raw/budgetwise_finance_dataset.csv` is missing.

## Supplementary

`row_evidence.md` holds the run details, duplicate and malformed-row counts,
repeated-ID counts at each stage and timing.

| Stage | Rows | Repeated IDs | Rows carrying them |
|---|---|---|---|
| Raw file | 15,900 | 1,680 | 3,580 |
| After 900 duplicates removed | 15,000 | 926 | 1,926 |
| Final cleaned records | 14,651 | 888 | 1,846 |
