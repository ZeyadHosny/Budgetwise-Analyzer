# Notes quality evidence

`classify_note_quality()` run on the `notes` column of all 15,900 raw rows of
`data/raw/budgetwise_finance_dataset.csv`, before duplicates are removed.

Command, from the repository root:

```bash
python3 -m unittest budgetwise.cleaning.notes.testing.test_note_quality -v
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

| Quality flag | Reason code | Result | Phase 1 |
|---|---|---|---|
| meaningful | none | 10,072 | 10,072 |
| low_information | NOTES_LOW_INFORMATION | 3,007 | 3,007 |
| missing (blank) | NOTES_MISSING | 2,335 | 2,335 |
| not_available (N/A) | NOTES_MISSING | 486 | 486 |
| Total | | 15,900 | 15,900 |

Every one of the 15,900 notes is returned unchanged.

## The six placeholders

| Placeholder | Rows |
|---|---|
| `!!!` | 533 |
| `xyz123` | 511 |
| `...` | 510 |
| `test` | 508 |
| `misc` | 474 |
| `asdfgh` | 471 |
| Total | 3,007 |

## Counts at each stage

The raw-file figures above match Phase 1 and come from the notes tests in the
run above. The final-record figures come from the pipeline: it removes exact
duplicates and skips rows with no usable amount before notes are counted, so
its figures are lower. Both are correct for their own population. The
pipeline figures are recorded in
`budgetwise/pipeline/supplementary/pipeline_evidence.md`.

| Quality | Raw file (15,900 rows) | Final cleaned records (14,651 rows) |
|---|---|---|
| meaningful | 10,072 | 9,296 |
| low_information | 3,007 | 2,765 |
| missing | 2,335 | 2,147 |
| not_available | 486 | 443 |

In the pipeline's log this gives 2,765 `notes_low_information` events and
2,590 `notes_missing` events (2,147 blank plus 443 N/A).

## Text, quality and log, end to end

**Source of these examples:** a run of the pipeline on the full dataset in a
test copy of the repository, not the run above. They are real output of that
run, lines 3 and 6 of the CSV, but they have not yet been captured from the
real branch's `output/logs/errors.log`. Replace them with lines from that file
after the next full run.

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
