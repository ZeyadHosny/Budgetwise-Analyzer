# interface/charts/implementation

Henrietta · `P3.6` · domain reviewer Sarah

## Function

```python
bar_chart(totals: dict, width: int = 40, title: str = "", sort_by_value: bool = False) -> str
```

Returns the chart as a string. It never prints: the menu prints it, and the tests assert on it.

## Behaviour

| Rule | How |
|---|---|
| Scaling | The largest value gets exactly `width` stars: `round(value / max_value * width)` |
| Small values | Any value above zero gets at least one star |
| Zero values | No stars, label and number still shown |
| Empty input | Returns `""` |
| All values zero | No division error; every bar is empty |
| Month keys | `("2023", "07")` renders as `2023-07` |
| Alignment | Labels left-aligned, numbers right-aligned with thousands separators; every line is the same length |
| Long labels | Cut to 16 characters |
| Order | Keeps the dictionary's order (chronological for months), or largest first with `sort_by_value=True` |
| Bad width | `width < 1` raises `ValueError` |

## Usage

```python
from budgetwise.analysis.aggregation import totals_by_category, totals_by_month
from budgetwise.interface.charts import bar_chart

print(bar_chart(totals_by_category(records, kind="expense"), sort_by_value=True))
print(bar_chart(totals_by_month(records, kind="expense")))
```

## Rules followed

- Does not calculate totals: `analysis/aggregation` provides them.
- Standard library only; no pandas or numpy (§2).
