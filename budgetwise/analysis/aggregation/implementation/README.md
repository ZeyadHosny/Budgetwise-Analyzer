# analysis/aggregation/implementation

Henrieta · `P3.1` · domain reviewer Zeyad

## Write these

```python
totals_by_category(transactions, kind=None) -> dict[str, float]
totals_by_month(transactions, kind=None)    -> dict[tuple[str, str], float]
unique_categories(transactions)             -> set[str]
count_by_category(transactions)             -> dict[str, int]
```

`kind` is `"expense"`, `"income"`, or `None` for both.

## The rule that is easy to get wrong

A transaction with no date **still counts toward its category total**, but must
not appear in any monthly total. §4.5:

> "Missing date: Log and exclude the row from date-based analysis (it may still
> count toward category totals)."

So `totals_by_category` includes it and `totals_by_month` skips it. The two
functions therefore do *not* sum to the same figure, and that is correct. Say so
in `data_structure_choices.md` before someone reports it as a bug.

## Use each structure deliberately

§4.2 names four structures and the workbook note for `P3.1` says to demonstrate
each explicitly. Do not use a dict where a set is the honest choice:

- `unique_categories` returns a **set** — membership is the whole point
- month keys are **tuples** — `("2023", "07")`, immutable and sortable
- totals are **dicts** — accumulate by key
- transactions arrive as a **list** — order preserved

`collections.defaultdict` and `collections.Counter` are standard library and
fair game.

## Do not

- Sum a signed amount. Use `kind` to select, and `amount` for the magnitude.
- Re-read files — you receive objects from `pipeline/`
- Import pandas or numpy — violates §2
