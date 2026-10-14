# interface/charts/testing

Henrietta · domain reviewer Sarah

## Cases covered

- [x] The largest value gets exactly `width` stars
- [x] A half-size value gets half the stars
- [x] A tiny non-zero value still gets one star
- [x] A zero value gets no stars but keeps its label
- [x] An empty dict returns an empty string
- [x] Equal values give equal bars; all-zero values cause no division error
- [x] Tuple month keys render as `2023-07`
- [x] Every line is the same length, numbers right-aligned with commas
- [x] Dictionary order kept by default; `sort_by_value` puts the largest first
- [x] Title line, long-label shortening, and `width < 1` rejected
- [x] Returns a string

## Run

From the project root:

```bash
python -m unittest budgetwise.interface.charts.testing.test_bar_chart -v
```

Expected result: `Ran 16 tests ... OK`.
