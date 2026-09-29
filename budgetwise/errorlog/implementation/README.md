# errorlog/implementation

Sarah · `P2.4` · domain reviewer Henrieta

## Write these

```python
class Reason:            # the shared vocabulary — agree at G1
    MISSING_DATE                = "missing_date"
    UNRECOGNIZED_DATE_FORMAT    = "unrecognized_date_format"
    IMPOSSIBLE_DATE             = "impossible_date"
    MISSING_AMOUNT              = "missing_amount"
    UNRECOGNIZED_AMOUNT_FORMAT  = "unrecognized_amount_format"
    SENTINEL_AMOUNT             = "sentinel_amount"
    MISSING_CATEGORY            = "missing_category"
    UNKNOWN_CATEGORY            = "unknown_category"
    DUPLICATE_ROW               = "duplicate_row"
    MISSING_REQUIRED_FIELD      = "missing_required_field"

class ErrorLog:
    record(line, field, reason, raw)   append one entry
    counts()                          dict of reason → count
    read()                            the lines, for menu option 4
```

## Rules

- The file is named `errors.log`. Not `error.log`, not `errors.txt`. §4.1 fixes it.
- Default location `output/logs/errors.log`. Create the folder if absent.
- One line per event. Keep it greppable.
- Always include the raw value — a log saying a date failed without saying which
  date is not evidence.
- Open the file once and keep the handle. Opening per row on 15,900 rows is slow.

## Why the codes live here

Four cleaners run in parallel. If dates logs `"bad date"` and amounts logs
`"invalid amount format"`, nothing can count them together, and §5 requires
counts of corrected and skipped records. One vocabulary, imported everywhere.

## Do not

- Print to the console — `interface/` does that
- Decide what counts as an error — the cleaners decide, this records
- Import pandas or numpy — violates §2
