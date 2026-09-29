# cleaning/rows/implementation

Sarah · `P2.4` · domain reviewer Henrieta

## Write these

```python
is_duplicate(raw_row: dict) -> bool
    True if this exact row has been seen before in this run.

has_required_fields(raw_row: dict) -> tuple[bool, str | None]
    (True, None) or (False, "missing_required_field")
```

## Duplicate means every field identical

§4.5, twice over:

> "A 'duplicate' means a fully identical row. A repeated transaction_id on rows
> that otherwise differ is not a duplicate — do not drop these."
>
> "Duplicate detection must be performed on the original raw rows before data
> normalization."

So the key is the **whole raw row**, not the transaction id:

```python
key = tuple(raw_row[c] for c in COLUMNS)   # all nine, as read
```

Keep a `set` of keys seen — §4.2 asks for sets, and this is the natural use.

## Why the ordering rule exists

`FOOD` and `Food` are different raw strings. After normalization both become
`Food`, and two genuinely different rows look identical. Detecting duplicates
after normalization would delete real transactions. The pipeline calls this
first, before any cleaning.

## Required fields

| Field | Missing → |
|---|---|
| `amount` | reject — there is no transaction without one |
| `transaction_type` | reject — direction is unknowable |
| `date` | **keep** — §4.5 allows it toward category totals |
| `category` | **keep** — becomes `Uncategorized` |
| `payment_mode`, `location`, `notes` | keep — not used in any required output |

Note that `location` and `notes` also contain the literal string `"nan"` in 331
and 486 rows. Treat it as blank, not as a value.

## Do not

- Use `transaction_id` alone as the duplicate key — it produces 1,900 wrong drops
- Normalize before comparing — violates the mandatory ordering
- Import pandas or numpy — violates §2
