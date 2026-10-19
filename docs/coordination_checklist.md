# Cleaning and pipeline coordination checklist

Owner: Sarah (`P2.0`) · Technical agreements reviewed by Patrick and Zeyad
Last updated: 2026-10-19 (final)

The record of the cleaning and pipeline tasks: owner, reviewer, pull request,
tests and final status. It replaces the earlier working checklist of
2026-10-12. Decisions are in [`decisions.md`](decisions.md) and the function
contracts in [`interfaces.md`](interfaces.md).

## 1. Final status

All cleaning tasks and the pipeline are merged to `main` and working with the
real model classes.

Full test suite on `main`, run from the repository root with
`python3 -m unittest`:

```
Ran 800 tests
OK (expected failures=3)
```

The three expected failures are checks on the loader and amount parser (review
items S05 and S09). They are marked in the code with `until_fixed`, not
hidden, and will pass once those fixes land.

## 2. Task status

| Task | Feature | Owner | Reviewer | Pull requests | Tests | Status |
|---|---|---|---|---|---|---|
| `P2.1` | `cleaning/dates` | Sarah | Henrietta | first version, #12 | 28 | Merged |
| `P2.2` | `cleaning/categories` | Henrietta | team | #18, #44 | in folder | Merged |
| `P2.3` | `cleaning/amounts` | Patrick | team | `feature/amount-parser` | in folder | Merged |
| `P2.4` | `cleaning/rows` | Sarah | Patrick | first version, #13, #38 | 47 | Merged |
| `P2.5` | `cleaning/payment_modes` | Henrietta | team | #19 | in folder | Merged |
| `P2.6` | `cleaning/locations` | Henrietta | team | #20 | in folder | Merged |
| `P2.7` | `cleaning/notes` | Sarah | Henrietta | first version, #14, #37 | 12 | Merged |
| `P2.8` | `errorlog` | Patrick | team | | in folder | Merged |
| `P2.9` | `loader` | Patrick | Zeyad | #52 | in folder | Merged |
| `P2.10` | `pipeline` | Sarah | Patrick, Zeyad | #10, model integration, #40 | 95 | Merged |
| `P2.0` | shared docs | Sarah | Patrick, Zeyad, Bahareh | #15 | docs only | Merged |
| `P3.1` | `models` | Zeyad | team | #16 | in folder | Merged |

Sarah's four folders hold 182 tests between them (47 + 28 + 12 + 95).

## 3. Acceptance criteria for Sarah's tasks

Final figures are from `budgetwise_synthetic_dirty.csv` (decision D01).

| Task | Accepted when | Result |
|---|---|---|
| `P2.1` | Every supported format parses to `YYYY-MM-DD`, or `None` with a reason; slash dates month first, hyphen dates day first; never raises | Met. 14,528 usable dates, 334 without (322 blank, 12 invalid) |
| `P2.4` | Exact duplicates found on raw rows with a set; repeated IDs kept and flagged; malformed rows never raise | Met. 804 exact duplicates; 163 repeated IDs on 328 rows, all kept |
| `P2.7` | Every note returned unchanged and labelled meaningful, low information, missing or not available | Met. Dirty file: 14,302 meaningful, 1,534 missing |
| `P2.10` | Input = valid + skipped + duplicates; duplicates judged before cleaning; every issue in `errors.log`; every valid record becomes one object in exactly one account | Met. 15,836 = 14,862 + 170 + 804; 14,862 objects, 0 failures |

## 4. Blockers

Most blockers from the earlier checklist are resolved. The two review items
still open are marked as expected failures in the tests.

| # | Blocker | Outcome |
|---|---|---|
| 1 | Pipeline used old method names, so `run()` failed with the real model classes | Resolved: pipeline uses `add_transaction()` and getters |
| 2 | Loader pads short rows and accepts a repeated header name (S05) | Partly resolved in #52. Remaining checks are expected failures |
| 3 | `parse_amount` removes every minus sign, so `1-2` becomes 12 (S09) | Open. Marked as an expected failure |
| 4 | Reason codes in several vocabularies (S08) | Resolved: one `Reason` list (D11) |
| 5 | Count definitions (S06) | Resolved: agreed in D08 |
| 6 | `errors.log` opened in append mode (S12) | Append mode kept; the report's timings used a fresh log for each run. *Confirm with Patrick* |
| 7 | Status of #11 | *Confirm with Bahareh whether it was closed* |
| 8 | Evidence files held figures from a test copy | Figures refreshed on `main`. `pipeline/README.md` and `pipeline_evidence.md` still say 4 expected failures; now 3 |

## 5. Still to do before submission

- [ ] Record the dataset **download date** in `data/README.md` (§4.5).
- [ ] Commit the final output files with `git add -f`, so the repository
      contains the output datasets (§5). See `.gitignore`.
- [ ] Collect signatures for the peer assessment
      ([`peer_assessment.md`](peer_assessment.md)).

## 6. Links

- [`requirements_checklist.md`](requirements_checklist.md)
- [`decisions.md`](decisions.md)
- [`interfaces.md`](interfaces.md)
- Evidence: `budgetwise/cleaning/dates/supplementary/date_evidence.md`,
  `budgetwise/cleaning/rows/supplementary/row_evidence.md`,
  `budgetwise/cleaning/notes/supplementary/notes_evidence.md`,
  `budgetwise/pipeline/supplementary/pipeline_evidence.md`
