# Running Monthly Budget Comparison

## Start the application

From the project root, run:

python main.py

## Individual comparison

1. Choose option 1 to load and clean the full dataset.
2. Choose option 6: Compare monthly budgets.
3. Enter a month, for example 2024-04.
4. Enter a category, for example Food.
5. Choose scope 1: One user.
6. Enter the user ID, for example U042.

Verified example:
- User: U042
- Month: 2024-04
- Category: Food
- Recorded expense: 4168
- Budget benchmark: 3900
- Result: over by 268

## Group comparison

After loading the dataset, choose option 6 and enter a month and category.

Choose:
- Scope 2 for selected user IDs separated by commas.
- Scope 3 for all users with dated records in the selected month.

Group spending and budgets cover the same included users.
Users without monthly records are excluded and identified.
Users without recorded category expenses are included but flagged.

## Interpretation

- over: recorded spending exceeds the benchmark
- under: recorded spending is below the benchmark
- equal: recorded spending equals the benchmark
- no_data: no dated records for the selection
- unbudgeted: no matching budget is defined
- incomplete_budget: only some group members have defined budgets

No recorded category expense does not prove actual spending was zero.
Group results do not replace individual results.

Limits are proposed project benchmarks for team review.
They are not actual user budgets or financial advice.

## Calculation evidence

See:
- docs/budget_policy.md
- budgetwise/analysis/budgets/supplementary/budget_justification.md

To reproduce the proposed limits, run from the project root:

python -m budgetwise.analysis.budgets.supplementary.calculate_budget_limits

## Verification

242 tests passed:
- 174 cleaning, loader, and pipeline tests
- 13 Budget model tests
- 17 individual monthly comparison tests
- 16 group comparison tests
- 22 existing menu tests

Additional main.py execution checks passed for:
- Individual comparison
- Automatic monthly group comparison
- Budget comparison after category filtering
- Choosing budget comparison before loading data

## Current scope

Budget comparison currently consumes cleaned dictionaries.
Transaction object creation, general financial summaries,
charts, and exports are separate work.
