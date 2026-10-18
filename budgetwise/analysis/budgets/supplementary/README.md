# analysis/budgets/supplementary

| File | Task | Feeds |
|---|---|---|
| `budget_justification.md` | `P3.3` | report — **required by §4.4** |

§4.4: *"Each team must define reasonable monthly budget limits for at least five
categories **and justify them**."*

This file is a graded deliverable. `budget_justification.md` is generated from
the cleaned dataset by
`budgetwise.analysis.budgets.implementation.generate_budget_evidence`. Review
its limits, method, and data before submission. The generator also records what
happens to categories with no configured limit.

Regenerate it and the JSON limits from the repository root with:

```bash
python -m budgetwise.analysis.budgets.implementation.generate_budget_evidence
```
