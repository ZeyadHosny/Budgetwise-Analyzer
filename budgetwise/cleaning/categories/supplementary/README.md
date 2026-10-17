# cleaning/categories/supplementary

Supporting material for category cleaning (`P1.2` profiling, `P2.2` implementation).

## Where the evidence lives

| What | Where | Feeds |
|---|---|---|
| Raw category profile: all variants and their counts | Bahareh's Phase 1 report: **[insert report title / file path]** | report, implementation details |
| Raw-to-approved category mapping | `config/category_mapping.csv` | report, §4.5 requires the mapping to be included |
| Decision on the approved category set | `docs/decisions.md`, decision `D04` | report, design decisions |

## Category profile summary

Measured on the D01 dataset, `data/raw/budgetwise_synthetic_dirty.csv`
(15,836 rows). It holds **212 distinct nonblank category variants** plus blank
values. The mapping in `config/category_mapping.csv` has entries for **20** of
them.

| Approved category | Variants present | Rows |
|---|---|---:|
| Bonus | `Bonus` | 743 |
| Education | `Education` | 342 |
| Entertainment | `Entertainment` | 1,079 |
| Food | `Fod`, `Food`, `Foodd` | 3,832 |
| Freelance | **none present** | 0 |
| Healthcare | `Health` | 236 |
| Investment | **none present** | 0 |
| Other | `Other`, `Others` | 611 |
| Rent | `Rent`, `Rentt`, `Rnt` | 3,119 |
| Salary | `Salary` | 741 |
| Savings | `Saving`, `Savings` | 578 |
| Transportation | `Travel`, `Travl` | 1,458 |
| Utilities | `Utilities`, `Utilties`, `Utlities` | 1,305 |
| Uncategorized | blank | 158 |
| **Unmapped — no entry in the mapping** | **192 variants** | **1,634** |
| **Total** | | **15,836** |

## The mapping is not closed against this dataset

§4.5 requires a **closed** mapping: every raw value has an entry, so nothing
falls through silently. That held for `budgetwise_finance_dataset.csv`, which
the mapping was built from. It does not hold here.

**192 variants covering 1,634 rows have no entry.** The pipeline reports them
as `unknown_category` and routes them to `Uncategorized`, so no row is lost,
but the normalization §4.5 asks for is not happening for them.

They fall into two groups:

**1. One missing category concept — `Other Income`, 749 rows across 15
variants** (`Other Income`, `Otehr Income`, `tOher Income`, `Other  Income`,
and so on). This is not a misspelling of anything in the approved set. It is
income that the dataset classes separately and the approved 14 has no name
for. It needs a decision, not a mapping entry: either add it, or fold it into
`Other` and say so in the report.

**2. Character scrambles — 177 variants, 885 rows.** `Foood`, `FFood`, `Fodo`,
`oFod`, `Ret`, `eRnt`, `Rnet`, `Rennt`, `ent`. Each is a recognisable
corruption of Food, Rent and the rest, but a closed mapping has to list every
one of them, and the tail is long.

## Two approved categories have no data at all

`Freelance` and `Investment` match **zero rows** in this dataset. Three
consequences the report has to acknowledge:

* `PASSIVE_INCOME_CATEGORIES = ("Investment",)` in
  `models/implementation/transaction.py` can never match, so
  `is_passive_income()` always returns False.
* `EARNED_INCOME_CATEGORIES` lists `Freelance`, which likewise never matches.
* The menu offers all 14 categories, so a user can select `Freelance` or
  `Investment` and will always be told nothing matched.

The income this dataset does carry is `Salary` (741), `Bonus` (743) and
`Other Income` (749, unmapped).

## What this needs from the team

Decision `D04` fixed the approved category set against the other dataset.
`D01` changed the dataset underneath it. `D04` has to be revisited: whether to
extend the mapping to close it, whether `Other Income` joins the approved set,
and what to do about two approved categories with no rows.
