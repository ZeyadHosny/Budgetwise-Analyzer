# pipeline/testing

Sarah (P2.10) · reviewer Patrick · model tests with Zeyad

These are the tests `G2` is judged on. One file: `test_runner.py`, 86 tests.

## Run

From the repository root:

```bash
python -m unittest budgetwise.pipeline.testing.test_runner -v
```

Or everything in the project:

```bash
python -m unittest discover
```

A run collecting 0 tests is not a pass. Read the skipped count too. A skipped
test proves nothing about the code it would have checked.

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
      (needs the model classes)

## What each group checks

| Class | Tests | Checks | Needs |
|---|---|---|---|
| `CleaningTests` | 16 | counts, cleaned values, each section 4.5 rule, the log file | |
| `OrderTests` | 2 | duplicates judged on raw rows; loading twice is safe | |
| `BadInputTests` | 7 | missing file, wrong header, empty file, no valid rows | |
| `RowValidationTests` | 5 | unusual ID kept and flagged; missing ID skipped with its field | |
| `FlaggedCountTests` | 4 | repeated IDs counted as flagged; one row counted once | |
| `FailureBoundaryTests` | 3 | a failure on one row never stops the later rows | |
| `AmountBoundaryTests` | 4 | 99,999,999 accepted, 100,000,000 rejected, sign rule | 1 waits for the amount parser fix |
| `LoaderStructureTests` | 4 | short rows, surplus fields, repeated header names | 3 wait for the loader fix |
| `ObjectTests` | 7 | objects built with the right class and values | models |
| `NoFactoryTests` | 3 | right subclass even without `create()` | models |
| `ClassUseTests` | 4 | every object is a child class; accounts filled correctly | models |
| `ObjectFailureTests` | 5 | a refused record is counted consistently everywhere | models |
| `FilterTests` | 9 | date range, category, filters leave cleaning counts alone | models |
| `AccountTests` | 5 | cash and bank hold the right objects | models, dataset |
| `FullDatasetTests` | 8 | 15,900 = 14,651 + 349 + 900 and the other baselines | dataset |

## Skipped tests

| Condition | Tests skipped | Until |
|---|---|---|
| `budgetwise.models` has no classes | 33 | Zeyad's classes are merged |
| Loader pads short rows or accepts a repeated header | 3 | Patrick's loader fix (review S05) |
| `parse_amount` accepts `1-2` | 1 | Patrick's parser fix (review S09) |
| Dataset not in `data/raw/` | 8, plus the 5 account tests | the CSV is present |

Each skip turns itself off when its condition is met. Nothing needs editing.

## How the tests are built

There is no fixtures folder. Each test writes its own small CSV to a temporary
folder and runs the real loader, the real cleaners and a real `ErrorLog` on
it. The rows are in the test, so every expected number can be checked by hand.
`SMALL_FILE` at the top of the file holds one row of every kind: a duplicate
pair, a repeated ID on a different row, a blank date, a blank category, a
`999999999` amount, a blank amount, an unknown type and a short row.

The tests never write to the real `output/logs/errors.log`.
