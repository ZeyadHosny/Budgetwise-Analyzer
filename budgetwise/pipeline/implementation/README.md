# pipeline/implementation

Sarah (P2.10) · `G2` · reviewer Patrick · model integration with Zeyad

One file: `runner.py`. It cleans nothing itself. It calls each feature's
function in the required order and joins the results.

## What it provides

Import from `budgetwise.pipeline`, never from this folder.

```python
clean_file(path, error_log=None) -> dict
    Loads the CSV and cleans every row. Needs no model classes.

run(path, start=None, end=None, category=None, error_log=None) -> dict
    Same cleaning, then builds the transaction objects, applies the menu's
    filters and fills the three accounts. This is what the menu calls.
```

`start` and `end` are `'YYYY-MM-DD'` text, both inclusive. `category` is a
category name and is matched after normalizing, so `food` finds `Food`.
`error_log` is an `ErrorLog`. If none is given, one is opened on
`output/logs/errors.log` and closed at the end.

Both functions return a dictionary, not an object. Use `result["counts"]`,
not `result.counts`. There is no `LoadResult` class.

| Key | From | Holds |
|---|---|---|
| `records` | both | list of dictionaries, one per valid row, **unfiltered** |
| `counts` | both | the figures below |
| `timings` | both | `{"load": seconds, "clean": seconds}` |
| `issues` | both | list of `(line_number, field, reason, raw_value)` |
| `error` | both | `None`, or a message if the file could not be read |
| `transactions` | `run` | list of `ExpenseTransaction` / `IncomeTransaction` that pass the filters |
| `accounts` | `run` | `{"cash": CashAccount, "bank": BankAccount, "unknown": UnknownAccount}` holding those same objects |

Each record has these keys: `line_number`, `transaction_id`, `user_id`,
`transaction_type`, `date` (`'YYYY-MM-DD'` or `None`), `category`, `amount`
(unsigned float), `original_currency` (`₹`, `$`, `Rs.`, `INR` or `plain`),
`payment_mode`, `location`, `notes`, `notes_quality`.

## Example

Run from the repository root:

```python
from budgetwise.pipeline import clean_file, run

result = clean_file("data/raw/budgetwise_finance_dataset.csv")
print(result["counts"]["input"], result["counts"]["valid"])    # 15900 14651

result = run("data/raw/budgetwise_finance_dataset.csv", category="Food")
print(len(result["transactions"]))
print(result["accounts"]["cash"].get_transaction_count())
```

## Order is mandatory

```
1. loader.load_rows(path)                 raw row + line number
2. cleaning.rows.is_duplicate             ON THE RAW ROW, first (section 4.5)
3. cleaning.rows.validate_raw_row         skip unusable rows, flag odd ones
4. cleaning.amounts.parse_amount          no usable amount: skip the row
5. cleaning.dates.parse_date              no date: row is KEPT, date is None
   cleaning.categories.normalize_category
   cleaning.payment_modes.normalize_payment_mode
   cleaning.locations.normalize_location
   cleaning.notes.classify_note_quality
6. cleaning.rows.find_repeated_ids        repeated IDs flagged, rows KEPT
7. models.ExpenseTransaction(...)         or IncomeTransaction(...), by transaction_type
8. date-range and category filters
9. account.add_transaction(transaction)   cash, bank or unknown, by payment mode
```

Step 2 cannot move. Section 4.5: *"Duplicate detection must be performed on
the original raw rows before data normalization."* Normalizing first merges
`FOOD` and `Food` and manufactures duplicates that do not exist.

Steps 1 to 6 are `clean_file`. `run` adds steps 7 to 9.

## Counts

Cleaning counts. These are the same whatever filter the menu asks for.

| Key | Meaning |
|---|---|
| `input` | rows read from the file |
| `duplicates` | exact duplicate raw rows removed |
| `skipped` | rows that could not be cleaned |
| `valid` | rows that could. Equals `len(result["records"])` |
| `corrected` | valid rows where a value was changed to its standard form |
| `flagged` | valid rows kept with a concern |
| `categories_normalized` | valid rows whose category text changed |
| `repeated_ids` | distinct IDs shared by two or more valid rows |
| `by_reason` | how many times each reason was logged |

`input = valid + skipped + duplicates` always holds.

A row is counted at most once in `corrected` and at most once in `flagged`,
however many reasons it has. A row can be in both.

Object counts. These describe steps 7 to 9 and are zero from `clean_file`.

| Key | Meaning |
|---|---|
| `objects_built` | cleaned records that became objects |
| `objects_failed` | cleaned records the classes refused |
| `returned` | objects left after the filters |

Once object building has finished, `objects_built + objects_failed = valid`.
This does not hold from `clean_file`, which builds no objects, or when `run`
stops early because the file could not be read or the model classes are
missing. An object failure does not change any cleaning count, but the row
is counted once as flagged, because `transaction_not_built` is logged on it.

## Row status

| Status | What happens | Examples |
|---|---|---|
| skipped | logged, not in `records` | exact duplicate, missing ID, user ID or type, blank or unreadable amount, amount of 100,000,000 or more |
| corrected | kept, value standardized | date reformatted, category or payment mode normalized, currency label or minus sign removed |
| flagged | kept, value left alone | no date, unusual ID format, repeated ID, blank or placeholder note |

A missing field and a blank field are different. A row that lacks one of the
nine fields is malformed. A row whose date, category, payment mode, location
or note is present but empty is valid, and that column's own cleaner decides
what to do.

Raw transaction IDs and cleaned ones are counted separately: 1,680 IDs repeat
in the raw file, 926 once exact duplicates are removed, and 888 among the
final cleaned records. `repeated_ids` is the last of these.

## How the model classes are used

| Class | Use |
|---|---|
| `Transaction` | parent, never built directly. No factory: the pipeline builds the child for `transaction_type` |
| `ExpenseTransaction`, `IncomeTransaction` | one object per cleaned row |
| `Account` | parent, never built directly. Supplies `add_transaction()` |
| `CashAccount`, `BankAccount`, `UnknownAccount` | one of each per load |
| `Budget` | not used here. It belongs to the budget analysis (P3.4) |

Cash goes to the cash account. Card, UPI and Bank Transfer go to the bank
account. Anything else, in practice a blank payment mode shown as `Unknown`,
goes to the unknown account.

Every value on a model object is private. Read it through its getter:
`get_transaction_id()`, `get_date()`, `get_category()`, `get_amount()`,
`get_payment_mode()`, `get_signed_amount()`, and on an account
`get_transactions()`, `get_transaction_count()`, `get_total_spent()`,
`get_total_received()`.

If `budgetwise.models` has no classes, `clean_file` still works and `run`
returns the cleaned records with a message in `error`.

## Rules

- Never raise on row content. A bad row is logged and skipped.
- Every skip, correction and flag goes to `errorlog` with its line number.
- Each row is cleaned once, and each cleaned record is visited once to build,
  filter and place its object.
- `load` and `clean` are timed separately. Section 5 asks for both.
- Reason codes created here are listed in one block at the top of
  `runner.py`. The team vocabulary is not yet approved.

## Do not

- Print. `interface/` does that
- Read files directly. `loader/` does that
- Import from another feature's `implementation/` folder
- Import pandas or numpy. That violates section 2
