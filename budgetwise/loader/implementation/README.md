# loader/implementation

**Unassigned** · no workbook task · interface agreed with Zeyad

## Write these

```python
load_rows(path: str) -> Iterator[tuple[int, dict[str, str]]]
    Yields (line_number, row_dict) for each data row.
    line_number is the real line in the file, starting at 2.

validate_header(fieldnames: list[str]) -> None
    Raises ValueError naming any missing or unexpected column.
```

## Must handle

| Case | Behaviour |
|---|---|
| UTF-8 BOM at the start of the file | Strip it — use `encoding="utf-8-sig"` |
| File does not exist | `FileNotFoundError` naming the path |
| Header missing a column | `ValueError` naming which |
| Row shorter than the header | Yield it; absent keys become `""` |
| Blank trailing line | Skip silently |

The BOM is not hypothetical — both supplied CSVs carry one. Opening with plain
`utf-8` makes the first column name `\ufefftransaction_id`, and every lookup of
`transaction_id` then fails.

## Expected header

```
transaction_id, user_id, date, transaction_type, category,
amount, payment_mode, location, notes
```

## Do not

- Clean, convert, or validate field contents — that is `cleaning/`
- Skip rows for being malformed — the cleaners decide that
- Print anything
- Import pandas or numpy — violates §2

## Use

`csv.DictReader` from the standard library. Yield rather than build a list, so
memory stays flat on a 15,900-row file.
