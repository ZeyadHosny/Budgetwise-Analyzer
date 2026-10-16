# cleaning/notes

Labels the quality of each note. The note text is never changed.

| | |
|---|---|
| **Responsible** | Sarah |
| **Domain reviewer** | Henrietta |
| **Task** | `P2.7`. Profiling from Bahareh's Phase 1 report (`P1.1`) |

## Folder contents

| Folder | File | Holds |
|---|---|---|
| `implementation/` | `note_quality.py` | the quality labels and the function |
| `testing/` | `test_note_quality.py` | 12 tests |
| `supplementary/` | `notes_evidence.md` | counts and evidence for the report |

## Rules

`notes` is free text, so nothing is mapped or corrected. Each note gets one
of four quality labels:

| Quality | Meaning | Reason | Count |
|---|---|---|---|
| `meaningful` | real text | none | 10,072 |
| `low_information` | one of `...` `!!!` `xyz123` `test` `misc` `asdfgh` | `NOTES_LOW_INFORMATION` | 3,007 |
| `missing` | blank or `None` | `NOTES_MISSING` | 2,335 |
| `not_available` | the text `N/A` | `NOTES_MISSING` | 486 |

Blank and `N/A` share a reason code but have separate labels, so each count
can be checked against Phase 1. Note quality never removes a row.

## Implementation

```python
from budgetwise.cleaning.notes import classify_note_quality

note, quality, reasons = classify_note_quality("xyz123")
# ("xyz123", "low_information", ["NOTES_LOW_INFORMATION"])
```

`classify_note_quality(raw_note)` returns `(note, quality, reasons)`. The note
is returned exactly as given. It is trimmed and lowercased only for the
comparison, and the whole note is compared, so `test` is a placeholder but
`test drive fee` is meaningful.

**Faulty input.** `None` becomes `""` with quality `missing`. Non-text input
is converted with `str()` first. These checks cover every input, so no
`try/except` is needed and the function never raises.

Only `pipeline/` calls this. It stores `note` and `quality` in each record as
`notes` and `notes_quality`. Reason codes come from `budgetwise.errorlog.Reason`.

## Testing

| Group | Checks |
|---|---|
| `MeaningfulNoteTests` | real notes returned unchanged; `test drive fee` stays meaningful |
| `LowInformationNoteTests` | blank, `N/A`, `None` and each placeholder get the right label and reason, in any capitals; non-text does not crash |
| `FullDatasetTests` | counts on all 15,900 rows match Phase 1; every note returned unchanged |

```bash
python3 -m unittest budgetwise.cleaning.notes.testing.test_note_quality -v
```

Run from the repository root. The 3 full-dataset tests are skipped if
`data/raw/budgetwise_finance_dataset.csv` is missing.

## Supplementary

`notes_evidence.md` holds the run details, quality counts, the count of each
placeholder, counts at each pipeline stage and an end-to-end example.

Key figures after cleaning (14,651 rows): 9,296 meaningful, 2,765
placeholders, 2,147 blank, 443 `N/A`.
