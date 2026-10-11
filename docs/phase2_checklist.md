# Phase 2 coordination checklist

Owner: Sarah (`P2.0`) · Technical agreements reviewed by Patrick and Zeyad
Last updated: 2026-10-11

One place that reconciles the workbook with what is actually in the
repository: every Phase 2 task, its branch, owner, reviewer, tests, pull
request and blocker. Baselines come from Bahareh's Phase 1 profiling report
(`P1.1`), which is linked here and not repeated.

**How to keep this current:** update your own row in the pull request that
changes its status. Anything marked *confirm* has not been verified by its
owner and must not be read as fact.

## 1. Task status

| Task | Feature | Owner | Reviewer | Branch | Pull request | Tests | Status |
|---|---|---|---|---|---|---|---|
| `P2.1` | `cleaning/dates` | Sarah | Henrieta | `feat/p2-1-cleaning-dates` | merged | 22, OK on `main` | Merged |
| `P2.1` fix | review S02, README | Sarah | Henrieta | `fix/p2-1-date-ambiguity-helper` | #12 | 24, OK | Awaiting approval |
| `P2.2` | `cleaning/categories` | Henrieta | *confirm* | `feat/p2-2-category-normalization` | *confirm* | *confirm* | Merged |
| `P2.2` fix | category corrections | Henrieta | *confirm* | `fix/p2-2-category-corrections` | *confirm* | *confirm* | *confirm* |
| `P2.3` | `cleaning/amounts` | Patrick | *confirm* | `feature/amount-parser` | *confirm* | *confirm* | Merged |
| `P2.4` | `cleaning/rows` | Sarah | Patrick | `feat/p2-4-cleaning-rows` | merged | 43, OK on `main` | Merged |
| `P2.4` fix | review S03, README | Sarah | Patrick | `fix/p2-4-repeated-id-missing-ids` | #13 | 47, OK | Awaiting approval |
| `P2.5` | `cleaning/payment_modes` | Henrieta | *confirm* | `feat/p2-2-payment-mode-normalization` | *confirm* | *confirm* | Merged |
| `P2.5` fix | payment-mode corrections | Henrieta | *confirm* | `fix/p2-5-payment-mode-corrections` | *confirm* | *confirm* | *confirm* |
| `P2.6` | `cleaning/locations` | Henrieta | *confirm* | `feat/p2-2-location-normalization` | *confirm* | *confirm* | Merged |
| `P2.6` fix | location corrections | Henrieta | *confirm* | `fix/p2-6-location-corrections` | *confirm* | *confirm* | *confirm* |
| `P2.7` | `cleaning/notes` | Sarah | *confirm* | `feat/p2-7-cleaning-notes` | merged | 12, OK on `main` | Merged |
| `P2.7` docs | README, evidence | Sarah | *confirm* | `docs/p2-7-notes-readme` | #14 | 12, OK | Awaiting approval |
| `P2.8` | `errorlog` | Patrick | *confirm* | *confirm* | *confirm* | *confirm* | Merged |
| `P2.9` | `loader` | Patrick | Zeyad | *confirm* | *confirm* | *confirm* | Merged |
| `P2.10` | `pipeline` | Sarah | Patrick | `feat/p2-10-cleaning-pipeline` | #10 | 86, OK, 37 skipped | Awaiting approval |
| integration | pipeline, Budget model, budgets, menu | Bahareh | *confirm* | *confirm* | #11 | *confirm* | Open. Overlap with #10 to be checked |

Tests for Sarah's rows were run on 2026-10-10 from the repository root with
`python3` and the dataset in `data/raw/`.

## 2. Acceptance criteria for Sarah's tasks

| Task | Accepted when |
|---|---|
| `P2.1` | Four formats and blanks parse to `YYYY-MM-DD` or `None` with a reason; 6,091 / 4,676 / 3,044 / 1,603 / 486 match Phase 1; never raises |
| `P2.4` | 900 exact duplicates found on raw rows with a set; 1,680 repeated IDs in the raw file and 926 after duplicates are removed, all kept; malformed rows never raise |
| `P2.7` | Every note returned unchanged; 10,072 / 3,007 / 2,335 / 486 match Phase 1 |
| `P2.10` | 15,900 = 14,651 valid + 349 skipped + 900 duplicates; duplicates judged before normalization; every issue in `errors.log`; object, filter and account tests pass against the real model classes |

## 3. Blockers

| # | Blocker | Review item | Owner | Next step |
|---|---|---|---|---|
| 1 | Model classes not in `budgetwise/models` on `main`, so 33 pipeline tests are skipped | S10 | Zeyad | Merge the classes with `Transaction.create()`; confirm whether #11 contains them |
| 2 | #10 and #11 may both change `budgetwise/pipeline` | | Sarah, Bahareh | Compare the file lists and agree which goes in first |
| 3 | Loader pads short rows, drops surplus fields, accepts repeated header names | S05 | Patrick | Fix loader and header check; 3 pipeline tests then run |
| 4 | `parse_amount` removes every minus sign, so `1-2` becomes 12 | S09 | Patrick | Validate numeric syntax; 1 pipeline test then runs |
| 5 | Payment-mode spellings (`Crd`, `Csh`, `BankTransfer` and others) map to `Unknown`: 5,271 raw rows | S10 | Henrieta | Merge `fix/p2-5-payment-mode-corrections`; Sarah re-runs the pipeline counts |
| 6 | Category names differ: mapping gives Transportation, Healthcare, Other; class design uses Travel, Health, Others | | Henrieta, Zeyad | Agree one set and record it in `decisions.md` |
| 7 | Reason-code names and casing not approved | S08 | Sarah, Patrick | Agree one vocabulary; record in `decisions.md`; align pipeline constants |
| 8 | Which account holds an `Unknown` payment mode | | Zeyad, Henrieta | Decide; one-line change in the pipeline |
| 9 | `errors.log` is opened in append mode, so it holds every load | S12 | Patrick | Decide whether logs keep history or describe one run |
| 10 | Definitions of corrected and flagged are proposed, not agreed | S06 | Sarah, Patrick | Agree at the next meeting; record in `decisions.md` |

## 4. Merge order

1. #12 dates, #13 rows, #14 notes. Independent of each other.
2. #13 rows before #10 pipeline, because the pipeline uses `find_repeated_ids`.
3. The model classes before the pipeline's object tests can count as evidence.
4. #10 and #11 only after blocker 2 is settled.
5. After the loader, amount and payment-mode fixes are merged, Sarah re-runs
   the pipeline and refreshes `pipeline/supplementary/pipeline_evidence.md`.

## 5. Approvals

Record each approval here when it happens: what was approved, by whom, and the
date. Nothing is listed until it has actually been approved.

| Date | What was approved | Approved by |
|---|---|---|
| | | |

## 6. Links

- Phase 1 profiling report (`P1.1`, Bahareh): *add the path or link*
- [`requirements_checklist.md`](requirements_checklist.md)
- [`decisions.md`](decisions.md)
- [`interfaces.md`](interfaces.md)
- Evidence: `budgetwise/cleaning/dates/supplementary/date_evidence.md`,
  `budgetwise/cleaning/rows/supplementary/row_evidence.md`,
  `budgetwise/cleaning/notes/supplementary/notes_evidence.md`,
  `budgetwise/pipeline/supplementary/pipeline_evidence.md`
