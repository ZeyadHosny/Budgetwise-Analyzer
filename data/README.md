# data

The raw datasets. **These files are never modified, renamed, or cleaned in
place.** Every output goes to `output/`.

## What is here

| File | Rows | Unique ids | Exact duplicate rows | Users | Date range |
|---|---|---|---|---|---|
| `raw/budgetwise_finance_dataset.csv` | 15,900 | 14,000 | 900 | 150 | 2021–2024 |
| `raw/budgetwise_synthetic_dirty.csv` | 15,836 | 14,858 | 804 | 192 | 2019–2022 |

Both carry the same nine columns:

```
transaction_id · user_id · date · transaction_type · category
amount · payment_mode · location · notes
```

**Download date: _to be recorded_** — §4.5 requires the row count and download
date in the README. The row counts are measured above; someone needs to supply
the date the files were obtained from Kaggle.

Source: <https://www.kaggle.com/datasets/mohammedarfathr/budgetwise-personal-finance-dataset>

## They are two different datasets, not two copies

**Zero rows are identical between them.** They are separate generated variants:

| | `budgetwise_finance_dataset` | `budgetwise_synthetic_dirty` |
|---|---|---|
| Amount median | 5,713 | 538 |
| Currency labels | `₹` `$` `Rs.` trailing `INR` | `₹` `$` only |
| Date formats | 5 shapes | 18 shapes, including `December 04 2021` |
| Thousands separators | none | ~5,400 rows |
| Sentinel `999999999` | **80 rows** | **none** |
| Category variants | 47 | 213 |
| Category damage | case and light typos | character scrambles |

## Which one the assignment was written against

`budgetwise_finance_dataset.csv`. The PDF's mandatory conventions only make
sense against it:

1. §4.5 says strip `₹`, `$`, **`Rs.`**, or a **trailing `INR`**. Only this file
   has `Rs.` and `INR` — in the other, those two rules are dead code.
2. §4.5 says treat amounts ≥ 100,000,000 as invalid, "**e.g. 999999999**". This
   file has 80 such rows. The other file's largest amount is 999,999.
3. §4.5's example canonical categories include **Investment**, which appears
   only in this file.
4. §4.5's own rationale states medians are "**~5,600–6,600** across $, ₹, Rs.,
   and plain-number rows". Measured here:

   | plain | ₹ | $ | Rs. | INR |
   |---|---|---|---|---|
   | 5,900 | 5,891 | 5,863 | 5,638 | 6,602 |

   Every one inside the stated band. The other file's medians are 540 / 512 /
   534, with no `Rs.` or `INR` rows at all.

**Do not merge the two files.** Different users, different years, different id
formats, and no shared rows — concatenating them would report totals over a
population that does not exist.

## Which one the reported figures use

**`budgetwise_synthetic_dirty.csv`**, by decision **D01** (2026-10-17), recorded
in `docs/decisions.md`.

That reverses the position this section argued. The reason for the switch is not
yet written into D01, and the evidence above still points the other way, so it
has to be supplied before `G5` — §7 marks reflection on design decisions, and an
unexplained reversal is exactly the kind of thing a reader will ask about.

Note what the switch means in practice. This file was kept as a robustness
fixture precisely *because* its formats — 18 date shapes, 213 category variants,
scrambled category names — are ones the cleaners were never designed for. The
headline figures now come from the harder file. That is defensible, and arguably
good evidence for §7's "correctness and robustness", but it is an argument
someone has to make explicitly rather than leave implied.

`budgetwise_finance_dataset.csv` stays in the repository. It still backs the
Phase 1 profiling evidence in each module's `supplementary/` folder, which has
not been re-measured against the new dataset.

## Licence — CC0: Public Domain

**Verified 2026-09-29. Both CSV files may be committed to a public repository.**

| Field | Value |
|---|---|
| Licence | **CC0: Public Domain** |
| Title | BudgetWise Personal Finance Dataset |
| Owner | Mohammed Arfath R |
| Total size | 2,184,425 bytes |
| Dataset last updated | 2025-09-29 |

Source: Kaggle dataset metadata API,
`https://www.kaggle.com/api/v1/datasets/view/mohammedarfathr/budgetwise-personal-finance-dataset`

Under CC0 the author has waived all copyright and related rights. The data may
be copied, modified, and redistributed by anyone, for any purpose, without
permission or attribution.

§3 says: *"Do not commit the raw dataset file to a public repository **if the
dataset licence restricts redistribution**."* CC0 imposes no such restriction,
so the condition does not apply and both files are committed here rather than
linked.

The Kaggle page is still cited above, and the download steps remain in this file,
because §3 also asks for download instructions regardless.

### Size check

Kaggle reports 2,184,425 bytes in total. The two local files measure
1,042,312 + 1,142,113 = **2,184,425 bytes** — an exact match, confirming both
published files are present and complete.

### Still outstanding

**The download date.** §4.5 requires the row count *and* the download date in the
README. Row counts are measured above; whoever obtained the files needs to supply
the date they were downloaded. The dataset itself has not changed since
2025-09-29, so any download after that date refers to this same version.
