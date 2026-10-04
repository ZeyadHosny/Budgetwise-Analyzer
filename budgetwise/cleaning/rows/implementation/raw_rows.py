"""
raw_rows.py  -  whole rows, before any column is cleaned  (task P2.4, Sarah)

WHAT THE PROJECT SAYS (Project-1.pdf 4.1, 4.2, 4.5)
  * A "duplicate" is a FULLY IDENTICAL row.
  * A repeated transaction_id on rows that otherwise differ is NOT a
    duplicate. Do not drop those rows.
  * Duplicate detection must run on the ORIGINAL RAW rows, BEFORE any
    normalization.
  * Use a set to detect duplicates.
  * Malformed rows must not crash the program.

WHAT THE PHASE 2 SPEC SAYS (sections 2, 4, 5 and 6)
  * Duplicate key = "the ordered tuple of all nine original CSV fields".
  * Repeated transaction IDs: "Retain the row; flag the repeated ID".
  * Public functions: validate_raw_row(...), raw_duplicate_key(...)
  * The repository contract (rows/__init__.py) also names is_duplicate and
    has_required_fields, so both are provided here as well.
  * Reason codes: DUPLICATE_RAW_ROW (skipped), REPEATED_TRANSACTION_ID
    (flagged), MALFORMED_ROW (skipped or flagged).

WHAT PHASE 1 FOUND (15,900 rows)
  * 900 exact duplicate rows, leaving 15,000 unique rows
  * 1,680 transaction IDs appear more than once

WHAT IS IN THIS FILE
  1. Checks for the three required columns (transaction_id, user_id,
     transaction_type)
  2. raw_duplicate_key(), is_duplicate() and split_exact_duplicates()
  3. validate_raw_row() and has_required_fields()
  4. find_repeated_ids()

HOW IT WORKS
  A raw row is a dictionary from csv.DictReader: column name -> raw text.
  Rows are passed around as (row_number, raw_row) pairs, so every problem
  can be traced back to its line in the CSV file.
"""

import re
from collections import Counter

EXPECTED_COLUMNS = (
    "transaction_id", "user_id", "date", "transaction_type", "category",
    "amount", "payment_mode", "location", "notes",
)

# Reason codes
DUPLICATE_RAW_ROW = "DUPLICATE_RAW_ROW"                  # skipped
REPEATED_TRANSACTION_ID = "REPEATED_TRANSACTION_ID"      # flagged, row KEPT
MALFORMED_ROW = "MALFORMED_ROW"                          # skipped or flagged


# --------------------------------------------------------------------------
# CHECKS FOR THE THREE REQUIRED COLUMNS
# A row cannot be used without transaction_id, user_id and transaction_type.
# Phase 1 found all three complete and correctly formatted in every row, so
# these checks only protect against bad input. Each returns (value, reasons):
#   value   : the value to use, or None if the row is unusable
#   reasons : [] if fine, otherwise [MALFORMED_ROW]
# --------------------------------------------------------------------------
TRANSACTION_ID_PATTERN = re.compile(r"T\d{4,5}")   # T4999 or T12828
USER_ID_PATTERN = re.compile(r"U\d{3}")            # U018
VALID_TRANSACTION_TYPES = {"expense": "Expense", "income": "Income"}


def _check_identifier(raw, pattern):
    """Shared logic for the two ID columns. Valid IDs are kept as they are."""
    # No ID at all (blank, or not even text): the row cannot be traced.
    if not isinstance(raw, str) or raw.strip() == "":
        return None, [MALFORMED_ROW]
    value = raw.strip()
    if pattern.fullmatch(value):
        return value, []
    # Unusual ID: we do not invent a new one. Keep it, but report it.
    return value, [MALFORMED_ROW]


def check_transaction_id(raw):
    """transaction_id must be "T" followed by 4 or 5 digits."""
    return _check_identifier(raw, TRANSACTION_ID_PATTERN)


def check_user_id(raw):
    """user_id must be "U" followed by 3 digits."""
    return _check_identifier(raw, USER_ID_PATTERN)


def check_transaction_type(raw):
    """transaction_type must be Expense or Income (capitals do not matter).

    This column, not the sign of the amount, gives the direction of the
    money, so a row without a valid type cannot be used.
    """
    if not isinstance(raw, str):
        return None, [MALFORMED_ROW]
    value = VALID_TRANSACTION_TYPES.get(raw.strip().lower())
    if value is None:          # blank, or a word that is not Expense/Income
        return None, [MALFORMED_ROW]
    return value, []


# The three required columns and the check used for each.
REQUIRED_COLUMN_CHECKS = (
    ("transaction_id", check_transaction_id),
    ("user_id", check_user_id),
    ("transaction_type", check_transaction_type),
)


def raw_duplicate_key(row):
    """Return the duplicate key: an immutable tuple of the nine raw values.

    The values are used exactly as they are in the file: no trimming, no
    lowercase, no parsing. "Food" and "food" therefore give different keys.
    """
    try:
        key = tuple(row.get(column) for column in EXPECTED_COLUMNS)
        # csv.DictReader puts surplus values under the key None.
        surplus = row.get(None)
        if surplus:
            key += tuple(surplus)
        return key
    except AttributeError:
        return (repr(row),)   # not a dictionary: compare it by its text


def is_duplicate(row, seen_keys):
    """Return True if this exact raw row has been seen before.

    seen_keys is a set that the caller creates once (seen_keys = set()) and
    passes in for every row. The first time a row appears its key is added
    to the set and the answer is False. Any later identical row gives True.
    A set lookup is instant, so the whole file is checked in a single pass.
    """
    key = raw_duplicate_key(row)
    if key in seen_keys:
        return True
    seen_keys.add(key)
    return False


def split_exact_duplicates(numbered_rows):
    """Return (unique_rows, duplicate_rows) for a whole list of numbered rows.

    The first occurrence of each row is unique. Every later identical copy
    is a duplicate.
    """
    seen_keys = set()
    unique_rows = []
    duplicate_rows = []
    for row_number, row in numbered_rows:
        if is_duplicate(row, seen_keys):
            duplicate_rows.append((row_number, row))
        else:
            unique_rows.append((row_number, row))
    return unique_rows, duplicate_rows


def validate_raw_row(row):
    """Check one raw row. Return (usable, problems).

    usable   : False means the row must be skipped
    problems : list of (column, detail). Every problem is logged with the
               reason code MALFORMED_ROW. A row can be usable and still have
               a problem (an oddly formatted ID is kept but flagged).

    Blank date, category, amount, payment_mode, location or notes are NOT
    problems here. Each of those has its own cleaner and its own rule.
    """
    try:
        # 1. Is it a record at all?
        if not hasattr(row, "get") or not hasattr(row, "keys"):
            return False, [("row", f"not a record: {type(row).__name__}")]

        # 2. Exactly nine fields? DictReader stores extra values under the
        #    key None and fills missing trailing values with None.
        if row.get(None):
            return False, [("row", "too many fields")]
        for column in EXPECTED_COLUMNS:
            if column not in row or row[column] is None:
                return False, [("row", "too few fields")]

        # 3. The three required columns.
        usable = True
        problems = []
        for column, check in REQUIRED_COLUMN_CHECKS:
            value, reasons = check(row[column])
            if value is None:
                usable = False
                problems.append((column, f"missing or unusable value {row[column]!r}"))
            elif reasons:
                problems.append((column, f"unexpected format {row[column]!r}"))
        return usable, problems
    except Exception as error:     # anything unexpected still must not crash
        return False, [("row", f"could not be checked: {error}")]


def has_required_fields(row):
    """Return True if the row can be used: nine fields, with a usable
    transaction_id, user_id and transaction_type. A simple yes/no version of
    validate_raw_row() for callers that do not need the details."""
    return validate_raw_row(row)[0]


def find_repeated_ids(numbered_rows):
    """Return {transaction_id: how many rows carry it} for IDs seen 2+ times.

    On the raw file this gives the Phase 1 figure (1,680). On rows that have
    already had exact duplicates removed, it gives only the IDs shared by
    rows that genuinely differ. Those rows are kept and flagged.
    """
    counts = Counter()
    for _, row in numbered_rows:
        try:
            counts[row.get("transaction_id")] += 1
        except AttributeError:
            continue
    return {transaction_id: count for transaction_id, count in counts.items() if count > 1}
