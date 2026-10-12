# Requirements checklist

DATA 5010 — Project 1: Personal Finance & Spending Analyzer
Due **Mon Oct 19, 2026, 11:59 PM EST** · Late deliverables are not accepted
Last updated: 2026-10-11 (Phase 2 status for `P2.1`, `P2.4`, `P2.7`, `P2.10`)

Every requirement in `Project-1.pdf`, in the order the assignment states them,
each mapped to its task in `DATA5010_Project1_Timeline_TeamPlan.xlsx`.

**Requirements come from the PDF. The workbook is checked against it, never the
reverse.** Where the assignment requires something the workbook does not cover,
the line says so.

### How to read a line

```
- [ ] Requirement as the assignment states it → P2.1 · Bahareh
```

| Marker | Meaning |
|---|---|
| `P2.1` `G2` | The workbook task that delivers it, and its owner |
| **A TASK NEEDS TO BE CREATED** | No workbook task covers this requirement |
| *decision needed* | A task exists, but the team must agree something first |
| *add to that task* | A task exists and plausibly covers it, but does not say so — add it explicitly |

Tick a box only when the work is merged to `main` and tested, not when it is
written. Cite the requirement in your pull request under "Closes".

---

## Phase 2 status: `P2.1`, `P2.4`, `P2.7` and `P2.10` (Sarah)

Added 2026-10-11. Links each requirement owned by these four tasks to the code
that delivers it and the tests that check it. Task IDs follow the current
workbook. Baselines are from Bahareh's Phase 1 profiling report (`P1.1`).

### Requirement to code to test

| Requirement | Source | Task | Code | Tests |
|---|---|---|---|---|
| Parse the four date formats into `YYYY-MM-DD` | §4.1, §4.5 | `P2.1` | `parse_date()` in `budgetwise/cleaning/dates/implementation/parser.py` | `ValidFormatTests`, `FullDatasetTests` in `budgetwise/cleaning/dates/testing/test_parser.py` |
| Slash dates read month first; hyphen dates read day first | §4.5 | `P2.1` | `DATE_FORMATS` in `parser.py` | `AmbiguousDateTests` |
| Missing or unparseable date returns `None` with a reason; never raises | §4.5 | `P2.1` | `parse_date()` | `MissingDateTests`, `InvalidDateTests` |
| A duplicate is a fully identical raw row, found with a set | §4.1, §4.2, §4.5 | `P2.4` | `raw_duplicate_key()`, `is_duplicate()`, `split_exact_duplicates()` in `budgetwise/cleaning/rows/implementation/raw_rows.py` | `DuplicateKeyTests`, `IsDuplicateTests`, `ExactDuplicateTests` in `budgetwise/cleaning/rows/testing/test_raw_rows.py` |
| A repeated `transaction_id` on differing rows is kept and flagged | §4.5 | `P2.4` | `find_repeated_ids()` | `RepeatedIdTests`, `FullDatasetTests` |
| Malformed or incomplete rows handled without crashing | §4.1 | `P2.4` | `validate_raw_row()`, `has_required_fields()` | `ValidateRawRowTests`, `HasRequiredFieldsTests` |
| Meaningful notes preserved exactly; blank, N/A and placeholders flagged | Phase 2 specification (not named in the PDF) | `P2.7` | `classify_note_quality()` in `budgetwise/cleaning/notes/implementation/note_quality.py` | `MeaningfulNoteTests`, `LowInformationNoteTests`, `FullDatasetTests` in `budgetwise/cleaning/notes/testing/test_note_quality.py` |
| Duplicate detection runs on raw rows before normalization | §4.5 | `P2.10` | step 2 of `_clean_rows()` in `budgetwise/pipeline/implementation/runner.py` | `OrderTests` in `budgetwise/pipeline/testing/test_runner.py` |
| Skipped, corrected and flagged rows logged with a reason | §4.1 | `P2.10` with `P2.8` | `_record_issue()` in `runner.py`, writing through `ErrorLog.record()` | `CleaningTests`, `RowValidationTests` |
| The program must not crash on bad input | §4.1 | `P2.10` | per-row guard in `_clean_rows()` | `BadInputTests`, `FailureBoundaryTests` |
| Counts reconcile: input = valid + skipped + duplicates | §5 | `P2.10` | `_empty_counts()`, `_summarise()` in `runner.py` | `CleaningTests`, `FlaggedCountTests`, `FullDatasetTests` |
| Transactions stored as a list of objects | §4.2 | `P2.10` with `P3.1` | `run()` and `_build_objects()` in `runner.py` | `ObjectTests`, `ClassUseTests` (skipped until the model classes are merged) |
| Load a subset by date range or by category | §4.1 | `P2.10` with `P3.5` | `_passes_filters()` in `runner.py` | `FilterTests` (skipped until the model classes are merged) |

### Have the tests actually been run?

Yes. Run by Sarah on 2026-10-10 from the repository root with `python3`, on the
branch of each pull request, with the dataset present in `data/raw/`.

| Task | Command | Result | Where the code is |
|---|---|---|---|
| `P2.1` | `python3 -m unittest budgetwise.cleaning.dates.testing.test_parser` | 24 tests, OK | Feature merged to `main`. Review fix S02 in pull request #12, awaiting approval |
| `P2.4` | `python3 -m unittest budgetwise.cleaning.rows.testing.test_raw_rows` | 47 tests, OK | Feature merged to `main`. Review fix S03 in pull request #13, awaiting approval |
| `P2.7` | `python3 -m unittest budgetwise.cleaning.notes.testing.test_note_quality` | 12 tests, OK | Feature merged to `main`. Documentation update in pull request #14, awaiting approval |
| `P2.10` | `python3 -m unittest budgetwise.pipeline.testing.test_runner` | 86 tests, OK, 37 skipped | **Not merged.** Pull request #10, awaiting approval |

The 37 skipped pipeline tests have not been run and prove nothing yet: 33 wait
for the model classes in `budgetwise/models` (`P3.1`), 3 for the loader fix and
1 for the amount parser fix. They start running by themselves once those are
merged.

Full-dataset results from the run above: 15,900 input = 14,651 valid + 349
skipped + 900 duplicates. Detail is in each feature's `supplementary/` folder.

### Which boxes are ticked, and why

A box is ticked only when the work is merged to `main` and tested. On that
rule, the date parsing lines and the two duplicate definitions below are
ticked. Every line that depends on the pipeline stays unticked until pull
request #10 is merged, even though its tests pass on the branch.

---

## §2 — Objective, scope, and constraints

### What the application must do

- [ ] Ingest transaction data from CSV files → **A TASK NEEDS TO BE CREATED** (see task 1)
- [ ] Clean and validate the data, handling errors gracefully rather than crashing → `P2.1`–`P2.4` all
- [ ] Represent transactions and accounts using an object-oriented class hierarchy, including inheritance → `P2.5` Zeyad
- [ ] Organize and aggregate data using lists, tuples, dictionaries, and sets → `P3.1` Henrieta
- [ ] Produce meaningful analysis: spending summaries, budget comparisons, **and trends** → `P3.2` Bahareh · `P3.3` Patrick · *trends: see note*
- [ ] Export results to a report file → `P3.4` Sarah

> **"Trends" appears only here.** §4.4 lists seven required outputs and none of
> them is named a trend. Monthly expenses and the text visualization are the
> closest fit. To be safe, the report should explicitly discuss what the monthly
> figures show over time — assign that to `P4.4`.

### Hard constraints

- [ ] **Core ingestion, cleaning, aggregation, and analysis use the Python standard library only** → `G3` Patrick · *add to that task*
- [ ] **pandas, NumPy, and other data-analysis libraries are not used** for those tasks → `G3` Patrick · `P4.1` Sarah · *add to that task*
- [ ] The user interface is a simple **text-based menu** → `P3.4` Sarah
- [ ] **No graphical user interface** is built → `P3.4` Sarah

> **This is the single most dangerous requirement in the assignment.** Permitted
> modules include `csv`, `datetime`, `json`, `collections`, and `os`. A single
> `import pandas` in the cleaning or analysis path violates a stated constraint,
> and no amount of working code compensates.
>
> No workbook task verifies this. `G3` says "verify mandatory conventions", which
> most naturally reads as the §4.5 data conventions, not the library rule. Add an
> explicit import check to `G3`'s exit criteria — grepping the source for
> `pandas` and `numpy` takes seconds and removes the risk entirely.

---

## §3 — Data

- [ ] All teams use the same dataset → `P0.2` Sarah · *decision needed: two CSVs are present; choose the official one*
- [ ] Record the file's row count and download date in `README.md` → `P0.2` Sarah · `P4.3` Zeyad
- [ ] Inspect the schema rather than assuming a fixed structure → `P1.1`–`P1.4` all
- [ ] Document any assumptions made about the data in the report → `P4.4` Henrieta
- [ ] Do not commit raw data to a public repository if the licence restricts redistribution — link to Kaggle and include download instructions in `README.md` → `P0.2` Sarah · `P4.3` Zeyad · *decision needed: verify the licence terms*

The assignment states the dataset contains multi-format dates, currency
inconsistencies, text typos and inconsistent capitalization, duplicate entries,
missing values, and a mix of income and expense records — with **roughly 30% of
records carrying some data issue**. That figure is a useful sanity check: if your
cleaning reports far fewer problems than that, your detection is probably too
narrow.

---

## §4.1 — Data ingestion and cleaning

- [ ] **Read transaction data from the BudgetWise CSV file(s)** → **A TASK NEEDS TO BE CREATED** (see task 1)
- [x] Parse and standardize the multiple date formats into a single consistent format → `P2.1` Sarah · profiling `P1.1` Bahareh
- [ ] Normalize inconsistent currency symbols and formats in the amount field into a single numeric representation → `P1.3` `P2.3` Patrick
- [ ] Handle malformed or incomplete rows — missing values, bad dates, unparseable amounts — using `try`/`except` → `P2.4` Sarah (row checks, merged) · `P2.10` Sarah (applied per row, pull request #10)
- [ ] **The program must not crash on bad input** → `P2.4` Sarah · `P2.10` Sarah (pull request #10) · `P4.1` Sarah
- [ ] Detect and remove or flag duplicate transaction entries → `P2.4` Sarah (detection, merged) · `P2.10` Sarah (removal and logging, pull request #10)
- [ ] Log skipped, corrected, or flagged rows to **`errors.log`**, each with a brief reason → `P2.8` Patrick (logger) · `P2.10` Sarah (pipeline writes every issue, pull request #10)
- [ ] Support loading the dataset, or a subset, through a menu-driven interface → `P1.5` Zeyad (skeleton) · `P3.4` Sarah (implementation)
- [ ] The menu is interactive — a `while` loop reading `input()`, **not a one-shot script** → `P3.4` Sarah

### The menu itself

The assignment prints the menu it expects, so each option is checked separately.

- [ ] `1. Load full dataset` → `P3.4` Sarah
- [ ] `2. Load transactions by date range` — prompts for start and end dates → `P3.4` Sarah
- [ ] `3. Load transactions by category` → `P3.4` Sarah
- [ ] `4. View error log` → `P3.4` Sarah
- [ ] `5. Exit` → `P3.4` Sarah
- [ ] Invalid menu input handled without crashing → `P3.4` Sarah

> §4.1's prose mentions only a date range, but the printed menu also requires
> **loading by category**. Both filters are required. Reading the paragraph and
> skipping the code block produces a program missing a graded feature.
>
> **Why the first line has no task.** `P0.2` downloads the file. `P2.1`–`P2.4`
> clean fields that have already been read. `P2.5` builds the classes. Gate `G2`
> requires that "the integrated loader/cleaner creates transaction objects
> without crash" — but nothing builds the loader. Unassigned: opening files,
> validating headers, iterating and numbering rows, passing rows to the four
> cleaners, assembling objects, and handling file and encoding failures.

---

## §4.2 — Data organization

- [ ] Store transactions as a **list** of objects → `P2.10` Sarah (pull request #10) · needs the model classes, `P3.1` Zeyad
- [ ] Use **dictionaries** to aggregate totals by category and by month → `P3.1` Henrieta
- [ ] Use **sets** to identify unique categories and detect duplicate transactions → `P3.1` Henrieta (unique categories) · `P2.4` Sarah (duplicates: set-based, merged and tested)
- [ ] Use **tuples** for fixed keys, for example `(year, month)` → `P3.1` Henrieta

> §4.2 also asks for unique **merchants**. Neither CSV has a merchant column —
> the nine columns are `transaction_id`, `user_id`, `date`, `transaction_type`,
> `category`, `amount`, `payment_mode`, `location`, `notes`. Document the absence
> in the report under `P4.4`. Do not relabel `location` or `notes` as merchants.

---

## §4.3 — Object-oriented design

- [ ] At least one clear example of **inheritance** → `P2.5` Zeyad
- [ ] The inheritance represents a meaningful "is-a" relationship, not an artificial subclass created to satisfy the requirement → `P2.5` Zeyad · `G1` Bahareh
- [ ] Appropriate use of **encapsulation** → `P2.5` Zeyad
- [ ] At least one class demonstrates encapsulation using **private or protected attributes** with methods or properties controlling access → `P2.5` Zeyad
- [ ] A **`Budget`** class comparing actual spending against category limits and flagging overages → `P2.5` Zeyad
- [ ] Justify the class design in the written report → `P4.4` Henrieta

> The `Transaction` / `Account` hierarchy in the PDF is explicitly **suggested,
> not required** — "the specific classes are up to your team". The workbook's
> `P2.5` mandates an Account hierarchy, but the data has no account-type field,
> only `user_id` and `payment_mode`.
>
> *Decision needed at `G1`:* design classes that fit the real schema and record
> the reasoning. Inventing account types to match the suggestion is exactly the
> artificial subclassing the assignment warns against.

---

## §4.4 — Analysis and reporting

The assignment names these seven outputs explicitly.

- [ ] Total income → `P3.2` Bahareh
- [ ] Total expenses → `P3.2` Bahareh
- [ ] Net balance → `P3.2` Bahareh
- [ ] Monthly expenses → `P3.2` Bahareh
- [ ] Top 5 spending categories → `P3.2` Bahareh
- [ ] Top 5 largest expense transactions → `P3.3` Patrick
- [ ] Budget vs. actual spending by category → `P3.3` Patrick

And:

- [ ] Clear **over/under indicators** on the budget comparison → `P3.3` Patrick
- [ ] Monthly budget limits defined for **at least five categories** → `P3.3` Patrick
- [ ] Those budget limits are **justified** → `P3.3` Patrick · `P4.4` Henrieta
- [ ] A simple text-based visualization of spending by month or category, e.g. a bar chart using `*` → `P3.4` Sarah
- [ ] Export a cleaned summary to a new CSV or JSON file → `P3.4` Sarah

---

## §4.5 — Data handling conventions

The assignment calls these **mandatory** and says to follow them exactly, so all
teams are graded on a consistent standard. Deviating costs marks even if the
program runs correctly.

### Amounts

- [ ] Strip the currency symbol or suffix — `₹`, `$`, `Rs.`, or trailing `INR` — and treat the remaining number as-is → `P2.3` Patrick
- [ ] **Attempt no currency conversion** → `P2.3` Patrick
- [ ] Log which currency symbol each row originally carried → `P2.3` Patrick
- [ ] Treat any amount ≥ **`100,000,000`** as invalid — exclude from totals and analysis, and log it → `P2.3` Patrick
- [ ] Treat amount as an **unsigned magnitude** → `P2.3` Patrick
- [ ] Determine direction from the **`transaction_type`** field, never from the sign of the amount → `P2.3` Patrick

### Dates

- [x] Convert all valid dates to **`YYYY-MM-DD`** → `P2.1` Sarah
- [x] Where day and month are both ≤ 12, read **slash-separated** dates as `MM/DD/YYYY` → `P2.1` Sarah
- [x] Where day and month are both ≤ 12, read **hyphen-separated two-digit-year** dates as `DD-MM-YY` → `P2.1` Sarah · four-digit-year hyphen dates also read day first, see `decisions.md`
- [ ] Document this date convention in the report → `P4.4` Henrieta
- [ ] Any date that cannot be parsed by these rules is logged and **excluded from date-based analysis** → `P2.1` Sarah (returns `None` with a reason, merged) · `P2.10` Sarah (logs it, pull request #10)
- [ ] A missing date is logged and excluded from date-based analysis, but the row **may still count toward category totals** → `P2.1` Sarah · `P2.10` Sarah (row kept with no date, pull request #10) · `P3.1` Henrieta

### Categories

- [ ] A missing category is assigned **`"Uncategorized"`**, never dropped → `P2.2` Henrieta
- [ ] Maintain a documented, **closed** mapping from raw category strings to a fixed set of normalized names → `P1.2` `P2.2` Henrieta
- [ ] Include the raw-to-normalized mapping in the report → `P4.4` Henrieta

> The assignment offers an example canonical set: Food, Rent, Transportation,
> Entertainment, Shopping, Utilities, Healthcare, Education, Salary, Investment,
> Other, Uncategorized. It is an example, not a mandate — but any set you choose
> must be closed and documented. Note that the raw data also contains Freelance,
> Bonus, Savings, and Misc, which have no home in that example list. Resolving
> that is part of `P1.2`.

### Rows

- [x] A duplicate is a **fully identical row** → `P2.4` Sarah
- [x] A repeated `transaction_id` on rows that otherwise differ is **not** a duplicate and must not be dropped → `P2.4` Sarah
- [ ] Duplicate detection is performed on the original **raw rows, before normalization** → `P2.4` Sarah (key uses raw values, merged) · `P2.10` Sarah (order enforced, pull request #10)
- [ ] Any date or amount format not covered by the parsing logic is logged and skipped — never crashes, never silently misparsed → `P2.1` Sarah · `P2.3` Patrick

### Provenance

- [ ] Record the dataset's row count and download date in `README.md` → `P0.2` Sarah · `P4.3` Zeyad

---

## §5 — Deliverables

### Submission

- [ ] Submit a **PDF** copy of the report via Canvas, one per group → `DUE` Bahareh
- [ ] The report contains the GitHub link → `P4.3` Zeyad
- [ ] The GitHub project contains the source code → `G4` Zeyad
- [ ] The GitHub project contains input and output datasets, **or links to them** → `P4.2` Patrick
- [ ] A clear `README.md` instructing how to run the code on the datasets → `P4.3` Zeyad
- [ ] The `README.md` also explains **how to comprehend the outputs** → `P4.3` Zeyad

### Report format — verified at `G5`

- [ ] Within **10 pages**, excluding references and peer assessment → `G5` Bahareh
- [ ] **Single-column** format → `G5` Bahareh
- [ ] **11pt** font size → `G5` Bahareh
- [ ] **Arial** font → `G5` Bahareh

### Report content

- [ ] Key problems studied → `P4.4` Henrieta
- [ ] Solutions proposed — theory, algorithms, and systems → `P4.4` Henrieta
- [ ] Implementation details — datasets, programming language, tools, code summary → `P4.4` Henrieta
- [ ] A **design flow diagram** based on important subroutines → `P1.5` Zeyad · `P5.1` Bahareh
- [ ] Limitations and future work → `P4.4` Henrieta
- [ ] **Conclusion** → `P5.1` Bahareh

### Key experimental results — measured, not estimated

The assignment lists these specifically, under both effectiveness and efficiency.

- [ ] Number of input records → `P3.5` Zeyad · `P4.2` Patrick
- [ ] Number of valid records → `P3.5` Zeyad
- [ ] Number of corrected records → `P3.5` Zeyad
- [ ] Number of invalid / skipped records → `P3.5` Zeyad
- [ ] Number of duplicates detected → `P3.5` Zeyad
- [ ] Number of categories normalized → `P3.5` Zeyad
- [ ] Execution time for **loading** → `P3.5` Zeyad
- [ ] Execution time for **cleaning** → `P3.5` Zeyad
- [ ] Execution time for **analysis** → `P3.5` Zeyad

### Peer assessment

The blank form is printed at the end of the assignment PDF. It has three columns.

- [ ] Peer assessment completed at the **end** of the report → `P5.4` Sarah
- [ ] Every member's **name** listed → `P5.4` Sarah
- [ ] Every member has a **written description of their individual contribution** → `P5.4` Sarah
- [ ] Every member has a **percentage of contribution** → `P5.4` Sarah
- [ ] The percentages **sum to 100%** → `P5.4` Sarah
- [ ] **Signed by all team members** → **A TASK NEEDS TO BE CREATED** (see task 3)

> `P5.4`'s completion criterion is only "Contribution table sums to 100%". The
> PDF additionally requires a written contribution description per member and
> signatures from everyone. Where contributions vary, members are graded
> **individually** from this form — so it directly affects each person's mark.

### Presentation — in class, Oct 19

- [ ] One **20-minute** slot → `P5.2` Henrieta · `P6.1` Zeyad · `P6.3` Henrieta
- [ ] Covers key problems studied → `P5.2` Henrieta
- [ ] Covers a clear overview of the pipeline → `P5.2` Henrieta
- [ ] Covers design choices → `P5.2` Henrieta
- [ ] Covers key findings → `P5.2` Henrieta
- [ ] Covers limitations → `P5.2` Henrieta
- [ ] Question-and-answer session with the audience → `P5.3` Patrick

---

## §6 — Where the marks are

| Component | Marks | Share |
|---|---|---|
| Report | 8 | 40% |
| Code and cleaned output datasets | 5 | 25% |
| Presentation | 5 | 25% |
| Q&A | 2 | 10% |
| **Total** | **20** | |

Worth noting when deciding where to spend the remaining time: **the report is
worth more than the code.** A working program with a thin report scores below a
good program with a thorough one. The presentation and Q&A together are worth
more than the code as well.

---

## §7 — Evaluation criteria

Not deliverables, but what the marks are awarded against. Re-read before `G3`
and `G5`.

- [ ] **Correctness & robustness** — the program runs on real, messy data without crashing → `G3` Patrick · `P4.1` Sarah
- [ ] **Code quality & design** — appropriate, well-structured use of OOP and data structures → `G1` Bahareh · `P3.5` Zeyad
- [ ] **Depth of analysis** — insightfulness and clarity of the reported findings → `P4.4` Henrieta
- [ ] **Report quality** — clarity, completeness, and reflection on design decisions → `P5.1` `G5` Bahareh
- [ ] **Presentation quality** — clarity of communication and **even participation across team members** → `P5.2` Henrieta · `P6.1` Zeyad

---

## §8 — Concepts the project must demonstrate

The assignment states what it is designed to exercise. These are not extra
requirements, but the grader is looking for each one to be visibly present.

| Concept | Where it shows up |
|---|---|
| Python fundamentals and control structures | throughout |
| Loops and functions | menu loop `P3.4`, all cleaners |
| Data structures I — lists and tuples | `P3.1` Henrieta |
| Data structures II — dictionaries and sets | `P3.1` Henrieta |
| File operations and error handling | `P2.4` Sarah, loader |
| Introduction to object-oriented programming | `P2.5` Zeyad |
| Object-oriented programming — inheritance | `P2.5` Zeyad |

If any concept is not clearly visible in the final code, that is a signal the
design has drifted from what the assignment is assessing.

---

## Tasks that need to be created

Four assignment requirements have no corresponding workbook task. Each needs an
owner and a slot in the schedule before the work it blocks can proceed.

| # | Requirement | Source | Blocks | Suggested owner |
|---|---|---|---|---|
| 1 | **CSV loading pipeline** — open files, validate headers, iterate and number rows, pass rows to the cleaners, assemble transaction objects, handle file and encoding errors | §2, §4.1 | `G2`, all of §4.2, every analysis task | Zeyad defines the interface; Sarah or Zeyad implements |
| 2 | **Repository creation and access** — create the GitHub repository, invite all five members, enable branch protection, agree the Python version | §5 (a GitHub link is required) | every task producing code | Zeyad |
| 3 | **Peer assessment signatures** — collect and verify signatures and written contribution descriptions from all five members, and confirm they appear in the submitted PDF | §5 | `DUE` | Sarah collects; Bahareh confirms |
| 4 | **Phase 2 entry point** — something runnable that loads and cleans the full dataset, so `G2` can be demonstrated | `G2` exit criteria | `G2` | Sarah or Zeyad |

> **Update 2026-10-11.** Tasks 1 and 4 now have workbook tasks. Reading the
> file is `P2.9` (loader, Patrick). Passing rows to the cleaners, assembling
> objects and giving `G2` something runnable is `P2.10` (pipeline, Sarah):
> `clean_file()` and `run()` in `budgetwise/pipeline`, pull request #10.

**Task 1 is the urgent one.** Four members build cleaning modules in parallel
during Phase 2 with no agreed structure to plug into, and `G2` is the first
moment the gap becomes visible.

**Task 4 has a cheaper alternative.** Rather than write a throwaway driver, pull
the bare menu skeleton from `P3.4` forward into Phase 2. `G2` then demonstrates
the real entry point, and the work is kept rather than discarded.

---

## Add to existing tasks

These requirements are plausibly within an existing task's scope, but that task
does not currently mention them. Add them to its exit criteria so they are not
assumed.

| Requirement | Task | Why it is at risk |
|---|---|---|
| Verify no pandas / NumPy in the core pipeline | `G3` `P4.1` | `G3` says "verify mandatory conventions", which reads as §4.5, not the §2 library rule |
| Explicit discussion of **trends** in the report | `P4.4` | "Trends" appears only in §2; §4.4's seven named outputs do not include one |
| Written contribution description per member | `P5.4` | `P5.4`'s criterion covers only the percentage total |

---

## Decisions the team must make

A task exists for each of these, but it cannot be completed until the team
agrees.

| Decision | Task | Why it matters |
|---|---|---|
| Which CSV is the official dataset | `P0.2` `G1` | Both are in `data/raw/`. They share no rows and cover different years and users. They must not be merged |
| Whether the licence permits committing raw data | `P0.2` `P4.3` | Determines whether the repository holds the CSVs or links to Kaggle |
| The class design, given the data has no account-type field | `P2.5` `G1` | The workbook mandates an Account hierarchy; the assignment marks it optional and warns against artificial subclasses |
| The closed category set, including Freelance, Bonus, Savings, and Misc | `P1.2` `G1` | The assignment's example canonical list has no home for these |
| Shared interfaces — the shape of a raw row, a cleaned row, a transaction object, and an error log entry | `P1.5` `G1` | Four people build cleaners in parallel against these |
| Budget scope — which five categories, what limits, and the justification | `P3.3` `G1` | The assignment requires written justification |
| How to handle the missing merchant column | `P4.4` | §4.2 asks for merchant sets the data cannot supply |
| Where the boundary sits between a **corrected** row and a **skipped** row | `P3.5` `G1` | §5 requires both counts reported separately. Without an agreed boundary the two numbers are arbitrary and cannot be compared between runs |

Each of these is recorded as `D01`–`D09` in [`decisions.md`](decisions.md), which
is where the outcome, the date, and the reasoning get written down.

---

## Using this file

1. Find the requirements carrying your task ID — that is your scope.
2. Cite the requirement in your pull request under "Closes".
3. Tick the box in the same pull request that delivers it.
4. At `G5`, every box is ticked or explicitly waived in writing.

An unticked box at `G5` is a lost mark. Raise blockers early rather than leaving
items open.
