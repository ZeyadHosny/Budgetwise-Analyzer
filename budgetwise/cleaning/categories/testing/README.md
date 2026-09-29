# cleaning/categories/testing

Henrieta · domain reviewer Sarah

## Required cases

- [ ] `Food`, `FOOD`, `food`, `Foods`, `Fod`, `Foodd` all → `Food`
- [ ] `Rent`, `RENT`, `rent`, `Rentt`, `Rnt` all → `Rent`
- [ ] `Travel`, `TRAVEL`, `Traval`, `Travl` all → `Travel`
- [ ] `""` → `("Uncategorized", "missing_category")`
- [ ] `"   "` → `("Uncategorized", "missing_category")`
- [ ] `Wobble` → `("Uncategorized", "unknown_category")`
- [ ] **Every one of the 47 raw variants maps to something** — not one falls through
- [ ] The returned name is always in the canonical set

The completeness test matters most. Write it as a loop over the distinct raw
values and assert each result is in the canonical set — that is the only way to
prove the mapping is genuinely closed.

## Fixtures

`fixtures/category_variants.csv` — all 47 raw strings with their expected
normalized name. Doubles as the table the report needs.

## Run

```bash
python -m unittest discover
```

A run collecting 0 tests is not a pass.
