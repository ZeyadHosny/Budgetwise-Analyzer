# menu

The interactive text menu - the program's entry point.

| | |
|---|---|
| **Responsible** | Zeyad |
| **Domain reviewer** | Patrick (`P3.5`) |
| **Task** | `P3.5` |
| **Assignment** | sec 4.1 menu-driven loading, five options, `while` loop over `input()`; sec 2 text menu, no GUI |
| **Depends on** | `P2.10` `run()` - Sarah; `P3.3` `P3.4` `P3.6` `P3.7` for display |
| **Status** | Implemented; the pipeline it calls is not yet written |

## The five options

sec 4.1 prints the menu it expects, so this is not open to interpretation:

```
=== BudgetWise Finance Analyzer ===
1. Load full dataset
2. Load transactions by date range
3. Load transactions by category
4. View error log
5. Exit
Choose an option:
```

**Option 3 is the one teams miss.** sec 4.1's prose mentions only a date
range; the category filter appears solely in the printed block.

## Nothing may crash

sec 7 grades *"the program runs on real, messy data without crashing"*, and
this is demonstrated live on Oct 19.

| Input | Response |
|---|---|
| `9`, `banana`, empty | `Please choose 1 to 5.` and reprompt |
| `2023-13-45` at a date prompt | `Not a valid date.` and reprompt |
| end date before start | rejected and reprompt |
| unknown category | lists the available ones and reprompts |
| `Ctrl+C` | exits cleanly, no traceback |

## This module owns the printing

Everywhere else returns values. `interface/` is the only place `print()` and
`input()` appear - that separation is what lets every other module be tested
without simulating a user.

## Running it before the pipeline exists

`run()` is `P2.10`. Until it lands, the menu runs against a small built-in
sample so the flow can be demonstrated:

```bash
python implementation/menu.py --demo
```

Remove the fallback once `P2.10` is merged.

## Folders

| Folder | Contents |
|---|---|
| `implementation/` | `menu.py` |
| `testing/` | `test_menu.py` - 18 cases, `input()` patched |
| `supplementary/` | `menu_flow.md` - feeds sec 5's design flow diagram |
