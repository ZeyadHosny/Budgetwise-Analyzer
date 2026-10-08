# Raw-row evidence

Measured on all 15,900 raw rows of `budgetwise_finance_dataset.csv`.

| Measure | Result | Phase 1 |
|---|---|---|
| Exact raw duplicates | 900 | 900 |
| Unique raw rows | 15,000 | 15,000 |
| Malformed rows | 0 | |
| Distinct transaction IDs | 14,000 | 14,000 |
| IDs occurring more than once in the raw file | 1,680 | 1,680 |
| of which repeat only through exact duplicates | 754 | |
| of which are shared by different rows (retained) | 926 | |

Only 754 of the 1,680 repeated IDs are explained by exact duplicates. The
other 926 sit on rows that differ, so removing rows by ID alone would have
deleted legitimate transactions.
