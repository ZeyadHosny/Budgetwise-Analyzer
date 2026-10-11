# cleaning/locations/testing
# cleaning/locations/testing

Henrietta · `P2.6` · domain reviewer Sarah

## What is tested

`test_parser.py` checks `normalize_location()` against all 42 location values profiled in the raw dataset, plus edge cases.

| Test | Inputs | Expected result |
|---|---|---|
| `test_all_profiled_location_variants` | All 42 profiled values: 10 cities × (`Pune`, `PUNE`, `pune`, `PUN`), plus `""` and `N/A` | Standard city name, or `Unknown` for `""` and `N/A` |
| `test_location_with_spaces` | `"  Pune  "` | `("Pune", "LOCATION_NORMALIZED")` |
| `test_missing_spaces` | `"   "` | `("Unknown", "LOCATION_UNKNOWN")` |
| `test_missing_none` | `None` | `("Unknown", "LOCATION_UNKNOWN")` |
| `test_unknown_location` | `"UnknownCity"` | `("Unknown", "LOCATION_UNKNOWN")` |

The first test checks each case with `subTest`. It also asserts that exactly 42 cases are listed, so a missing case makes it fail.


## Run

From the project root:

```bash
python -m unittest budgetwise.cleaning.locations.testing.test_parser -v
```


