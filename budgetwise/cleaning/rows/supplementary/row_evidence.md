# Raw-row evidence

Measured on all 15,900 raw rows of `data/raw/budgetwise_finance_dataset.csv`,
read with `csv.DictReader`, using the functions in `raw_rows.py`.

Command, from the repository root:

```bash
python -m unittest budgetwise.cleaning.rows.testing.test_raw_rows -v
```

Python version, branch and commit: fill in after running on the real branch.

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
  blank or sentinel amount. That step belongs to the pipeline.
- Rows with no ID are never counted as sharing an ID. The dataset has none,
  so this rule changes no figure here. It protects against bad input.

## Speed

Splitting duplicates, finding repeated IDs twice and validating every row
takes about 0.1 seconds on the 15,900 rows. Duplicates and repeated IDs are
each found in one pass, using a set and a counter.

## Tests

47 tests, all passing. Seven use the full dataset and are skipped if the CSV
is not in `data/raw/`.
