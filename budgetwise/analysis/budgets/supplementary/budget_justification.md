# Monthly Budget Justification

## Method

Limits use cleaned expense transactions from `budgetwise_synthetic_dirty.csv`. The observed month window is 2019-01 through 2021-12 (36 calendar months). Undated transactions are excluded. Months with no spending in a category are included as zero, so every category uses the same window.

For each configured category, the limit is its median monthly spend rounded up to the next 500 dataset units. The median is less sensitive to one unusually expensive month than the mean. The 75th percentile and maximum are shown as context, not used to set the limit. No currency conversion is performed.

These are historical spending-based planning limits, not a claim that the amounts are affordable or financially advisable for every household. The team should revise them if its goals or circumstances differ from the historical pattern.

## Proposed Limits

| Category | Median monthly spend | 75th percentile | Highest month | Proposed limit |
|---|---:|---:|---:|---:|
| Entertainment | 16,940.50 | 24,727.50 | 1,020,422.00 | 17,000.00 |
| Food | 66,707.50 | 334,624.00 | 2,076,935.00 | 67,000.00 |
| Rent | 50,027.00 | 65,611.25 | 1,059,832.00 | 50,500.00 |
| Transportation | 27,107.50 | 32,370.00 | 1,034,836.00 | 27,500.00 |
| Utilities | 22,831.50 | 32,467.00 | 2,018,625.00 | 23,000.00 |

The configured categories are retained from `monthly_budgets.json`. Categories with spending but no configured limit are reported as `unbudgeted` by the comparison function.
