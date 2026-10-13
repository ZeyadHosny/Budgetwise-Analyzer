# interface/export

Writes the cleaned summary out as CSV or JSON.

| | |
|---|---|
| **Responsible** | Sarah |
| **Domain reviewer** | Bahareh (`P3.4`) |
| **PR approval** | Zeyad or Patrick — see `CONTRIBUTING.md` |
| **Tasks** | `P3.4` |
| **Status** | Implemented |

## 1. What this folder does

§4.4 requires exporting a cleaned summary to a new CSV or JSON file, and §5
requires the GitHub repository to contain the **output datasets** — so this
module produces a graded deliverable, not a convenience.

Filenames follow `CONTRIBUTING.md` §7:

```
output/cleaned/cleaned_budgetwise_finance_dataset_2026-10-12.csv
output/summaries/summary_budgetwise_finance_dataset_2026-10-12.json
```

The date matters. At `G4` results are frozen for the report, and dated filenames
make "which run produced this number" answerable.

## 2. How other modules use it

```python
from budgetwise.interface.export import export_cleaned, export_summary

export_cleaned(transactions, dataset="budgetwise_finance_dataset")
export_summary(summary_dict, dataset="budgetwise_finance_dataset")
```

Called from `menu/` after a load completes.
For date-range and category queries, both files contain only the selected transactions; the JSON records the filter used. Cleaning counts still describe the complete source file.
The JSON also includes per-month budget statuses from the configured limits.
For partial date-range months, the period coverage is identified explicitly;
the selected spend is compared against the full monthly limit.

## 3. What it produces

`cleaned_..._2026-10-12.csv` — one row per valid transaction, cleaned:

```csv
transaction_id,user_id,date,transaction_type,category,amount,original_currency
T4999,U018,2023-07-14,Expense,Food,5891.00,₹
T12828,U133,2023-03-02,Income,Salary,48200.00,plain
```

`summary_..._2026-10-12.json` — the figures plus the run's provenance:

```json
{
  "dataset": "budgetwise_finance_dataset.csv",
  "generated": "2026-10-12T14:22:05",
  "counts": { "input": 15900, "valid": 14100, "duplicates": 900 },
  "totals": { "income": 14082330.0, "expenses": 79441210.0 },
  "top_categories": [["Food", 8210400.0], ["Rent", 7980120.0]]
}
```

`original_currency` is not decoration — §4.5 requires logging which symbol each
row originally carried, and this is where that survives into the output.

## 4. Requirements and tasks covered

| Requirement | Source | Task |
|---|---|---|
| Export a cleaned summary to a new CSV or JSON file | §4.4 | `P3.4` |
| Export results to a report file | §2 | `P3.4` |
| GitHub contains input and output datasets, or links | §5 | `P4.2` |
| Log which currency symbol each row originally had | §4.5 | `P2.3` `P3.4` |
| Record which dataset produced the results | §3 | `P0.2` `P4.3` |

## 5. Folders

| Folder | Contents |
|---|---|
| `implementation/` | `csv_export.py`, `json_export.py` |
| `testing/` | `test_csv_export.py`, `test_json_export.py` |
| `supplementary/` | `output_format_spec.md` |

## 6. Done when

- [ ] Both CSV and JSON export work
- [ ] Filenames follow the dated convention exactly
- [ ] The output names which dataset produced it
- [ ] `original_currency` is carried through
- [ ] The CSV reopens cleanly in Excel and in `csv.DictReader`
- [ ] Output folders are created if missing
