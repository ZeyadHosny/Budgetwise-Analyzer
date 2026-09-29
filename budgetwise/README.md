# budgetwise

The application package. Every feature lives in its own folder and follows the
same shape, so that once you understand one folder you understand all of them.

## How a feature folder is arranged

```
cleaning/dates/
├── README.md              owner, reviewer, tasks, what it produces
├── __init__.py            the public surface — what other modules may import
├── implementation/        the code the program actually runs
├── testing/               tests and fixtures for this feature only
└── supplementary/         profiling findings and report evidence
```

| Folder | What belongs here | Who reads it |
|---|---|---|
| `implementation/` | The working code. One concern per file. | The program |
| `testing/` | Tests and small fixtures for this feature alone. Whole-pipeline tests live in `/tests/`. | `python -m unittest discover` |
| `supplementary/` | Phase 1 profiling output and the evidence `P4.4` needs for the report. | Whoever writes the report |

## Imports stay flat

Folders are deep, but nobody types deep paths. Each feature's `__init__.py`
re-exports its public functions:

```python
# budgetwise/cleaning/dates/__init__.py
from .implementation.parser import parse_date
```

so every other module writes:

```python
from budgetwise.cleaning.dates import parse_date
```

**A feature's `__init__.py` is its contract.** If it is not exported there, no
other module may use it. Changing that file affects everyone, so it needs review
from Zeyad or Patrick.

## The features

| Feature | Owner | Tasks | Does |
|---|---|---|---|
| `loader/` | **unassigned** | — | Reads the CSV and yields numbered raw rows |
| `pipeline/` | Sarah, Zeyad | `G2` | Runs raw rows through the cleaners and builds objects |
| `models/` | Zeyad | `P2.5` | Transaction and Budget classes |
| `errorlog/` | Sarah | `P2.4` | Writes `errors.log` and owns the reason codes |
| `cleaning/dates/` | Bahareh | `P1.1` `P2.1` | Date parsing |
| `cleaning/categories/` | Henrieta | `P1.2` `P2.2` | Category normalization |
| `cleaning/amounts/` | Patrick | `P1.3` `P2.3` | Amount and currency parsing |
| `cleaning/rows/` | Sarah | `P1.4` `P2.4` | Duplicates and row validation |
| `analysis/aggregation/` | Henrieta | `P3.1` | Totals by category and month |
| `analysis/summaries/` | Bahareh | `P3.2` | Income, expenses, balance, top five |
| `analysis/budgets/` | Patrick | `P3.3` | Budget vs actual |
| `interface/menu/` | Sarah | `P3.4` | The text menu and filters |
| `interface/charts/` | Sarah | `P3.4` | Text bar chart |
| `interface/export/` | Sarah | `P3.4` | CSV and JSON export |
| `metrics/` | Zeyad | `P3.5` | Timings and run counts |

Phase 2 folders exist now. Phase 3 folders are created when Phase 3 begins.

## Rules that apply everywhere

- **Standard library only** in ingestion, cleaning, aggregation, and analysis.
  No pandas, no NumPy — see `Project-1.pdf` §2.
- **Cleaning functions never raise.** They return a value and a reason code.
- **Cleaning functions never print and never read files.** `pipeline/` supplies
  the data; `interface/` does the talking.
- **Protected attributes use `_name`, private use `__name`.** §4.3 grades this.
