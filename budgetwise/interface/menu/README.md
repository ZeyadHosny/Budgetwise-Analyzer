# menu

The interactive text menu. `main.py` starts it with `run_menu()`.

```
=== BudgetWise Finance Analyzer ===
1. Load full dataset
2. Load transactions by date range
3. Load transactions by category
4. View error log
5. Exit
Choose an option:
```

## Options

| Option | What it does |
|---|---|
| `1` | Runs the pipeline on the dataset in `budgetwise/settings.py` and prints the export paths and cleaning counts. |
| `2` | Shows the dataset's date range, asks for a start and end date (`YYYY-MM-DD`), and runs the pipeline on that range. Undated rows are excluded. |
| `3` | Lists the 14 categories, asks for one (case-insensitive), and runs the pipeline on that category. |
| `4` | Prints `output/logs/errors.log`, or a message if it does not exist. |
| `5` | Exits. |

The menu repeats after options 1-4.

## Invalid input

| Input | Response |
|---|---|
| Anything other than `1`-`5` | `Please choose 1 to 5.` and asks again |
| Invalid date, e.g. `2023-13-45` | `Not a valid date.` and asks again |
| End date before start date | Explains the problem and asks for both dates again |
| Range outside the data | Accepted, with a note that it falls outside the dataset range |
| Unknown category | Lists the valid categories and asks again |
| Missing dataset file | `Could not open the dataset` and returns to the menu |
| `Ctrl+C` or end of input | Exits without a traceback |

## Demo mode

Runs the menu on six built-in sample rows, without reading the CSV. Run from the repository folder:

```bash
python -m budgetwise.interface.menu.implementation.menu --demo
```

The unit tests use the same sample data (`demo_run`).

## Files

| Path | Contents |
|---|---|
| `implementation/menu.py` | Menu loop, input prompts, and result summary |
| `testing/test_menu.py` | Unit tests with `input()` patched |
| `supplementary/menu_flow.md` | Flow of each option through the program |

End-to-end menu tests are in `tests/end_to_end/test_menu_e2e.py`.
