# Monthly Budget Justification

## Method

Limits use cleaned expense transactions from `budgetwise_synthetic_dirty.csv`. The observed month window is 2019-01 through 2021-12 (36 calendar months). Undated transactions are excluded. Months with no spending in a category are included as zero, so every category uses the same window.

For each configured category, the limit is its median monthly spend rounded up to the next 500 dataset units. The median is less sensitive to one unusually expensive month than the mean. The 75th percentile and maximum are shown as context, not used to set the limit. No currency conversion is performed.

These are historical spending-based planning limits, not a claim that the amounts are affordable or financially advisable for every household. The team should revise them if its goals or circumstances differ from the historical pattern.

## Proposed Limits

| Category | Median monthly spend | 75th percentile | Highest month | Proposed limit |
|---|---:|---:|---:|---:|
| Entertainment | 15,285.00 | 22,872.75 | 1,020,422.00 | 15,500.00 |
| Food | 66,556.50 | 334,575.50 | 2,076,935.00 | 67,000.00 |
| Rent | 49,631.00 | 64,764.00 | 1,059,262.00 | 50,000.00 |
| Transportation | 24,077.50 | 28,971.00 | 1,030,811.00 | 24,500.00 |
| Utilities | 21,967.00 | 25,491.00 | 2,017,517.00 | 22,000.00 |

The configured categories are retained from `monthly_budgets.json`. Categories with spending but no configured limit are reported as `unbudgeted` by the comparison function.
