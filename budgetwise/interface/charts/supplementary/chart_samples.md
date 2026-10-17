# Chart samples — interface/charts

Henrietta · `P3.6` · for the report and slides

Generated from the full D01 dataset (`data/raw/budgetwise_synthetic_dirty.csv`)
through `clean_file()` → `totals_by_category` / `totals_by_month` →
`bar_chart()`. Regenerated 2026-10-17 after decision `D01` changed the dataset.

**Provisional:** this run is from before the `G4` code freeze. Regenerate both
charts from the frozen run before they go into the report or slides.

## Expense spending by category

```python
bar_chart(totals_by_category(records, kind="expense"),
          width=40, title="Expense spending by category", sort_by_value=True)
```

```
Expense spending by category
Food            ****************************************  15,059,930
Rent            ****************************              10,364,133
Utilities       ************************                   8,970,763
Transportation  **********************                     8,110,333
Entertainment   **********                                 3,852,311
Uncategorized   *******                                    2,716,414
Other           ****                                       1,459,247
Savings         ****                                       1,393,730
Education       ***                                        1,262,210
Healthcare      *                                            158,963
```

`Uncategorized` sits sixth at 2,716,414. On this dataset that bar is not only
blank categories: 1,634 rows carry a category string with no entry in
`config/category_mapping.csv` and are routed there. See
`budgetwise/cleaning/categories/supplementary/README.md`. Worth a word in the
slides, because a reader will assume it means "missing".

`Freelance` and `Investment` are absent from the chart because this dataset
has no rows in either — they are income categories in the approved set with no
data behind them here.

## Expense spending by month (2022)

```python
monthly = totals_by_month(records, kind="expense")
bar_chart({k: v for k, v in monthly.items() if k[0] == "2022"},
          width=40, title="Expense spending by month, 2022")
```

```
Expense spending by month, 2022
2022-01  *****                                       251,798
2022-02  **********************                    1,178,925
2022-03  **********************                    1,177,657
2022-04  **********************                    1,167,312
2022-05  **********************                    1,178,511
2022-06  ***                                         185,548
2022-07  ****                                        215,992
2022-08  **********************                    1,153,679
2022-09  ****************************************  2,145,155
2022-10  ****                                        202,779
2022-11  ****                                        206,187
2022-12  **********************                    1,161,851
```

The dataset spans 2019 to 2022, so 2022 is the last full year. The earlier
sample used 2023, which does not exist in this dataset.

Undated transactions are not in the monthly chart (§4.5), so the twelve months
add up to less than the category total. **On this dataset that gap is large:**
2,581 of 14,862 cleaned records have no usable date, 17% of them, because 2,259
date values match no parsing rule. The twelve bars above therefore omit
considerably more than a reader would expect. State the dated/undated split
alongside the chart.
