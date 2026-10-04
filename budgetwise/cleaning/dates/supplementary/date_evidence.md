# Date parsing evidence

`parse_date()` run on all 15,900 raw rows of `budgetwise_finance_dataset.csv`.

| Measure | Result | Phase 1 |
|---|---|---|
| YYYY-MM-DD (unchanged) | 6,091 | 6,091 |
| MM/DD/YYYY (normalized) | 4,676 | 4,676 |
| DD-MM-YY (normalized) | 3,044 | 3,044 |
| DD-MM-YYYY (normalized) | 1,603 | 1,603 |
| Missing | 486 | 486 |
| Invalid | 0 | 0 |
| Ambiguous slash dates | 1,865 | 1,865 |
| Ambiguous DD-MM-YY dates | 1,198 | not reported |
| Ambiguous DD-MM-YYYY dates | 650 | not reported |

In DD-MM-YYYY dates the first number exceeds 12 in 953 rows and the second
never does, which supports the day-first reading. All parsed dates fall
between 2021 and 2024.
