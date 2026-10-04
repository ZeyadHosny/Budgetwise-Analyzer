# notes

**Owner:** Sarah · **Task:** P2.7

Classifies each note's quality. The note text is never changed.

```python
from budgetwise.cleaning.notes import classify_note_quality

classify_note_quality("Electricity bill")  # ("Electricity bill", "meaningful", [])
classify_note_quality("xyz123")            # ("xyz123", "low_information", ["NOTES_LOW_INFORMATION"])
classify_note_quality("")                  # ("", "missing", ["NOTES_MISSING"])
classify_note_quality("N/A")               # ("N/A", "not_available", ["NOTES_MISSING"])
```

Known placeholders: `...`, `!!!`, `xyz123`, `test`, `misc`, `asdfgh`. The whole
note is compared, so "test drive fee" is meaningful.

| Quality | Result on 15,900 rows | Phase 1 |
|---|---|---|
| meaningful | 10,072 | 10,072 |
| low_information | 3,007 | 3,007 |
| missing | 2,335 | 2,335 |
| not_available | 486 | 486 |

Tests: `testing/test_note_quality.py` (12).
