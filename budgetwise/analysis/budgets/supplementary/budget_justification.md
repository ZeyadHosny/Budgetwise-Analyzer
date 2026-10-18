# Monthly Budget Justification

## Method

Limits use cleaned expense transactions from `budgetwise_synthetic_dirty.csv`. The observed month window is 2019-01 through 2022-12 (48 calendar months). Undated transactions are excluded. Months with no spending in a category are included as zero, so every category uses the same window.

For each configured category, the limit is its median monthly spend rounded up to the next 500 dataset units. The median is less sensitive to one unusually expensive month than the mean. The 75th percentile and maximum are shown as context, not used to set the limit. No currency conversion is performed.

These are historical spending-based planning limits, not a claim that the amounts are affordable or financially advisable for every household. The team should revise them if its goals or circumstances differ from the historical pattern.

## Proposed Limits

| Category | Median monthly spend | 75th percentile | Highest month | Proposed limit |
|---|---:|---:|---:|---:|
| Entertainment | 13,396.00 | 20,926.50 | 1,019,660.00 | 13,500.00 |
| Food | 52,377.50 | 68,096.25 | 2,069,270.00 | 52,500.00 |
| Rent | 42,219.50 | 53,336.25 | 1,053,719.00 | 42,500.00 |
| Transportation | 20,805.00 | 25,453.50 | 1,029,830.00 | 21,000.00 |
| Utilities | 17,294.50 | 20,584.50 | 1,015,679.00 | 17,500.00 |

The configured categories are retained from `monthly_budgets.json`. Categories with spending but no configured limit are reported as `unbudgeted` by the comparison function.
