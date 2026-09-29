# pipeline

Runs raw rows through every cleaner and builds the cleaned dataset.

| | |
|---|---|
| **Responsible** | Sarah, with Zeyad |
| **Domain reviewer** | All team (`G2`) |
| **PR approval** | Zeyad or Patrick — see `CONTRIBUTING.md` |
| **Tasks** | `G2` |
| **Status** | Not started |

## 1. What this folder does

The orchestration layer. It takes raw rows from `loader/`, puts them through
the four cleaning modules in the correct order, builds `Transaction` objects, and
returns them along with the counts and timings the report needs.

**Order matters and is mandatory.** Duplicate detection runs on raw rows *before*
any normalization (§4.5). Normalizing first would collapse `FOOD` and `Food` into
one value and make rows look identical that were not.

```
raw row
  → duplicate check      (cleaning/rows — on the raw row, before anything else)
  → date parse           (cleaning/dates)
  → amount parse         (cleaning/amounts)
  → category normalize   (cleaning/categories)
  → required-field check (cleaning/rows)
  → Transaction object   (models)
```

## 2. How other modules use it

```python
from budgetwise.pipeline import run

result = run("data/raw/budgetwise_finance_dataset.csv")
result.transactions     # list of Transaction objects
result.counts           # dict of the numbers the report needs
result.timings          # seconds for load, clean, total
```

`main.py` and `interface/menu/` call this. Nothing else.

## 3. What it produces

A `LoadResult` carrying:

| Field | Example | Feeds |
|---|---|---|
| `transactions` | list of 14,100 objects | all of `analysis/` |
| `counts["input"]` | 15,900 | report — number of input records |
| `counts["valid"]` | 14,100 | report — number of valid records |
| `counts["corrected"]` | 4,802 | report — number of corrected records |
| `counts["skipped"]` | 900 | report — invalid/skipped records |
| `counts["duplicates"]` | 900 | report — duplicates detected |
| `counts["categories_normalized"]` | 12,300 | report — categories normalized |
| `timings` | `{"load": 0.4, "clean": 1.9}` | report — execution time |

Those seven counts are named individually in §5 as required results. They are
produced here because this is the only place that sees every row.

## 4. Requirements and tasks covered

| Requirement | Source | Task |
|---|---|---|
| Duplicate detection performed on raw rows before normalization | §4.5 | `P2.4` `G2` |
| Store transactions as a list of objects | §4.2 | `G2` |
| Program must not crash on bad input | §4.1 | `G2` `P4.1` |
| Number of input / valid / corrected / skipped records | §5 | `P3.5` |
| Number of duplicates detected, categories normalized | §5 | `P3.5` |
| Execution time for loading, cleaning, analysis | §5 | `P3.5` |

## 5. Folders

| Folder | Contents |
|---|---|
| `implementation/` | `pipeline.py`, `stages.py` |
| `testing/` | `test_pipeline.py`, `fixtures/mini_dataset.csv` |
| `supplementary/` | `integration_notes.md`, `interface_conflicts.md` |

## 6. Done when

- [ ] Full 15,900-row dataset runs start to finish without raising
- [ ] All seven counts produced and cross-checked by hand on a small file
- [ ] Duplicate detection demonstrably runs before normalization
- [ ] Every skipped or corrected row appears in `errors.log`
- [ ] `counts["input"]` equals the file's row count exactly
