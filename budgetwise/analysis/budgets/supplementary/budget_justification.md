# Monthly Budget Justification

## Method

Limits use cleaned expense transactions from `budgetwise_finance_dataset.csv`. The observed month window is 2021-01 through 2024-12 (48 calendar months). Undated transactions are excluded. Months with no spending in a category are included as zero, so every category uses the same window.

For each configured category, the limit is its median monthly spend rounded up to the next 500 dataset units. The median is less sensitive to one unusually expensive month than the mean. The 75th percentile and maximum are shown as context, not used to set the limit. No currency conversion is performed.

These are historical spending-based planning limits, not a claim that the amounts are affordable or financially advisable for every household. The team should revise them if its goals or circumstances differ from the historical pattern.

## Proposed Limits

| Category | Median monthly spend | 75th percentile | Highest month | Proposed limit |
|---|---:|---:|---:|---:|
| Entertainment | 135,900.50 | 167,722.00 | 2,107,986.00 | 136,000.00 |
| Food | 248,068.50 | 1,246,203.00 | 3,271,264.00 | 248,500.00 |
| Rent | 726,636.00 | 1,626,315.75 | 2,842,440.00 | 727,000.00 |
| Transportation | 195,699.00 | 217,403.00 | 1,244,537.00 | 196,000.00 |
| Utilities | 156,163.00 | 203,884.25 | 1,219,072.00 | 156,500.00 |

The configured categories are retained from `monthly_budgets.json`. Categories with spending but no configured limit are reported as `unbudgeted` by the comparison function.
