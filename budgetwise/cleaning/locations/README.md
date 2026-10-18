# Location cleaning

## Interface

```python
from budgetwise.cleaning.locations import normalize_location

normalize_location(raw: str | None) -> tuple[str, str | None]
```

| Input | Returns |
|---|---|
| Already a standard name, e.g. `"Pune"` | `("Pune", None)` |
| A known variant, e.g. `"PUNE"`, `"PUN"`, `" Pune "` | `("Pune", "LOCATION_NORMALIZED")` |
| `None`, `""`, whitespace only, `N/A`, or not recognized | `("Unknown", "LOCATION_UNKNOWN")` |

The function always returns a usable name and never drops a row. The pipeline
writes the reason codes to `output/logs/errors.log` in lowercase.

## Mapping

The mapping is a dictionary in `implementation/parser.py`. Lookups ignore case
and surrounding spaces. Each city is accepted in full or as a three-letter code:

```
Ahmedabad (AHM)   Bangalore (BAN)   Chennai (CHE)   Delhi (DEL)     Hyderabad (HYD)
Jaipur (JAI)      Kolkata (KOL)     Lucknow (LUC)   Mumbai (MUM)    Pune (PUN)
```

`Bengaluru`, the city's official name, also maps to `Bangalore`. The synthetic
dirty dataset uses it on 1,539 raw rows and never uses `Bangalore` itself, so
without it the city would be missing from every location count.

On the synthetic dirty dataset, every nonblank value is now recognized. The 686
retained `Unknown` rows are all blank.

## Files

| Folder | Contents |
|---|---|
| `implementation/` | `parser.py` |
| `testing/` | `test_parser.py` |

## Tests

6 tests cover all 42 profiled values, `Bengaluru`, whitespace, missing values
and unknown values.

```bash
python -m unittest budgetwise.cleaning.locations.testing.test_parser -v
```
