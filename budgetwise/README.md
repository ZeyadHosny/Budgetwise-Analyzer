# budgetwise

The application package. Every feature lives in its own folder and follows the
same shape, so once you understand one folder you understand all of them.

## How a feature folder is arranged

```
cleaning/dates/
├── README.md              owner, reviewer, tasks, what it produces
├── __init__.py            the public surface: what other modules may import
├── implementation/        the code the program runs
├── testing/               tests and fixtures for this feature
└── supplementary/         profiling findings and report evidence
```

| Folder | What belongs here | Who reads it |
|---|---|---|
| `implementation/` | The working code. One concern per file. | The program |
| `testing/` | Tests and small fixtures for this feature alone. Whole-program tests live in `/tests/`. | `python3 -m unittest discover` |
| `supplementary/` | Profiling output and the evidence needed for the report. | Whoever writes the report |

Every `testing/` folder needs an `__init__.py`; without it, its tests are
silently skipped.

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

Owners are taken from each feature's own README. Rows marked *confirm* disagree
between files and need checking by the team.

### Phase 2: loading and cleaning

| Feature | Owner | Task | Does |
|---|---|---|---|
| `loader/` | Patrick | `P2.9` | Reads the CSV and returns numbered raw rows |
| `errorlog/` | Patrick | `P2.8` | Writes `errors.log` and owns the shared `Reason` codes |
| `cleaning/dates/` | Sarah | `P2.1` | Converts every date to `YYYY-MM-DD` |
| `cleaning/categories/` | Henrietta | `P2.2` | Maps category variants to the approved set |
| `cleaning/amounts/` | Patrick | `P2.3` | Turns amount text into unsigned numbers |
| `cleaning/rows/` | Sarah | `P2.4` | Finds exact duplicate rows and checks each row is usable |
| `cleaning/payment_modes/` | Henrietta | `P2.5` | Maps payment modes to standard names |
| `cleaning/locations/` | Henrietta | `P2.6` | Maps locations to standard city names |
| `cleaning/notes/` | Sarah | `P2.7` | Labels note quality; note text is never changed |
| `pipeline/` | Sarah | `P2.10` | Runs every cleaner in order, builds transaction objects and accounts |

### Phase 3: models, analysis and interface

| Feature | Owner | Task | Does |
|---|---|---|---|
| `models/` | Zeyad | `P3.1` | Transaction and account classes |
| `analysis/aggregation/` | Henrietta | `P3.2` | Totals by category and by month |
| `analysis/summaries/` | Bahareh | `P3.3` | Income, expenses, balance, rankings and account summaries |
| `analysis/budgets/` | Patrick | *confirm* | Budget against actual spending |
| `interface/menu/` | Zeyad | `P3.5` | The text menu and filters; the program's entry point |
| `interface/charts/` | Henrietta | `P3.6` | Text bar chart of spending |
| `interface/export/` | *confirm* (Sarah or Patrick) | *confirm* (`P3.4` or `P3.7`) | CSV and JSON export |
| `metrics/` | Henrietta | `P3.8` | Run counts and timings |

All folders now exist. `analysis/budgets/` and `interface/export/` hold only
their READMEs so far.

## Rules that apply everywhere

- **Standard library only** in loading, cleaning, aggregation and analysis.
  No pandas, no NumPy (`Project-1.pdf` section 2).
- **Cleaning functions never raise.** They return a value and a reason code.
- **Cleaning functions never print and never read files.** `pipeline/` supplies
  the data; `interface/` does the talking.
- **Protected attributes use `_name`, private use `__name`.** Section 4.3 grades this.
