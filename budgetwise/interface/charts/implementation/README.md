# interface/charts/implementation

Sarah · `P3.4` · domain reviewer Bahareh

## Write this

```python
bar_chart(totals: dict, width: int = 40, title: str = "") -> str
```

Returns the chart as a string. Returning rather than printing means the tests can
assert on it, and `export/` could reuse it.

## Scaling

The largest value gets `width` stars; everything else is proportional:

```python
stars = round(value / max_value * width)
```

Guard the empty case — `max()` on an empty dict raises, and a chart of nothing
should be an empty string.

## Make it line up

| Problem | Fix |
|---|---|
| Ragged labels | pad to the longest, or truncate to a fixed width |
| Ragged numbers | right-align with a fixed format |
| Tiny bar invisible | give any non-zero value at least one star |
| Month keys are tuples | render `("2023","07")` as `2023-07` |

Use f-string alignment — `f"{label:<12}"` and `f"{value:>12,.0f}"` — rather than
manual spaces.

## Do not

- Calculate totals — `analysis/aggregation` hands them to you
- Print — return the string, `menu/` prints it
- Import pandas or numpy — violates §2
