# Agreed interfaces

**Status: outstanding.** Owner: Zeyad · Task: `P1.5` · Agreed at: `G1`

**Updated 2026-10-11 by Sarah** for `P2.1`, `P2.4`, `P2.7` and `P2.10` only:
the rows marked *implemented* below, and the section "What `clean_file()` and
`run()` return". These now match the code and each feature's `__init__.py`.
Rows owned by other people are unchanged and still need their owners to confirm.

The function signatures every module depends on. Written **before** Phase 2
implementation starts, so four people building cleaners in parallel are building
against something already settled.

This closes flag `F04` — the plan requires agreed interfaces but no task produces
a concrete contract.

## Where the contracts actually live

Each feature's `__init__.py` is the enforceable version of this document:

```python
# budgetwise/cleaning/dates/__init__.py
from .implementation.parser import parse_date
```

This file records the signatures and the reasoning; `__init__.py` is what Python
checks. **They must agree.** See `CONTRIBUTING.md` §6.

## To be filled in at P1.5

| Module | Function | Signature | Owner |
|---|---|---|---|
| `loader` | `load_rows` | `(path) -> Iterator[tuple[int, dict]]` | unassigned |
| `cleaning/dates` | `parse_date` | `(raw_date) -> tuple[str \| None, list[str]]` · *implemented* · returns `(date_or_None, reasons_list)` | Sarah (`P2.1`) |
| `cleaning/categories` | `normalize` | `(raw) -> tuple[str, str \| None]` | Henrieta |
| `cleaning/amounts` | `parse_amount` | `(raw) -> tuple[float \| None, str \| None, str \| None]` | Patrick |
| `cleaning/rows` | `is_duplicate` | `(raw_row, seen_keys) -> bool` · *implemented* · `seen_keys` is a `set` the caller creates once per load | Sarah (`P2.4`) |
| `cleaning/rows` | `validate_raw_row` | `(raw_row) -> tuple[bool, list[tuple[str, str]]]` · *implemented* · returns `(usable, problems)`, each problem a `(column, detail)` pair | Sarah (`P2.4`) |
| `cleaning/rows` | `has_required_fields` | `(raw_row) -> bool` · *implemented* · the yes/no form of `validate_raw_row` | Sarah (`P2.4`) |
| `cleaning/rows` | `find_repeated_ids` | `(numbered_rows) -> dict[str, int]` · *implemented* · IDs on two or more rows, with the row count | Sarah (`P2.4`) |
| `cleaning/notes` | `classify_note_quality` | `(raw_note) -> tuple[str, str, list[str]]` · *implemented* · returns `(note, quality, reasons_list)` | Sarah (`P2.7`) |
| `errorlog` | `ErrorLog.record` | `(line, field, reason, raw) -> None` | Patrick (`P2.8`). Previously listed under Sarah |
| `models` | `Transaction` | see `budgetwise/models/README.md` | Zeyad |
| `pipeline` | `clean_file` | `(path, error_log=None) -> dict` · *implemented, pull request #10* | Sarah (`P2.10`) |
| `pipeline` | `run` | `(path, start=None, end=None, category=None, error_log=None) -> dict` · *implemented, pull request #10* · there is no `LoadResult` class | Sarah (`P2.10`), models with Zeyad |

The signatures above are proposals drawn from each feature's README. Confirm,
amend, or replace them at `G1`, then uncomment the matching `__init__.py` lines.

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
| `accounts` | `run` only | `dict` | `{"cash": CashAccount, "bank": BankAccount}` holding those same objects |

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
| `no_account` | `run` only: returned objects in neither account |

Two rules always hold:

- `input = valid + skipped + duplicates`
- `objects_built + objects_failed = valid`

The menu's filters change `transactions`, `accounts`, `returned` and
`no_account` only. They never change `records` or the cleaning counts.

## Shapes that need agreeing

- **Raw row** — a `dict[str, str]` of the nine columns, exactly as read
- **Reason code** — the vocabulary in `budgetwise/errorlog/`
- **LoadResult** — resolved for `P2.10`: there is no `LoadResult` class. `clean_file` and `run` return the dictionary described above
- **Retained vs skipped** — implemented as `input = valid + skipped + duplicates`. The definitions of corrected and flagged are proposed in [`decisions.md`](decisions.md) and still need team agreement
