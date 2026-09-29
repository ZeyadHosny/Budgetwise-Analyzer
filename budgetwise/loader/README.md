# loader

Reads the raw CSV and hands out numbered rows. It does no cleaning.

| | |
|---|---|
| **Responsible** | **Unassigned — a task needs to be created** |
| **Domain reviewer** | Zeyad (interface) |
| **PR approval** | Zeyad or Patrick — see `CONTRIBUTING.md` |
| **Tasks** | None. This work is not in the workbook. |
| **Status** | Not started · **blocked on assigning an owner** |

## 1. What this folder does

Opens a dataset file, checks the header, and yields one raw row at a time
with its line number attached. It validates nothing about the *contents* of a
row — a row full of garbage is still passed on, because deciding what counts as
garbage belongs to the cleaning modules.

The row number matters: every entry in `errors.log` has to say which line it
came from, and that is the only place the number is known.

Both datasets have the same nine columns:

```
transaction_id · user_id · date · transaction_type · category
amount · payment_mode · location · notes
```

## 2. How other modules use it

```python
from budgetwise.loader import load_rows

for line_no, row in load_rows("data/raw/budgetwise_finance_dataset.csv"):
    ...   # row is a dict of raw strings, exactly as read
```

Only `pipeline/` calls this.

## 3. What it produces

| Situation | Result |
|---|---|
| Valid file | Yields `(2, {...})`, `(3, {...})`, … — numbering starts at 2, the first data line |
| File missing | Raises `FileNotFoundError` with the attempted path |
| Header wrong | Raises `ValueError` naming the missing or unexpected columns |
| Row has too few fields | Yielded anyway, with missing keys set to `""` |

This is the one module permitted to raise, because a file that cannot be opened
is not a data-quality problem — it is a setup problem, and the user must be told
immediately.

## 4. Requirements and tasks covered

| Requirement | Source | Task |
|---|---|---|
| Read transaction data from the BudgetWise CSV file(s) | §4.1 | **none — task needed** |
| Ingest transaction data from CSV files | §2 | **none — task needed** |
| Program must not crash on bad input | §4.1 | `P4.1` |

`G2` requires "the integrated loader/cleaner creates transaction objects without
crash", but no task builds this. See `docs/requirements_checklist.md`, task 1.

## 5. Folders

| Folder | Contents |
|---|---|
| `implementation/` | `csv_reader.py`, `header_check.py` |
| `testing/` | `test_csv_reader.py`, `fixtures/malformed_rows.csv` |
| `supplementary/` | `loader_interface_notes.md` |

## 6. Done when

- [ ] Reads both CSVs in `data/raw/` without error
- [ ] Line numbers match the file exactly — check one by hand
- [ ] Missing file and bad header raise clear, named errors
- [ ] Short rows are yielded, not dropped
- [ ] Reads the whole 15,900-row file without loading it all into memory
