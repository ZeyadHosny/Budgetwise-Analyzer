# cleaning/dates/testing

Bahareh · domain reviewer Zeyad

## Required cases

- [ ] `2023-07-14` → `2023-07-14`
- [ ] `07/14/2023` → `2023-07-14`
- [ ] `14-07-2023` → `2023-07-14`
- [ ] `07/08/2023` → `2023-07-08` — slash ambiguity, month first
- [ ] `07-08-23` → `2023-08-07` — hyphen ambiguity, day first
- [ ] `""` → `(None, "missing_date")`
- [ ] `"   "` → `(None, "missing_date")` — whitespace counts as blank
- [ ] `14th July` → `(None, "unrecognized_date_format")`
- [ ] `31/02/2023` → `(None, "impossible_date")` — not a crash
- [ ] Never raises, for any input including `None` and numbers

The two ambiguity cases are the ones worth most. They are the only rules where a
wrong answer looks completely normal and quietly corrupts every monthly figure.

## Fixtures

`fixtures/date_cases.csv` — one row per case above, with the expected output
beside it, so the table can be read as documentation.

## Run

```bash
python -m unittest discover
```

A run collecting 0 tests is not a pass.
