# Proposed Monthly Budget Policy

Status: Proposed for team review.

## Purpose

Define transparent monthly category benchmarks for budget comparison.
These benchmarks are not users' actual budgets or financial advice.

## Calculation method

1. Use cleaned Expense records with valid dates from 2021–2023.
2. Group records by user, year, month, and normalized category.
3. Sum expense amounts within each group.
4. Calculate the median of the observed monthly totals for each category.
5. Round the median upward to the nearest 100 dataset units.

Formula:

limit = 100 * ceil(median(observed monthly totals) / 100)

The median reduces the influence of unusually large totals.
Rounding makes the limits easier to read and explain.

## Missing information

- Do not create zero totals for absent user/category/month combinations.
- Keep explicitly recorded zero totals.
- Exclude undated expenses from monthly calculations only.
- Keep otherwise eligible expenses with Unknown payment modes.
- Report categories without a configured limit as "unbudgeted".
- Treat currency labels as cosmetic and perform no currency conversion.

## User limits

Start with one shared default per category for all users.
User-specific overrides may be added later with a documented reason.

## Monthly comparison

Support comparisons for any available year and month.

Comparisons for 2021–2023 are descriptive comparisons using the
same period that generated the benchmarks.

Comparisons for 2024 use records outside the baseline period.

For group comparisons, sum spending and budget limits for the same
selected users, month, and category.

## Next steps

Reproduce and document the candidate limits, review them with the team,
and store the selected limits in config/monthly_budgets.json.
