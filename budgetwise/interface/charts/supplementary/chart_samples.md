# Chart samples

Text charts for the report and slides, generated from
`budgetwise_synthetic_dirty.csv` through `clean_file()`, the aggregation
functions and `bar_chart()`. Regenerated 2026-10-18 after the date fix (PR #43)
and the category, payment-mode and location mapping fixes.

## Expense spending by category

```python
bar_chart(totals_by_category(records, kind="expense"),
          width=40, title="Expense spending by category", sort_by_value=True)
```

```
Expense spending by category
Food            ****************************************  16,187,376
Rent            **************************                10,462,237
Utilities       **********************                     9,037,864
Transportation  ********************                       8,242,883
Entertainment   **********                                 3,909,424
Education       ******                                     2,278,225
Other           ****                                       1,499,397
Savings         ****                                       1,431,665
Healthcare      *                                            170,160
Uncategorized   *                                            128,803
```

`Uncategorized` (128,803) now holds only rows with a blank category or the
ambiguous value `ent`. `Freelance` and `Investment` do not appear because the
dataset has no rows in either.

## Expense spending by month, 2022

```python
monthly = totals_by_month(records, kind="expense")
bar_chart({k: v for k, v in monthly.items() if k[0] == "2022"},
          width=40, title="Expense spending by month, 2022")
```

```
Expense spending by month, 2022
2022-01  *****                                       289,270
2022-02  **********************                    1,205,432
2022-03  **********************                    1,201,072
2022-04  **********************                    1,202,513
2022-05  ***********************                   1,225,491
2022-06  ****                                        215,224
2022-07  ****                                        239,158
2022-08  **********************                    1,181,199
2022-09  ****************************************  2,162,544
2022-10  ****                                        236,814
2022-11  ***********************                   1,226,271
2022-12  **********************                    1,186,722
```

2022 is the last full year in the dataset, which runs from 2019 to 2022. Months
above 1 million each contain one or more 999,999 transactions.

Undated rows are not in the monthly chart (§4.5). 334 of the 14,862 retained
rows (2.2%) have no usable date, so the monthly bars omit 243,341 of expenses.
State this beside the chart.
