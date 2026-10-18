# Category cleaning

## Interface

```python
from budgetwise.cleaning.categories import normalize_category

normalize_category(raw: str | None, transaction_type: str | None = None) -> tuple[str, str | None]
```

| Input | Returns |
|---|---|
| Already an approved name, e.g. `"Food"` | `("Food", None)` |
| A known variant, e.g. `"FOOD"`, `"Foood"`, `" Food "` | `("Food", "CATEGORY_NORMALIZED")` |
| An `Other Income` variant on an income row | `("Other", "CATEGORY_NORMALIZED")` |
| `None`, `""` or whitespace only | `("Uncategorized", "CATEGORY_UNCATEGORIZED")` |
| Not in the mapping | `("Uncategorized", "unknown_category")` |

The function always returns a usable name and never drops a row. The pipeline
writes the reason codes to `output/logs/errors.log` in lowercase.

## Approved categories

```
Food        Rent        Transportation   Entertainment   Utilities
Education   Healthcare  Savings          Other           Freelance
Investment  Bonus       Salary           Uncategorized
```

`Travel` maps to `Transportation`, `Health` to `Healthcare`, and `Misc`,
`Others` and `Other Income` to `Other` (decision `D04`). Income and expense
totals are always calculated separately, so income `Other` never mixes with
expense `Other`. `Freelance` and `Investment` have no rows in the synthetic
dirty dataset.

## Mapping

The mapping is data, not code: `config/category_mapping.csv` holds
`raw,normalized` pairs and is loaded once at import. Lookups ignore case and
surrounding spaces. Attaching the CSV meets §4.5's requirement to include the
mapping in the report.

| Dataset | Nonblank variants | Covered |
|---|---:|---|
| `budgetwise_finance_dataset.csv` | 46 | all 46 |
| `budgetwise_synthetic_dirty.csv` | 212 | all but `ent` |

The synthetic dirty dataset added 192 variants (1,634 raw rows, 1,540
retained). A variant is mapped when it differs from one approved name by a
single letter and from every other name by at least three. 191 are mapped:
166 in the CSV and 25 `Other Income` variants in `parser.py`. The pipeline
passes the transaction type, so `Other Income` becomes `Other` only on income
rows; on an expense row it stays `Uncategorized`.

Two cases stay `Uncategorized`, with the reason logged:

| Value | Rows (raw / retained) | Reason |
|---|---|---|
| `ent` | 19 / 18 | One letter from `Rent`, but also the start of `Entertainment`; nothing in the rows shows which was meant |
| blank | 158 / 154 | Missing value |

Every added variant, with its counts, is listed in
`supplementary/dirty_variant_mapping.md`.

## Tests

55 tests cover all 46 variants in the original dataset, the new spelling
variants, `Other Income` on income and expense rows, the ambiguous `ent`, whitespace, missing values and
unknown values.

```bash
python -m unittest budgetwise.cleaning.categories.testing.test_parser -v
```
