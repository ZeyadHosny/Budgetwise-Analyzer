# Date parsing evidence

`parse_date()` run on the `date` column of all 15,900 raw rows of
`data/raw/budgetwise_finance_dataset.csv`, before duplicates are removed.

Command, from the repository root:

```bash
python3 -m unittest budgetwise.cleaning.dates.testing.test_parser -v
```

## Run details

| | |
|---|---|
| Run by | Sarah, 2026-10-10, from the repository root |
| Command | `python3 -m unittest budgetwise.cleaning.dates.testing.test_parser` |
| Branch and commit | `fix/p2-1-date-ambiguity-helper` at commit `2301c4f` |
| Python | `python3` in the VS Code terminal. VS Code showed Python 3.14.7 as its interpreter; confirm with `python3 --version` |
| Result | `Ran 24 tests in 0.157s`, `OK`: 24 passed, 0 failed, 0 errors, 0 skipped |
| Dataset | present in `data/raw/`, so the 4 dataset tests ran |
| Merged | First version from `feat/p2-1-cleaning-dates`. The S02 correction and this evidence in #12 |

The dataset figures below were also measured in a separate test copy of the
repository and agree with this run, since the dataset tests passed.

## Formats

| Measure | Result | Phase 1 |
|---|---|---|
| YYYY-MM-DD (unchanged) | 6,091 | 6,091 |
| MM/DD/YYYY (normalized) | 4,676 | 4,676 |
| DD-MM-YY (normalized) | 3,044 | 3,044 |
| DD-MM-YYYY (normalized) | 1,603 | 1,603 |
| Missing | 486 | 486 |
| Invalid | 0 | 0 |
| Total | 15,900 | 15,900 |

9,323 dates were converted to YYYY-MM-DD (4,676 + 3,044 + 1,603). All 486
missing dates are blank. All parsed dates fall between 2021-01-01 and
2024-12-31.

## Ambiguous dates

A date is ambiguous when it is a real date and its day and month are both
from 1 to 12, so the two numbers could be read either way.

| Format | Ambiguous | Phase 1 | Rule that settles it |
|---|---|---|---|
| MM/DD/YYYY | 1,865 | 1,865 | slash is month first (section 4.5) |
| DD-MM-YY | 1,198 | not reported | hyphen with two-digit year is day first (section 4.5) |
| DD-MM-YYYY | 650 | not reported | hyphen is day first (team convention) |

These counts are unchanged by review correction S02. That correction stops
dates that are not real, such as `00/05/2023`, from being counted. The
dataset contains none, so the figures stay the same.

## Evidence for the day-first reading of hyphen dates

| Format | First number above 12 | Second number above 12 |
|---|---|---|
| MM/DD/YYYY | 0 | 2,811 |
| DD-MM-YY | 1,846 | 0 |
| DD-MM-YYYY | 953 | 0 |

In both hyphen formats the first number goes above 12 and the second never
does, so the first number is the day. In slash dates it is the other way
round. The data agrees with every rule used.

## Missing dates at each stage

| Population | Rows with no date |
|---|---|
| Raw file (15,900 rows) | 486 |
| After exact duplicates are removed (15,000 rows) | 462 |
| Final cleaned records (14,651 rows), from the pipeline | 454 |

Rows with no date are kept. They are left out of date-based analysis only.

## Tests

24 tests: 20 that use small hand-written inputs and 4 that use the full
dataset. All 24 passed in the run above. The 4 dataset tests are skipped if
the CSV is not in `data/raw/`.


## Dirty file (`budgetwise_synthetic_dirty.csv`)

`parse_date()` on the `date` column of all 15,836 raw rows.

| Result | Rows |
|---|---|
| Already `YYYY-MM-DD` | 4,430 |
| Converted (`DATE_NORMALIZED`) | 11,050 |
| Missing (blank) | 344 |
| Invalid (`29/10/19` style: slash dates are month first) | 12 |

Formats: `MM/DD/YYYY` 4,750, `YYYY-MM-DD` 4,430, `DD-MM-YY` 3,925,
`Month DD YYYY` 2,350, `YYYY/MM/DD` 21, `MM/DD/YY` 16, blank 344.

Day-first evidence: in `DD-MM-YY` dates the first number is above 12 in 2,388
rows and the second never is; in `MM/DD/YYYY` dates the second is above 12 in
2,846 rows and the first never is.

After the pipeline (14,862 retained rows): 14,528 have a usable date,
334 do not (322 missing, 12 invalid). Those 334 are left out of date-based
analysis and still count by category.
