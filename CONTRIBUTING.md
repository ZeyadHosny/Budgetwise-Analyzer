# Contributing

DATA 5010 - Project 1: Personal Finance & Spending Analyzer
Last updated: 2026-10-19

## Pull requests

All changes reach `main` through a pull request with one approval from another team member. Nobody approves their own work.

A pull request description states what changed, which requirement it covers, and how it was tested. Mention in the title if it changes a shared file: `budgetwise/settings.py`, `budgetwise/models/`, `budgetwise/loader/`, `config/`, or any feature's `__init__.py`.

## Branches and commits

Branch: `<type>/<task-id>-<short-description>`, lowercase with hyphens, e.g. `feat/p3-6-text-bar-chart`.
Types: `feat`, `fix`, `test`, `docs`, `chore`.

Commit: `<TASK-ID>: <imperative summary>`, e.g. `P2.6: map Bengaluru to Bangalore`.

Delete a branch after it is merged.

## Package layout

Each feature folder under `budgetwise/` contains:

```
README.md          what the feature does and produces
__init__.py        the functions and classes other features may import
implementation/    code
testing/           unit tests (must contain __init__.py)
supplementary/     evidence for the report (optional)
```

Import from a feature's package, not from its `implementation/` folder:

```python
from budgetwise.cleaning.dates import parse_date                     # yes
from budgetwise.cleaning.dates.implementation.parser import parse_date  # no
```

Shared settings (dataset path and budget baseline) are in `budgetwise/settings.py`.

## Code rules

- Standard library only for loading, cleaning, aggregation, and analysis. `tests/test_structure.py` fails if `pandas` or `numpy` is imported.
- `snake_case` for modules, functions, and variables; `PascalCase` for classes; `UPPER_SNAKE` for constants.
- Use `_protected` or `__private` attributes with properties where access needs control.

## Data and outputs

- Raw files in `data/raw/` keep their Kaggle filenames and are never edited.
- Generated files use the run date:
  - `output/cleaned/cleaned_<dataset>_<YYYY-MM-DD>.csv`
  - `output/summaries/summary_<dataset>_<YYYY-MM-DD>.json`
  - `output/summaries/charts_<dataset>_<YYYY-MM-DD>.txt`
  - `output/logs/errors.log`
- `output/` is ignored by Git. Add submission results with `git add -f`.

## Tests

Run from the repository folder before opening a pull request:

```bash
python -m unittest discover
```

The current result is `Ran 806 tests ... OK (expected failures=3)`. Check the number of tests, not only `OK`; a `testing/` folder without `__init__.py` is skipped silently.

## Quick reference

```
BRANCH   feat/p3-6-text-bar-chart
COMMIT   P2.6: map fooood to Food
REVIEW   one approval, never your own
IMPORT   from budgetwise.<area>.<feature> import <name>
TESTS    python -m unittest discover   (806 tests, 3 expected failures)
```
