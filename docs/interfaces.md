# Agreed interfaces

**Status: complete.** Owner: Zeyad · Task: `P1.5` · Decision D05

Last updated 2026-10-19. Every row below matches the merged code and each
feature's `__init__.py`.

The function signatures every module depends on, so people building modules in
parallel built against something already settled.

## Where the contracts actually live

Each feature's `__init__.py` is the enforceable version of this document:

```python
# budgetwise/cleaning/dates/__init__.py
from .implementation.parser import parse_date
```

This file records the signatures and the reasoning; `__init__.py` is what Python
checks. **They must agree.** See `CONTRIBUTING.md` §6.

## Function signatures

| Module | Function | Signature | Owner |
|---|---|---|---|
| `loader` | `load_rows` | `(filename) -> Iterator[tuple[int, dict]]` · *implemented* · yields `(line_number, raw_row)` | Patrick (`P2.9`) |
| `cleaning/dates` | `parse_date` | `(raw_date) -> tuple[str \| None, list[str]]` · *implemented* · returns `(date_or_None, reasons_list)` | Sarah (`P2.1`) |
| `cleaning/categories` | `normalize_category` | `(raw, transaction_type=None) -> tuple[str, str \| None]` · *implemented* · `transaction_type` decides where Other Income goes | Henrietta (`P2.2`) |
| `cleaning/amounts` | `parse_amount` | `(raw) -> tuple[float \| None, str \| None, str \| None]` · *implemented* | Patrick (`P2.3`) |
| `cleaning/rows` | `is_duplicate` | `(raw_row, seen_keys) -> bool` · *implemented* · `seen_keys` is a `set` the caller creates once per load | Sarah (`P2.4`) |
| `cleaning/rows` | `validate_raw_row` | `(raw_row) -> tuple[bool, list[tuple[str, str]]]` · *implemented* · returns `(usable, problems)`, each problem a `(column, detail)` pair | Sarah (`P2.4`) |
| `cleaning/rows` | `has_required_fields` | `(raw_row) -> bool` · *implemented* · the yes/no form of `validate_raw_row` | Sarah (`P2.4`) |
| `cleaning/rows` | `find_repeated_ids` | `(numbered_rows) -> dict[str, int]` · *implemented* · IDs on two or more rows, with the row count | Sarah (`P2.4`) |
| `cleaning/notes` | `classify_note_quality` | `(raw_note) -> tuple[str, str, list[str]]` · *implemented* · returns `(note, quality, reasons_list)` | Sarah (`P2.7`) |
| `errorlog` | `ErrorLog.record` | `(line, field, reason, raw) -> None` · *implemented* | Patrick (`P2.8`) |
| `models` | `Transaction`, `ExpenseTransaction`, `IncomeTransaction` | `(transaction_id, user_id, date, category, amount, payment_mode='', original_currency='plain')` · *implemented, merged in #16* · no `create()` factory | Zeyad (`P3.1`) |
| `models` | `Account.add_transaction` | `(transaction) -> None` · *implemented, merged in #16* · inherited by `CashAccount`, `BankAccount`, `UnknownAccount` | Zeyad (`P3.1`) |
| `pipeline` | `clean_file` | `(path, error_log=None) -> dict` · *implemented, merged in #10* | Sarah (`P2.10`) |
| `pipeline` | `run` | `(path, start=None, end=None, category=None, error_log=None) -> dict` · *implemented, merged in #10, working with the real model classes* · there is no `LoadResult` class | Sarah (`P2.10`), models with Zeyad |


### Notes on the implemented contracts

- **`parse_date`** returns a **list** of reasons, not one reason. The list is
  empty when nothing needs reporting, for example a date already in
  `YYYY-MM-DD`. Codes: `DATE_NORMALIZED`, `MISSING_DATE`, `INVALID_DATE`.
- **`is_duplicate`** takes **two** arguments. It adds each new row's key to
  `seen_keys`, so the caller must start every load with an empty set.
- **`validate_raw_row`** returns `(usable, problems)`. A row can be usable and
  still have a problem: an unusual ID such as `X99` is kept and flagged.
  `usable` is `False` when a field is absent, or `transaction_id`, `user_id`
  or `transaction_type` cannot be used.
- **`has_required_fields`** returns a plain `bool`, not a tuple. It does not
  look at the amount. A row with no amount is skipped by the pipeline, using
  `parse_amount`.
- **`classify_note_quality`** returns the note text unchanged. `quality` is one
  of `meaningful`, `low_information`, `missing`, `not_available`. Codes:
  `NOTES_MISSING`, `NOTES_LOW_INFORMATION`. `None` gives an empty note.
- A **raw row** passed to these functions is a `dict` of column name to text.
  **Numbered rows** are `(line_number, raw_row)` pairs, as `load_rows` yields.
- **Malformed raw rows.** `validate_raw_row` follows the shapes
  `csv.DictReader` produces:

  | Line in the file | Shape of the raw row | Result |
  |---|---|---|
  | all nine fields | nine keys, each a string (possibly `""`) | checked normally |
  | a field missing at the end | that key's value is `None` | not usable: "too few fields" |
  | extra values at the end | the extras in a list under the key `None` | not usable: "too many fields" |
  | not a `dict` at all | anything else | not usable, never raises |

  `load_rows` fills a missing field with `""`, so a short row reaches the
  cleaners as an ordinary row. Rows with extra values are rejected and logged.
  The remaining loader checks are expected failures in the tests (review S05).

### Model classes, as merged in #16

The pipeline builds one object per cleaned record and reads it back only
through getters, because every attribute is private.

| Class | Getters and methods the pipeline and tests use |
|---|---|
| `ExpenseTransaction`, `IncomeTransaction` | `get_transaction_id()`, `get_user_id()`, `get_date()`, `get_category()`, `get_amount()`, `get_payment_mode()`, `get_original_currency()`, `get_transaction_type()`, `get_signed_amount()`, `has_date()`, `get_month()`, `to_dict()` |
| `CashAccount`, `BankAccount`, `UnknownAccount` | `add_transaction()`, `get_transactions()` (a copy), `get_transaction_count()`, `get_total_spent()`, `get_total_received()`, `is_reconcilable()`, `describe()`, `get_kind()` |

`Transaction` has no `create()` factory. The pipeline builds the child that
matches `transaction_type` and raises `ValueError` for any other value, which
it logs as `transaction_not_built`. If a factory is added later, the pipeline
uses it.

**If the model classes cannot be imported,** `clean_file` still works, and
`run` returns the cleaned records with no transactions, empty `accounts`, and
`error` set to `"rows were cleaned, but budgetwise.models has no Transaction
class yet"`. The pipeline tests treat a missing model package as an error.

## What `clean_file()` and `run()` return

Both return a `dict`. Import them from `budgetwise.pipeline`.

`clean_file(path)` loads and cleans. It needs no model classes. `run(path, ...)`
does the same cleaning, then builds the objects, applies the menu's filters and
fills the accounts.

| Key | Returned by | Type | Holds |
|---|---|---|---|
| `records` | both | `list[dict]` | one cleaned record per valid row, never filtered |
| `counts` | both | `dict` | see below |
| `timings` | both | `dict[str, float]` | `{"load": seconds, "clean": seconds}` |
| `issues` | both | `list[tuple]` | `(line_number, field, reason, raw_value)` for every logged event |
| `error` | both | `str \| None` | `None`, or a message if the file could not be read |
| `transactions` | `run` only | `list` | `ExpenseTransaction` / `IncomeTransaction` objects that pass the filters |
| `accounts` | `run` only | `dict` | `{"cash": CashAccount, "bank": BankAccount, "unknown": UnknownAccount}` holding those same objects |

**A cleaned record** has these keys:

| Key | Type | Example |
|---|---|---|
| `line_number` | `int` | `2` |
| `transaction_id` | `str` | `"T4999"` |
| `user_id` | `str` | `"U018"` |
| `transaction_type` | `str` | `"Expense"` or `"Income"` |
| `date` | `str \| None` | `"2023-04-25"`, or `None` if missing or invalid |
| `category` | `str` | `"Education"` |
| `amount` | `float` | `3888.0`, always unsigned |
| `original_currency` | `str` | `"₹"`, `"$"`, `"Rs."`, `"INR"` or `"plain"` |
| `payment_mode` | `str` | `"Card"` |
| `location` | `str` | `"Ahmedabad"` |
| `notes` | `str` | `"Movie tickets"`, unchanged |
| `notes_quality` | `str` | `"meaningful"` |

**`counts`** has these keys:

| Key | Meaning |
|---|---|
| `input` | rows read from the file |
| `duplicates` | exact duplicate raw rows removed |
| `skipped` | rows that could not be cleaned |
| `valid` | rows that could. Equals `len(records)` |
| `corrected` | valid rows where a value was changed to its standard form |
| `flagged` | valid rows kept with a concern |
| `categories_normalized` | valid rows whose category text changed |
| `repeated_ids` | distinct IDs shared by two or more valid rows |
| `by_reason` | `dict` of reason code to number of events |
| `objects_built` | `run` only: cleaned records that became objects |
| `objects_failed` | `run` only: cleaned records the classes refused |
| `returned` | `run` only: objects left after the filters |

Rules:

- `input = valid + skipped + duplicates` always holds, from both functions.
- `objects_built + objects_failed = valid` holds **only once `run` has finished
  building objects**. It does not hold for `clean_file`, which builds none, or
  when `run` stops early because the file could not be read or the model
  classes are missing. In those cases both object counts are `0`.
- Every returned object is in exactly one account: cash for `Cash`; bank for
  `Card`, `UPI`, `Bank Transfer`; unknown for anything else, in practice a
  blank payment mode shown as `Unknown`.
- A record the classes refuse is logged as `transaction_not_built` and so is
  counted once in `flagged` (decision D08). On the final run there were none.

The menu's filters change `transactions`, `accounts` and `returned` only. They
never change `records` or the cleaning counts.

## Shapes agreed

- **Raw row**: a `dict[str, str]` of the nine columns, exactly as read
- **Reason code**: the one `Reason` list in `budgetwise/errorlog/` (decision D11)
- **LoadResult**: there is no `LoadResult` class. `clean_file` and `run` return the dictionary described above
- **Retained vs skipped**: `input = valid + skipped + duplicates`. Corrected and flagged are defined in decision D08 in [`decisions.md`](decisions.md)
