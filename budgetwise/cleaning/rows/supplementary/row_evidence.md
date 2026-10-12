# Raw-row evidence

Measured on all 15,900 raw rows of `data/raw/budgetwise_finance_dataset.csv`,
read with `csv.DictReader`, using the functions in `raw_rows.py`.

Command, from the repository root:

```bash
python -m unittest budgetwise.cleaning.rows.testing.test_raw_rows -v
```

## Run details

| | |
|---|---|
| Run by | Sarah, 2026-10-10, from the repository root |
| Command | `python3 -m unittest budgetwise.cleaning.rows.testing.test_raw_rows` |
| Branch and commit | `fix/p2-4-repeated-id-missing-ids` at commit `251fc81` |
| Python | `python3` in the VS Code terminal. VS Code showed Python 3.14.7 as its interpreter; confirm with `python3 --version` |
| Result | `Ran 47 tests in 0.101s`, `OK`: 47 passed, 0 failed, 0 errors, 0 skipped |
| Dataset | present in `data/raw/`, so the 7 dataset tests ran |
| Merged | First version from `feat/p2-4-cleaning-rows`. The S03 correction and this evidence in #13 |

## Duplicates and malformed rows

| Measure | Result | Phase 1 |
|---|---|---|
| Raw rows | 15,900 | 15,900 |
| Exact raw duplicates | 900 | 900 |
| Unique raw rows | 15,000 | 15,000 |
| Malformed rows (wrong field count, or unusable required field) | 0 | |
| Rows with a missing or blank transaction ID | 0 | 0 |
| Rows with an unusual ID or type format | 0 | |
| Distinct transaction IDs | 14,000 | 14,000 |

## Repeated transaction IDs

The figure depends on which rows are counted, so each population is stated.

| Population | Distinct repeated IDs | Rows carrying them |
|---|---|---|
| Raw file (15,900 rows) | 1,680 | 3,580 |
| After exact duplicates are removed (15,000 rows) | 926 | 1,926 |
| Final cleaned records (14,651 rows), from the pipeline | 888 | 1,846 |

- 1,680 is the Phase 1 figure.
- 754 of the 1,680 repeat only because of exact duplicates. They stop being
  repeated once the 900 duplicate rows are removed.
- The other 926 sit on rows that differ, so removing rows by ID alone would
  have deleted legitimate transactions. All of those rows are kept.
- 888 is lower than 926 because some of those rows are later skipped for a
  blank or sentinel amount. That step belongs to the pipeline. The 888 IDs
  and the 1,846 rows carrying them are measured by the pipeline, in
  `budgetwise/pipeline/supplementary/pipeline_evidence.md`, not here.
- Rows with no ID are never counted as sharing an ID. The dataset has none,
  so this rule changes no figure here. It protects against bad input.

## Speed

Measured, not estimated:

| What | Time | Where |
|---|---|---|
| All 47 tests, including the 7 that read the full 15,900-row file | 0.101 seconds | the run above |
| Splitting duplicates, finding repeated IDs twice and validating every row of the full file | about 0.09 seconds | a timed run in a test copy of the repository |

Duplicates and repeated IDs are each found in one pass, using a set and a
counter.

## Tests

47 tests: 40 that use small hand-written rows and 7 that use the full
dataset. All 47 passed in the run above. The 7 dataset tests are skipped if
the CSV is not in `data/raw/`.
