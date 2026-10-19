# Decision record

Every decision the team made that affects more than one module, with the
reasoning and evidence behind it. All figures are from the final run on
`budgetwise_synthetic_dirty.csv` and match the report.

A decision that is not written down gets re-argued. A decision without its
reasoning cannot be defended in the report or in Q&A.

## Format

```
## Dxx: Short title
Date · Decided by · Task
**Decision:** what was agreed.
**Why:** the reasoning and evidence.
**Affects:** which modules or documents.
```

---

## Summary

| # | Decision | Status |
|---|---|---|
| D01 | `budgetwise_synthetic_dirty.csv` is the official dataset | Agreed, implemented |
| D02 | The dataset licence permits committing the raw files | Closed |
| D03 | Class design: transaction subclasses and payment-method account groups | Agreed, implemented |
| D04 | A closed set of 14 categories | Agreed, implemented |
| D05 | Shared interfaces between modules | Agreed, recorded in [`interfaces.md`](interfaces.md) |
| D06 | Budget scope: five categories, limits from the 2019 to 2021 median | Agreed, implemented |
| D07 | No merchant column in the data | Agreed |
| D08 | Definitions of valid, skipped, duplicate, corrected and flagged | Agreed, implemented |
| D09 | The CSV loader is a separate module (`P2.9`) | Agreed, implemented |
| D10 | Hyphen dates with a four-digit year are read day first | Agreed, implemented |
| D11 | One shared reason-code list | Agreed, implemented |

---

## D01: `budgetwise_synthetic_dirty.csv` is the official dataset

Recorded 2026-10-17 · Agreed by the team · `P0.2`

**Decision:** `data/raw/budgetwise_synthetic_dirty.csv` (15,836 rows, nine
columns) is the dataset every reported figure comes from.
`budgetwise_finance_dataset.csv` stays in the repository. The same code cleans
both files with no special cases, and the date tests still run on both.

**Why:** It is the harder and more realistic test of the cleaning rules. It
has more category spellings, scrambled names, more users and a wider date
range, so reporting from it is the stronger demonstration of robustness
(§7, correctness and robustness).

**What we had to accept, and how we handled it.** Some of the §4.5 examples
only appear in the finance file:

| Evidence | Present in |
|---|---|
| `Rs.` and `INR` currency labels | finance file only |
| `999999999` sentinel rows (80) | finance file only |
| `Investment` as a category | finance file only |

The rules for these are still implemented and tested with hand-made rows and
on the finance file, so they are ready if the data contains them.

When the decision was first recorded, the date cleaner did not yet read every
date format in the dirty file, and 2,581 records had no usable date. The date
cleaner was then extended to the dirty file's formats. On the final run:

| Measure | Dirty file |
|---|---:|
| Records with a usable date | 14,528 |
| Records with no usable date | 334 (322 blank, 12 invalid) |

The 334 undated records stay in overall and category totals but are left out
of monthly figures (§4.5). The report states this in Table 3 and Table 4.

**Affects:** every figure in the report · `analysis/budgets/` limits ·
`interface/menu/` default dataset · `data/README.md`.

---

## D03: Class design

Agreed by the team · `P3.1`

**Decision:**

- `Transaction` is the parent class. `ExpenseTransaction` and
  `IncomeTransaction` inherit from it and each overrides
  `get_signed_amount()` and `get_transaction_type()`.
- `Account` is the parent of `CashAccount`, `BankAccount` and
  `UnknownAccount`. These are **payment-method groups**, not real bank
  accounts: Cash goes to `CashAccount`; Card, UPI and Bank Transfer go to
  `BankAccount`; anything else goes to `UnknownAccount`.
- `Budget` is a separate class that compares monthly spending with a limit.
- All attributes are private and read through getters. The amount setter
  rejects missing, non-numeric, non-finite and negative values.

**Why:** The data has transaction types and payment modes but no account IDs
or balances. Grouping by payment mode uses information the data really has,
without inventing bank accounts. Expense and income are a genuine "is a"
relationship.

**Affects:** `models/` · `pipeline/` · the report (Figure 1).

---

## D04: A closed set of 14 categories

Agreed by the team · `P1.2` `P2.2`

**Decision:** Every category maps to one of: Food, Rent, Transportation,
Entertainment, Utilities, Education, Healthcare, Savings, Salary, Bonus,
Freelance, Investment, Other, Uncategorized.

- `Travel` maps to Transportation, `Health` to Healthcare, `Others` and
  `Misc` to Other.
- `Other Income` and its spellings map to Other only for Income rows;
  otherwise they become Uncategorized.
- A blank or unrecognized category becomes Uncategorized and is logged.

**Why:** A closed set is required by §4.5. Bonus, Freelance and Savings are
real categories in the data, so they are kept rather than forced into Other.

**Result:** 3,969 category changes: 3,718 mapped to a standard name and 251
set to Uncategorized (154 blank, 97 unrecognized).

**Affects:** `config/category_mapping.csv` · `cleaning/categories/` · every
category total.

---

## D05: Shared interfaces

Agreed by the team · `P1.5`

**Decision:** Each feature exposes its functions through its `__init__.py`.
The signatures, the cleaned record and the result of `clean_file()` and
`run()` are recorded in [`interfaces.md`](interfaces.md).

---

## D06: Budget scope

Agreed by the team · `P3.4`

**Decision:** Monthly limits are set for the five highest-spending expense
categories: Entertainment, Food, Rent, Transportation and Utilities. Each
limit is that category's median monthly spending from January 2019 to
December 2021, including months with no spending and excluding undated
records, rounded up to the next 500. The limits are then used for 2022.

| Category | Total expenses | Monthly limit |
|---|---:|---:|
| Food | 16,147,568 | 67,000 |
| Rent | 10,441,106 | 50,500 |
| Utilities | 9,037,864 | 23,000 |
| Transportation | 8,242,883 | 27,500 |
| Entertainment | 3,909,424 | 17,000 |

These five are 89.6% of all expenses. Categories with spending but no limit
are reported as `unbudgeted`, never as zero.

**Why:** The median is not pulled up by one unusually expensive month, so it
gives a limit someone could plan against. The limits describe historical
spending across the dataset, not advice for a household.

**Limits are generated, not typed.** `config/monthly_budgets.json` and
`budgetwise/analysis/budgets/supplementary/budget_justification.md` are both
written by:

```bash
python -m budgetwise.analysis.budgets.implementation.generate_budget_evidence
```

**Affects:** `config/monthly_budgets.json` · `analysis/budgets/` · the report
(Table 6). §4.4 requires the limits to be justified.

---

## D07: No merchant column

Agreed by the team · `P4.4`

**Decision:** §4.2 mentions unique merchants, but neither dataset has a
merchant column. We do not relabel `location` or `notes` as merchants.
Unique categories are found with a set instead (`unique_categories()`).

---

## D08: Definitions of the pipeline counts

Proposed 2026-10-11 · Agreed by the team · `P2.10`, feeds `P3.8`

**Decision:** Every input row ends in exactly one of three places, so
`input = valid + skipped + duplicates` always holds.

| Count | A row is counted here when |
|---|---|
| `duplicates` | it is an exact copy of an earlier raw row, judged before any cleaning |
| `skipped` | it cannot be used: the row is malformed, for example it has extra fields; `transaction_id`, `user_id` or `transaction_type` cannot be used; or the amount is blank, unreadable or 100,000,000 or more |
| `valid` | everything else. One cleaned record each |

Two more counts describe the valid rows only:

| Count | A valid row is counted here when |
|---|---|
| `corrected` | at least one value was changed to a standard form: date reformatted; category, payment mode or location normalized; blank category set to Uncategorized; payment mode or location set to Unknown; currency label or minus sign removed |
| `flagged` | it was kept with a concern and the value left alone: no usable date, unrecognized category, unusual ID, repeated ID, blank or placeholder note, or a record the model classes refused |

Rules:

- A row is counted **at most once** in each, however many reasons it has.
- A row **can be in both**, so `corrected + flagged` can exceed `valid`.
- A missing or invalid date makes a row flagged, never skipped (§4.5).
- A repeated `transaction_id` makes a row flagged, never a duplicate (§4.5).
- A blank amount makes a row skipped.

**Final results on the dirty file:**

| Measure | Count |
|---|---:|
| Input | 15,836 |
| Exact duplicates removed | 804 |
| Skipped (all blank amounts) | 170 |
| Valid | 14,862 (93.8%) |
| Corrected | 12,862 |
| Flagged | 2,103 |
| In both | 1,744 |
| Repeated IDs / rows affected | 163 / 328 |
| Objects built / failed | 14,862 / 0 |

15,836 = 14,862 + 170 + 804. The finance file reconciles the same way:
15,900 = 14,651 + 349 + 900.

**Why:** §5 requires valid, corrected and skipped to be reported separately.
One definition makes the numbers comparable between runs, and counting a row
once stops a single messy row inflating the totals.

**Affects:** `pipeline/` · `metrics/` · the report (Table 3) ·
[`interfaces.md`](interfaces.md).

---

## D09: The CSV loader is its own module

Agreed by the team · `P2.9`

**Decision:** `budgetwise/loader` reads the file, checks the header and yields
`(line_number, raw_row)` pairs. The pipeline (`P2.10`) passes each row to the
cleaners and builds the objects.

---

## D10: Hyphen dates with a four-digit year are read day first

Recorded 2026-10-11 · Agreed by the team · `P2.1`

**Decision:** A date of the form `NN-NN-YYYY` is read as `DD-MM-YYYY`, so
`04-11-2024` is 4 November 2024.

| Separator and year | Read as | Source |
|---|---|---|
| slash, four-digit year | `MM/DD/YYYY` | §4.5, mandatory |
| hyphen, two-digit year | `DD-MM-YY` | §4.5, mandatory |
| hyphen, four-digit year | `DD-MM-YYYY` | this decision |

The separator decides how a date is read, never the numbers in it. A date
that does not exist, such as 31 February, is rejected and logged, never
swapped around.

**Why:** §4.5 gives no rule for a hyphen date with a four-digit year. Reading
it day first matches the mandatory hyphen rule, and the data supports it: in
the finance file's 1,603 such dates, the first number is above 12 in 953 rows
and the second number never is. Month first would make 953 dates impossible.

Evidence: `budgetwise/cleaning/dates/supplementary/date_evidence.md`.

**Affects:** `cleaning/dates/` · every monthly figure · the date convention
in the report (§4.5).

---

## D11: One shared reason-code list

Proposed 2026-10-11 · Agreed by the team · `P2.8` `P2.10`

**Decision:** Every reason code comes from the one `Reason` list in
`budgetwise/errorlog/implementation/reason_codes.py`. The pipeline writes
every code to `errors.log` in lowercase, so one event always has one name.

**Why:** Counts by reason in the report only mean something if each event
always has the same name.

**Affects:** `errorlog/` · every cleaner · `pipeline/`.

---

## D02: The dataset licence permits committing the raw files

2026-09-29 · verified against Kaggle's dataset metadata API · `P0.2` `P4.3`

**Decision:** Both CSV files are committed to the repository. The repository may
be public. No Kaggle-only link is required.

**Why:** The dataset is licensed **CC0: Public Domain**. The author has waived
all copyright and related rights, so the data may be copied, modified, and
redistributed by anyone without permission or attribution.

§3's instruction is conditional (*"if the dataset licence restricts
redistribution"*), and CC0 imposes no restriction, so the condition does not
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
