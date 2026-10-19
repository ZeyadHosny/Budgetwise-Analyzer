# Requirements checklist

DATA 5010, Project 1: Personal Finance & Spending Analyzer
Due **Mon Oct 19, 2026, 11:59 PM EST** · Late deliverables are not accepted
Last updated: 2026-10-19 (final). Figures are from the official dataset,
`budgetwise_synthetic_dirty.csv` (decision D01), and match the report.

Every requirement in `Project-1.pdf`, in the order the assignment states them,
each mapped to its task in `DATA5010_Project1_Timeline_TeamPlan.xlsx`.

**Requirements come from the PDF. The workbook is checked against it, never the
reverse.**

### How to read a line

```
- [x] Requirement as the assignment states it → P2.1 · Sarah
```

A box is ticked when the work is merged to `main` and tested, or, for the
report and presentation, when it is in the final version. The few boxes still
open are listed under **Still open** at the end.

---

## Cleaning and pipeline status: `P2.1`, `P2.4`, `P2.7` and `P2.10` (Sarah)

Links each requirement owned by these four tasks to the code that delivers it
and the tests that check it.

### Requirement to code to test

| Requirement | Source | Task | Code | Tests |
|---|---|---|---|---|
| Parse every supported date format into `YYYY-MM-DD` | §4.1, §4.5 | `P2.1` | `parse_date()` in `budgetwise/cleaning/dates/implementation/parser.py` | `ValidFormatTests`, `FullDatasetTests` in `budgetwise/cleaning/dates/testing/test_parser.py` |
| Slash dates read month first; hyphen dates read day first | §4.5 | `P2.1` | `DATE_FORMATS` in `parser.py` | `AmbiguousDateTests` |
| Missing or unparseable date returns `None` with a reason; never raises | §4.5 | `P2.1` | `parse_date()` | `MissingDateTests`, `InvalidDateTests` |
| A duplicate is a fully identical raw row, found with a set | §4.1, §4.2, §4.5 | `P2.4` | `raw_duplicate_key()`, `is_duplicate()`, `split_exact_duplicates()` in `budgetwise/cleaning/rows/implementation/raw_rows.py` | `DuplicateKeyTests`, `IsDuplicateTests`, `ExactDuplicateTests` in `budgetwise/cleaning/rows/testing/test_raw_rows.py` |
| A repeated `transaction_id` on differing rows is kept and flagged | §4.5 | `P2.4` | `find_repeated_ids()` | `RepeatedIdTests`, `FullDatasetTests` |
| Malformed or incomplete rows handled without crashing | §4.1 | `P2.4` | `validate_raw_row()`, `has_required_fields()` | `ValidateRawRowTests`, `HasRequiredFieldsTests` |
| Meaningful notes preserved exactly; blank, N/A and placeholders flagged | team specification (not named in the PDF) | `P2.7` | `classify_note_quality()` in `budgetwise/cleaning/notes/implementation/note_quality.py` | `MeaningfulNoteTests`, `LowInformationNoteTests`, `FullDatasetTests` in `budgetwise/cleaning/notes/testing/test_note_quality.py` |
| Duplicate detection runs on raw rows before normalization | §4.5 | `P2.10` | step 2 of `_clean_rows()` in `budgetwise/pipeline/implementation/runner.py` | `OrderTests` in `budgetwise/pipeline/testing/test_runner.py` |
| Skipped, corrected and flagged rows logged with a reason | §4.1 | `P2.10` with `P2.8` | `_record_issue()` in `runner.py`, writing through `ErrorLog.record()` | `CleaningTests`, `RowValidationTests` |
| The program must not crash on bad input | §4.1 | `P2.10` | per-row guard in `_clean_rows()` | `BadInputTests`, `FailureBoundaryTests` |
| Counts reconcile: input = valid + skipped + duplicates | §5 | `P2.10` | `_empty_counts()`, `_summarise()` in `runner.py` | `CleaningTests`, `FlaggedCountTests`, `FullDatasetTests` |
| Transactions stored as a list of objects | §4.2 | `P2.10` with `P3.1` | `run()` and `_build_objects()` in `runner.py` | `ObjectTests`, `ClassUseTests` |
| Load a subset by date range or by category | §4.1 | `P2.10` with `P3.5` | `_passes_filters()` in `runner.py` | `FilterTests` |

### Test results on `main`

Run from the repository root with `python3 -m unittest`, dataset present in
`data/raw/`:

| Folder | Tests |
|---|---|
| `cleaning/rows` | 47 |
| `cleaning/dates` | 28 |
| `cleaning/notes` | 12 |
| `pipeline` | 95 |
| **Whole repository** | **800 tests, OK (expected failures=3)** |

The three expected failures are checks on the loader and amount parser (review
items S05 and S09). They are marked with `until_fixed`, not hidden.

Full-dataset result: 15,836 input = 14,862 valid + 170 skipped + 804
duplicates. All 14,862 valid records became transaction objects, with no
failures. Detail is in each feature's `supplementary/` folder.

---

## §2: Objective, scope, and constraints

### What the application must do

- [x] Ingest transaction data from CSV files → `P2.9` Patrick (loader) · `P2.10` Sarah (pipeline)
- [x] Clean and validate the data, handling errors gracefully rather than crashing → `P2.1`–`P2.4` all
- [x] Represent transactions and accounts using an object-oriented class hierarchy, including inheritance → `P3.1` Zeyad
- [x] Organize and aggregate data using lists, tuples, dictionaries, and sets → `P3.2` Henrietta
- [x] Produce meaningful analysis: spending summaries, budget comparisons, **and trends** → `P3.3` Bahareh · `P3.4` Patrick · trends: monthly expenses in 2022, report Figure 3
- [x] Export results to a report file → `P3.7` Patrick

> **"Trends" appears only here.** §4.4 lists seven required outputs and none of
> them is named a trend. The report covers it with the monthly expenses for
> 2022 (Figure 3), noting the highest month (September) and the lowest (June).

### Hard constraints

- [x] **Core ingestion, cleaning, aggregation, and analysis use the Python standard library only** → `G3` Patrick · checked: no pandas or NumPy import anywhere
- [x] **pandas, NumPy, and other data-analysis libraries are not used** for those tasks → `G3` Patrick · `P4.1` Henrietta
- [x] The user interface is a simple **text-based menu** → `P3.5` Zeyad
- [x] **No graphical user interface** is built → `P3.5` Zeyad

> **This is the single most dangerous requirement in the assignment.** Permitted
> modules include `csv`, `datetime`, `json`, `collections`, and `os`. A single
> `import pandas` in the cleaning or analysis path violates a stated constraint,
> and no amount of working code compensates.
>
> Checked with `grep -rn "import pandas\|import numpy" budgetwise/`: no matches.

---

## §3: Data

- [x] All teams use the same dataset → `P0.2` Sarah · `budgetwise_synthetic_dirty.csv`, decision D01
- [ ] Record the file's row count and download date in `README.md` → `P0.2` Sarah · `P4.3` Zeyad · **row counts recorded in `data/README.md`; download date still missing**
- [x] Inspect the schema rather than assuming a fixed structure → `P1.1`–`P1.4` all
- [x] Document any assumptions made about the data in the report → `P4.4` Henrietta
- [x] Do not commit raw data to a public repository if the licence restricts redistribution, link to Kaggle and include download instructions in `README.md` → `P0.2` Sarah · `P4.3` Zeyad · licence is CC0, so both files are committed (D02)

The assignment states the dataset contains multi-format dates, currency
inconsistencies, text typos and inconsistent capitalization, duplicate entries,
missing values, and a mix of income and expense records, with **roughly 30% of
records carrying some data issue**. That figure is a useful sanity check: if your
cleaning reports far fewer problems than that, your detection is probably too
narrow.

---

## §4.1: Data ingestion and cleaning

- [x] **Read transaction data from the BudgetWise CSV file(s)** → `P2.9` Patrick (loader) · `P2.10` Sarah (pipeline)
- [x] Parse and standardize the multiple date formats into a single consistent format → `P2.1` Sarah · profiling `P1.1` Bahareh
- [x] Normalize inconsistent currency symbols and formats in the amount field into a single numeric representation → `P1.3` `P2.3` Patrick
- [x] Handle malformed or incomplete rows, missing values, bad dates, unparseable amounts, using `try`/`except` → `P2.4` Sarah (row checks, merged) · `P2.10` Sarah (applied per row, merged in #10)
- [x] **The program must not crash on bad input** → `P2.4` Sarah · `P2.10` Sarah (merged in #10) · `P4.1` Henrietta
- [x] Detect and remove or flag duplicate transaction entries → `P2.4` Sarah (detection, merged) · `P2.10` Sarah (removal and logging, merged in #10)
- [x] Log skipped, corrected, or flagged rows to **`errors.log`**, each with a brief reason → `P2.8` Patrick (logger) · `P2.10` Sarah (pipeline writes every issue, merged in #10)
- [x] Support loading the dataset, or a subset, through a menu-driven interface → `P1.5` Zeyad (skeleton) · `P3.5` Zeyad (implementation)
- [x] The menu is interactive, a `while` loop reading `input()`, **not a one-shot script** → `P3.5` Zeyad

### The menu itself

The assignment prints the menu it expects, so each option is checked separately.

- [x] `1. Load full dataset` → `P3.5` Zeyad
- [x] `2. Load transactions by date range`, prompts for start and end dates → `P3.5` Zeyad
- [x] `3. Load transactions by category` → `P3.5` Zeyad
- [x] `4. View error log` → `P3.5` Zeyad
- [x] `5. Exit` → `P3.5` Zeyad
- [x] Invalid menu input handled without crashing → `P3.5` Zeyad

> §4.1's prose mentions only a date range, but the printed menu also requires
> **loading by category**. Both filters are required. Reading the paragraph and
> skipping the code block produces a program missing a graded feature.
>
> Reading the file is `P2.9` (loader). Passing rows to the cleaners and
> building the objects is `P2.10` (pipeline).

---

## §4.2: Data organization

- [x] Store transactions as a **list** of objects → `P2.10` Sarah with `P3.1` Zeyad
- [x] Use **dictionaries** to aggregate totals by category and by month → `P3.2` Henrietta
- [x] Use **sets** to identify unique categories and detect duplicate transactions → `P3.2` Henrietta (`unique_categories()`) · `P2.4` Sarah (duplicates)
- [x] Use **tuples** for fixed keys, for example `(year, month)` → `P3.2` Henrietta

> §4.2 also asks for unique **merchants**. Neither CSV has a merchant column , 
> the nine columns are `transaction_id`, `user_id`, `date`, `transaction_type`,
> `category`, `amount`, `payment_mode`, `location`, `notes`. Document the absence
> in the report under `P4.4`. Do not relabel `location` or `notes` as merchants.

---

## §4.3: Object-oriented design

- [x] At least one clear example of **inheritance** → `P3.1` Zeyad
- [x] The inheritance represents a meaningful "is-a" relationship, not an artificial subclass created to satisfy the requirement → `P3.1` Zeyad · `G1` Bahareh
- [x] Appropriate use of **encapsulation** → `P3.1` Zeyad
- [x] At least one class demonstrates encapsulation using **private or protected attributes** with methods or properties controlling access → `P3.1` Zeyad
- [x] A **`Budget`** class comparing actual spending against category limits and flagging overages → `P3.1` Zeyad
- [x] Justify the class design in the written report → `P4.4` Henrietta

> Decided in D03. `ExpenseTransaction` and `IncomeTransaction` inherit from
> `Transaction`. `CashAccount`, `BankAccount` and `UnknownAccount` inherit from
> `Account` and group transactions by payment mode, which the data has, rather
> than inventing bank accounts, which it does not. `Budget` compares spending
> with limits. The report justifies the design (Figure 1).

---

## §4.4: Analysis and reporting

The assignment names these seven outputs explicitly.

- [x] Total income → `P3.3` Bahareh
- [x] Total expenses → `P3.3` Bahareh
- [x] Net balance → `P3.3` Bahareh
- [x] Monthly expenses → `P3.3` Bahareh
- [x] Top 5 spending categories → `P3.3` Bahareh
- [x] Top 5 largest expense transactions → `P3.4` Patrick
- [x] Budget vs. actual spending by category → `P3.4` Patrick

And:

- [x] Clear **over/under indicators** on the budget comparison → `P3.4` Patrick
- [x] Monthly budget limits defined for **at least five categories** → `P3.4` Patrick
- [x] Those budget limits are **justified** → `P3.4` Patrick · `P4.4` Henrietta
- [x] A simple text-based visualization of spending by month or category, e.g. a bar chart using `*` → `P3.6` Henrietta
- [x] Export a cleaned summary to a new CSV or JSON file → `P3.7` Patrick

---

## §4.5: Data handling conventions

The assignment calls these **mandatory** and says to follow them exactly, so all
teams are graded on a consistent standard. Deviating costs marks even if the
program runs correctly.

### Amounts

- [x] Strip the currency symbol or suffix, `₹`, `$`, `Rs.`, or trailing `INR`, and treat the remaining number as-is → `P2.3` Patrick
- [x] **Attempt no currency conversion** → `P2.3` Patrick
- [x] Log which currency symbol each row originally carried → `P2.3` Patrick
- [x] Treat any amount ≥ **`100,000,000`** as invalid, exclude from totals and analysis, and log it → `P2.3` Patrick
- [x] Treat amount as an **unsigned magnitude** → `P2.3` Patrick
- [x] Determine direction from the **`transaction_type`** field, never from the sign of the amount → `P2.3` Patrick

### Dates

- [x] Convert all valid dates to **`YYYY-MM-DD`** → `P2.1` Sarah
- [x] Where day and month are both ≤ 12, read **slash-separated** dates as `MM/DD/YYYY` → `P2.1` Sarah
- [x] Where day and month are both ≤ 12, read **hyphen-separated two-digit-year** dates as `DD-MM-YY` → `P2.1` Sarah · four-digit-year hyphen dates also read day first, see `decisions.md`
- [x] Document this date convention in the report → `P4.4` Henrietta
- [x] Any date that cannot be parsed by these rules is logged and **excluded from date-based analysis** → `P2.1` Sarah (returns `None` with a reason, merged) · `P2.10` Sarah (logs it, merged in #10)
- [x] A missing date is logged and excluded from date-based analysis, but the row **may still count toward category totals** → `P2.1` Sarah · `P2.10` Sarah (row kept with no date, merged in #10) · `P3.2` Henrietta

### Categories

- [x] A missing category is assigned **`"Uncategorized"`**, never dropped → `P2.2` Henrietta
- [x] Maintain a documented, **closed** mapping from raw category strings to a fixed set of normalized names → `P1.2` `P2.2` Henrietta
- [x] Include the raw-to-normalized mapping in the report → `P4.4` Henrietta

> The assignment offers an example canonical set: Food, Rent, Transportation,
> Entertainment, Shopping, Utilities, Healthcare, Education, Salary, Investment,
> Other, Uncategorized. It is an example, not a mandate, but any set you choose
> must be closed and documented. Note that the raw data also contains Freelance,
> Bonus, Savings, and Misc, which have no home in that example list. Resolved in
> D04: a closed set of 14 categories.

### Rows

- [x] A duplicate is a **fully identical row** → `P2.4` Sarah
- [x] A repeated `transaction_id` on rows that otherwise differ is **not** a duplicate and must not be dropped → `P2.4` Sarah
- [x] Duplicate detection is performed on the original **raw rows, before normalization** → `P2.4` Sarah (key uses raw values, merged) · `P2.10` Sarah (order enforced, merged in #10)
- [x] Any date or amount format not covered by the parsing logic is logged and skipped, never crashes, never silently misparsed → `P2.1` Sarah · `P2.3` Patrick · one open amount case is an expected failure (S09)

### Provenance

- [ ] Record the dataset's row count and download date in `README.md` → `P0.2` Sarah · `P4.3` Zeyad · **download date still missing**

---

## §5: Deliverables

### Submission

- [ ] Submit a **PDF** copy of the report via Canvas, one per group → `DUE` Bahareh
- [x] The report contains the GitHub link → `P4.3` Zeyad
- [x] The GitHub project contains the source code → `G4` Zeyad
- [ ] The GitHub project contains input and output datasets, **or links to them** → `P4.2` Patrick · **inputs committed; final outputs must be committed with `git add -f`**
- [x] A clear `README.md` instructing how to run the code on the datasets → `P4.3` Zeyad
- [x] The `README.md` also explains **how to comprehend the outputs** → `P4.3` Zeyad

### Report format: verified at `G5`

- [ ] Within **10 pages**, excluding references and peer assessment → `G5` Bahareh
- [ ] **Single-column** format → `G5` Bahareh
- [ ] **11pt** font size → `G5` Bahareh
- [ ] **Arial** font → `G5` Bahareh

### Report content

- [x] Key problems studied → `P4.4` Henrietta
- [x] Solutions proposed, theory, algorithms, and systems → `P4.4` Henrietta
- [x] Implementation details, datasets, programming language, tools, code summary → `P4.4` Henrietta
- [x] A **design flow diagram** based on important subroutines → `P1.5` Zeyad · `P5.1` Bahareh
- [x] Limitations and future work → `P4.4` Henrietta
- [x] **Conclusion** → `P5.1` Bahareh

### Key experimental results: measured, not estimated

The assignment lists these specifically, under both effectiveness and efficiency.

- [x] Number of input records → `P3.8` Henrietta · `P4.2` Patrick
- [x] Number of valid records → `P3.8` Henrietta
- [x] Number of corrected records → `P3.8` Henrietta
- [x] Number of invalid / skipped records → `P3.8` Henrietta
- [x] Number of duplicates detected → `P3.8` Henrietta
- [x] Number of categories normalized → `P3.8` Henrietta
- [x] Execution time for **loading** → `P3.8` Henrietta
- [x] Execution time for **cleaning** → `P3.8` Henrietta
- [x] Execution time for **analysis** → `P3.8` Henrietta

### Peer assessment

The blank form is printed at the end of the assignment PDF. It has three columns.

- [ ] Peer assessment completed at the **end** of the report → `P5.4` Sarah
- [x] Every member's **name** listed → `P5.4` Sarah
- [x] Every member has a **written description of their individual contribution** → `P5.4` Sarah
- [x] Every member has a **percentage of contribution** → `P5.4` Sarah
- [x] The percentages **sum to 100%** → `P5.4` Sarah
- [ ] **Signed by all team members** → `P5.4` Sarah collects · Bahareh confirms in the PDF

> `P5.4`'s completion criterion is only "Contribution table sums to 100%". The
> PDF additionally requires a written contribution description per member and
> signatures from everyone. Where contributions vary, members are graded
> **individually** from this form, so it directly affects each person's mark.

### Presentation: in class, Oct 19

- [ ] One **20-minute** slot → `P5.2` Henrietta · `P6.1` Zeyad · `P6.3` Henrietta
- [x] Covers key problems studied → `P5.2` Henrietta
- [x] Covers a clear overview of the pipeline → `P5.2` Henrietta
- [x] Covers design choices → `P5.2` Henrietta
- [x] Covers key findings → `P5.2` Henrietta
- [x] Covers limitations → `P5.2` Henrietta
- [ ] Question-and-answer session with the audience → `P5.3` Patrick

---

## §6: Where the marks are

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

## §7: Evaluation criteria

Not deliverables, but what the marks are awarded against. Re-read before `G3`
and `G5`.

- [x] **Correctness & robustness**: the program runs on real, messy data without crashing → `G3` Patrick · `P4.1` Henrietta
- [x] **Code quality & design**: appropriate, well-structured use of OOP and data structures → `G1` Bahareh · `P3.8` Henrietta
- [x] **Depth of analysis**: insightfulness and clarity of the reported findings → `P4.4` Henrietta
- [x] **Report quality**: clarity, completeness, and reflection on design decisions → `P5.1` `G5` Bahareh
- [ ] **Presentation quality**: clarity of communication and **even participation across team members** → `P5.2` Henrietta · `P6.1` Zeyad

---

## §8: Concepts the project must demonstrate

The assignment states what it is designed to exercise. These are not extra
requirements, but the grader is looking for each one to be visibly present.

| Concept | Where it shows up |
|---|---|
| Python fundamentals and control structures | throughout |
| Loops and functions | menu loop `P3.5`, all cleaners |
| Data structures I, lists and tuples | `P3.2` Henrietta |
| Data structures II, dictionaries and sets | `P3.2` Henrietta |
| File operations and error handling | `P2.4` Sarah, loader |
| Introduction to object-oriented programming | `P3.1` Zeyad |
| Object-oriented programming, inheritance | `P3.1` Zeyad |

If any concept is not clearly visible in the final code, that is a signal the
design has drifted from what the assignment is assessing.

---

## Tasks that needed to be created

Four assignment requirements had no workbook task at the start. The outcome is
below the table.

| # | Requirement | Source | Blocks | Suggested owner |
|---|---|---|---|---|
| 1 | **CSV loading pipeline**: open files, validate headers, iterate and number rows, pass rows to the cleaners, assemble transaction objects, handle file and encoding errors | §2, §4.1 | `G2`, all of §4.2, every analysis task | Zeyad defines the interface; Sarah or Zeyad implements |
| 2 | **Repository creation and access**: create the GitHub repository, invite all five members, enable branch protection, agree the Python version | §5 (a GitHub link is required) | every task producing code | Zeyad |
| 3 | **Peer assessment signatures**: collect and verify signatures and written contribution descriptions from all five members, and confirm they appear in the submitted PDF | §5 | `DUE` | Sarah collects; Bahareh confirms |
| 4 | **Entry point for `G2`**: something runnable that loads and cleans the full dataset, so `G2` can be demonstrated | `G2` exit criteria | `G2` | Sarah or Zeyad |

> **Update 2026-10-11.** Tasks 1 and 4 now have workbook tasks. Reading the
> file is `P2.9` (loader, Patrick). Passing rows to the cleaners, assembling
> objects and giving `G2` something runnable is `P2.10` (pipeline, Sarah):
> `clean_file()` and `run()` in `budgetwise/pipeline`, merged in #10.

**Outcome.** Tasks 1 and 4 became `P2.9` and `P2.10`. Task 2 is done: the
repository exists with all five members. Task 3 is in progress: see
[`peer_assessment.md`](peer_assessment.md).

---

## Add to existing tasks

These requirements were not named in their task at the start. All three are
now done: no pandas or NumPy (checked), trends discussed in the report
(Figure 3), and a written description for each member in the peer
assessment.

| Requirement | Task | Why it is at risk |
|---|---|---|
| Verify no pandas / NumPy in the core pipeline | `G3` `P4.1` | `G3` says "verify mandatory conventions", which reads as §4.5, not the §2 library rule |
| Explicit discussion of **trends** in the report | `P4.4` | "Trends" appears only in §2; §4.4's seven named outputs do not include one |
| Written contribution description per member | `P5.4` | `P5.4`'s criterion covers only the percentage total |

---

## Decisions the team made

Each of these needed a team decision before its task could be completed.

| Decision | Task | Why it matters |
|---|---|---|
| Which CSV is the official dataset | `P0.2` `G1` | Both are in `data/raw/`. They share no rows and cover different years and users. They must not be merged |
| Whether the licence permits committing raw data | `P0.2` `P4.3` | Determines whether the repository holds the CSVs or links to Kaggle |
| The class design, given the data has no account-type field | `P3.1` `G1` | The workbook mandates an Account hierarchy; the assignment marks it optional and warns against artificial subclasses |
| The closed category set, including Freelance, Bonus, Savings, and Misc | `P1.2` `G1` | The assignment's example canonical list has no home for these |
| Shared interfaces, the shape of a raw row, a cleaned row, a transaction object, and an error log entry | `P1.5` `G1` | Four people build cleaners in parallel against these |
| Budget scope, which five categories, what limits, and the justification | `P3.4` `G1` | The assignment requires written justification |
| How to handle the missing merchant column | `P4.4` | §4.2 asks for merchant sets the data cannot supply |
| Where the boundary sits between a **corrected** row and a **skipped** row | `P3.8` `G1` | §5 requires both counts reported separately. Without an agreed boundary the two numbers are arbitrary and cannot be compared between runs |

All of these are now decided and recorded in [`decisions.md`](decisions.md):
dataset D01, licence D02, classes D03, categories D04, interfaces D05, budgets
D06, merchants D07, corrected and skipped D08.

---

## Using this file

1. Find the requirements carrying your task ID, that is your scope.
2. Cite the requirement in your pull request under "Closes".
3. Tick the box in the same pull request that delivers it.
4. At `G5`, every box is ticked or explicitly waived in writing.

An unticked box at `G5` is a lost mark. Raise blockers early rather than leaving
items open.

---

## Still open

Everything else above is ticked. These boxes are still open:

| Item | Owner | What to do |
|---|---|---|
| Dataset download date in the README | `P0.2` `P4.3` | Add the date to `data/README.md` |
| Output datasets in the repository | `P4.2` | `git add -f` the final cleaned CSV and summary JSON |
| Peer assessment signed and at the end of the report | `P5.4` `DUE` | Collect signatures; add the page to the PDF |
| Report format: 10 pages, single column, Arial 11pt | `G5` | Check the exported PDF, not the editor |
| PDF submitted on Canvas | `DUE` | Before 11:59 PM EST, Oct 19 |
| Presentation and Q&A | all | In class, Oct 19 |
