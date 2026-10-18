# Charts

Draws text bar charts of spending with `*` characters (§4.4).

| | |
|---|---|
| **Responsible** | Henrietta |
| **Domain reviewer** | Sarah |
| **PR approval** | Zeyad or Patrick (see `CONTRIBUTING.md`) |
| **Task** | `P3.6` |
| **Status** | Implemented |

## Interface

```python
from budgetwise.interface.charts import bar_chart

bar_chart(totals: dict, width: int = 40, title: str = "",
          sort_by_value: bool = False) -> str
```

It takes the dictionaries from `analysis/aggregation` and returns the chart as
a string. It never prints, so the menu decides where it goes and the tests can
check it.

## Behaviour

| Rule | How |
|---|---|
| Scaling | The largest value gets `width` stars; others get `round(value / max * width)` |
| Small values | Any value above zero gets at least one star |
| Zero and empty | A zero value shows no stars; an empty dict returns `""` |
| Month keys | `("2022", "06")` is shown as `2022-06` |
| Alignment | Labels left, numbers right with thousands separators; long labels cut to 16 characters |
| Order | Dictionary order (date order for months), or largest first with `sort_by_value=True` |
| Bad width | `width < 1` raises `ValueError` |

## Example

Expense spending by category, synthetic dirty dataset (top five):

```
Food            ****************************************  16,187,376
Rent            **************************                10,462,237
Utilities       **********************                     9,037,864
Transportation  ********************                       8,242,883
Entertainment   **********                                 3,909,424
```

Full category and monthly charts are in `supplementary/chart_samples.md`.

## Files

| Folder | Contents |
|---|---|
| `implementation/` | `bar_chart.py` |
| `testing/` | `test_bar_chart.py` |
| `supplementary/` | `chart_samples.md` |

## Tests

16 tests cover scaling, small and zero values, empty input, equal values,
month keys, alignment, ordering, titles, long labels and invalid widths.

```bash
python -m unittest budgetwise.interface.charts.testing.test_bar_chart -v
```
