# cleaning/notes

Classifies the quality of each note. The note text is never changed.

| | |
|---|---|
| **Responsible** | Sarah |
| **Domain reviewer** | Henrieta (`P2.7`) |
| **PR approval** | Zeyad or Patrick. See `CONTRIBUTING.md` |
| **Tasks** | `P2.7` implementation. Profiling is Bahareh's Phase 1 report (`P1.1`) |
| **Status** | First version merged from `feat/p2-7-cleaning-notes`. No defect found in the Phase 2 review. This README and the evidence merged in #14 |

## 1. What this folder does

`notes` is free text, not a closed list like category, so nothing is mapped
or corrected. This folder only labels each note with a quality, so the report
can say how many notes carry real information.

There are four quality labels:

| Quality | Meaning | Reason code |
|---|---|---|
| `meaningful` | real text | none |
| `low_information` | one of six known placeholders | `NOTES_LOW_INFORMATION` |
| `missing` | blank, or only spaces, or no value at all | `NOTES_MISSING` |
| `not_available` | the text `N/A` | `NOTES_MISSING` |

Blank and `N/A` share one reason code but keep separate quality labels, so
each can be matched to its own Phase 1 count.

The six known placeholders are `...`, `!!!`, `xyz123`, `test`, `misc` and
`asdfgh`. This is a closed list taken from Phase 1.

**Note quality alone never removes a row.** Every row is kept whatever its
note says. A row can still be removed for another reason, such as being an
exact duplicate or having no usable amount, but never because of its note.

## 2. How other modules use it

```python
from budgetwise.cleaning.notes import classify_note_quality

note, quality, reasons = classify_note_quality("xyz123")
# note    -> "xyz123"                     the text, unchanged
# quality -> "low_information"
# reasons -> ["NOTES_LOW_INFORMATION"]    a list, empty for a meaningful note
```

Only `pipeline/` calls this. It stores `note` and `quality` in the cleaned
record as `notes` and `notes_quality`, and logs each reason.

Everything the folder exports:

| Name | What it is |
|---|---|
| `classify_note_quality(raw_note)` | returns `(note, quality, reasons)` |
| `MEANINGFUL`, `LOW_INFORMATION`, `MISSING`, `NOT_AVAILABLE` | the four quality labels |
| `NOTES_MISSING`, `NOTES_LOW_INFORMATION` | the two reason codes |
| `PLACEHOLDER_NOTES` | the six placeholders |

## 3. What it produces

| Input | Note returned | Quality | Reasons |
|---|---|---|---|
| `"Electricity bill"` | `"Electricity bill"` | `meaningful` | none |
| `"  Lunch  "` | `"  Lunch  "` | `meaningful` | none |
| `"test drive fee"` | `"test drive fee"` | `meaningful` | none |
| `"xyz123"` | `"xyz123"` | `low_information` | `NOTES_LOW_INFORMATION` |
| `"Test"`, `" test "` | unchanged | `low_information` | `NOTES_LOW_INFORMATION` |
| `""` | `""` | `missing` | `NOTES_MISSING` |
| `"   "` | `"   "` | `missing` | `NOTES_MISSING` |
| `"N/A"`, `"n/a"` | unchanged | `not_available` | `NOTES_MISSING` |
| `None` | `""` | `missing` | `NOTES_MISSING` |
| `123` (a number) | `"123"` | `meaningful` | none |

How the input is handled:

- **Text is returned exactly as given**, including capitals and spaces at
  the ends. Only the comparison ignores capitals and outer spaces. This
  promise applies to text: the two cases below are the only ones where the
  value returned is not the value passed in.
- **The whole note is compared**, not part of it. `test` is a placeholder, but
  `test drive fee` is a real note.
- **`None` becomes an empty note.** There is no text to keep, so the note
  returned is `""` and the quality is `missing`.
- **A value that is not text is converted to text** with `str()`, then
  classified like any other note. A number such as `123` becomes `"123"` and
  is `meaningful`. Values read from a CSV file are always text, so this only
  protects against bad input from other code.
- **It never raises**, for any input.

Expected on the main dataset: 10,072 meaningful, 3,007 low information, 2,335
missing and 486 not available. See `supplementary/notes_evidence.md`.

## 4. Requirements and tasks covered

| Requirement | Source | Task |
|---|---|---|
| Preserve meaningful free text exactly as observed | Phase 2 specification | `P2.7` |
| Flag blank, N/A and known placeholders; do not replace meaningful text | Phase 2 specification | `P2.7` |
| Log flagged records with a reason | section 4.1 | `P2.7` `P2.8` |
| Program must not crash on bad input | section 4.1 | `P2.7` |

The assignment does not name the notes column. The rules come from the team's
Phase 2 specification, and the baselines from Bahareh's Phase 1 report.

## 5. Folders

| Folder | Contents |
|---|---|
| `implementation/` | `note_quality.py` |
| `testing/` | `test_note_quality.py`, 12 tests |
| `supplementary/` | `notes_evidence.md` |

Run the tests from the repository root:

```bash
python -m unittest budgetwise.cleaning.notes.testing.test_note_quality -v
```

Three of the 12 tests use the full dataset and are skipped if the CSV is not
in `data/raw/`.

## 6. Done when

- [x] Every note in the dataset is returned unchanged
- [x] All four quality counts match Phase 1
- [x] Each of the six placeholders is flagged, in any capitals
- [x] A note that is exactly a placeholder, such as `test`, is flagged; a
      longer note that contains one, such as `test drive fee`, stays meaningful
- [x] Note quality never removes a row
- [x] `None` and non-text input do not raise
