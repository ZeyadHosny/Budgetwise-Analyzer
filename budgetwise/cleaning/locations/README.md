# Location Cleaning

Cleans raw location values and maps each one to a single standard city name.

## Responsibility

| Item | Details |
|---|---|
| Responsible | Henrietta |
| Domain reviewer | Sarah |
| PR approval | Zeyad or Patrick |
| Tasks | `P1` location profiling (Bahareh) and `P2.6` implementation |
| Status | Implemented and under review |

## Purpose

The raw dataset's `location` column has 42 distinct values. Each city appears in up to four forms:

- title case: `Pune`
- uppercase: `PUNE`
- lowercase: `pune`
- three-letter abbreviation: `PUN`

Some rows also have a blank value or `N/A`. Values can also carry extra spaces, such as `" Pune "`.

This module maps every variant to one standard city name. It returns a reason code whenever the value was changed or could not be identified.



### How it works

1. Blank, whitespace-only, and `None` values return `Unknown`.
2. The value is stripped of surrounding spaces and lowercased for lookup.
3. `n/a` returns `Unknown`.
4. Recognized values return the standard city name. If the original value differs from the standard name in any way, the reason code is `LOCATION_NORMALIZED`. This includes capitalization, abbreviations, and whitespace.
5. Anything else returns `Unknown` with `LOCATION_UNKNOWN`, so it shows up in the error log instead of passing through silently.

## Mapping

The mapping is closed. Unrecognized values are never passed through unchanged.

| Standard name | Accepted variants (case-insensitive, spaces trimmed) |
|---|---|
| Ahmedabad | `Ahmedabad`, `AHMEDABAD`, `ahmedabad`, `AHM` |
| Bangalore | `Bangalore`, `BANGALORE`, `bangalore`, `BAN` |
| Chennai | `Chennai`, `CHENNAI`, `chennai`, `CHE` |
| Delhi | `Delhi`, `DELHI`, `delhi`, `DEL` |
| Hyderabad | `Hyderabad`, `HYDERABAD`, `hyderabad`, `HYD` |
| Jaipur | `Jaipur`, `JAIPUR`, `jaipur`, `JAI` |
| Kolkata | `Kolkata`, `KOLKATA`, `kolkata`, `KOL` |
| Lucknow | `Lucknow`, `LUCKNOW`, `lucknow`, `LUC` |
| Mumbai | `Mumbai`, `MUMBAI`, `mumbai`, `MUM` |
| Pune | `Pune`, `PUNE`, `pune`, `PUN` |
| Unknown | blank (931 rows), `N/A` (331 rows), whitespace only, `None`, any unrecognized value |

That's 10 cities × 4 variants plus blank and `N/A`, which gives the 42 profiled values.

### Reference

The variants above come from the Phase 1 location profiling in Bahareh's Phase 1 report.

## Reason Codes

| Reason code | Meaning |
|---|---|
| `LOCATION_NORMALIZED` | A recognized location was changed to its standard name (capitalization, abbreviation, or surrounding spaces) |
| `LOCATION_UNKNOWN` | The location was missing, blank, `N/A`, or not recognized; set to `Unknown` |
| `None` | The value was already the standard name; nothing to log |


## Testing

Tests are in `testing/test_parser.py`:

- `test_all_profiled_location_variants`: all 42 profiled values, checked with `subTest` and an assertion that exactly 42 cases are listed
- `test_location_with_spaces`: `" Pune "` → `LOCATION_NORMALIZED`
- `test_missing_spaces`: whitespace only → `Unknown`
- `test_missing_none`: `None` → `Unknown`
- `test_unknown_location`: unrecognized value → `Unknown`

Run from the project root:

```bash
python -m unittest budgetwise.cleaning.locations.testing.test_parser -v
```
