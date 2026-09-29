# output

Everything the program writes. Nothing here is edited by hand.

| Folder | Contains |
|---|---|
| `cleaned/` | `cleaned_<dataset>_<YYYY-MM-DD>.csv` — one row per valid transaction |
| `summaries/` | `summary_<dataset>_<YYYY-MM-DD>.json` — totals and run counts |
| `logs/` | `errors.log` — every skipped, corrected, or flagged row |

`errors.log` is that exact name because §4.1 requires it.

## Why these are not tracked in git day to day

Every run overwrites them, and committing each run would bury real changes in
noise. `.gitignore` excludes the contents.

**But §5 requires the repository to contain the output datasets.** So at `G4`,
when results are frozen for the report, the final files are committed
deliberately:

```bash
git add -f output/cleaned/cleaned_budgetwise_finance_dataset_2026-10-12.csv
git add -f output/summaries/summary_budgetwise_finance_dataset_2026-10-12.json
git add -f output/logs/errors.log
```

Dated filenames mean the committed outputs can be matched to the figures in the
report.
