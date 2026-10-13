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
| `totals.income` | Income total for the selected transactions |
| `totals.expenses` | Expense total for the selected transactions |
| `totals.net` | Selected income minus selected expenses |
| `top_categories` | Up to five `[category, total]` expense pairs from the selection, highest total first |

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
  "totals": {"income": 14082330.0, "expenses": 79441210.0, "net": -65358880.0},
  "top_categories": [["Food", 8210400.0], ["Rent", 7980120.0]]
}
```