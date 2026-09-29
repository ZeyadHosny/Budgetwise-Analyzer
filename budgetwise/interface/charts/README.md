# interface/charts

The text-based bar chart of spending.

| | |
|---|---|
| **Responsible** | Sarah |
| **Domain reviewer** | Bahareh (`P3.4`) |
| **PR approval** | Zeyad or Patrick — see `CONTRIBUTING.md` |
| **Tasks** | `P3.4` |
| **Status** | Not started |

## 1. What this folder does

§4.4 requires *"a simple text-based visualization of spending by month or
category (e.g., bar chart using `*` characters)"*.

Small requirement, and one of the easier marks in the project. It is also the
thing an audience actually looks at during the presentation, so it is worth
getting to look tidy.

## 2. How other modules use it

```python
from budgetwise.interface.charts import bar_chart

print(bar_chart(totals_by_category(transactions), width=40))
```

Takes the dict `analysis/aggregation` already produces. Returns a string — it
does not print, so it can be tested.

## 3. What it produces

```
Food       ****************************************  8,210,400
Rent       *************************************      7,980,120
Travel     *********************                      4,602,880
Utilities  ***************                            3,201,440
Entertain  ***********                                2,410,100
```

By month:

```
2023-05  **************************                   1,180,220
2023-06  *********************************            1,402,910
2023-07  ****************************                 1,204,880
```

## 4. Requirements and tasks covered

| Requirement | Source | Task |
|---|---|---|
| Simple text-based visualization of spending by month or category | §4.4 | `P3.4` |
| Bar chart using `*` characters | §4.4 | `P3.4` |
| Text-based interface, no GUI | §2 | `P3.4` |

## 5. Folders

| Folder | Contents |
|---|---|
| `implementation/` | `bar_chart.py` |
| `testing/` | `test_bar_chart.py` |
| `supplementary/` | `chart_samples.md` |

## 6. Done when

- [ ] Renders by category and by month
- [ ] Bars scale to the largest value and fit the stated width
- [ ] Labels and numbers align in columns
- [ ] Empty input returns an empty string, not a crash
- [ ] A saved sample is in `chart_samples.md` for the report and slides
