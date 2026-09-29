# Shared definitions

**Status: outstanding.** This is the remaining `P0.1` deliverable.

One agreed meaning for each term below, so that five people writing separate
modules describe the same thing the same way. Several of these feed directly
into the report's required counts (§5), and two of them — duplicate and
uncategorized — are defined by the assignment itself and are not ours to choose.

Owner: Zeyad · Agreed at: `G1` · Related: [`decisions.md`](decisions.md)

## Rows and records

- Raw row
- Cleaned row
- Valid row
- Invalid row
- Skipped row
- Corrected row
- Flagged row
- Missing value

## Duplicates

- Duplicate transaction
- Repeated transaction ID

## Dates

- Missing date
- Unrecognized date format

## Categories

- Missing category
- Uncategorized transaction
- Raw category
- Normalized category
- Category mapping

## Amounts

- Unrecognized amount format
- Outlier / sentinel amount
- Currency label / symbol

## Objects

- Valid transaction object
- Income transaction
- Expense transaction

## Analysis

- Date-based analysis
- Category-based analysis

## Datasets and logging

- Raw dataset
- Cleaned dataset
- Error log entry

---

**Why this matters more than it looks.** §5 requires the report to state the
number of *valid*, *corrected*, and *skipped* records. If Bahareh counts a
reformatted date as corrected and Patrick counts a stripped currency symbol as
untouched, those three numbers cannot be produced consistently — and they are
graded.
