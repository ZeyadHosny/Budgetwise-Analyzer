# Phase 2 coordination checklist

Owner: Sarah (`P2.0`) · Technical agreements reviewed by Patrick and Zeyad
Last updated: 2026-10-12

One place that reconciles the workbook with what is actually in the
repository: every Phase 2 task, its branch, owner, reviewer, tests, pull
request and blocker. Baselines come from Bahareh's Phase 1 profiling report
(`P1.1`), which is linked here and not repeated.

**How to keep this current:** update your own row in the pull request that
changes its status. Anything marked *confirm* has not been verified by its
owner and must not be read as fact.

Merge status below is taken from `git log` on `main` on 2026-10-12.

## 1. Gates

| Gate | Status | Evidence |
|---|---|---|
| `G1` | *confirm with Patrick* | |
| `G2` | **Not approved.** The cleaning modules, the pipeline and the model classes are all merged, but the pipeline did not yet work with the real model classes. The fix is in the model-integration pull request below | Bahareh's follow-up review, 2026-10-11 |

## 2. Task status

| Task | Feature | Owner | Reviewer | Branch | Pull request | Tests | Status |
|---|---|---|---|---|---|---|---|
| `P2.1` | `cleaning/dates` | Sarah | Henrieta | `feat/p2-1-cleaning-dates` | first version | 22, OK | Merged |
| `P2.1` fix | review S02, README | Sarah | Henrieta | `fix/p2-1-date-ambiguity-helper` | #12 | 24, OK | Merged |
| `P2.2` | `cleaning/categories` | Henrieta | *confirm* | `feat/p2-2-category-normalization` | *confirm* | *confirm* | Merged |
| `P2.2` fix | category corrections | Henrieta | *confirm* | `fix/p2-2-category-corrections` | #18 | *confirm* | Merged |
| `P2.3` | `cleaning/amounts` | Patrick | *confirm* | `feature/amount-parser` | *confirm* | *confirm* | Merged |
| `P2.4` | `cleaning/rows` | Sarah | Patrick | `feat/p2-4-cleaning-rows` | first version | 43, OK | Merged |
| `P2.4` fix | review S03, README | Sarah | Patrick | `fix/p2-4-repeated-id-missing-ids` | #13 | 47, OK | Merged |
| `P2.5` | `cleaning/payment_modes` | Henrieta | *confirm* | `feat/p2-2-payment-mode-normalization` | *confirm* | *confirm* | Merged |
| `P2.5` fix | payment-mode corrections | Henrieta | *confirm* | `fix/p2-5-payment-mode-corrections` | #19 | *confirm* | Merged |
| `P2.6` | `cleaning/locations` | Henrieta | *confirm* | `feat/p2-2-location-normalization` | *confirm* | *confirm* | Merged |
| `P2.6` fix | location corrections | Henrieta | *confirm* | `fix/p2-6-location-corrections` | #20 | *confirm* | Merged |
| `P2.7` | `cleaning/notes` | Sarah | Henrieta | `feat/p2-7-cleaning-notes` | first version | 12, OK | Merged |
| `P2.7` docs | README, evidence | Sarah | Henrieta | `docs/p2-7-notes-readme` | #14 | 12, OK | Merged |
| `P2.8` | `errorlog` | Patrick | *confirm* | *confirm* | *confirm* | *confirm* | Merged |
| `P2.9` | `loader` | Patrick | Zeyad | *confirm* | *confirm* | *confirm* | Merged |
| `P2.10` | `pipeline` | Sarah | Patrick | `feat/p2-10-cleaning-pipeline` | #10 | 86, OK, 37 skipped (before the models existed) | Merged |
| `P2.10` fix | pipeline with the real model classes | Sarah | Patrick, Zeyad | `fix/p2-10-model-integration` | *add number when opened* | 90, OK, 4 expected failures (test copy) | **Open: to be pushed** |
| `P2.0` | shared docs | Sarah | Patrick, Zeyad, Bahareh | `docs/p2-0-coordination-updates` | #15 | documentation only | Merged |
| `P3.1` | `models`: transactions and accounts | Zeyad | *confirm* | `feat/p3-1-adding-accounts-transactions` | #16 | *confirm* | Merged |
| integration | pipeline, Budget model, budgets, menu | Bahareh | *confirm* | *confirm* | #11 | *confirm* | Not merged. *Confirm whether closed* |

## 3. Acceptance criteria for Sarah's tasks

| Task | Accepted when |
|---|---|
| `P2.1` | Four formats and blanks parse to `YYYY-MM-DD` or `None` with a reason; 6,091 / 4,676 / 3,044 / 1,603 / 486 match Phase 1; never raises |
| `P2.4` | 900 exact duplicates found on raw rows with a set; 1,680 repeated IDs in the raw file and 926 after duplicates are removed, all kept; malformed rows never raise |
| `P2.7` | Every note returned unchanged; 10,072 / 3,007 / 2,335 / 486 match Phase 1 |
| `P2.10` | 15,900 = 14,651 valid + 349 skipped + 900 duplicates; duplicates judged before normalization; every issue in `errors.log`; objects built with Zeyad's real classes and every one placed in exactly one account; all pipeline tests pass on `main` apart from the expected failures for Patrick's open fixes |

## 4. Blockers

| # | Blocker | Review item | Owner | Next step |
|---|---|---|---|---|
| 1 | Pipeline called `add()` and read attributes; the real classes use `add_transaction()` and getters, so `run()` failed with the merged models | follow-up P2.10 | Sarah | Push `fix/p2-10-model-integration`, re-run on the branch, open the pull request |
| 2 | Loader fills a missing field with `""`, drops extra values, and accepts a repeated header name | S05 | Patrick | Fix `load_rows` and `validate_header`; 3 pipeline expected failures then pass |
| 3 | `parse_amount` removes every minus sign, so `1-2` becomes 12. **Checked against the merged version on 2026-10-12: still present** | S09 | Patrick | Validate numeric syntax; 1 pipeline expected failure then passes |
| 4 | Reason-code names and casing not agreed. Date, row and notes codes are not in the `Reason` list | S08, D11 | Sarah, Patrick | Agree one vocabulary; add a test that every logged code is in it |
| 5 | Count definitions, including whether a refused object counts as flagged | S06, D08 | Sarah, Patrick | Agree at the next meeting; record in `decisions.md` |
| 6 | `errors.log` is opened in append mode, so it holds every load | S12 | Patrick | Decide whether logs keep history or describe one run |
| 7 | Status of #11 and whether it overlaps `budgetwise/pipeline` | | Bahareh | Confirm whether it is closed |
| 8 | Evidence files hold figures from a test copy for the model-integration fix | final verification | Sarah | Re-run on the real branch; record Python version, commit, pass/fail/skip counts and log lines |

Resolved since 2026-10-11, and removed from this list:

- Model classes not on `main`: merged in #16.
- Payment-mode misspellings mapped to `Unknown`: fixed in #19. Only blank
  payment modes remain `Unknown`.
- Category names differed between the mapping and the class design: the
  merged classes use Transportation, Healthcare and Other, matching the
  mapping.
- Which account holds an `Unknown` payment mode: Zeyad's `UnknownAccount`
  (#16), used by the pipeline fix.

## 5. Merge order from here

1. `fix/p2-10-model-integration` first. Analysis, budgets and the menu
   (`P3.2` to `P3.5`) depend on `run()` working with the real classes.
2. Patrick's loader and amount fixes, in any order. No pipeline change is
   needed when they land.
3. After 2, Sarah re-runs the pipeline and refreshes
   `budgetwise/pipeline/supplementary/pipeline_evidence.md`.
4. `G2` review once 1 to 3 are done.

## 6. Approvals

A merge to `main` requires one approving review under `CONTRIBUTING.md`. The
approver and date for each are on its pull request page; copy them here.

| Pull request | What | Merged | Approved by | Date |
|---|---|---|---|---|
| #10 | Pipeline | yes | *confirm* | *confirm* |
| #12 | Dates fix (S02) | yes | *confirm* | *confirm* |
| #13 | Rows fix (S03) | yes | *confirm* | *confirm* |
| #14 | Notes documentation | yes | *confirm* | *confirm* |
| #15 | Shared documentation | yes | *confirm* | *confirm* |
| #16 | Model classes | yes | *confirm* | *confirm* |
| #18 | Category corrections | yes | *confirm* | *confirm* |
| #19 | Payment-mode corrections | yes | *confirm* | *confirm* |
| #20 | Location corrections | yes | *confirm* | *confirm* |

Team decisions (`D08`, `D10`, `D11`) are approved in `decisions.md`, not here.

## 7. Links

- Phase 1 profiling report (`P1.1`, Bahareh): *add the path or link*
- [`requirements_checklist.md`](requirements_checklist.md)
- [`decisions.md`](decisions.md)
- [`interfaces.md`](interfaces.md)
- Evidence: `budgetwise/cleaning/dates/supplementary/date_evidence.md`,
  `budgetwise/cleaning/rows/supplementary/row_evidence.md`,
  `budgetwise/cleaning/notes/supplementary/notes_evidence.md`,
  `budgetwise/pipeline/supplementary/pipeline_evidence.md`
