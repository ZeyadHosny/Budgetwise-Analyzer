# pipeline

Runs every cleaner in the required order, builds the transaction objects and
accounts, and returns the counts the report needs. It cleans nothing itself.

| | |
|---|---|
| **Responsible** | Sarah |
| **Domain reviewer** | Patrick. Model integration with Zeyad |
| **Task** | `P2.10` |

## Folder contents

| Folder | File | Holds |
|---|---|---|
| `implementation/` | `runner.py` | `clean_file()` and `run()` |
| `testing/` | `test_runner.py` | 90 tests |
| `supplementary/` | `pipeline_evidence.md` | full-dataset counts, log samples and run details for the report |

## Rules

- Duplicates are found on the raw rows, before any cleaning (section 4.5).
- Only two things remove a row: it cannot be used (duplicate, or a missing
  ID, user ID or type), or it has no usable amount. Everything else is
  cleaned or flagged and the row is kept.
- A row with no date is kept, left out of date filters, and still counted by
  category (section 4.5).
- Direction comes from `transaction_type`, never from the amount's sign.
- One bad row is logged and skipped. It never stops the run (section 4.1).

## Implementation

```python
from budgetwise.pipeline import clean_file, run

result = run("data/raw/budgetwise_finance_dataset.csv")
run(path, start="2023-01-01", end="2023-12-31")    # date range, inclusive
run(path, category="Food")                         # one category
```

| Function | Does | Used by |
|---|---|---|
| `run(path, start, end, category, error_log)` | cleans, then builds objects, applies filters, fills accounts | the menu |
| `clean_file(path, error_log)` | cleaning only; needs no model classes | tests, metrics |

Both return a dictionary (`result["counts"]`, not `result.counts`):

| Key | Holds |
|---|---|
| `records` | one dictionary per valid row, unfiltered |
| `counts` | the figures below |
| `timings` | `{"load": seconds, "clean": seconds}` |
| `issues` | `(line_number, field, reason, raw_value)` for every logged issue |
| `error` | `None`, or a message if the file could not be read |
| `transactions` | `run` only: objects that pass the filters |
| `accounts` | `run` only: `{"cash", "bank", "unknown"}` holding the same objects |

If no `error_log` is given, one is opened on `output/logs/errors.log` and
closed at the end.

**Steps**

| Step | Function | From | Result |
|---|---|---|---|
| 1 | `load_rows()` | loader | numbered raw rows |
| 2 | `is_duplicate()` | rows | exact duplicate: removed |
| 3 | `validate_raw_row()` | rows | unusable: skipped; unusual ID: flagged |
| 4 | `parse_amount()` | amounts | no usable amount (blank, unreadable, 100,000,000 or more): skipped |
| 5 | `parse_date()`, `normalize_category()`, `normalize_payment_mode()`, `normalize_location()`, `classify_note_quality()` | dates, categories, payment modes, locations, notes | cleaned or flagged; row kept |
| 6 | `find_repeated_ids()` | rows | repeated IDs flagged; rows kept |
| 7 | `ExpenseTransaction` / `IncomeTransaction` | models | one object per row, chosen by type |
| 8 | date and category filters | | from the menu |
| 9 | `add_transaction()` | models | Cash to `CashAccount`; Card, UPI, Bank Transfer to `BankAccount`; Unknown to `UnknownAccount` |

**Model classes.** `Transaction` and `Account` are parents and never built
directly. Each row becomes an `ExpenseTransaction` or `IncomeTransaction`, and
the same object goes into the list and into one account through
`add_transaction()`, which all three accounts inherit. All attributes are
private and read through getters such as `get_amount()`. `Budget` is not used
here; it belongs to the budget analysis.

**Counts**

| Count | Meaning | Full dataset |
|---|---|---|
| `input` | rows read | 15,900 |
| `duplicates` | exact duplicates removed | 900 |
| `skipped` | rows that could not be cleaned | 349 |
| `valid` | rows cleaned | 14,651 |
| `corrected` | valid rows with a value standardised | 14,587 |
| `flagged` | valid rows kept with a concern | 6,768 |
| `categories_normalized` | valid rows whose category changed | 10,955 |
| `repeated_ids` | distinct IDs on two or more valid rows | 888 |
| `objects_built` / `objects_failed` | records turned into objects / refused | 14,651 / 0 |
| `returned` | objects left after filters | 14,651 with no filter |

`input = valid + skipped + duplicates` always holds. A row counts at most once
as corrected and once as flagged, and can be both. Filters change only
`returned`, `transactions` and `accounts`.

**Faulty input**

| Problem | Handling |
|---|---|
| File cannot be loaded | `try/except`: `error` set, `file_not_loaded` logged, no crash |
| Any error on one row | `try/except` per row: logged as `malformed_row`, row skipped, run continues |
| A class refuses a value | `try/except`: logged as `transaction_not_built`, counted in `objects_failed` |
| Model classes missing | `try/except ImportError`: cleaning still works, `error` explains |
| Log left open | `finally` closes any log the pipeline opened |

Reason codes come from `budgetwise.errorlog.Reason`.

## Testing

| Group | Checks |
|---|---|
| `CleaningTests`, `OrderTests` | counts, cleaned values, section 4.5 rules, duplicates judged on raw rows |
| `BadInputTests`, `FailureBoundaryTests` | missing files, bad values and unexpected errors never stop the run |
| `ObjectTests`, `NoFactoryTests`, `ClassUseTests`, `AccountTests` | the right subclass is built and placed in the right account |
| `FilterTests` | date range and category filters; cleaning counts unchanged |
| `RowValidationTests`, `FlaggedCountTests`, `ObjectFailureTests` | review items S04, S06, S07 |
| `AmountBoundaryTests`, `LoaderStructureTests` | teammates' open defects (S05, S09) |
| `FullDatasetTests` | the counts above on all 15,900 rows |

```bash
python3 -m unittest budgetwise.pipeline.testing.test_runner -v
```

Run from the repository root. Expected: `Ran 90 tests`, `OK (expected failures=4)`.
The 4 expected failures check Patrick's loader and amount parser (S05, S09);
they pass once those fixes are merged. The full-dataset tests are skipped if
`data/raw/budgetwise_finance_dataset.csv` is missing.

## Supplementary

`pipeline_evidence.md` holds the run details, cleaning and object counts,
repeated-ID counts at each stage, payment-mode figures, every reason logged on
the full dataset with its count, and sample lines from `errors.log`.

Totals on the full dataset: income 144,624,974, expenses 165,749,066,
net -21,124,092. Accounts: cash 3,502, bank 10,425, unknown 724.

## Open points

| Point | Owner |
|---|---|
| Loader pads short rows and drops surplus fields (S05) | Patrick |
| `parse_amount` removes every minus sign, so `1-2` becomes 12 (S09) | Patrick |
