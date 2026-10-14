# interface/charts

The text-based bar chart of spending.

| | |
|---|---|
| **Responsible** | Henrietta |
| **Domain reviewer** | Sarah (`P3.6`) |
| **PR approval** | Zeyad or Patrick — see `CONTRIBUTING.md` |
| **Tasks** | `P3.6` |
| **Status** | Implemented and under review |

## 1. What this folder does

§4.4 requires *"a simple text-based visualization of spending by month or
category (e.g., bar chart using `*` characters)"*.

Small requirement, and one of the easier marks in the project. It is also the
thing an audience actually looks at during the presentation, so it is worth
getting to look tidy.

## 2. How other modules use it

```python
from budgetwise.interface.charts import bar_chart

print(bar_chart(totals_by_category(transactions, kind="expense"), width=40))
```

Takes the dict `analysis/aggregation` already produces. Returns a string — it
does not print, so it can be tested.

## 3. What it produces

Expense totals from the full dataset (provisional, before `G4`):

```
Rent            ****************************************  48,822,528
Food            *******************************           38,410,740
Utilities       ***************                           18,244,248
Entertainment   *************                             16,168,446
Transportation  ************                              14,222,100
```

By month:

```
2023-05  *************                             1,538,647
2023-06  ******************************            3,627,880
2023-07  *****************************             3,525,434
```

## 4. Requirements and tasks covered

| Requirement | Source | Task |
|---|---|---|
| Simple text-based visualization of spending by month or category | §4.4 | `P3.6` |
| Bar chart using `*` characters | §4.4 | `P3.6` |
| Text-based interface, no GUI | §2 | `P3.6` |

## 5. Folders

| Folder | Contents |
|---|---|
| `implementation/` | `bar_chart.py` |
| `testing/` | `test_bar_chart.py` |
| `supplementary/` | `chart_samples.md` |

## 6. Done when

- [x] Renders by category and by month
- [x] Bars scale to the largest value and fit the stated width
- [x] Labels and numbers align in columns
- [x] Empty input returns an empty string, not a crash
- [x] A saved sample is in `chart_samples.md` for the report and slides (regenerate after `G4`)
