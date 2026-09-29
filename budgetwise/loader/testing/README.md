# loader/testing

**Unassigned** · domain reviewer Zeyad

## Required cases

- [ ] Both real CSVs in `data/raw/` load without error
- [ ] Row count matches — 15,900 and 15,836
- [ ] First yielded line number is 2, not 1 or 0
- [ ] A file with a UTF-8 BOM gives a clean `transaction_id` key
- [ ] Missing file raises `FileNotFoundError` naming the path
- [ ] Header missing `amount` raises `ValueError` naming `amount`
- [ ] A row with six fields instead of nine is still yielded
- [ ] A blank final line does not produce an empty row

## Fixtures

`fixtures/malformed_rows.csv` — a small hand-written file holding a short row, a
blank line, and a row with an embedded comma inside quotes. Keep it under twenty
lines so the expected output can be checked by eye.

## Run

```bash
python -m unittest discover
```

A run collecting 0 tests is not a pass.
