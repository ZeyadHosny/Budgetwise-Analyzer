# Category Cleaning

This feature cleans and standardizes transaction category values into a fixed set of approved categories.

## Responsibility

| Item | Details |
|---|---|
| Responsible | Henrietta |
| Domain reviewers | Bahareh (`P1.2`) and Sarah (`P2.2`) |
| PR approval | Zeyad or Patrick |
| Tasks | `P1.2` profiling and `P2.2` implementation |
| Status | Implemented and under review |

## Purpose

The raw dataset contains category values with:

- different capitalization
- spelling mistakes
- abbreviations
- extra spaces
- missing values

These values are converted into approved category names. Examples:

```
FOOD    -> Food
Fod     -> Food
Rentt   -> Rent
Traval  -> Transportation
Helth   -> Healthcare
Misc    -> Other
```

Missing or blank categories are kept in the dataset and mapped to `Uncategorized`.

## Approved Categories

The 14 approved categories:

```
Food            Rent            Transportation   Entertainment
Utilities       Education       Healthcare       Savings
Other           Freelance       Investment       Bonus
Salary          Uncategorized
```

## Category Mapping

The raw-to-normalized category mapping is stored in:

```
config/category_mapping.csv
```

It covers all 46 nonblank category variants found in the raw dataset. The mapping is closed, so unknown values are never passed through unchanged.

### Reference

The category variants and counts come from Bahareh's Phase 1 category profiling (`P1.2`)
## Public Function

```python
from budgetwise.cleaning.categories import normalize_category

normalize_category(raw: str | None) -> tuple[str, str | None]
```

The function returns `(normalized_category, reason_code)`:

| Situation | Returns |
|---|---|
| Value is already the approved name (`"Food"`) | `("Food", None)` |
| Value was changed: case, spelling, abbreviation, or extra spaces | `("Food", "CATEGORY_NORMALIZED")` |
| Value is `None`, `""`, or whitespace only | `("Uncategorized", "CATEGORY_UNCATEGORIZED")` |
| Value is not in the mapping | `("Uncategorized", "unknown_category")` |

The function always returns a usable category name and never causes a row to be dropped.

## Reason Codes

| Reason Code | Meaning |
|---|---|
| `CATEGORY_NORMALIZED` | The category was corrected or standardized, including removing extra spaces |
| `CATEGORY_UNCATEGORIZED` | The category was missing or blank |
| `unknown_category` | The value was not found in the approved mapping |

The cleaning pipeline (`budgetwise/pipeline/implementation/runner.py`) writes these codes to `output/logs/errors.log` in lowercase (`category_normalized`, `category_uncategorized`, `unknown_category`).


## Implementation Update

Whitespace handling was corrected so values with extra spaces (for example `" Food "`) are recorded as `CATEGORY_NORMALIZED`.

## Testing

The tests cover:

- all 46 profiled nonblank variants (capitalization, spelling mistakes, abbreviations)
- extra spaces
- missing values: `""`, `"   "`, and `None`
- unknown categories

Run from the project root:

```bash
python -m unittest budgetwise.cleaning.categories.testing.test_parser -v
```

Expected result: 51 tests, all passing.

## Project Connection

The category work is completed in two stages:

```
P1.2 -> profile and organize raw category values (Bahareh)
P2.2 -> implement category normalization (Henrietta)
```

The category variants identified during `P1.2` are used to build the normalization rules for `P2.2`.