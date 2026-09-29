# cleaning/dates/implementation

Bahareh · `P2.1` · domain reviewer Zeyad

## Write this

```python
parse_date(raw: str) -> tuple[str | None, str | None]
    success → ("2023-07-14", None)
    failure → (None, "reason_code")
```

## Must handle — counts are from the real dataset

| Shape | Count | Rule |
|---|---|---|
| `YYYY-MM-DD` | 6,091 | pass through after validating |
| `MM/DD/YYYY` | 4,676 | slash + ambiguous → month first |
| `DD-MM-YY` | 3,044 | hyphen + 2-digit year → day first |
| `DD-MM-YYYY` | 1,603 | day first |
| blank | 486 | → `(None, "missing_date")` |

## The ambiguity rule, exactly as §4.5 states it

> "For ambiguous numeric dates where both the day and month are ≤12, interpret
> the date using MM/DD/YYYY for slash-separated dates and DD-MM-YY for
> hyphen-separated two-digit-year dates."

So the **separator decides**, not the values:

- `07/08/2023` → `2023-07-08` — July 8th
- `07-08-23` → `2023-08-07` — August 7th

Getting this backwards silently shifts thousands of rows into the wrong month
and every monthly total is wrong. Test both.

## Rules

- Never raise. Every input returns a tuple.
- Unknown shape → `(None, "unrecognized_date_format")`
- Valid shape, impossible date such as `31/02/2023` → `(None, "impossible_date")`
- Two-digit years: `22` means 2022. The data spans 2021–2024.

## Do not

- Read files or print — `pipeline/` and `interface/` do that
- Write to the log yourself — return the reason, the pipeline records it
- Import pandas or numpy — violates §2

## Use

`datetime.datetime.strptime` from the standard library, inside `try`/`except`.
