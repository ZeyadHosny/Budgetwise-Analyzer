# errorlog

Writes `errors.log` and owns the reason codes every cleaner uses.

| | |
|---|---|
| **Responsible** | Sarah |
| **Domain reviewer** | Henrieta (`P2.4`) |
| **PR approval** | Zeyad or Patrick — see `CONTRIBUTING.md` |
| **Tasks** | `P2.4` |
| **Status** | Not started |

## 1. What this folder does

One place records every row the program skipped, corrected, or flagged, and
one place defines the vocabulary for *why*.

The reason codes matter more than the writer. Four people write cleaning modules
in parallel, and if each invents its own wording the log becomes unsearchable and
the report's counts cannot be produced. The codes are defined here and imported
by all four.

`errors.log` is a filename the assignment mandates exactly (§4.1).

## 2. How other modules use it

```python
from budgetwise.errorlog import ErrorLog, Reason

log = ErrorLog("output/logs/errors.log")
log.record(line=487, field="date", reason=Reason.MISSING_DATE, raw="")
log.record(line=902, field="amount", reason=Reason.SENTINEL_AMOUNT, raw="999999999")
```

All four cleaning modules and `pipeline/` use this.

## 3. What it produces

Lines in `output/logs/errors.log`:

```
line 487  | date     | missing_date              | ""
line 902  | amount   | sentinel_amount           | "999999999"
line 1145 | category | missing_category          | ""
line 2301 | date     | unrecognized_date_format  | "14th July"
line 3044 | row      | duplicate_row             | "T4999,U018,..."
```

And the counts §5 requires, grouped by reason.

## 4. Requirements and tasks covered

| Requirement | Source | Task |
|---|---|---|
| Log skipped, corrected, or flagged rows to `errors.log` with a brief reason | §4.1 | `P2.4` |
| The file is named exactly `errors.log` | §4.1 | `P2.4` |
| Unparseable dates and amounts are logged | §4.5 | `P2.4` |
| Sentinel amounts are logged | §4.5 | `P2.4` |
| Number of corrected / skipped / duplicate records | §5 | `P3.5` |
| Menu option 4 displays the error log | §4.1 | `P3.4` |

## 5. Folders

| Folder | Contents |
|---|---|
| `implementation/` | `logger.py`, `reason_codes.py` |
| `testing/` | `test_logger.py` |
| `supplementary/` | `log_format_spec.md` |

## 6. Done when

- [ ] `reason_codes.py` agreed at `G1` and imported by all four cleaners
- [ ] Every line carries line number, field, reason, and the raw value
- [ ] Counts by reason available for the report
- [ ] The log file is created if the folder is missing
- [ ] Writing 900 duplicate entries does not noticeably slow the run
