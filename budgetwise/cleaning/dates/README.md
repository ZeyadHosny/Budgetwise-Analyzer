# cleaning/dates

Converts every raw date to `YYYY-MM-DD`, or returns `None` with a reason code.

| | |
|---|---|
| **Responsible** | Sarah |
| **Domain reviewer** | Henrietta |
| **Task** | `P2.1`. Profiling from Bahareh's Phase 1 report (`P1.1`) |

## Folder contents

| Folder | File | Holds |
|---|---|---|
| `implementation/` | `parser.py` | the date rules and functions |
| `testing/` | `test_parser.py` | 24 tests |
| `supplementary/` | `date_evidence.md` | counts and evidence for the report |

## Rules

The separator and the length of the year decide how a date is read, never
the numbers in it:

| Format | Count | Read as | Source |
|---|---|---|---|
| `YYYY-MM-DD` | 6,091 | already standard | |
| `MM/DD/YYYY` | 4,676 | month first | section 4.5 |
| `DD-MM-YY` | 3,044 | day first | section 4.5 |
| `DD-MM-YYYY` | 1,603 | day first | team decision D10 |
| blank | 486 | missing | |

A missing or invalid date never removes a row. The pipeline keeps the row,
leaves it out of date-based analysis and still counts it by category.

## Implementation

```python
from budgetwise.cleaning.dates import parse_date

date, reasons = parse_date("03-04-22")    # ("2022-04-03", ["DATE_NORMALIZED"])
```

| Function | Returns |
|---|---|
| `parse_date(raw_date)` | `(date, reasons)`. `date` is `'YYYY-MM-DD'` or `None`; `reasons` is a list, empty if nothing changed |
| `find_date_format(raw)` | the format name a date matches, or `None` |
| `is_ambiguous_date(raw)` | `True` if a valid slash or hyphen date has day and month both 1 to 12. Report counts only |

How `parse_date` works:

1. Blank, `N/A` or `None` returns `missing_date`.
2. The text is matched against four strict patterns, one per format.
3. The match is read with `datetime.strptime`, which rejects impossible dates.
4. A date already exactly `YYYY-MM-DD` returns no reason. Anything converted
   returns `DATE_NORMALIZED`.

| Input | Date | Reason |
|---|---|---|
| `2023-07-14` | `2023-07-14` | none |
| `07/08/2023` | `2023-07-08` | `DATE_NORMALIZED` (slash: month first) |
| `03-04-22` | `2022-04-03` | `DATE_NORMALIZED` (hyphen: day first) |
| `""`, `N/A`, `None` | `None` | `missing_date` |
| `31-02-23` | `None` | `INVALID_DATE` (not a real date) |
| `8/5/2022`, `14th July` | `None` | `INVALID_DATE` (no format matches) |

**Faulty input.** `try/except ValueError` around `strptime` catches impossible
dates. Non-text input returns `INVALID_DATE`. Unrecognised formats are
reported, never guessed. The function never raises.

Only `pipeline/` calls this. Reason codes come from `budgetwise.errorlog.Reason`.

## Testing

| Group | Checks |
|---|---|
| `ValidFormatTests` | each of the four formats converts correctly |
| `AmbiguousDateTests` | slash dates month first, hyphen dates day first; invalid dates never counted as ambiguous |
| `MissingDateTests` | blank, spaces, `N/A` and `None` return `missing_date` |
| `InvalidDateTests` | impossible dates, unknown formats and non-text input return `INVALID_DATE` |
| `FullDatasetTests` | counts on all 15,900 rows match Phase 1 |

```bash
python3 -m unittest budgetwise.cleaning.dates.testing.test_parser -v
```

Run from the repository root. The 4 full-dataset tests are skipped if
`data/raw/budgetwise_finance_dataset.csv` is missing.

## Supplementary

`date_evidence.md` holds the run details, format counts, ambiguous-date
counts and missing dates at each stage, for the report (section 4.5).

Key figures: 9,323 dates converted, 6,091 already standard, 486 missing,
0 invalid. In `DD-MM-YYYY` dates the first number is above 12 in 953 rows and
the second never is, which supports reading them day first.
