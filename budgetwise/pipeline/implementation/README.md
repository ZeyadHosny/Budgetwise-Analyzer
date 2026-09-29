# pipeline/implementation

Sarah with Zeyad · `G2` · reviewed by all team

## Write these

```python
run(path: str, *, start=None, end=None, category=None) -> LoadResult
    Loads, cleans, and builds objects. Optional filters for the menu.

LoadResult
    .transactions  list[Transaction]
    .counts        dict[str, int]
    .timings       dict[str, float]
```

## Order is mandatory

```
1. loader.load_rows(path)          raw row + line number
2. cleaning.rows.is_duplicate      ON THE RAW ROW — §4.5 requires this first
3. cleaning.dates.parse_date
4. cleaning.amounts.parse_amount
5. cleaning.categories.normalize
6. cleaning.rows.has_required_fields
7. models.Transaction(...)
```

Step 2 cannot move. §4.5: *"Duplicate detection must be performed on the original
raw rows before data normalization."* Normalizing first merges `FOOD` and `Food`
and manufactures duplicates that do not exist.

## Rules

- Never raise on row content. A bad row is logged and skipped.
- Every skip, correction, and flag goes to `errorlog` with its line number.
- Count as you go. Do not re-scan afterwards to produce the numbers.
- Time `load` and `clean` separately — §5 asks for both.

## Do not

- Print — `interface/` does that
- Read files directly — `loader/` does that
- Import pandas or numpy — violates §2
