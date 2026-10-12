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
| D08 | Corrected vs skipped — where the boundary sits | `P3.5` `P2.10` | three reported counts · **proposal recorded below, awaiting agreement** |
| D09 | Who owns the CSV loader | — | all of Phase 2 |
| D10 | How hyphen dates with a four-digit year are read | `P2.1` | `cleaning/dates/`, every date-based figure · **recorded below, date and names to be filled in** |
| D11 | One shared reason-code vocabulary and casing | `P2.8` `P2.10` | `errorlog/`, every cleaner, `pipeline/` · **proposal recorded below, awaiting agreement** |

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

## Recorded for Phase 2 — awaiting sign-off

Added 2026-10-11 by Sarah for `P2.1` and `P2.10`. Each entry says plainly
whether it has been agreed. Move an entry to **Closed** only when the date and
the people who agreed it are filled in.

## D10 — Hyphen dates with a four-digit year are read day first

Date: *fill in* · Decided by: *fill in the names* · `P2.1`

**Decision:** A date of the form `NN-NN-YYYY` is read as `DD-MM-YYYY`. So
`04-11-2024` is 4 November 2024.

This completes the set of date rules. The first two are mandatory in §4.5; the
third is the team's own:

| Separator and year | Read as | Source |
|---|---|---|
| slash, four-digit year | `MM/DD/YYYY` | §4.5, mandatory |
| hyphen, two-digit year | `DD-MM-YY` | §4.5, mandatory |
| hyphen, four-digit year | `DD-MM-YYYY` | this decision |

The separator alone decides how a date is read, never the numbers in it.

**Why:** §4.5 gives a rule for hyphen dates with a two-digit year but says
nothing about a four-digit year, and the dataset has 1,603 of them. Reading
them day first is consistent with the mandatory hyphen rule, and the data
supports it: across those 1,603 rows the first number is above 12 in 953 rows
and the second number is never above 12. A month-first reading would make 953
dates impossible. 650 of the 1,603 are ambiguous (both numbers 12 or less) and
are settled by this rule.

Evidence: `budgetwise/cleaning/dates/supplementary/date_evidence.md`.

**Affects:** `budgetwise/cleaning/dates/` · every monthly figure in
`analysis/` · the date convention the report must document (§4.5, `P4.4`).

**Status:** implemented and tested in `parse_date()`, merged to `main`. The
date and the names of those who agreed still need recording here.

## D08 — Corrected, flagged and skipped: definitions of the pipeline counts

**Proposed** 2026-10-11 by Sarah · **not yet agreed** · to be confirmed with
Patrick and Zeyad · `P2.10`, feeds `P3.5`

**Proposal:** Every input row ends in exactly one of three places, and
`input = valid + skipped + duplicates` always holds.

| Count | A row is counted here when |
|---|---|
| `duplicates` | it is an exact copy of an earlier raw row, judged before any cleaning |
| `skipped` | it cannot be cleaned: a field is absent; `transaction_id`, `user_id` or `transaction_type` cannot be used; or the amount is blank, unreadable or 100,000,000 or more |
| `valid` | everything else. One cleaned record each |

Two further counts describe the **valid** rows only:

| Count | A valid row is counted here when |
|---|---|
| `corrected` | at least one value was changed to its standard form: date reformatted, category, payment mode or location normalized, currency label or minus sign removed |
| `flagged` | it was kept with at least one concern and the value left alone: no date, unusual ID format, repeated ID, blank or placeholder note |

Rules for these two:

- A row is counted **at most once** in each, however many reasons it carries.
- A row **can be in both**. `corrected + flagged` can therefore exceed `valid`.
- A row with no issue at all is in neither.
- A missing or invalid date makes a row flagged, never skipped (§4.5).
- A repeated `transaction_id` makes a row flagged, never a duplicate (§4.5).

Counts for building objects are kept separate (`objects_built`,
`objects_failed`), so a class refusing a record never changes `valid` or
`skipped`. Such a record is logged as `transaction_not_built`, and because
that is not a correction it currently makes the row **flagged**. The code,
`interfaces.md` and this entry all say the same; the team should confirm it.

**Why:** §5 requires valid, corrected and skipped to be reported separately.
Without one definition the numbers cannot be compared between runs. Counting a
row once per action, not once per reason, stops a single messy row inflating
the totals. Keeping a missing date as flagged follows §4.5, which says such
rows may still count toward category totals.

On the full dataset this gives 15,900 = 14,651 valid + 349 skipped + 900
duplicates, with 14,587 corrected and 6,768 flagged. The last two will change
when the payment-mode mapping is fixed.

**Affects:** `budgetwise/pipeline/` · `metrics/` · the §5 results table in the
report · `interfaces.md`.

**Open questions for the team:**

- Is "skipped" the right status for a row with a blank amount (271 rows after
  duplicates are removed)? The Phase 2 specification's wording is looser.
- Should a payment mode or location set to `Unknown` count as corrected, as it
  does now, or as flagged?
- Should a record the model classes refuse count as flagged, as it does now,
  or only in `objects_failed`?

## D11 — One shared reason-code vocabulary

**Proposed** 2026-10-11 by Sarah · **not yet agreed** · needs Patrick
(`P2.8`), with Henrieta and Zeyad for their cleaners · `P2.10`

**The problem:** three vocabularies are in use.

| Where | Casing | Examples |
|---|---|---|
| `budgetwise/errorlog/` `Reason` list | lowercase | `missing_date`, `unrecognized_date_format`, `impossible_date`, `duplicate_row`, `missing_required_field`, `sentinel_amount` |
| Cleaners for dates, rows, notes, categories, payment modes, locations | UPPERCASE | `MISSING_DATE`, `INVALID_DATE`, `DATE_NORMALIZED`, `MALFORMED_ROW`, `NOTES_MISSING`, `CATEGORY_NORMALIZED` |
| Phase 2 specification | UPPERCASE | `DUPLICATE_RAW_ROW`, `MALFORMED_ROW`, `SENTINEL_AMOUNT_INVALID` |

The names also differ, not only the casing: the date cleaner returns
`INVALID_DATE`, while the `Reason` list has `unrecognized_date_format` and
`impossible_date` and no `invalid_date`.

**Current behaviour, pending a decision:** the pipeline converts every code to
lowercase before logging, so `errors.log` is consistent within itself. The
logger writes whatever it is given and does not require lowercase. Every code
the pipeline creates itself is listed in one block at the top of
`budgetwise/pipeline/implementation/runner.py`, so a change is made in one
place.

**Proposal for discussion:** the `Reason` list in `budgetwise/errorlog/`
becomes the single vocabulary. It gains the codes it lacks
(`date_normalized`, `invalid_date` or the two it already has, `malformed_row`,
`repeated_transaction_id`, the notes, category, payment-mode and location
codes), and each cleaner returns codes from it. Casing to be chosen once and
applied everywhere.

**Why it matters:** the professor requires traceable logging with a reason.
Counts by reason in the report are only meaningful if one event always has one
name.

**Affects:** `errorlog/` · every cleaner · `pipeline/` · the pipeline test
that checks codes are lowercase, which should be replaced by a test against
the agreed list.

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
