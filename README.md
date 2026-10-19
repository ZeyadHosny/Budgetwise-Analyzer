# BudgetWise Personal Finance & Spending Analyzer

DATA 5010 - Project 1

A Python menu application that cleans transaction data and exports spending summaries, monthly trends, budget comparisons, and text charts.

Repository: [Budgetwise-Analyzer](https://github.com/ZeyadHosny/Budgetwise-Analyzer)

## Setup

Use Python 3.10 or newer. The application uses the standard library only; no packages or environment variables are required. Verified on Windows 11 with Python 3.14.6.

Open a terminal in the `Budgetwise-Analyzer` folder containing `main.py`. All commands and paths below are relative to that folder. The exports are written to absolute paths, but `errors.log` is written relative to the current folder, so running `python Budgetwise-Analyzer/main.py` from a parent folder writes the log elsewhere and option `4` will not find it.

```bash
python main.py
```

## Data

This project uses `data/raw/budgetwise_synthetic_dirty.csv`, downloaded on **September 28, 2026** from the [BudgetWise Personal Finance Dataset on Kaggle](https://www.kaggle.com/datasets/mohammedarfathr/budgetwise-personal-finance-dataset).

Compared with `budgetwise_finance_dataset.csv`, the dirty dataset contains a wider variety of date formats and category inconsistencies: 213 distinct raw category values versus 47. We use it to exercise cleaning and error handling across these formatting issues and corner cases.

| File | Data rows, excluding header | Valid date range after cleaning |
|---|---:|---|
| `budgetwise_synthetic_dirty.csv` | 15,836 | 2019-01-01 to 2022-12-31 |

If the file is missing, download it from the Kaggle page and place it in `data/raw/`, keeping its filename.

Input columns: `transaction_id`, `user_id`, `date`, `transaction_type`, `category`, `amount`, `payment_mode`, `location`, `notes`.

## Run the analysis

| Menu option | Action |
|---|---|
| `1` | Load the full dataset and export all results. |
| `2` | Enter inclusive start and end dates as `YYYY-MM-DD`. For the 2022 results, enter `2022-01-01` and `2022-12-31`. |
| `3` | Choose a displayed category, such as `Food`; matching ignores case. |
| `4` | Display `output/logs/errors.log`. |
| `5` | Exit. |

## Cleaning and budget settings

Set the input file and budget baseline in `budgetwise/settings.py`. The menu, timing script, and budget-generation script share `DATASET_PATH`. `BUDGET_BASELINE_START` and `BUDGET_BASELINE_END` are `2019-01-01` and `2021-12-31`; review them if changing datasets. The menu derives its date-range hint from the selected file. Budget generation requires complete calendar months and data in the first and last baseline months.

- Exact duplicate raw rows are removed before normalization. Different rows sharing a transaction ID are retained and flagged.
- Currency labels are removed without conversion. Amounts are unsigned magnitudes; `transaction_type` determines income or expense. Invalid amounts, including values at least 100,000,000, are excluded.
- Dates become `YYYY-MM-DD`. Ambiguous slash dates use month/day/year; hyphen dates with two-digit years use day-month-year. Missing or invalid dates remain in overall/category totals but are excluded from monthly analysis and date filters.
- Category mappings are in `config/category_mapping.csv`. Missing or unrecognized categories become `Uncategorized`.

Monthly limits in `config/monthly_budgets.json` are Food **67,000**, Rent **50,500**, Transportation **27,500**, Utilities **23,000**, and Entertainment **17,000**, in dataset units. These use each category's median monthly expenses during 2019-2021, rounded up to 500; 2022 is reserved for comparison.

To recalculate the monthly budget limits using the dataset and baseline dates in `budgetwise/settings.py`, run:

```bash
python -m budgetwise.analysis.budgets.implementation.generate_budget_evidence
```

This updates the limits in `config/monthly_budgets.json` and writes the calculations and explanation to `budgetwise/analysis/budgets/supplementary/budget_justification.md`, replacing their previous contents.

### Using a different dataset

1. Place the CSV in `data/raw/`; it must use the input columns listed above. Review `config/category_mapping.csv` if it introduces new category names.
2. Edit `DATASET_PATH`, `BUDGET_BASELINE_START`, and `BUDGET_BASELINE_END` in `budgetwise/settings.py`. For `budgetwise_finance_dataset.csv`, use `2021-01-01` through `2023-12-31` as the baseline and reserve 2024 for comparison.
3. Close any running menu, then run these commands from the repository folder:

```bash
python -m budgetwise.analysis.budgets.implementation.generate_budget_evidence
python main.py
```

The first command recalculates category medians and replaces the budget limits (rounded up to 500) and justification. After it succeeds, use menu option `1` for the full dataset or `2` for the comparison period. Changing settings alone does not update the saved limits; regenerate them when switching back, too. The menu's date-range hint updates automatically.

## Read the outputs

Options `1`-`3` automatically create these files. `<dataset>` is the selected CSV filename without `.csv` (`budgetwise_synthetic_dirty` by default); `<date>` is the run date.

| File | Contents |
|---|---|
| `output/cleaned/cleaned_<dataset>_<date>.csv` | Selected cleaned transactions: IDs, date, type, category, amount, and original currency label. |
| `output/summaries/summary_<dataset>_<date>.json` | Selection, cleaning counts, income, expenses, net balance, top five spending categories and expense transactions, monthly results, account totals, and budgets. |
| `output/summaries/charts_<dataset>_<date>.txt` | Text bar charts of expenses by category and month. |
| `output/logs/errors.log` | Source line, field, reason, and raw value for cleaning issues. |

Net balance means income minus expenses. Budget `difference` means actual minus limit; statuses are `over`, `under`, `exact`, or `unbudgeted`. Monthly comparisons use full monthly limits; the combined comparison prorates limits for partial months and includes only months with selected expenses. Undated expenses are excluded from budget comparisons.

Cleaning counts describe the whole input file; financial results and cleaned exports describe the selected transactions. Corrected rows are included in valid rows. `categories_normalized` counts changed rows, not distinct categories.

**Each run replaces the exports for the same day, including filtered runs and `run_timings.py`, which runs the full pipeline.** Copy results before another run if needed. Running the tests also writes `cleaned_test_*`, `summary_test_*`, and `charts_test_*` files to `output/`; these are test artifacts, not results. The error log appends across runs. The raw CSV file is unchanged.

## Reproduce and check results

Before running the examples below:

1. In `budgetwise/settings.py`, keep `budgetwise_synthetic_dirty.csv` as the dataset and `2019-01-01` through `2021-12-31` as the budget baseline.
2. From the `Budgetwise-Analyzer` folder, regenerate the budget limits and start the application:

```bash
python -m budgetwise.analysis.budgets.implementation.generate_budget_evidence
python main.py
```

In the outputs below, the entered values are shown after each prompt, `<absolute-path>` represents the location of your repository, and the filename date changes with your run date.

### Example 1: Full dataset

At `Choose an option:`, enter `1`. No dates or category are needed. The program cleans the entire file, analyzes all retained transactions, and prints the export paths and cleaning counts. The menu then appears again; enter `5` to exit (or `4` to view the log first).

```text
=== BudgetWise Finance Analyzer ===
1. Load full dataset
2. Load transactions by date range
3. Load transactions by category
4. View error log
5. Exit
Choose an option: 1
  Cleaned CSV: <absolute-path>/output/cleaned/cleaned_budgetwise_synthetic_dirty_2026-10-19.csv
  JSON summary: <absolute-path>/output/summaries/summary_budgetwise_synthetic_dirty_2026-10-19.json
  Charts: <absolute-path>/output/summaries/charts_budgetwise_synthetic_dirty_2026-10-19.txt

  Dataset cleaning:
    Rows read:              15,836
    Valid rows:             14,862
    Duplicates removed:        804
    Invalid rows skipped:      170
    See output/logs/errors.log for cleaning reasons.

  Selected results:
    Matching transactions: 14,862

=== BudgetWise Finance Analyzer ===
1. Load full dataset
2. Load transactions by date range
3. Load transactions by category
4. View error log
5. Exit
Choose an option: 5
  Goodbye.
```

`Rows read` counts input records, excluding the header. `Valid rows` are retained after cleaning; duplicate and invalid rows are excluded. `Matching transactions` counts the transactions used in this analysis. It equals `Valid rows` here because option `1` applies no filter.

The printed paths point to the results:

| Output | How to read this run |
|---|---|
| Cleaned CSV | Contains 14,862 transaction rows plus the header. Each row is a retained transaction with a nonnegative amount; `transaction_type` gives its direction. A blank date means the transaction has no usable date. `original_currency` preserves the currency label, or `plain` when none was present. |
| JSON summary | `selection.type` is `all`. `metrics.counts` contains the cleaning counts. `total_breakdown` contains overall totals, the top five spending categories, five largest expenses, combined budgets, and account totals. `monthly_breakdown.months` contains each month's totals, rankings, and budget comparisons. |
| Charts | Shows spending by category and month. Longer bars mean higher expenses; the number beside each bar is the expense total. For example, Food totals 16,147,568. |
| `output/logs/errors.log` | Explains corrections, exclusions, and flags using source CSV line numbers. For example, `line=2 field=date reason=date_normalized` records a date-format correction, not a rejected transaction. One row can produce several log entries, and previous runs remain in the log. |

In the JSON, January 2019 Food spending is **52,014** against a **67,000** monthly limit: `status` is `under` and `difference` is **-14,986**. This is a monthly comparison; the combined budget section covers the full selected period.

Check these full-dataset results in the JSON summary:

| Measure | Result |
|---|---:|
| Valid records | 14,862 |
| Duplicates removed | 804 |
| Invalid records skipped | 170 |
| Corrected records | 12,862 |
| Rows with category changes | 3,969 |
| Total income | 134,553,045 |
| Total expenses | 53,348,034 |
| Net balance | 81,205,011 |

The counts reconcile: **15,836 = 14,862 + 170 + 804**. Corrected records are part of the valid records, not additional rows. Overall totals include undated transactions, so monthly totals may not sum to the overall totals.

### Example 2: Date range (2022 comparison period)

Check Example 1's results first: Examples 2 and 3 overwrite the same day's output files. Copy them if you need to keep them.

At `Choose an option:`, enter `2`, then `2022-01-01` and `2022-12-31`. When the menu appears again, enter `5` to exit.

```text
=== BudgetWise Finance Analyzer ===
1. Load full dataset
2. Load transactions by date range
3. Load transactions by category
4. View error log
5. Exit
Choose an option: 2
  Selected dataset date range: 2019-01-01 to 2022-12-31.
  Rows with no date are excluded from a date range.
Start date (YYYY-MM-DD): 2022-01-01
End date   (YYYY-MM-DD): 2022-12-31
  Cleaned CSV: <absolute-path>/output/cleaned/cleaned_budgetwise_synthetic_dirty_2026-10-19.csv
  JSON summary: <absolute-path>/output/summaries/summary_budgetwise_synthetic_dirty_2026-10-19.json
  Charts: <absolute-path>/output/summaries/charts_budgetwise_synthetic_dirty_2026-10-19.txt

  Dataset cleaning:
    Rows read:              15,836
    Valid rows:             14,862
    Duplicates removed:        804
    Invalid rows skipped:      170
    See output/logs/errors.log for cleaning reasons.

  Selected results:
    Matching transactions: 3,604
  Range 2022-01-01 to 2022-12-31. Rows with no date are excluded from a date range

=== BudgetWise Finance Analyzer ===
1. Load full dataset
2. Load transactions by date range
3. Load transactions by category
4. View error log
5. Exit
Choose an option: 5
  Goodbye.
```

The cleaning counts are the same as option `1` because they describe the whole file. Only the 3,604 dated 2022 transactions are analyzed and exported. In the JSON, `selection` is `{"type": "date_range", "start": "2022-01-01", "end": "2022-12-31"}`; total income is **31,742,979**, total expenses **11,571,710**, and net balance **20,171,269**.

### Example 3: One category (Food)

At `Choose an option:`, enter `3`, then `food`. When the menu appears again, enter `5` to exit.

```text
=== BudgetWise Finance Analyzer ===
1. Load full dataset
2. Load transactions by date range
3. Load transactions by category
4. View error log
5. Exit
Choose an option: 3
  Categories:
    Bonus, Education, Entertainment, Food
    Freelance, Healthcare, Investment, Other
    Rent, Salary, Savings, Transportation
    Uncategorized, Utilities
Category (one of the above): food
  Cleaned CSV: <absolute-path>/output/cleaned/cleaned_budgetwise_synthetic_dirty_2026-10-19.csv
  JSON summary: <absolute-path>/output/summaries/summary_budgetwise_synthetic_dirty_2026-10-19.json
  Charts: <absolute-path>/output/summaries/charts_budgetwise_synthetic_dirty_2026-10-19.txt

  Dataset cleaning:
    Rows read:              15,836
    Valid rows:             14,862
    Duplicates removed:        804
    Invalid rows skipped:      170
    See output/logs/errors.log for cleaning reasons.

  Selected results:
    Matching transactions: 3,696
  Category Food. The filter runs after normalization, so 'Fod' and 'Foodd' match too.

=== BudgetWise Finance Analyzer ===
1. Load full dataset
2. Load transactions by date range
3. Load transactions by category
4. View error log
5. Exit
Choose an option: 5
  Goodbye.
```

Only the 3,696 Food transactions are analyzed and exported, including undated ones. In the JSON, `selection` is `{"type": "category", "category": "Food"}`; total income is **0**, total expenses **16,147,568** (the same Food total as the full-run chart), and net balance **-16,147,568**.
### Tests and execution time

Run the existing tests and measure execution times:

```bash
python -m unittest discover
python budgetwise/metrics/supplementary/run_timings.py --runs 7
```

The timing script runs the full pipeline several times and reports each stage's time (loading, cleaning, analysis, export, and others) as a median and min-max in milliseconds. Timings vary by machine.

Use this script, not the JSON summary, for execution-time results. The JSON summary also has a `metrics.timings_seconds` section, but it times only loading and cleaning; its `analysis` field is always `0.0` and should be ignored.

Expected test result: `Ran 804 tests ... OK`. The suite also prints a note that test cases TC-038, TC-049, TC-076, TC-086, and TC-087 are checked manually.

## Code layout

`main.py` starts the menu. `budgetwise/` contains loading, cleaning, models, analysis, exports, and metrics; `config/` holds mappings and limits. Feature tests are beside their modules, and `tests/` contains integration tests. `docs/` contains project documentation.
