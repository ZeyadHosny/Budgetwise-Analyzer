# pipeline

Runs raw rows through every cleaner and builds the cleaned dataset.

| | |
|---|---|
| **Responsible** | Sarah. Model integration with Zeyad |
| **Domain reviewer** | Patrick (`P2.10`). All team at `G2` |
| **PR approval** | Zeyad or Patrick. See `CONTRIBUTING.md` |
| **Tasks** | `P2.10` implementation · `G2` integration |
| **Status** | Merged; includes account-backed monthly budget comparisons |

## 1. What this folder does

The orchestration layer. It cleans nothing itself. It takes raw rows from
`loader/`, puts them through every cleaning feature in the correct order,
builds the transaction objects, places them in their accounts, and returns
them along with the counts and timings the report needs.

**Order matters and is mandatory.** Duplicate detection runs on raw rows
*before* any normalization (section 4.5). Normalizing first would collapse
`FOOD` and `Food` into one value and make rows look identical that were not.

```
raw row
  1. duplicate check        cleaning/rows    on the raw row, before anything else
  2. row validation         cleaning/rows    skip unusable rows, flag odd ones
  3. amount parse           cleaning/amounts no usable amount: skip the row
  4. date parse             cleaning/dates   no date: row is KEPT
  5. category normalize     cleaning/categories
  6. payment mode normalize cleaning/payment_modes
  7. location normalize     cleaning/locations
  8. note quality           cleaning/notes
all cleaned rows
  9. repeated IDs flagged   cleaning/rows    rows are KEPT
 10. transaction object     models           Expense or Income
 11. menu filters           date range, category
 12. account                models           cash, bank or unknown
 13. monthly budget compare  analysis/budgets via each account's transactions
```

Only two things remove a row: it cannot be used at all (duplicate, or a
missing ID, user ID or type), or it has no usable amount. Everything else is
cleaned or flagged and the row is kept.

## 2. How other modules use it

```python
from budgetwise.pipeline import clean_file, run

result = run("data/raw/budgetwise_finance_dataset.csv")
result["transactions"]     # list of ExpenseTransaction / IncomeTransaction
result["accounts"]         # {"cash": CashAccount, "bank": BankAccount, "unknown": UnknownAccount}
result["account_breakdown"] # counts and totals calculated through account getters
result["counts"]           # dict of the numbers the report needs
result["timings"]          # seconds for load and clean
result["budget_comparisons"] # monthly category status, based on returned accounts
result["error"]            # None, or a message if the file could not be read

run(path, start="2023-01-01", end="2023-12-31")    # menu option 2
run(path, category="Food")                         # menu option 3
```

`main.py` and `interface/menu/` call `run`. Nothing else does.

`clean_file(path)` does the cleaning only and returns the cleaned records as
plain dictionaries. It needs no model classes, so it is what the tests and the
metrics use when objects are not required.

Both return a **dictionary**. There is no `LoadResult` class, so write
`result["counts"]`, not `result.counts`.

## 3. What it produces

| Key | Example on the full dataset | Feeds |
|---|---|---|
| `transactions` | list of 14,651 objects | all of `analysis/` |
| `accounts` | one `CashAccount`, one `BankAccount`, one `UnknownAccount` | report: cash versus bank |
| `account_breakdown` | transaction count, total spent, total received per account | summary JSON |
| `records` | list of 14,651 dictionaries, unfiltered | export, metrics |
| `counts["input"]` | 15,900 | report: number of input records |
| `counts["valid"]` | 14,651 | report: number of valid records |
| `counts["corrected"]` | 14,587 | report: number of corrected records |
| `counts["skipped"]` | 349 | report: invalid/skipped records |
| `counts["duplicates"]` | 900 | report: duplicates detected |
| `counts["categories_normalized"]` | 10,955 | report: categories normalized |
| `timings` | `{"load": 0.04, "clean": 0.5}` | report: execution time |
| `budget_comparisons` | monthly category limits, actuals, statuses, and differences | summary JSON |
| `issues` | list of `(line, field, reason, raw)` | view error log |
| `error` | `None` | menu message |

Those seven figures are named individually in section 5 as required results.
They are produced here because this is the only place that sees every row.

`input = valid + skipped + duplicates` always holds: 15,900 = 14,651 + 349 + 900.

Further counts (`flagged`, `repeated_ids`, `by_reason`, and the object counts)
are described in `implementation/README.md`.

## 4. How the model classes are used

Section 4.3 asks for object-oriented design with inheritance and
encapsulation. The pipeline is where the classes first meet the data.

| Class | Kind | What the pipeline does with it |
|---|---|---|
| `Transaction` | parent | Never built directly. It has no factory, so the pipeline builds the child that matches `transaction_type` |
| `ExpenseTransaction` | child of `Transaction` | One object for every cleaned Expense row |
| `IncomeTransaction` | child of `Transaction` | One object for every cleaned Income row |
| `Account` | parent | Never built directly. It supplies `add_transaction()`, which all three children inherit |
| `CashAccount` | child of `Account` | One per load. Holds the Cash transactions |
| `BankAccount` | child of `Account` | One per load. Holds Card, UPI and Bank Transfer |
| `UnknownAccount` | child of `Account` | One per load. Holds rows whose payment mode is blank, shown as `Unknown` |
| `Budget` | stands alone | Used by the monthly comparison after accounts are populated; account getters supply its transactions |

How they work together for one row:

```
cleaned values
   -> ExpenseTransaction(...) or IncomeTransaction(...)   chosen by transaction_type
   -> appended to result["transactions"]      the list of objects (section 4.2)
   -> cash, bank or unknown .add_transaction(txn)   the SAME object, not a copy
```

- **Inheritance.** Every object in the list is a child class, and also a
  `Transaction`. Code that only needs an amount or a date can treat them all
  alike. Code that needs the direction calls `get_signed_amount()`, which each
  child answers differently.
- **Encapsulation.** Every attribute on the model classes is private. The
  pipeline passes cleaned values to the constructor and to
  `add_transaction()`, and reads values back only through getters such as
  `get_amount()`. The classes check what they are given. An amount is cleaned to an unsigned number first, so the
  class always receives a value it accepts.
- **Two containers, one set of objects.** The list answers "what was spent on
  Food". The accounts answer "how much went through cash and how much through
  the bank, and how much has no recorded payment method".
- **Efficiency.** Each cleaned row is visited once to build its object, apply
  the filters and place it in an account.

A payment mode that is neither cash nor a bank channel, in practice a blank
one shown as `Unknown`, goes in the `UnknownAccount`. Zeyad's model provides
that account for exactly these rows. All objects are also in the list, so they
count in every total.

If the classes refuse a row, it is logged as `transaction_not_built` and
counted in `counts["objects_failed"]`. The cleaning counts do not change.

## 5. Requirements and tasks covered

| Requirement | Source | Task |
|---|---|---|
| Duplicate detection performed on raw rows before normalization | section 4.5 | `P2.4` `P2.10` `G2` |
| Store transactions as a list of objects | section 4.2 | `P2.10` |
| Use sets to detect duplicate transactions | section 4.2 | `P2.4` `P2.10` |
| Load the dataset, or a subset by date range or category | section 4.1 | `P2.10` `P3.5` |
| Log skipped, corrected and flagged records with a reason | section 4.1 | `P2.8` `P2.10` |
| Program must not crash on bad input | section 4.1 | `P2.10` `P4.1` |
| Object-oriented design with inheritance and encapsulation | section 4.3 | `P3.1`, used here |
| Number of input / valid / corrected / skipped records | section 5 | `P3.8` |
| Number of duplicates detected, categories normalized | section 5 | `P3.8` |
| Execution time for loading and cleaning | section 5 | `P3.8` |

## 6. Folders

| Folder | Contents |
|---|---|
| `implementation/` | `runner.py` |
| `testing/` | `test_runner.py`, 90 tests |
| `supplementary/` | `pipeline_evidence.md` |

Run the tests from the repository root:

```bash
python3 -m unittest budgetwise.pipeline.testing.test_runner -v
```

Each subfolder has its own README with the detail.

## 7. Done when

- [x] Full 15,900-row dataset runs start to finish without raising
- [x] All seven counts produced and cross-checked by hand on a small file
- [x] Duplicate detection demonstrably runs before normalization
- [x] Every skipped, corrected or flagged row appears in `errors.log`
- [x] `counts["input"]` equals the file's row count exactly
- [x] Object, filter and account tests run against the real classes in
      `budgetwise/models` (merged in #16)

## 8. Open points

| Point | Owner |
|---|---|
| Loader pads short rows and drops surplus fields | Patrick |
| `parse_amount` removes every minus sign, so `1-2` becomes 12 | Patrick |
| Reason-code names and casing not yet approved | Sarah and Patrick |
