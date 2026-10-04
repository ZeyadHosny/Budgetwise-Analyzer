# Notes quality evidence

`classify_note_quality()` run on all 15,900 raw rows of `budgetwise_finance_dataset.csv`.

| Quality flag | Reason code | Result | Phase 1 |
|---|---|---|---|
| meaningful | none | 10,072 | 10,072 |
| low_information | NOTES_LOW_INFORMATION | 3,007 | 3,007 |
| missing (blank) | NOTES_MISSING | 2,335 | 2,335 |
| not_available (N/A) | NOTES_MISSING | 486 | 486 |

Every note is returned unchanged. The six known placeholders are
`...`, `!!!`, `xyz123`, `test`, `misc` and `asdfgh`.
