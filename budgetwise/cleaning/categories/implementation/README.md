# cleaning/categories/implementation

Henrieta · `P2.2` · domain reviewer Sarah

## Write this

```python
normalize(raw: str) -> tuple[str, str | None]
    success → ("Food", None)
    missing → ("Uncategorized", "missing_category")
    unknown → ("Uncategorized", "unknown_category")
```

Always returns a usable name. Never `None`, never a dropped row.

## The mapping lives in config, not in code

`config/category_mapping.csv` holds `raw,normalized` pairs. Load it once. Keeping
it as data rather than a dictionary literal means §4.5's "include this mapping in
your report" is satisfied by attaching a file everyone can read.

## A problem to raise at G1

The assignment's example canonical set is:

> Food, Rent, Transportation, Entertainment, Shopping, Utilities, Healthcare,
> Education, Salary, Investment, Other, Uncategorized

The raw data also contains **Freelance (490), Bonus (442), Savings (110)** and
**Misc**, which have no home in that list. It is an example, not a mandate — but
whatever set the team picks must be closed and documented.

Do not decide this alone. It changes every total in the report.

## Rules

- Normalize case and strip whitespace before looking up.
- The mapping is **closed** — no silent pass-through of unknown strings.
- Unknown → `"Uncategorized"` plus `unknown_category`, so the log shows what was
  missed and the mapping can be extended.
- Count normalizations. §5 requires "number of categories normalized".

## Do not

- Guess with fuzzy matching. A documented table is the requirement; a similarity
  score cannot be printed in a report.
- Import pandas or numpy — violates §2.
