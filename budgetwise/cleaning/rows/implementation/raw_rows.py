"""Row checks (P2.4, Sarah).

Works on whole raw rows, before any column is cleaned:
  * exact duplicate detection with a set
  * required-field validation
  * repeated transaction IDs (counted and flagged, never removed)
Rules are explained in README.md.
"""

import re
from collections import Counter

from budgetwise.errorlog import Reason

EXPECTED_COLUMNS = (
    "transaction_id", "user_id", "date", "transaction_type", "category",
    "amount", "payment_mode", "location", "notes",
)

TRANSACTION_ID_PATTERN = re.compile(r"T\d{4,5}")   # T4999 or T12828
USER_ID_PATTERN = re.compile(r"U\d{3}")            # U018
VALID_TRANSACTION_TYPES = {"expense": "Expense", "income": "Income"}


# Required-column checks. Each returns (value, reasons); value is None
# when the row cannot be used.

def _check_identifier(raw, pattern):
    """Shared check for the two ID columns."""
    if not isinstance(raw, str) or raw.strip() == "":
        return None, [Reason.MALFORMED_ROW]       # no ID: row cannot be traced
    value = raw.strip()
    if pattern.fullmatch(value):
        return value, []
    return value, [Reason.MALFORMED_ROW]          # unusual ID: kept, reported


def check_transaction_id(raw):
    """transaction_id must be "T" followed by 4 or 5 digits."""
    return _check_identifier(raw, TRANSACTION_ID_PATTERN)


def check_user_id(raw):
    """user_id must be "U" followed by 3 digits."""
    return _check_identifier(raw, USER_ID_PATTERN)


def check_transaction_type(raw):
    """transaction_type must be Expense or Income, in any capitals.

    It gives the direction of the money, so a row without it is unusable.
    """
    if not isinstance(raw, str):
        return None, [Reason.MALFORMED_ROW]
    value = VALID_TRANSACTION_TYPES.get(raw.strip().lower())
    if value is None:
        return None, [Reason.MALFORMED_ROW]
    return value, []


REQUIRED_COLUMN_CHECKS = (
    ("transaction_id", check_transaction_id),
    ("user_id", check_user_id),
    ("transaction_type", check_transaction_type),
)


# Duplicates

def raw_duplicate_key(row):
    """Return a tuple of the nine raw values, used exactly as in the file."""
    try:
        key = tuple(row.get(column) for column in EXPECTED_COLUMNS)
        surplus = row.get(None)            # DictReader stores extra values here
        if surplus:
            key += tuple(surplus)
        return key
    except AttributeError:
        return (repr(row),)                # not a dictionary


def is_duplicate(row, seen_keys):
    """Return True if this exact raw row is already in seen_keys.

    The caller creates one set per load. New keys are added to it.
    """
    key = raw_duplicate_key(row)
    if key in seen_keys:
        return True
    seen_keys.add(key)
    return False


def split_exact_duplicates(numbered_rows):
    """Return (unique_rows, duplicate_rows). The first copy is kept."""
    seen_keys = set()
    unique_rows = []
    duplicate_rows = []
    for row_number, row in numbered_rows:
        if is_duplicate(row, seen_keys):
            duplicate_rows.append((row_number, row))
        else:
            unique_rows.append((row_number, row))
    return unique_rows, duplicate_rows


# Validation

def validate_raw_row(row):
    """Return (usable, problems), where problems is a list of (column, detail).

    A row can be usable and still have a problem (an unusual ID is kept and
    flagged). Blank optional fields are left to their own cleaners.
    """
    try:
        if not hasattr(row, "get") or not hasattr(row, "keys"):
            return False, [("row", f"not a record: {type(row).__name__}")]

        # DictReader puts extra values under None and fills missing ones with None.
        if row.get(None):
            return False, [("row", "too many fields")]
        for column in EXPECTED_COLUMNS:
            if column not in row or row[column] is None:
                return False, [("row", "too few fields")]

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
    except Exception as error:             # bad input must never crash
        return False, [("row", f"could not be checked: {error}")]


def has_required_fields(row):
    """Return True if validate_raw_row() finds the row usable."""
    return validate_raw_row(row)[0]


# Repeated IDs

def find_repeated_ids(numbered_rows):
    """Return {transaction_id: row count} for IDs on two or more rows.

    Rows with no ID are ignored. IDs are compared after trimming spaces,
    as the pipeline stores them.
    """
    counts = Counter()
    for _, row in numbered_rows:
        try:
            transaction_id = row.get("transaction_id")
        except AttributeError:
            continue                       # not a record
        if not isinstance(transaction_id, str):
            continue
        transaction_id = transaction_id.strip()
        if transaction_id:
            counts[transaction_id] += 1
    return {transaction_id: count for transaction_id, count in counts.items() if count > 1}
