# Monthly Budget Benchmark Justification

Status: Proposed for team review.

## Data and method

The calculation uses the repository dataset after running the
existing cleaning pipeline.

Cleaning results:
- Input: 15,900 rows
- Retained: 14,651 rows
- Skipped: 349 rows
- Exact duplicates removed: 900 rows

Eligible records are cleaned Expense transactions with valid dates
from January 1, 2021 through December 31, 2023.

For each user, year, month, and normalized category, amounts are summed.
The median of these observed monthly totals is rounded upward
to the nearest 100 dataset units.

Formula:
limit = 100 * ceil(median(observed monthly totals) / 100)

## Reproduced results

| Category | Expense rows | Observed user-months | Users | Median | Proposed limit |
|---|---:|---:|---:|---:|---:|
| Food | 2204 | 1779 | 150 | 3871.00 | 3900 |
| Rent | 1793 | 1514 | 150 | 8811.50 | 8900 |
| Transportation | 1344 | 1180 | 150 | 5556.00 | 5600 |
| Utilities | 1078 | 962 | 150 | 5510.50 | 5600 |
| Entertainment | 909 | 841 | 150 | 5327.00 | 5400 |
| Education | 670 | 627 | 149 | 5545.00 | 5600 |
| Healthcare | 406 | 390 | 137 | 5116.50 | 5200 |

All seven calculated limits match config/monthly_budgets.json.
The existing 174 cleaning, loader, and pipeline tests passed.

## Justification and limitations

The median reduces the influence of unusually large monthly totals.
Rounding makes the limits easy to explain.

Absent user/category/month combinations are not treated as zero.
Explicitly recorded zero amounts are included.
Undated expenses remain available for overall analysis but are
excluded from monthly calculations.

Currency labels are cosmetic under the assignment convention.
Amounts are combined without currency conversion.

These limits describe recorded spending in observed category-months.
They are project benchmarks, not actual user budgets or evidence
of what users can afford.

Shared defaults apply to all users unless a documented override exists.
Categories without a limit are reported as unbudgeted.

Comparisons may cover any available month.
Comparisons for 2021–2023 use the same period that generated the limits
and must be labeled as descriptive baseline-period comparisons.
2024 is outside the calculation baseline.

## Reproduction

Run this command from the project root:

python -m budgetwise.analysis.budgets.supplementary.calculate_budget_limits

The script prints the cleaning counts and evidence table.
It does not modify the budget configuration.

See docs/budget_policy.md for the proposed comparison policy.
