# tests

Whole-pipeline tests. Tests for a single feature live beside that feature, in its
own `testing/` folder.

| File or folder | Task | Owner | Purpose |
|---|---|---|---|
| `test_structure.py` | `P0.1` | Zeyad | The repository keeps its agreed shape |
| `end_to_end/` | `G3` | Patrick | Full dataset runs and produces correct outputs |
| `robustness/` | `P4.1` | Sarah | Malformed input never crashes the program |

## test_structure.py — runs today, before any feature exists

Eight tests guarding three things that otherwise fail **silently**:

| Guard | Why it matters |
|---|---|
| Every feature folder has its seven required files | Nobody arrives to find their workspace half-missing |
| Every `testing/` folder has `__init__.py` | Without it, unittest skips that folder and still prints `OK` — see `CONTRIBUTING.md` §6 |
| No `pandas` or `numpy` anywhere in `budgetwise/` or `main.py` | `Project-1.pdf` §2 forbids it and **no workbook task checks it** |
| `data/raw/` totals 2,184,425 bytes | Matches what Kaggle publishes; catches line-ending corruption of the raw data |

The pandas check is the valuable one. §2's restriction is the single constraint
that could undermine the whole submission, and until now nothing enforced it. Now
a stray `import pandas` fails the suite the moment it is added, rather than being
noticed at `G3` — or not at all.

## Why these are separate

A test in `budgetwise/cleaning/dates/testing/` asks whether date parsing works.
A test here asks whether the **program** works — the loader, four cleaners, the
models, the analysis, and the export, together, on 15,900 real rows.

`G3`'s rule is that **each member tests a module they did not own**. These
folders are deliberately shared ground: nobody owns them, so nobody is marking
their own work.

## Running

```bash
python -m unittest discover
```

Discovers tests here and inside every feature folder in one pass.

## end_to_end — G3

The full dataset, start to finish, verifying the mandatory conventions hold in
the real output:

- All 900 duplicates removed, all 1,900 repeated ids kept
- No amount at or above 100,000,000 in any total
- Every date in the output is `YYYY-MM-DD`
- Every category is in the agreed canonical set
- Counts reconcile: input = valid + skipped + duplicates
- Both CSV and JSON exports written and re-readable

## robustness — P4.1

Deliberately hostile input. The program must not crash on any of it:

- Empty file, header only, header missing a column
- Rows with too few and too many fields
- Dates such as `31/02/2023`, `99-99-99`, `14th July`
- Amounts such as `abc`, `₹₹5`, `--5`, `999999999`
- A file with no valid rows at all
- Every field blank on the same row
