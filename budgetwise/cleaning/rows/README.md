# cleaning/rows

Detects duplicate rows and checks that a row has what it needs.

| | |
|---|---|
| **Responsible** | Sarah |
| **Domain reviewer** | Patrick (`P1.4`) · Henrieta (`P2.4`) |
| **PR approval** | Zeyad or Patrick — see `CONTRIBUTING.md` |
| **Tasks** | `P1.4` profiling · `P2.4` implementation |
| **Status** | Not started |

## 1. What this folder does

Two jobs, both working on the whole row rather than a single field.

**Duplicates.** The main dataset has **900 exactly identical rows**. It also has
**1,900 repeated `transaction_id` values on rows that differ** — and §4.5 is
explicit that those are *not* duplicates and must not be dropped.

**Required fields.** A row missing its amount cannot become a transaction. A row
missing its date still can, because §4.5 says such rows may still count toward
category totals.

## 2. How other modules use it

```python
from budgetwise.cleaning.rows import is_duplicate, has_required_fields

if is_duplicate(raw_row):          # called on the RAW row, before normalization
    log.record(line, "row", Reason.DUPLICATE_ROW, raw=...)
    continue
```

Only `pipeline/` calls this.

## 3. What it produces

| Situation | Result |
|---|---|
| Row identical to one already seen | `True` — skip and log |
| Same `transaction_id`, any other field differs | `False` — **keep it** |
| `FOOD` vs `Food`, rest identical | `False` — different raw rows |
| Row with no `amount` | fails required-fields, skipped |
| Row with no `date` | passes — excluded from date analysis only |

Expected on the main dataset: 900 duplicates removed, 1,900 repeated IDs kept.

## 4. Requirements and tasks covered

| Requirement | Source | Task |
|---|---|---|
| Detect and remove or flag duplicate transaction entries | §4.1 | `P2.4` |
| A duplicate is a fully identical row | §4.5 | `P2.4` |
| A repeated `transaction_id` on differing rows is not a duplicate | §4.5 | `P2.4` |
| Duplicate detection on raw rows, before normalization | §4.5 | `P2.4` `G2` |
| Handle malformed or incomplete rows with `try`/`except` | §4.1 | `P2.4` |
| Use sets to detect duplicate transactions | §4.2 | `P2.4` |
| Number of duplicates detected | §5 | `P3.5` |

## 5. Folders

| Folder | Contents |
|---|---|
| `implementation/` | `duplicates.py`, `validator.py` |
| `testing/` | `test_duplicates.py`, `test_validator.py` |
| `supplementary/` | `duplicate_profile.md` |

## 6. Done when

- [ ] Exactly 900 duplicates found in the main dataset
- [ ] All 1,900 repeated-ID rows kept
- [ ] A test proves case variants are treated as different raw rows
- [ ] Rows missing `amount` rejected; rows missing only `date` kept
- [ ] Runs over 15,900 rows without noticeable delay
