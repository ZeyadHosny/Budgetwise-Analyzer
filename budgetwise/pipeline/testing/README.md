# pipeline/testing

Sarah (P2.10) · reviewer Patrick · model tests with Zeyad

These are the tests `G2` is judged on. One file: `test_runner.py`, 90 tests.

## Run

From the repository root:

```bash
python3 -m unittest budgetwise.pipeline.testing.test_runner -v
```

Or everything in the project:

```bash
python3 -m unittest discover
```

Use `python` instead of `python3` if that is what your computer calls it.

A run collecting 0 tests is not a pass. Read the skipped and expected-failure
counts too.

Expected result today: `Ran 90 tests` and `OK (expected failures=4)`.

## Required cases

- [x] Full dataset runs end to end with no exception
- [x] `counts["input"]` equals 15,900 for the main dataset
- [x] `counts["duplicates"]` equals 900 for the main dataset
- [x] Duplicate detection sees raw values. A file with `Fod` and `Food` on
      otherwise-identical rows yields **two** records, not one
- [x] A row with an unparseable date is kept and still counts by category
- [x] A row with a `999999999` amount is excluded and logged
- [x] Every skipped row has a matching `errors.log` entry
- [x] Date-range and category filters return the expected subset
- [x] Objects are built with Zeyad's real classes and placed in the right
      account

## What each group checks

| Class | Tests | Checks | Needs |
|---|---|---|---|
| `CleaningTests` | 17 | counts, cleaned values, each section 4.5 rule, the log file | |
| `OrderTests` | 2 | duplicates judged on raw rows; loading twice is safe | |
| `BadInputTests` | 7 | missing file, wrong header, empty file, no valid rows | |
| `RowValidationTests` | 5 | unusual ID kept and flagged; missing ID skipped with its field | |
| `FlaggedCountTests` | 4 | repeated IDs counted as flagged; one row counted once | |
| `FailureBoundaryTests` | 3 | a failure on one row never stops the later rows | |
| `AmountBoundaryTests` | 4 | 99,999,999 accepted, 100,000,000 rejected, sign rule | 1 expected failure until the amount parser fix |
| `LoaderStructureTests` | 4 | short rows, surplus fields, repeated header names | 3 expected failures until the loader fix |
| `ObjectTests` | 7 | objects built with the right class, values read through getters | |
| `NoFactoryTests` | 5 | `Transaction` has no `create()`; the right subclass is still built; a factory is used if one is added | |
| `ClassUseTests` | 4 | every object is a child class; cash, bank and unknown accounts filled correctly | |
| `ObjectFailureTests` | 5 | a refused record is counted consistently everywhere | |
| `FilterTests` | 9 | date range, category, filters leave cleaning counts alone | |
| `AccountTests` | 6 | each account holds only its own payment modes; every object is in exactly one | dataset |
| `FullDatasetTests` | 8 | 15,900 = 14,651 + 349 + 900 and the other baselines | dataset |

## Expected failures and skipped tests

The model classes are merged (#16), so the object, filter and account tests
always run. If `budgetwise.models` cannot be imported, the whole file errors,
which is deliberate: a missing model is a failure, not a reason to skip.

| Condition | Tests | Shown as | Until |
|---|---|---|---|
| Loader pads short rows or accepts a repeated header | 3 | expected failures | Patrick's loader fix (review S05) |
| `parse_amount` accepts `1-2` | 1 | expected failure | Patrick's parser fix (review S09) |
| Dataset not in `data/raw/` | 8, plus the 6 account tests | skipped | the CSV is present |

An expected failure still runs. It is how the suite records a known defect in
someone else's code without hiding it: the result line reports it, and once
the fix is merged the test passes normally with nothing to edit. To make
these four count as plain failures instead, remove the `@until_fixed(...)`
line above each one.

## How the tests are built

There is no fixtures folder. Each test writes its own small CSV to a temporary
folder and runs the real loader, the real cleaners and a real `ErrorLog` on
it. The rows are in the test, so every expected number can be checked by hand.
`SMALL_FILE` at the top of the file holds one row of every kind: a duplicate
pair, a repeated ID on a different row, a blank date, a blank category, a
`999999999` amount, a blank amount, an unknown type and a short row.

The tests never write to the real `output/logs/errors.log`.
