# cleaning/rows

Detects duplicate rows and checks that a row has what it needs.

| | |
|---|---|
| **Responsible** | Sarah |
| **Domain reviewer** | Patrick (`P2.4`) |
| **PR approval** | Zeyad or Patrick. See `CONTRIBUTING.md` |
| **Tasks** | `P2.4` implementation. Profiling is Bahareh's Phase 1 report (`P1.1`) |
| **Status** | Implemented and merged. Phase 2 review correction S03 applied |

## 1. What this folder does

Three jobs, all working on the whole row, not on a single field.

**Duplicates.** The main dataset has **900 exactly identical rows**. A
duplicate is a row whose nine raw values all match an earlier row. The
comparison uses the values exactly as they are in the file: no trimming, no
lowercase, no parsing.

**Repeated IDs.** **1,680** `transaction_id` values appear more than once in
the raw file. Section 4.5 is explicit that a repeated ID on rows that differ
is *not* a duplicate and must not be dropped. Those rows are kept and flagged.

**Required fields.** A row needs all nine fields, and a usable
`transaction_id`, `user_id` and `transaction_type`. Without those it cannot
be traced or given a direction, so it is skipped.

This folder does **not** judge the amount, date, category, payment mode,
location or notes. A blank in any of those is not a row problem. Each has its
own cleaner and its own rule. In particular, a row with no amount passes the
row check here and is skipped later by the pipeline, using the amount cleaner.

## 2. How other modules use it

```python
from budgetwise.cleaning.rows import is_duplicate, validate_raw_row

seen_keys = set()                    # create ONE set per load
for line, raw_row in rows:
    if is_duplicate(raw_row, seen_keys):     # on the RAW row, before normalization
        log.record(line, "row", Reason.DUPLICATE_ROW, raw_row["transaction_id"])
        continue
    usable, problems = validate_raw_row(raw_row)
```

Only `pipeline/` calls this.

Everything the folder exports:

| Name | Signature | Returns |
|---|---|---|
| `raw_duplicate_key` | `(row)` | tuple of the nine raw values, plus any surplus values |
| `is_duplicate` | `(row, seen_keys)` | `True` if this exact row was seen before. Adds new keys to the set |
| `split_exact_duplicates` | `(numbered_rows)` | `(unique_rows, duplicate_rows)` |
| `validate_raw_row` | `(row)` | `(usable, problems)`. `problems` is a list of `(column, detail)` |
| `has_required_fields` | `(row)` | `True` or `False`. The yes/no form of `validate_raw_row` |
| `find_repeated_ids` | `(numbered_rows)` | `{transaction_id: number of rows}` for IDs on two or more rows |
| `EXPECTED_COLUMNS` | | the nine column names, in file order |
| `DUPLICATE_RAW_ROW`, `REPEATED_TRANSACTION_ID`, `MALFORMED_ROW` | | reason codes |

A row is a dictionary of column name to raw text. `numbered_rows` is a list of
`(line_number, row)` pairs, as the loader produces.

`is_duplicate` takes **two** arguments. The caller owns the set, so loading a
file twice in one session starts from an empty set each time.

`has_required_fields` returns a plain `True` or `False`, not a tuple. Use
`validate_raw_row` when the reasons are needed, as the pipeline does.

## 3. What it produces

| Situation | Result |
|---|---|
| Row identical to one already seen | `is_duplicate` gives `True`: skip and log |
| Same `transaction_id`, any other field differs | `False`: **keep it**, flag the repeated ID |
| `FOOD` vs `Food`, rest identical | `False`: different raw rows |
| Missing or blank `transaction_id`, `user_id` or `transaction_type` | not usable: skipped |
| `transaction_type` that is not Expense or Income | not usable: skipped |
| Unusual ID such as `X99` | usable, with a problem: **kept and flagged** |
| Fewer or more than nine fields | not usable: skipped |
| Row with no `amount` | passes here. The pipeline skips it using the amount cleaner |
| Row with no `date` | passes. Kept, and left out of date analysis only |
| Something that is not a row at all | not usable. Never raises |

Missing and blank are different. A field that is absent, which
`csv.DictReader` reports as `None`, makes the row malformed. A field that is
present but empty is a blank value, and only matters for the three required
columns.

Repeated IDs: a row with no ID (missing, `None`, blank, only spaces, or not
text) is never counted, so two rows that both lack an ID do not "share" one.
IDs are compared after removing spaces at the ends, which is how the pipeline
stores them, so this folder and the pipeline always agree.

Expected on the main dataset: 900 duplicates removed, 15,000 rows left, no
malformed rows. Repeated-ID figures depend on which rows are counted:

| Rows counted | Distinct repeated IDs | Rows carrying them |
|---|---|---|
| Raw file, 15,900 rows | 1,680 | 3,580 |
| After exact duplicates are removed, 15,000 rows | 926 | 1,926 |
| Final cleaned records, 14,651 rows (from the pipeline) | 888 | 1,846 |

## 4. Requirements and tasks covered

| Requirement | Source | Task |
|---|---|---|
| Detect and remove or flag duplicate transaction entries | section 4.1 | `P2.4` |
| A duplicate is a fully identical row | section 4.5 | `P2.4` |
| A repeated `transaction_id` on differing rows is not a duplicate | section 4.5 | `P2.4` |
| Duplicate detection on raw rows, before normalization | section 4.5 | `P2.4` `G2` |
| Handle malformed or incomplete rows with `try`/`except` | section 4.1 | `P2.4` |
| Use sets to detect duplicate transactions | section 4.2 | `P2.4` |
| Number of duplicates detected | section 5 | `P3.8` |

Baselines come from Bahareh's Phase 1 profiling report.

## 5. Folders

| Folder | Contents |
|---|---|
| `implementation/` | `raw_rows.py` |
| `testing/` | `test_raw_rows.py`, 47 tests |
| `supplementary/` | `row_evidence.md` |

Run the tests from the repository root:

```bash
python -m unittest budgetwise.cleaning.rows.testing.test_raw_rows -v
```

Seven of the 47 tests use the full dataset and are skipped if the CSV is not
in `data/raw/`.

## 6. Done when

- [x] Exactly 900 duplicates found in the main dataset
- [x] Every row with a repeated ID is kept (1,680 IDs in the raw file)
- [x] A test proves case variants are treated as different raw rows
- [x] Rows missing a required field are rejected; rows missing only `date` kept
- [x] Rows with no ID are never reported as sharing an ID
- [x] Runs over 15,900 rows without noticeable delay (about 0.1 seconds)

Rejecting a row for a missing `amount` is done in `pipeline/`, not here.

## 7. Open points for the pipeline integration

- The loader currently fills a short row with blanks and drops surplus
  fields, so the "fewer or more than nine fields" checks only take effect
  once the loader keeps the row's real shape (review S05, Patrick).
- Reason-code names and casing are not yet approved by the team (review S08).
