# Menu flow

sec 5 requires a *"design flow diagram based on important subroutines"*. The
menu is where every path through the program begins, so this is the backbone
of that diagram.

## The loop

```
run_menu()
└── while True:
    ├── print the banner and five options
    ├── choice = prompt_choice()          reprompts on anything but 1-5
    └── dispatch
```

## Option 1 - load full dataset

```
run(dataset)                              P2.10 Sarah
└── returns {transactions, accounts, counts, timings}
format_summary(result)                    prints the counts
```

## Option 2 - load by date range

```
prompt_date_range()
├── _read_date("Start date")              reprompts on a bad date
├── _read_date("End date")
└── rejects an end before the start
run(dataset, start=..., end=...)
```

Rows with no date cannot fall inside a range, so the 486 undated rows drop out
here - they are present under option 1.

## Option 3 - load by category

```
prompt_category()
├── matches case-insensitively
└── lists the 14 canonical names when the input is unknown
run(dataset, category=...)
```

The filter runs **after** normalization, so `food`, `Fod` and `Foodd` all
match `Food`.

## Option 4 - view error log

```
view_error_log()                          reads output/logs/errors.log
```

No pipeline run at all. An absent or empty log gets a message rather than
blank output.

## Option 5 - exit

`return` from `run_menu()`. Nothing to save - exports happen during a load.

## Anything else

Reprompt. `Ctrl+C` and end-of-input exit cleanly without a traceback.

## Why the pipeline is injected

`run_menu(pipeline_run=...)` takes the pipeline as an argument rather than
importing it. Two reasons: the tests can drive the whole loop with a stub, and
this module compiles today even though `P2.10` is not written yet. Once the
pipeline lands, `main.py` passes the real `run`.
