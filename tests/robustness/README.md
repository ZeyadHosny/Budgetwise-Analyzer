# Robustness Tests

These tests check that the program does not crash on bad input.

Each test cleans a small sample file and confirms that:

- the program returns a result instead of an error
- every input row is counted as valid, skipped or duplicate
- every kept row has a valid amount, category and date

## What is tested

| Area | Examples |
|---|---|
| Files | Missing, empty, header only, wrong columns, no valid rows |
| Rows | Too few or too many fields, blank rows, duplicates, special characters |
| Dates | `31/02/2023`, `99-99-99`, `14th July` |
| Amounts | `abc`, `₹₹5`, `999999999`, `-50`, `--5` |
| Full dataset | All 15,900 rows |

## Known issues

Four tests are marked as expected failures. They describe problems that still
need fixing in other parts of the program:

| Problem | Where |
|---|---|
| Files saved as "CSV UTF-8" in Excel are rejected | Loader |
| Rows with extra fields are kept with wrong values | Loader |
| Blank lines are counted as rows | Loader |
| `--5` is accepted as an amount | Amounts |

When a problem is fixed, remove `@unittest.expectedFailure` from its test.

## Run

```bash
python -m unittest tests.robustness.test_hostile_input -v
```

Expected result: 21 tests, OK (expected failures=4).