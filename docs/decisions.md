# Decision record

Every decision the team makes that affects more than one person. Date it, name
who agreed it, and say what evidence supported it.

A decision that is not written down gets re-argued. A decision without its
reasoning cannot be defended in the report or in Q&A.

## Format

```
## D01 — Short title
Date · Decided by · Task
**Decision:** what was agreed.
**Why:** the reasoning and evidence.
**Affects:** which modules or documents.
```

---

## Open — to be closed at G1

These block work that is already scheduled. Each needs a decision, not a
discussion.

| # | Decision | Task | Blocks |
|---|---|---|---|
| D01 | Which CSV is the official dataset | `P0.2` | every reported figure |
| ~~D02~~ | ~~Whether the Kaggle licence permits committing raw data~~ | `P0.2` `P4.3` | **closed — see below** |
| D03 | Class design, given the data has no account-type field | `P2.5` | `models/`, the report |
| D04 | The closed category set — six contested names | `P1.2` | `cleaning/categories/`, every total |
| D05 | Shared interfaces — raw row, cleaned row, transaction, error entry | `P1.5` | all four cleaners |
| D06 | Budget scope — which five categories, what limits, what justification | `P3.3` | `analysis/budgets/`, the report |
| D07 | How to handle the missing merchant column | `P4.4` | §4.2 compliance |
| D08 | Corrected vs skipped — where the boundary sits | `P3.5` | three reported counts |
| D09 | Who owns the CSV loader | — | all of Phase 2 |

### D01 — dataset evidence already gathered

`data/README.md` sets out the case that `budgetwise_finance_dataset.csv` is the
file the assignment was written against: it is the only one containing `Rs.` and
`INR` labels, the only one with `999999999` sentinel rows, and the only one whose
per-symbol medians fall in the 5,600–6,600 band §4.5 cites. The decision still
needs making and recording.

### D04 — the six contested category names

`config/category_mapping.csv` marks 20 rows `G1` across six names: `Travel`
(vs *Transportation*), `Health` (vs *Healthcare*), `Others` (vs *Other*),
`Bonus`, `Freelance`, and `Savings` — the last three absent from the
assignment's example list entirely. Also note `Shopping` appears in the example
list but in neither dataset.

---

## Closed

## D02 — The dataset licence permits committing the raw files

2026-09-29 · verified against Kaggle's dataset metadata API · `P0.2` `P4.3`

**Decision:** Both CSV files are committed to the repository. The repository may
be public. No Kaggle-only link is required.

**Why:** The dataset is licensed **CC0: Public Domain**. The author has waived
all copyright and related rights, so the data may be copied, modified, and
redistributed by anyone without permission or attribution.

§3's instruction is conditional — *"if the dataset licence restricts
redistribution"* — and CC0 imposes no restriction, so the condition does not
apply.

Verified from `https://www.kaggle.com/api/v1/datasets/view/mohammedarfathr/budgetwise-personal-finance-dataset`:

```json
{
  "licenseName": "CC0: Public Domain",
  "title": "BudgetWise Personal Finance Dataset",
  "ownerName": "Mohammed Arfath R",
  "totalBytes": 2184425,
  "lastUpdated": "2025-09-29T14:30:50.82Z"
}
```

Kaggle's reported 2,184,425 bytes matches the two local files exactly
(1,042,312 + 1,142,113), confirming both published files are present and
complete.

**Affects:** `data/raw/` keeps both CSVs · `.gitignore` continues not to exclude
them · the repository may be public · `README.md` still cites the Kaggle page and
download steps, which §3 asks for regardless.

**Still open:** the **download date**, which §4.5 requires in the README
alongside the row count. The dataset has not changed since 2025-09-29, so any
download after that refers to this same version.
