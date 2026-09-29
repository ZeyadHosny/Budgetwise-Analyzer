# BudgetWise Personal Finance & Spending Analyzer

DATA 5010 — Project 1
Due **Mon Oct 19, 2026, 11:59 PM EST**

A Python application that reads real transaction data, cleans and validates it,
models it with object-oriented classes, and reports spending summaries and
budget comparisons.

Built with the **Python standard library only** for ingestion, cleaning,
aggregation, and analysis, as required by the assignment.

## Running it

```bash
python main.py
```

No installation and no dependencies — Python 3.10 or newer is all that is
needed.

```
=== BudgetWise Finance Analyzer ===
1. Load full dataset
2. Load transactions by date range
3. Load transactions by category
4. View error log
5. Exit
```

## Running the tests

```bash
python -m unittest discover
```

Check the number of tests reported, not just that it says `OK`. See
`CONTRIBUTING.md` §6 for why.

## The data

Both files live in `data/raw/` and are never modified. See
[`data/README.md`](data/README.md) for row counts, provenance, and the evidence
on which one the assignment was written against.

## Where things are

| Path | Contents |
|---|---|
| `main.py` | Entry point |
| `budgetwise/` | The application — one folder per feature |
| `config/` | Category mapping and monthly budget limits |
| `data/raw/` | The original datasets, untouched |
| `output/` | Cleaned exports, summaries, and `errors.log` |
| `tests/` | Whole-pipeline tests |
| `docs/` | Requirements checklist and team documents |

Start at [`budgetwise/README.md`](budgetwise/README.md) — it explains how a
feature folder is arranged and lists who owns each one.

## Understanding the output

| File | Contains |
|---|---|
| `output/cleaned/cleaned_<dataset>_<date>.csv` | One row per valid transaction, cleaned and standardized |
| `output/summaries/summary_<dataset>_<date>.json` | Totals, top categories, budget comparison, run counts |
| `output/logs/errors.log` | Every row skipped, corrected, or flagged, with the reason |

Filenames carry the dataset and the run date, so any figure in the report can be
traced back to the run that produced it.

## Contributing

Read [`CONTRIBUTING.md`](CONTRIBUTING.md) before your first change. It covers
branch and commit naming, the review process, and how the package fits together.

## Status

Scaffolded. The structure, documentation, and requirements mapping are in place;
the implementation is not yet written. See
[`docs/requirements_checklist.md`](docs/requirements_checklist.md).
