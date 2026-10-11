# cleaning/categories/supplementary

Supporting material for category cleaning (`P1.2` profiling, `P2.2` implementation).

## Where the evidence lives

| What | Where | Feeds |
|---|---|---|
| Raw category profile: all variants and their counts | Bahareh's Phase 1 report: **[insert report title / file path]** | report, implementation details |
| Raw-to-approved category mapping | `config/category_mapping.csv` | report, §4.5 requires the mapping to be included |
| Decision on the approved category set | `docs/decisions.md`, decision `D04` | report, design decisions |

## Category profile summary

The raw dataset (`data/raw/budgetwise_finance_dataset.csv`, 15,900 rows) has 46 nonblank category variants plus blank values. After normalization they map to 14 approved categories:

| Approved category | Raw variants | Rows |
|---|---|---|
| Food | `Food`, `food`, `FOOD`, `Foods`, `Fod`, `Foodd` | 3,356 |
| Rent | `Rent`, `rent`, `RENT`, `Rentt`, `Rnt` | 2,712 |
| Transportation | `Travel`, `travel`, `TRAVEL`, `Traval`, `Travl` | 1,985 |
| Utilities | `Utilities`, `utilities`, `Utility`, `Utilties`, `Utlities` | 1,589 |
| Entertainment | `Entertainment`, `entertainment`, `Entertain`, `Entrtnmnt` | 1,335 |
| Education | `Education`, `education`, `Educaton`, `EDU` | 1,036 |
| Other | `Other`, `Others`, `others`, `OTHERS`, `Misc` | 740 |
| Healthcare | `Health`, `health`, `HEALTH`, `Helth` | 623 |
| Freelance | `Freelance` | 490 |
| Investment | `Investment` | 482 |
| Bonus | `Bonus` | 442 |
| Salary | `Salary` | 430 |
| Savings | `Savings`, `savings`, `SAVINGS`, `Saving` | 395 |
| Uncategorized | blank | 285 |
| **Total** | | **15,900** |

