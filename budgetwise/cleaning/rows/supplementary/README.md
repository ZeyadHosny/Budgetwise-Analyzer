# cleaning/rows/supplementary

| File | Task | Feeds |
|---|---|---|
| `duplicate_profile.md` | `P1.4` | report — implementation details |

Record the duplicate key chosen and why, the 900 exact duplicates, the 1,900
repeated ids deliberately kept, and the blank counts per column:

```
date 486 · category 285 · amount 291 · payment_mode 808
location 931 (+331 "nan") · notes 2,335 (+486 "nan")
```

The distinction between 900 and 1,900 is worth stating plainly in the report. It
is the clearest example in the project of a rule that looks like a detail and
changes thousands of rows.
