# interface/menu

The text menu the user drives the program with.

| | |
|---|---|
| **Responsible** | Sarah |
| **Domain reviewer** | Zeyad (`P1.5` skeleton) · Bahareh (`P3.4`) |
| **PR approval** | Zeyad or Patrick — see `CONTRIBUTING.md` |
| **Tasks** | `P1.5` skeleton · `P3.4` implementation |
| **Status** | Not started |

## 1. What this folder does

The program's front door. §4.1 is explicit that this must be an **interactive
menu, not a one-shot script** — a `while` loop reading `input()` that lets the
user choose what gets loaded.

The assignment prints the menu it expects, so it is not open to interpretation:

```
=== BudgetWise Finance Analyzer ===
1. Load full dataset
2. Load transactions by date range
3. Load transactions by category
4. View error log
5. Exit
Choose an option:
```

All five options are graded separately. **Option 3 is the one teams miss** — the
prose in §4.1 mentions only a date range, and the category filter appears solely
in this block.

## 2. How other modules use it

```python
from budgetwise.interface.menu import run_menu

run_menu()      # called by main.py, and nothing else
```

This module calls `pipeline.run()` and the display modules. Nothing calls it
except `main.py`.

## 3. What it produces

A session:

```
=== BudgetWise Finance Analyzer ===
1. Load full dataset
...
Choose an option: 2
Start date (YYYY-MM-DD): 2023-01-01
End date   (YYYY-MM-DD): 2023-12-31

Loaded 3,842 transactions (2023-01-01 to 2023-12-31)
  Skipped 214 rows — see output/logs/errors.log
```

Invalid input never crashes:

```
Choose an option: 9
  Please choose 1 to 5.

Choose an option: banana
  Please choose 1 to 5.
```

## 4. Requirements and tasks covered

| Requirement | Source | Task |
|---|---|---|
| Menu-driven loading, interactive, not a one-shot script | §4.1 | `P3.4` |
| `while` loop reading `input()` | §4.1 | `P3.4` |
| Option 1 — load full dataset | §4.1 | `P3.4` |
| Option 2 — load by date range | §4.1 | `P3.4` |
| Option 3 — load by category | §4.1 | `P3.4` |
| Option 4 — view error log | §4.1 | `P3.4` |
| Option 5 — exit | §4.1 | `P3.4` |
| Invalid input handled without crashing | §4.1 | `P3.4` `P4.1` |
| Text-based menu, no GUI | §2 | `P3.4` |

## 5. Folders

| Folder | Contents |
|---|---|
| `implementation/` | `menu.py`, `prompts.py`, `filters.py` |
| `testing/` | `test_menu.py`, `test_filters.py` |
| `supplementary/` | `menu_flow.md` |

## 6. Done when

- [ ] All five options work
- [ ] Option 3 exists — the one most often missed
- [ ] Invalid input reprompts instead of crashing
- [ ] Malformed dates at the prompt are rejected politely
- [ ] `Ctrl+C` exits without a traceback
- [ ] `menu_flow.md` written — feeds the report's flow diagram
