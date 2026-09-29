# config

Values the program reads at startup, kept as data rather than hard-coded so that
changing them does not mean changing code — and so they can go into the report
as evidence.

| File | Owner | Task | Required by |
|---|---|---|---|
| `category_mapping.csv` | Henrieta | `P1.2` `P2.2` | §4.5 — mapping must be documented and included in the report |
| `monthly_budgets.json` | Patrick | `P3.3` | §4.4 — at least five categories, with justification |

## category_mapping.csv

Every raw category string found in the data, mapped to a normalized name. The
mapping must be **closed** — §4.5 requires that every raw value has an entry, so
nothing falls through silently.

Pre-filled from the real data: all **47** distinct raw category strings found in
`budgetwise_finance_dataset.csv`, with their row counts.

| Column | Meaning |
|---|---|
| `raw` | The string as it appears in the data |
| `proposed_normalized` | The suggested canonical name |
| `rows` | How many rows carry this raw value |
| `decision` | `ok` — settled · `G1` — the team must decide |
| `note` | Whether it is an exact match, case variant, or typo, and what is contested |

Grouping the 47 strings into families is not in doubt — `FOOD`, `Fod`, and
`Foodd` are plainly the same thing. What each family should be **called** is,
because the data and the assignment's example list disagree.

### Six names need deciding at G1

§4.5's example canonical set is *Food, Rent, Transportation, Entertainment,
Shopping, Utilities, Healthcare, Education, Salary, Investment, Other,
Uncategorized*. It is an example, not a mandate — but the differences should be
deliberate:

| Proposed | Rows | The question |
|---|---|---|
| `Travel` | 1,985 | The example list says **Transportation**. Keep `Travel`, or rename? |
| `Health` | 623 | The example list says **Healthcare**. Keep `Health`, or rename? |
| `Others` | ~560 | The example list says **Other**, singular. Also folds in `Misc` |
| `Bonus` | 442 | Income category, absent from the example list. Keep, or fold into `Salary`? |
| `Freelance` | 490 | Income category, absent from the example list. Keep, or fold into `Salary`? |
| `Savings` | 195 | Absent from the example list. Keep, or fold into `Investment`? |

Note also that **`Shopping`** appears in the example list but never in the data —
no rows map to it. Say so in the report rather than leaving a reader to wonder.

Whatever is decided, record it in
`budgetwise/cleaning/categories/supplementary/mapping_rationale.md`. §4.5
requires the mapping appear in the report, and a set that departs from the
assignment's example needs a sentence explaining why.

## monthly_budgets.json

Monthly spending limits per category. §4.4 requires at least five, **and requires
them justified**. The justification goes in
`budgetwise/analysis/budgets/supplementary/budget_justification.md` — it is a
graded part of the report, not a note.

The file ships with five placeholder limits. Replace them with figures the team
can defend, and record the reasoning.
