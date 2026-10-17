# Notes quality evidence

`classify_note_quality()` run on the `notes` column of all 15,836 raw rows of
`data/raw/budgetwise_synthetic_dirty.csv`, the D01 dataset, before duplicates
are removed.

**Re-measured 2026-10-17 for decision `D01`.** The earlier
`budgetwise_finance_dataset.csv` figures are kept in a `finance` column,
because what this dataset does *not* contain is the important part.

Command, from the repository root:

```bash
python -m unittest budgetwise.cleaning.notes.testing.test_note_quality -v
```

## Run details

| | |
|---|---|
| Run by | Sarah, 2026-10-10, from the repository root |
| Command | `python3 -m unittest budgetwise.cleaning.notes.testing.test_note_quality` |
| Branch and commit | `docs/p2-7-notes-readme` at commit `ab879f4` |
| Python | `python3` in the VS Code terminal. VS Code showed Python 3.14.7 as its interpreter; confirm with `python3 --version` |
| Result | `Ran 12 tests in 0.030s`, `OK`: 12 passed, 0 failed, 0 errors, 0 skipped |
| Dataset | present in `data/raw/`, so the 3 dataset tests ran |
| Merged | First version from `feat/p2-7-cleaning-notes`. The documentation update and this evidence in #14 |

## Quality counts on the raw file

| Quality flag | Reason code | D01 dataset | finance (old) |
|---|---|---:|---:|
| meaningful | none | 14,302 | 10,072 |
| low_information | NOTES_LOW_INFORMATION | **0** | 3,007 |
| missing (blank) | NOTES_MISSING | 1,534 | 2,335 |
| not_available (N/A) | NOTES_MISSING | **0** | 486 |
| Total | | 15,836 | 15,900 |

Every one of the 15,836 notes is returned unchanged.

## The six placeholders do not occur in this dataset

| Placeholder | D01 dataset | finance (old) |
|---|---:|---:|
| `!!!` | 0 | 533 |
| `xyz123` | 0 | 511 |
| `...` | 0 | 510 |
| `test` | 0 | 508 |
| `misc` | 0 | 474 |
| `asdfgh` | 0 | 471 |
| Total | **0** | 3,007 |

There are also no `N/A` values. So `classify_note_quality()` only ever returns
`meaningful` or `missing` on this dataset: the `low_information` and
`not_available` branches are never reached.

**This is a loss of test coverage, not a simplification.** The rule is still
required — §4.5 asks that placeholder notes not be treated as meaningful text —
and the branches still work. But the only thing exercising them now is the
hand-written `PlaceholderTests` in
`budgetwise/cleaning/notes/testing/test_note_quality.py`, where the six
placeholders are supplied directly. The dataset no longer corroborates them,
and the class docstring there carries the same warning.

## Counts at each stage

The raw-file figures above match Phase 1 and come from the notes tests in the
run above. The final-record figures come from the pipeline: it removes exact
duplicates and skips rows with no usable amount before notes are counted, so
its figures are lower. Both are correct for their own population. The
pipeline figures are recorded in
`budgetwise/pipeline/supplementary/pipeline_evidence.md`.

| Quality | Raw file (15,836 rows) | Final cleaned records (14,862 rows) |
|---|---:|---:|
| meaningful | 14,302 | 13,427 |
| low_information | 0 | 0 |
| missing | 1,534 | 1,435 |
| not_available | 0 | 0 |

In the pipeline's log this gives 0 `notes_low_information` events and 1,435
`notes_missing` events, all of them blank.

## Text, quality and log, end to end

**These two examples came from `budgetwise_finance_dataset.csv` and cannot be
reproduced on the D01 dataset**, which contains no placeholder notes and no
`N/A` values. They are kept because they document the intended behaviour of
the `low_information` and `not_available` paths, which is still what the code
does. They are no longer a record of output from the dataset being reported
on, and must not be cited in the report as if they were.

For one row, the pipeline keeps the text, stores the quality and writes the
reason to the log:

```
record["notes"]         -> 'asdfgh'
record["notes_quality"] -> 'low_information'
errors.log              -> line=3 field=notes reason=notes_low_information raw='asdfgh'
```

```
record["notes"]         -> 'N/A'
record["notes_quality"] -> 'not_available'
errors.log              -> line=6 field=notes reason=notes_missing raw='N/A'
```

The pipeline writes reason codes in lowercase. The casing is a team decision
that is still open (review S08).

## Tests

12 tests: 9 that use small hand-written inputs and 3 that use the full
dataset. All 12 passed in the run above. The 3 dataset tests are skipped if
the CSV is not in `data/raw/`.
