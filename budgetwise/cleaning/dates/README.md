# cleaning/dates

Parses every date in the raw data into a single standard format.

| | |
|---|---|
| **Responsible** | Sarah |
| **Domain reviewer** | Henrieta (`P2.1`) |
| **PR approval** | Zeyad or Patrick. See `CONTRIBUTING.md` |
| **Tasks** | `P2.1` implementation. Profiling is Bahareh's Phase 1 report (`P1.1`) |
| **Status** | First version merged from `feat/p2-1-cleaning-dates`. Review correction S02 and this README merged in #12 |

## 1. What this folder does

Converts a raw date string into `YYYY-MM-DD`, or reports why it could not.
It never raises and never guesses. A date that cannot be read returns `None`
with a reason code.

The main dataset contains four date formats, plus blanks:

| Format | Count | Example | Read as |
|---|---|---|---|
| `YYYY-MM-DD` | 6,091 | `2023-07-14` | already standard |
| `MM/DD/YYYY` | 4,676 | `07/14/2023` | month first |
| `DD-MM-YY` | 3,044 | `03-04-22` | day first |
| `DD-MM-YYYY` | 1,603 | `14-07-2023` | day first |
| blank | 486 | | missing |

The separator decides how a date is read, never the numbers in it:

- A **slash** date is always month first (required by section 4.5).
- A **hyphen** date with a two-digit year is always day first (required by
  section 4.5).
- A **hyphen** date with a four-digit year is day first. This is the team's
  convention. The data supports it: the first number is above 12 in 953 of
  these rows and the second number never is.

The formats are strict about digit counts. `8/5/2022` and `2022/08/05` match
no format and are reported, not guessed.

## 2. How other modules use it

```python
from budgetwise.cleaning.dates import parse_date

parsed, reasons = parse_date("03-04-22")     # ("2022-04-03", ["DATE_NORMALIZED"])
for reason in reasons:
    log.record(line, "date", reason, "03-04-22")
```

Only `pipeline/` calls this.

Everything the folder exports:

| Name | Signature | Returns |
|---|---|---|
| `parse_date` | `(raw_date)` | `(date, reasons)`. `date` is `'YYYY-MM-DD'` text or `None`. `reasons` is a **list**, empty when there is nothing to report |
| `find_date_format` | `(raw)` | the format name a raw date matches, or `None` |
| `is_ambiguous_date` | `(raw)` | `True` if a real slash or hyphen date has day and month both from 1 to 12 |
| `DATE_NORMALIZED`, `MISSING_DATE`, `INVALID_DATE` | | reason codes |

`find_date_format` and `is_ambiguous_date` are only used to produce the
report evidence. Parsing does not depend on them.

## 3. What it produces

| Input | Date returned | Reasons |
|---|---|---|
| `2023-07-14` | `"2023-07-14"` | none |
| `07/14/2023` | `"2023-07-14"` | `DATE_NORMALIZED` |
| `07/08/2023` | `"2023-07-08"` | `DATE_NORMALIZED`. Slash, so month first |
| `03-04-22` | `"2022-04-03"` | `DATE_NORMALIZED`. Hyphen, so day first |
| `14-07-2023` | `"2023-07-14"` | `DATE_NORMALIZED` |
| `" 2023-07-14 "` (outer spaces) | `"2023-07-14"` | `DATE_NORMALIZED`. Spaces removed |
| `""`, spaces, `N/A`, `None` | `None` | `MISSING_DATE` |
| `14th July`, `8/5/2022` | `None` | `INVALID_DATE`. No format matches |
| `31-02-23`, `31/02/2023` | `None` | `INVALID_DATE`. Right shape, not a real date |
| a number or other non-text value | `None` | `INVALID_DATE` |

Only a date that is **exactly** `YYYY-MM-DD`, with nothing around it, returns
no reason, because nothing was changed. The same date with spaces at either
end, such as `" 2023-07-14 "`, returns `"2023-07-14"` with `DATE_NORMALIZED`,
because the spaces were removed.

An invalid or missing date never removes a row. `parse_date` only returns
`None`; the pipeline keeps the row, leaves it out of date-based analysis such
as monthly totals and date-range loading, and still counts it toward category
totals (section 4.5).

**Ambiguous dates.** A date is ambiguous when its day and month are both 12
or less, so it could be read either way. The rules above settle every one.
`is_ambiguous_date` counts them for the report. It only counts dates that
`parse_date` accepts, so `00/05/2023` is not counted: it is not a date at all.

**Reason codes, still to agree with Patrick.** This folder returns
`DATE_NORMALIZED`, `MISSING_DATE` and `INVALID_DATE`. The pipeline writes them
to the log in lowercase. Patrick's `errorlog` list has `missing_date`,
`unrecognized_date_format` and `impossible_date`. Lowercasing makes
`MISSING_DATE` match, but it cannot make the other names match:
`date_normalized` has no entry in his list, and `invalid_date` covers what his
list splits into two codes. One vocabulary has to be agreed and recorded
(review S08, `docs/decisions.md` D11). Until then these codes are unchanged.

Expected on the main dataset: 15,414 dates parsed, 486 missing, 0 invalid.

## 4. Requirements and tasks covered

| Requirement | Source | Task |
|---|---|---|
| Parse and standardize multiple date formats | section 4.1 | `P2.1` |
| Convert all valid dates to `YYYY-MM-DD` | section 4.5 | `P2.1` |
| Slash and ambiguous: read as `MM/DD/YYYY` | section 4.5 | `P2.1` |
| Hyphen and two-digit year: read as `DD-MM-YY` | section 4.5 | `P2.1` |
| Unparseable dates logged and excluded from date-based analysis | section 4.5 | `P2.1` |
| Missing dates logged and excluded, may still count in category totals | section 4.5 | `P2.1` |
| Unrecognized formats logged and skipped, never crash | section 4.5 | `P2.1` |
| Document the date convention in the report | section 4.5 | `P4.4` |

Baselines come from Bahareh's Phase 1 profiling report.

## 5. Folders

| Folder | Contents |
|---|---|
| `implementation/` | `parser.py` |
| `testing/` | `test_parser.py`, 24 tests |
| `supplementary/` | `date_evidence.md` |

Run the tests from the repository root:

```bash
python -m unittest budgetwise.cleaning.dates.testing.test_parser -v
```

Four of the 24 tests use the full dataset and are skipped if the CSV is not
in `data/raw/`.

## 6. Done when

- [x] All four formats and blanks are handled correctly
- [x] Both required ambiguity rules, and the team's third, covered by tests
- [x] Blank and junk input return `None` with the right reason code
- [x] Never raises, for any input
- [x] Invalid dates are never counted as ambiguous
- [x] `date_evidence.md` written. It is report material
