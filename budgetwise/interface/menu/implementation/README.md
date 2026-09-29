# interface/menu/implementation

Sarah · `P3.4` · domain reviewer Bahareh

## Write these

```python
run_menu() -> None                 the while loop
prompt_date_range() -> tuple[str, str]
prompt_category() -> str
```

## The menu is fixed by the assignment

Print these five options, in this order. Option 3 is required even though §4.1's
prose only mentions a date range — the printed block in the PDF includes it.

## Every prompt must survive nonsense

Three people will demo this live at the presentation, and an audience member may
well be invited to try it. Nothing typed at a prompt should produce a traceback:

| Input | Response |
|---|---|
| `9` | `Please choose 1 to 5.` and reprompt |
| `banana` | same |
| empty | same |
| `2023-13-45` at a date prompt | `Not a valid date.` and reprompt |
| end date before start date | `End date is before start date.` and reprompt |
| a category that does not exist | show the available categories |
| `Ctrl+C` | exit cleanly, no traceback |

## This module owns the printing

Everywhere else in the package returns values. `interface/` is the only place
`print()` and `input()` appear. That separation is what lets every other module
be tested without simulating a user.

## Bring the skeleton forward

`P3.4` sits in Phase 3, after `G2` — but `G2` has to demonstrate that the
dataset loads and cleans, and this is the only thing that runs the pipeline. A
bare version with option 1 and option 5 working is enough for `G2`, and it is
work you keep rather than a throwaway script.

## Do not

- Put calculation here — call `analysis/`
- Read files — call `pipeline.run()`
- Import pandas or numpy — violates §2
