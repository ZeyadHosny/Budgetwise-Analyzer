# cleaning/dates

Parses every date in the raw data into a single standard format.

| | |
|---|---|
| **Responsible** | Bahareh |
| **Domain reviewer** | Sarah (`P1.1`) · Zeyad (`P2.1`) |
| **PR approval** | Zeyad or Patrick — see `CONTRIBUTING.md` |
| **Tasks** | `P1.1` profiling · `P2.1` implementation |
| **Status** | Not started |

## 1. What this folder does

Converts a raw date string into `YYYY-MM-DD`, or reports why it could not.
It never raises and never guesses silently — an unparseable date returns `None`
with a reason code.

The main dataset contains five date shapes:

| Shape | Count | Example |
|---|---|---|
| `YYYY-MM-DD` | 6,091 | `2023-07-14` |
| `MM/DD/YYYY` | 4,676 | `07/14/2023` |
| `DD-MM-YY` | 3,044 | `03-04-22` |
| `DD-MM-YYYY` | 1,603 | `14-07-2023` |
| blank | 486 | |

## 2. How other modules use it

```python
from budgetwise.cleaning.dates import parse_date

parsed, reason = parse_date("03-04-22")
if parsed is None:
    log.record(line, "date", reason, raw="03-04-22")
```

Only `pipeline/` calls this.

## 3. What it produces

| Input | Returns | Reason |
|---|---|---|
| `2023-07-14` | `"2023-07-14"` | — |
| `07/14/2023` | `"2023-07-14"` | — |
| `07/08/2023` | `"2023-07-08"` | — slash + ambiguous → `MM/DD/YYYY` |
| `03-04-22` | `"2022-04-03"` | — hyphen + 2-digit year → `DD-MM-YY` |
| `14-07-2023` | `"2023-07-14"` | — |
| `""` | `None` | `missing_date` |
| `14th July` | `None` | `unrecognized_date_format` |
| `31/02/2023` | `None` | `impossible_date` |

Rows returning `None` are excluded from date-based analysis but still count
toward category totals (§4.5).

## 4. Requirements and tasks covered

| Requirement | Source | Task |
|---|---|---|
| Parse and standardize multiple date formats | §4.1 | `P2.1` |
| Convert all valid dates to `YYYY-MM-DD` | §4.5 | `P2.1` |
| Slash + ambiguous → `MM/DD/YYYY` | §4.5 | `P2.1` |
| Hyphen + two-digit year → `DD-MM-YY` | §4.5 | `P2.1` |
| Unparseable dates logged and excluded from date-based analysis | §4.5 | `P2.1` |
| Missing dates logged and excluded, may still count in category totals | §4.5 | `P2.1` |
| Unrecognized formats logged and skipped, never crash | §4.5 | `P2.1` |
| Document the date convention in the report | §4.5 | `P4.4` |

## 5. Folders

| Folder | Contents |
|---|---|
| `implementation/` | `parser.py`, `formats.py` |
| `testing/` | `test_parser.py`, `fixtures/date_cases.csv` |
| `supplementary/` | `date_format_findings.md`, `ambiguity_decision.md` |

## 6. Done when

- [ ] All five shapes above parse correctly
- [ ] Both ambiguity rules covered by tests
- [ ] Blank and junk input return `None` with the right reason code
- [ ] Never raises, for any input
- [ ] `date_format_findings.md` written — report material
