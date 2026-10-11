# cleaning/locations/implementation
# cleaning/locations/implementation

Henrietta · `P2.6` · domain reviewer Sarah

## What this does

`parser.py` provides one public function:

```python
normalize_location(raw: str | None) -> tuple[str, str | None]
```

| Situation | Returns |
|---|---|
| Already the standard name | `("Pune", None)` |
| Changed: case, abbreviation, or extra spaces | `("Pune", "LOCATION_NORMALIZED")` |
| Missing: `None`, `""`, whitespace only, or `N/A` | `("Unknown", "LOCATION_UNKNOWN")` |
| Unknown: not in the mapping | `("Unknown", "LOCATION_UNKNOWN")` |

It always returns a usable name. It never returns `None` as the location and never drops a row.

## Mapping

The mapping is a dictionary inside `parser.py`. It covers 10 cities, each in full and as a three-letter abbreviation:

```
Ahmedabad (AHM)   Bangalore (BAN)   Chennai (CHE)   Delhi (DEL)     Hyderabad (HYD)
Jaipur (JAI)      Kolkata (KOL)     Lucknow (LUC)   Mumbai (MUM)    Pune (PUN)
```

Lookups ignore case, so `PUNE`, `pune` and `Pune` all match.

## How it works

1. `None`, `""`, or whitespace only → `Unknown` + `LOCATION_UNKNOWN`.
2. Strip spaces and lowercase the value.
3. `n/a` → `Unknown` + `LOCATION_UNKNOWN`.
4. Found in the mapping → return the standard name. If the raw value differs from it in any way, including extra spaces, also return `LOCATION_NORMALIZED`. If it is identical, the reason is `None`.
5. Not found → `Unknown` + `LOCATION_UNKNOWN`, so the log shows what was missed.

