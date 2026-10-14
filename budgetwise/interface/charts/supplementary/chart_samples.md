# Chart samples — interface/charts

Henrietta · `P3.6` · for the report and slides

Generated from the full dataset (`data/raw/budgetwise_finance_dataset.csv`) through
`clean_file()` → `totals_by_category` / `totals_by_month` → `bar_chart()`.

**Provisional:** this run is from before the `G4` code freeze. Regenerate both
charts from the frozen run before they go into the report or slides.

## Expense spending by category

```python
bar_chart(totals_by_category(records, kind="expense"),
          width=40, title="Expense spending by category", sort_by_value=True)
```

```
Expense spending by category
Rent            ****************************************  48,822,528
Food            *******************************           38,410,740
Utilities       ***************                           18,244,248
Entertainment   *************                             16,168,446
Transportation  ************                              14,222,100
Education       ***********                               12,956,677
Healthcare      *****                                      5,824,809
Other           ****                                       5,112,146
Uncategorized   ***                                        3,104,685
Savings         **                                         2,882,687
```

## Expense spending by month (2023)

```python
monthly = totals_by_month(records, kind="expense")
bar_chart({k: v for k, v in monthly.items() if k[0] == "2023"},
          width=40, title="Expense spending by month, 2023")
```

```
Expense spending by month, 2023
2023-01  **********************                    2,674,720
2023-02  ***************                           1,811,021
2023-03  **********                                1,219,285
2023-04  **************                            1,699,889
2023-05  *************                             1,538,647
2023-06  ******************************            3,627,880
2023-07  *****************************             3,525,434
2023-08  ************************                  2,853,261
2023-09  *********************                     2,540,270
2023-10  **********************                    2,648,689
2023-11  ****************************************  4,824,396
2023-12  **********************                    2,639,398
```

Undated transactions are not in the monthly chart (§4.5), so the twelve months
add up to less than the category total.
