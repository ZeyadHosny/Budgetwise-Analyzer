# Output Format Specification

## Cleaned CSV

The file contains one row per valid transaction selected by the menu query.
Amounts are formatted with two decimal places. A missing date is an empty
field. The UTF-8 BOM keeps the rupee symbol readable in Excel.

| Column | Meaning |
|---|---|
| `transaction_id` | Transaction identifier from the source row |
| `user_id` | User identifier from the source row |
| `date` | Normalized `YYYY-MM-DD` date, or blank when missing |
| `transaction_type` | `Expense` or `Income` |
| `category` | Normalized category |
| `amount` | Cleaned unsigned amount with two decimal places |
| `original_currency` | Original currency symbol/label, or `plain` if none |

Example row:

```csv
T4999,U018,2023-07-14,Expense,Food,5891.00,₹
```

## Summary JSON

The summary contains already-calculated figures; export does not recompute them.

| Key | Meaning |
|---|---|
| `dataset` | Source dataset filename |
| `generated` | Local generation timestamp in ISO 8601 format |
| `scope` | `transactions selected by menu query` |
| `selection` | Query type and selected date range or category |
| `selected_transactions` | Number of rows written to the CSV |
| `counts.input` | Raw rows read from the complete source file |
| `counts.valid` | Cleaned rows retained from the complete source file |
| `counts.duplicates` | Exact duplicate rows removed |
| `counts.skipped` | Rows rejected during cleaning |
| `counts.corrected` | Retained rows with at least one corrected value |
| `counts.flagged` | Retained rows with at least one concern |
| `counts.categories_normalized` | Rows whose category changed during normalization |
| `counts.repeated_ids` | Distinct transaction IDs shared by multiple retained rows |
| `counts.by_reason` | Reason code to number-of-events mapping |
| `timings.load` | Dataset loading duration, in seconds |
| `timings.clean` | Cleaning duration, in seconds |
| `total_breakdown.totals` | Overall income, expenses, and net |
| `total_breakdown.top_categories` | Up to five expense `[category, total]` pairs, highest first |
| `total_breakdown.largest_expenses` | Up to five largest expense transaction dictionaries |
| `total_breakdown.budget_by_category` | Aggregate actual and allowed budget across the selected period |
| `total_breakdown.account_breakdown` | Count, spent, and received per cash, bank, and unknown account |
| `total_breakdown.chart_data` | Expense totals by category for rendering the chart |
| `total_breakdown.bar_chart` | Rendered text chart of expenses by category |
| `monthly_breakdown.months` | Per-month totals, top categories, largest expenses, and budget results |
| `monthly_breakdown.chart_data` | Expense totals by month for rendering the chart |
| `monthly_breakdown.bar_chart` | Rendered text chart of expenses by month |
| `category_breakdown` | Per-category income, expenses, net, count, and monthly expenses |

The pipeline builds account totals through each account object's getters.
Status is `over`, `under`, `exact`, or `unbudgeted`. Overall budget status
compares cumulative spending with the sum of monthly limits over the selected
period; partial months are prorated. Monthly comparisons use the existing
`Budget` model. The pipeline returns chart data, and the menu renders it with
`interface/charts` before exporting.

Example:

```json
{
  "dataset": "budgetwise_finance_dataset.csv",
  "generated": "2026-10-13T14:22:05",
  "scope": "transactions selected by menu query",
  "selection": {"type": "all"},
  "selected_transactions": 14100,
  "counts": {"input": 15900, "valid": 14651, "duplicates": 900},
  "timings": {"load": 0.04, "clean": 0.5},
  "total_breakdown": {
    "totals": {"income": 14082330.0, "expenses": 79441210.0, "net": -65358880.0},
    "top_categories": [["Food", 8210400.0], ["Rent", 7980120.0]],
    "largest_expenses": [{"transaction_id": "T4999", "amount": 9984.0}],
    "budget_by_category": [
      {"category": "Food", "limit": 11928000.0, "actual": 8210400.0,
       "status": "under", "difference": -3717600.0}
    ],
    "account_breakdown": {
      "cash": {"transaction_count": 3799, "total_spent": 20000000.0, "total_received": 1000000.0},
      "bank": {"transaction_count": 11293, "total_spent": 55000000.0, "total_received": 13000000.0},
      "unknown": {"transaction_count": 808, "total_spent": 5000000.0, "total_received": 500000.0}
    },
    "chart_data": [{"category": "Food", "expenses": 8210400.0}],
    "bar_chart": "Expenses by category\\nFood  ********  8,214,000"
  },
  "monthly_breakdown": {
    "months": [{
      "month": "2023-07",
      "totals": {"income": 30000.0, "expenses": 250000.0, "net": -220000.0},
      "top_categories": [["Food", 250000.0]],
      "largest_expenses": [{"transaction_id": "T4999", "amount": 9984.0}],
      "budget_comparisons": [{"category": "Food", "limit": 248500.0,
        "actual": 250000.0, "status": "over", "difference": 1500.0}]
    }],
    "chart_data": [{"month": "2023-07", "expenses": 250000.0}],
    "bar_chart": "Expenses by month\\n2023-07  ********  250,000"
  },
  "category_breakdown": [{
    "category": "Food",
    "totals": {"income": 0.0, "expenses": 8210400.0, "net": -8210400.0},
    "transaction_count": 3120,
    "monthly_expenses": [{"month": "2023-07", "expenses": 250000.0}]
  }]
}
```