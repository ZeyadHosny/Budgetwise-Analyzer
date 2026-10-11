# cleaning/categories/implementation

Henrietta · `P2.2` · domain reviewer Sarah

## What this does

`parser.py` provides one public function:

```python
normalize_category(raw: str | None) -> tuple[str, str | None]
```

| Situation | Returns |
|---|---|
| Already the approved name | `("Food", None)` |
| Changed: case, spelling, abbreviation, or extra spaces | `("Food", "CATEGORY_NORMALIZED")` |
| Missing: `None`, `""`, or whitespace only | `("Uncategorized", "CATEGORY_UNCATEGORIZED")` |
| Unknown: not in the mapping | `("Uncategorized", "UNKNOWN_CATEGORY")` |

It always returns a usable name. It never returns `None` as the category and never drops a row.

## The mapping lives in config, not in code

`config/category_mapping.csv` holds `raw,normalized` pairs for all 46 nonblank variants found in the raw dataset. `_load_mapping()` reads it once when the module is imported. Keys are stripped and lowercased, so lookups ignore case.

Keeping the mapping as data rather than a dictionary in the code means §4.5's "include this mapping in your report" is met by attaching the CSV file.

## Approved categories

The team chose a closed set of 14 categories:

```
Food, Rent, Transportation, Entertainment, Utilities, Education, Healthcare,
Savings, Other, Freelance, Investment, Bonus, Salary, Uncategorized
```

- `Travel` and its variants map to `Transportation`.
- `Misc` and `Others` map to `Other`.
- `Freelance`, `Bonus`, `Savings`, `Salary`, and `Investment` are kept as their own categories because they appear often in the raw data.
- `Shopping`, from the assignment's example list, is not used because it does not appear in the data.

## How it works

1. `None`, `""`, or whitespace only → `Uncategorized` + `CATEGORY_UNCATEGORIZED`.
2. Strip spaces and lowercase the value, then look it up in the mapping.
3. Found → return the approved name. If the raw value differs from the approved name in any way, including extra spaces, also return `CATEGORY_NORMALIZED`. If it is identical, the reason is `None`.
4. Not found → `Uncategorized` + `UNKNOWN_CATEGORY`, so the log shows what was missed and the mapping can be extended.


## Connection to the pipeline

`budgetwise/pipeline/implementation/runner.py` calls `normalize_category()` on every row. It writes the reason codes to `output/logs/errors.log` in lowercase and counts normalizations (`categories_normalized`) for the §5 summary.