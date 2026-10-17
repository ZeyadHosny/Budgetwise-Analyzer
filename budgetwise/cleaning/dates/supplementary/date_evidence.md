# Date parsing evidence

`parse_date()` run on the `date` column of all 15,836 raw rows of
`data/raw/budgetwise_synthetic_dirty.csv`, the D01 dataset, before duplicates
are removed.

**Re-measured 2026-10-17 for decision `D01`.** The original figures below were
taken on `budgetwise_finance_dataset.csv` and are kept in the `finance` column
for comparison, because the difference between the two is itself evidence for
the report.

Command, from the repository root:

```bash
python -m unittest budgetwise.cleaning.dates.testing.test_parser -v
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

| Measure | D01 dataset | finance (old) |
|---|---:|---:|
| YYYY-MM-DD (unchanged) | 4,430 | 6,091 |
| MM/DD/YYYY (normalized) | 4,750 | 4,676 |
| DD-MM-YY (normalized) | 3,925 | 3,044 |
| DD-MM-YYYY (normalized) | **0** | 1,603 |
| Missing (blank) | 344 | 486 |
| **Invalid (no rule matches)** | **2,387** | **0** |
| Total | 15,836 | 15,900 |

8,675 dates were converted to YYYY-MM-DD (4,750 + 3,925). All parsed dates
fall between 2019-01-01 and 2022-12-31.

**The 2,387 invalid values are the headline difference.** This dataset carries
18 date shapes against the 5 `parse_date()` implements, so 2,387 values match
no rule and are rejected rather than normalized. Blank plus invalid accounts
for every unrecognised value: 344 + 2,387 = 2,731.

`DD-MM-YYYY` does not occur here at all, so the team convention recorded in
`D10` — hyphen with a four-digit year is read day first — is not exercised by
this dataset. The rule still stands; it simply has no data behind it now.

## Ambiguous dates

A date is ambiguous when it is a real date and its day and month are both
from 1 to 12, so the two numbers could be read either way.

| Format | Ambiguous | finance (old) | Rule that settles it |
|---|---:|---:|---|
| MM/DD/YYYY | 1,904 | 1,865 | slash is month first (section 4.5) |
| DD-MM-YY | 1,537 | 1,198 | hyphen with two-digit year is day first (section 4.5) |
| DD-MM-YYYY | 0 | 650 | hyphen is day first (team convention) — no rows here |

These counts are unchanged by review correction S02. That correction stops
dates that are not real, such as `00/05/2023`, from being counted. The
dataset contains none, so the figures stay the same.

## Evidence for the day-first reading of hyphen dates

| Format | First number above 12 | Second number above 12 |
|---|---:|---:|
| MM/DD/YYYY | 0 | 2,846 |
| DD-MM-YY | 2,388 | 0 |
| DD-MM-YYYY | no rows | no rows |

The pattern holds on this dataset too: in the hyphen format the first number
goes above 12 and the second never does, so the first number is the day. In
slash dates it is the other way round. `DD-MM-YYYY` has no rows here, so the
evidence for `D10` rests on the earlier dataset only.

## Missing dates at each stage

| Population | Rows with no date |
|---|---:|
| Raw file (15,836 rows), blank only | 344 |
| After exact duplicates are removed (15,032 rows), blank only | 327 |
| Final cleaned records (14,862 rows), from the pipeline | **2,581** |

The jump at the last row is not an error. The first two rows count blank
values; the pipeline figure also includes the 2,259 values that survive
deduplication but match no date rule, and so reach analysis with no date:
322 blank + 2,259 unreadable = 2,581.

**That is 17% of valid rows, against 3% on the earlier dataset.** Rows with no
date are kept and still count toward category totals, but every monthly figure
excludes them, so the dated/undated split belongs in the reported results
rather than in a footnote.

## Tests

24 tests: 20 that use small hand-written inputs and 4 that use the full
dataset. All 24 passed in the run above. The 4 dataset tests are skipped if
the CSV is not in `data/raw/`.
