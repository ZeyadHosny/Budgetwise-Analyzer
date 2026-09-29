# Project naming and rules

DATA 5010 — Project 1: Personal Finance & Spending Analyzer
Status: agreed at P0.1 · Last updated: 2026-09-29

This document is the single source of truth for how we name things and how work
reaches `main`. Read it once before your first task, then use the quick
reference at the end.

[Working on a task](#8-working-on-a-task) gives the full command sequence for a
single task, from branching through to merge.

---

## 1. How work reaches `main`

**`main` is protected. Nobody pushes to it directly.**

Every change — code, tests, or documentation — goes through a pull request (PR)
and needs **one approval before it merges**.

| Whose work | Who approves it |
|---|---|
| Bahareh, Henrieta, Sarah | Zeyad or Patrick |
| Zeyad | Patrick |
| Patrick | Zeyad |

Nobody approves their own work.

**Same-day review rule.** A PR opened before 6:00 PM gets reviewed that day.
If both reviewers are unavailable for more than 24 hours, post in the team chat
and the PR may be merged with a written note explaining why review was skipped.

Reviews should be small and quick. If a PR is hard to review, it is too big —
split it.

---

## 2. Branch names

```
<type>/<task-id>-<short-description>
```

Every branch carries its **workbook task ID** from
`DATA5010_Project1_Timeline_TeamPlan.xlsx`. This keeps the plan and the
repository speaking the same language: anyone can look at the open branches and
see exactly which planned tasks are in progress.

### Types

| Type | Use it for | Example |
|---|---|---|
| `feat` | New functionality | `feat/p2-1-date-parser` |
| `fix` | Correcting code already merged | `fix/p2-3-currency-suffix` |
| `test` | Tests added on their own | `test/p2-2-category-mapping` |
| `docs` | Documentation only | `docs/p0-1-shared-definitions` |
| `chore` | Config, `.gitignore`, tooling | `chore/repo-scaffold` |

### Rules

- **Lowercase only.** Use hyphens. Never underscores, never spaces.
- **Flatten the task ID:** `P2.1` becomes `p2-1`, `G2` becomes `g2`.
- **Keep it under about 50 characters.**
- **One branch per task.** Delete the branch after it merges.
- Description is 2–4 words saying what the branch does.

### Good and bad

```
GOOD   feat/p3-2-monthly-summaries
GOOD   fix/p2-4-duplicate-key
GOOD   docs/p0-1-project-rules

BAD    Feature/P2.1_DateParser      uppercase, underscores, dot
BAD    zeyad-branch                 names a person, not the work
BAD    fix                          which fix?
BAD    feat/p2-1-parse-all-the-dates-and-also-fix-the-logging-thing   too long
```

Branches are named after **work**, not after people. Members pick up more than
one area over the project, and a branch named after someone tells you nothing
about what is in it.

---

## 3. Commit messages

```
<TASK-ID>: <imperative summary>
```

```
P2.1: parse DD-MM-YY hyphen-separated dates
P2.4: log duplicate rows with reason codes
P3.2: add net balance calculation
```

- Start with the task ID in capitals, then a colon and a space.
- **Imperative mood**: "add", "fix", "parse" — not "added", "fixing".
- Keep the first line under 72 characters.
- If more explanation is needed, leave a blank line and write it below.

Commit small and often. A commit should be one coherent change you could
describe in one sentence.

---

## 4. Pull requests

**Title:** `P2.1 — Date parser and logging`

**Body:** state three things.

1. What changed.
2. Which requirements or checklist items it closes.
3. How you tested it.

**If your PR touches a shared file, say so in the title.** Shared files are
`models.py`, `loader.py`, anything in `config/`, and any agreed interface.
Changes there affect everyone's work, so they get closer review.

Example:

```
Title: P2.1 — Date parser and logging

What changed
  Added parse_date() handling the four date formats in the raw dataset.
  Unparseable dates return None and are written to errors.log with a reason.

Closes
  Requirement 4.5 "Date Parsing" — valid dates converted to YYYY-MM-DD.
  Requirement 4.5 "Missing date" — logged and excluded from date analysis.

How I tested
  Added tests/test_date_parser.py with 14 cases covering each format,
  the ambiguous MM/DD vs DD-MM rule, blanks, and junk input. All pass.
```

---

## 5. Python naming

| Thing | Convention | Example |
|---|---|---|
| Module (file) | `snake_case.py` | `date_parser.py` |
| Test module | `test_<module>.py` | `test_date_parser.py` |
| Class | `PascalCase` | `ExpenseTransaction` |
| Function, variable | `snake_case` | `parse_amount()` |
| Constant | `UPPER_SNAKE` | `SENTINEL_THRESHOLD = 100_000_000` |
| Protected attribute | `_single_underscore` | `self._balance` |
| Private attribute | `__double_underscore` | `self.__account_id` |

### Why the last two rows matter

These are not style preferences. The assignment grades us on encapsulation:

> "At least one class must demonstrate encapsulation using private/protected
> attributes and appropriate methods or properties to control access to those
> attributes." — Project-1.pdf §4.3

Writing `self._balance` instead of `self.balance` by habit means we satisfy this
requirement as we go, rather than trying to retrofit it the week before
submission.

### Other rules

- **No single-letter names** except loop counters (`i`, `j`) and comprehensions.
- **Names say what the thing is**: `expense_totals_by_month`, not `data2`.
- **Module names are nouns**, function names start with a **verb**:
  `parse_date()`, `normalize_category()`, `load_transactions()`.
- Use the standard library only for ingestion, cleaning, aggregation, and
  analysis. No pandas or NumPy in the core pipeline — see Project-1.pdf §2.

---

## 6. How the package fits together

Each feature lives in its own folder with the same three subfolders:

```
budgetwise/cleaning/dates/
├── README.md              who owns it, what it produces
├── __init__.py            ← what the rest of the team may use
├── implementation/        Bahareh's code
├── testing/               Bahareh's tests
└── supplementary/         Bahareh's findings for the report
```

This section explains the one file in there that is not obvious: `__init__.py`.

### `__init__.py` is the folder's front desk

It decides what the outside world can reach. Everything else in the folder is
private.

Suppose Bahareh writes her date parser at
`cleaning/dates/implementation/parser.py`:

```python
def parse_date(raw):
    ...
```

Her `__init__.py` contains one line:

```python
# budgetwise/cleaning/dates/__init__.py
from .implementation.parser import parse_date
```

Because of that line, everyone else writes:

```python
from budgetwise.cleaning.dates import parse_date          # works
```

**Delete that line and the same import fails:**

```
ImportError: cannot import name 'parse_date' from 'budgetwise.cleaning.dates'
```

The only thing that would work then is the full internal path:

```python
from budgetwise.cleaning.dates.implementation.parser import parse_date
```

### Why the short version matters

That long import looks like a cosmetic annoyance. It is not. It hard-codes
**where Bahareh keeps her files** into Patrick's code.

Picture the week after `G1`. Bahareh's `parser.py` has grown and she splits it
into `parser.py` and `formats.py`. A reasonable thing to do inside her own
folder.

| | With the front desk | Without it |
|---|---|---|
| Bahareh splits her file | Updates her own `__init__.py`. One line. | — |
| Patrick's code | Unchanged | **Breaks** |
| Sarah's code | Unchanged | **Breaks** |
| `pipeline/` | Unchanged | **Breaks** |
| Who has to be told | Nobody | Everyone |

With five people working in parallel, the second column is how a Tuesday
disappears.

### The rule this gives us

> **Never import from another feature's `implementation/` folder.**
> If you need something that is not exported in their `__init__.py`, ask the
> owner to export it. Do not reach in and take it.

This is what makes the folder structure real rather than decorative:

| Part of a feature folder | Who may change it | Review needed |
|---|---|---|
| `implementation/`, `testing/`, `supplementary/` | The owner alone. Rename, split, rewrite freely. | Normal |
| `__init__.py` | Changing it changes what everyone else depends on. | **Zeyad or Patrick** |

A feature's `__init__.py` is therefore the written agreement about what that
person is delivering. That is why they are written **first**, at `P1.5`, before
anyone starts implementing — so four people building cleaning modules in
parallel are all building against something already agreed.

### `testing/__init__.py` — a different, sharper reason

Test folders need one too, and skipping it fails in a way that is easy to miss.

Two identical tests, in two folders. One folder has `__init__.py`, the other
does not:

```
$ python -m unittest discover

Ran 1 test in 0.000s

OK
```

**It found one of the two and reported `OK`.** No warning. No error. The test in
the folder without `__init__.py` was never collected, and the run looked green.

This is the reason for the rule in section 8: *never treat a passing run as a
pass without checking how many tests ran.* A suite that silently shrinks is
worse than one that fails, because nobody investigates a green result.

### What this means in practice

| File | Who writes it | When |
|---|---|---|
| `<feature>/__init__.py` | Zeyad, with the owner | `P1.5`, before implementation starts |
| `implementation/__init__.py` | Already created, leave empty | — |
| `testing/__init__.py` | Already created, leave empty | — |

Right now each feature's `__init__.py` holds its intended contract as a comment:

```python
"""Date parsing. Converts raw date strings to YYYY-MM-DD."""

# Contract — uncomment once implementation/parser.py exists.
# from .implementation.parser import parse_date
```

Uncomment the line when your implementation file exists. Until then the package
imports cleanly and nothing is broken.

## 7. Data and output files

| File | Rule |
|---|---|
| Raw datasets | **Never renamed. Never edited.** Keep original Kaggle filenames in `data/raw/` |
| Error log | **`errors.log`** — this exact name is required by the assignment |
| Cleaned dataset | `cleaned_<dataset>_<YYYY-MM-DD>.csv` |
| Summary export | `summary_<dataset>_<YYYY-MM-DD>.json` |
| Docs inside `docs/` | `lower_snake_case.md` |
| Root-level standard files | `ALL_CAPS.md` — `README.md`, `CONTRIBUTING.md`, `LICENSE` |
| Folder readmes | exactly `README.md` |

Examples:

```
data/raw/budgetwise_finance_dataset.csv        original, untouched
data/raw/budgetwise_synthetic_dirty.csv        original, untouched
output/logs/errors.log                         required filename
output/cleaned/cleaned_budgetwise_finance_dataset_2026-10-12.csv
output/summaries/summary_budgetwise_finance_dataset_2026-10-12.json
```

**Why raw files are never renamed.** The original filename is part of the
dataset's provenance. The README records each file's row count and download
date, and those records only mean something if the filenames still match the
source.

**Why outputs carry a date.** At Gate 4 we freeze the results used in the
report. Dated filenames make "which run produced this number" a question with
an answer.

**Why markdown has two conventions.** A small set of filenames is recognised by
GitHub itself — `README.md` is rendered automatically when you open a folder,
and `CONTRIBUTING.md` is linked from the page where you open a pull request.
Those keep their conventional ALL-CAPS spelling so the platform recognises them.
Every other document is ordinary reference material and uses lowercase
`snake_case.md` like the rest of the repository.

---

## 8. Working on a task

The full sequence for one task, from start to merge.

```bash
# 1. Start from an up-to-date main
git checkout main
git pull

# 2. Create your branch, named after the task
git checkout -b feat/p2-1-date-parser

# 3. Do the work. Commit as you go.
git add budgetwise/cleaning/dates/implementation/parser.py
git add budgetwise/cleaning/dates/testing/test_parser.py
git commit -m "P2.1: parse DD-MM-YY hyphen-separated dates"

# 4. Run the tests before you push
python -m unittest discover

# 5. Push your branch
git push -u origin feat/p2-1-date-parser

# 6. Open a pull request on GitHub, request review
#    from Zeyad or Patrick, and fill in the three-part body.

# 7. Address any review comments, then merge.

# 8. Clean up
git checkout main
git pull
git branch -d feat/p2-1-date-parser
```

**Check how many tests ran, not just that it said `OK`.** A run reporting
`Ran 0 tests` is not a pass. Neither is a run that reports fewer tests than you
expected — see section 6 for how a missing `testing/__init__.py` silently drops a
whole folder while still printing `OK`. Note the number your suite normally
reports, and question it when it falls.

**We use `unittest` from the standard library**, so there is nothing to install.
`Project-1.pdf` §2 forbids pandas and NumPy in the core pipeline; using the
standard library for tests too removes any argument about where that line sits.

**If `git pull` reports a conflict**, stop and ask Zeyad or Patrick before
continuing. Conflicts are normal and fixable, but resolving one incorrectly can
silently delete a teammate's work.

---

## 9. Quick reference

```
BRANCH     <type>/<task-id>-<short-description>
           feat/p2-1-date-parser

COMMIT     <TASK-ID>: <imperative summary>
           P2.1: parse DD-MM-YY hyphen-separated dates

PR TITLE   P2.1 — Date parser and logging
           (add "[shared]" if it touches models.py, loader.py, or config/)

PYTHON     modules   date_parser.py        classes    ExpenseTransaction
           functions parse_date()          constants  SENTINEL_THRESHOLD
           protected self._balance         private    self.__account_id

FILES      errors.log                              (exact name, required)
           cleaned_<dataset>_<YYYY-MM-DD>.csv
           summary_<dataset>_<YYYY-MM-DD>.json
           raw data files are never renamed or edited

REVIEW     one approval before merge · nobody approves their own work
           PR before 6 PM is reviewed the same day

IMPORTS    from budgetwise.cleaning.dates import parse_date        yes
           from budgetwise.cleaning.dates.implementation.parser    no
           never import from another feature's implementation/
           changing your __init__.py needs review — it is a contract

TESTS      python -m unittest discover
           check the count, not just the OK
```

---

## Changing these rules

These conventions are a team agreement, not a fixed standard. To change one,
raise it with the team, and once agreed, update this file in a `docs/` branch
and note the date at the top. Do not change conventions silently — half the
repository following an old rule is worse than either rule on its own.
