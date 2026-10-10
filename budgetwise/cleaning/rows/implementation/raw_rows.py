"""
raw_rows.py - Whole-row checks before column cleaning (task P2.4, Sarah).

WHAT THE PROJECT SAYS (Project-1.pdf 4.1, 4.2, 4.5)
  * A duplicate is a fully identical row.
  * A repeated transaction_id on otherwise different rows is not a
    duplicate. Do not drop those rows.
  * Duplicate detection must run on original raw rows before normalization.
  * Use a set to detect duplicates.
  * Malformed rows must not crash the application.

WHAT THE PHASE 2 SPEC SAYS (sections 2, 4, 5 and 6)
  * Duplicate key: the ordered tuple of all nine original CSV fields.
  * Repeated transaction IDs: retain the row and flag the repeated ID.
  * Public functions include validate_raw_row() and raw_duplicate_key().
  * The repository contract also names is_duplicate() and
    has_required_fields(), so both are provided.
  * Reason codes:
      DUPLICATE_RAW_ROW: skipped duplicate.
      REPEATED_TRANSACTION_ID: flagged repeated ID.
      MALFORMED_ROW: skipped or flagged malformed input.

REPORTED PHASE 1 BASELINES (BEFORE CLEANING)
  * 15,900 raw rows.
  * 900 exact duplicate rows, leaving 15,000 unique raw rows.
  * 1,680 transaction IDs appearing more than once.

These figures document the earlier profiling results. This module does
not assert that every input file has those counts.

CONTENTS
  1. Checks for transaction_id, user_id, and transaction_type.
  2. Raw duplicate keys and duplicate separation.
  3. Structural row validation.
  4. Repeated transaction-ID counting.

INPUT AND OUTPUT CONTRACT
  A normal raw row is a csv.DictReader dictionary containing original
  field strings. Numbered rows are (source_line, raw_row) pairs.

  Functions return values, validation details, or duplicate information.
  This module does not call a logger, construct transaction objects,
  or mutate field values in the supplied rows.

  Duplicate-key values and transaction IDs must be hashable. Normal CSV
  strings and None satisfy this condition.
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
# Phase 1 reported these fields as complete and correctly formatted.
# These checks also protect against future invalid input.
#
# Each check returns (value, reasons):
#   value: usable checked value, or None
#   reasons: [] when accepted without a flag, otherwise [MALFORMED_ROW]
# --------------------------------------------------------------------------
TRANSACTION_ID_PATTERN = re.compile(r"T\d{4,5}")   # T4999 or T12828
USER_ID_PATTERN = re.compile(r"U\d{3}")            # U018
VALID_TRANSACTION_TYPES = {"expense": "Expense", "income": "Income"}


def _check_identifier(raw, pattern):
    """Check an identifier against a supplied regular expression.

    Args:
        raw: Original identifier value.
        pattern: Compiled regular expression used with fullmatch().

    Returns:
        A (value, reasons) tuple:
            Missing, blank, or non-string input returns
            (None, [MALFORMED_ROW]).
            A matching identifier returns its stripped value and [].
            A nonblank identifier with an unexpected format returns its
            stripped value and [MALFORMED_ROW].

    Notes:
        Unexpected formats are flagged rather than rejected.
        Leading and trailing whitespace is removed from the returned
        value, but the original row is not modified.
    """
    # No usable identifier was provided.
    if not isinstance(raw, str) or raw.strip() == "":
        return None, [MALFORMED_ROW]

    value = raw.strip()
    if pattern.fullmatch(value):
        return value, []

    # Unusual ID: do not invent a replacement. Keep it and report it.
    return value, [MALFORMED_ROW]


def check_transaction_id(raw):
    """Check the expected transaction-ID format.

    Args:
        raw: Original transaction_id value.

    Returns:
        Checked value and reason-code list from _check_identifier().

    Notes:
        The expected format is "T" followed by four or five digits.
        Nonblank values with other formats are retained and flagged.
        Missing or non-string values are unusable.
    """
    return _check_identifier(raw, TRANSACTION_ID_PATTERN)


def check_user_id(raw):
    """Check the expected user-ID format.

    Args:
        raw: Original user_id value.

    Returns:
        Checked value and reason-code list from _check_identifier().

    Notes:
        The expected format is "U" followed by three digits.
        Nonblank values with other formats are retained and flagged.
        Missing or non-string values are unusable.
    """
    return _check_identifier(raw, USER_ID_PATTERN)


def check_transaction_type(raw):
    """Validate and normalize transaction type to Expense or Income.

    Args:
        raw: Original transaction_type value.

    Returns:
        ("Expense", []) or ("Income", []) for accepted text, ignoring
        surrounding whitespace and capitalization.
        Unsupported, blank, or non-string input returns
        (None, [MALFORMED_ROW]).

    Notes:
        This field, not the amount sign, determines money direction.
        Accepted capitalization and whitespace variations do not produce
        an issue code here. The pipeline can log those normalizations.
        The supplied row is not modified.
    """
    if not isinstance(raw, str):
        return None, [MALFORMED_ROW]

    value = VALID_TRANSACTION_TYPES.get(raw.strip().lower())
    if value is None:          # Blank or not Expense/Income.
        return None, [MALFORMED_ROW]

    return value, []


# The three required columns and the check used for each.
REQUIRED_COLUMN_CHECKS = (
    ("transaction_id", check_transaction_id),
    ("user_id", check_user_id),
    ("transaction_type", check_transaction_type),
)


def raw_duplicate_key(row):
    """Build an immutable comparison key from original field values.

    Args:
        row: Raw dictionary normally produced by csv.DictReader.

    Returns:
        An ordered tuple of values for EXPECTED_COLUMNS.
        Missing keys contribute None. Surplus CSV values stored under
        the key None are appended when present.

        If accessing the mapping raises AttributeError, returns a
        one-element tuple containing repr(row).

    Notes:
        No trimming, capitalization changes, or parsing is performed.
        For example, "Food" and "food" produce different keys.

        For a normal nine-field row, the key has nine values.
        Surplus values distinguish malformed rows with different extra
        content; structural validation subsequently rejects those rows.

        Values must be hashable when this key is used in a set.
        This function does not validate the row or modify it.
    """
    try:
        key = tuple(row.get(column) for column in EXPECTED_COLUMNS)

        # csv.DictReader puts surplus values under the key None.
        surplus = row.get(None)
        if surplus:
            key += tuple(surplus)

        return key
    except AttributeError:
        return (repr(row),)   # Compare non-mapping input by its text.


def is_duplicate(row, seen_keys):
    """Check whether a raw-row key has already been encountered.

    Args:
        row: Raw row passed to raw_duplicate_key().
        seen_keys: Mutable set shared across rows in one detection run.

    Returns:
        True when the key is already present.
        False for its first occurrence.

    Side Effects:
        Adds a previously unseen key to seen_keys.

    Notes:
        Set lookup has average constant-time complexity; it is not
        literally instantaneous. Keys must contain hashable values.
        Errors from key construction or set operations propagate.
    """
    key = raw_duplicate_key(row)
    if key in seen_keys:
        return True

    seen_keys.add(key)
    return False


def split_exact_duplicates(numbered_rows):
    """Separate first occurrences from later identical raw rows.

    Args:
        numbered_rows: Iterable of (source_line, raw_row) pairs.

    Returns:
        A (unique_rows, duplicate_rows) tuple containing two lists.
        Both lists preserve encounter order and source-line identifiers.

    Notes:
        The first occurrence of each raw key is retained in unique_rows.
        Each later occurrence is placed in duplicate_rows.
        No normalization or transaction-ID-only deduplication is used.
        Row dictionaries are referenced without being copied or mutated.

        Call this before cleaning. Exceptions from pair unpacking or
        duplicate-key processing propagate to the caller.
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
    """Check row structure and the three required identifying fields.

    Args:
        row: Raw mapping expected to contain the nine dataset columns.

    Returns:
        A (usable, problems) tuple:
            usable: False when the row must be skipped.
            problems: List of (column, detail) pairs describing issues
                for the pipeline to log as MALFORMED_ROW.

        A row may be usable while containing flagged identifier formats.

    Validation:
        Rejects input without get() and keys() methods.
        Rejects truthy surplus CSV values under the key None.
        Rejects absent expected columns or values of None.
        Checks transaction_id, user_id, and transaction_type.

        Empty strings in optional fields are left to their field
        cleaners. Empty amounts may later cause row exclusion.

    Error Handling:
        Exceptions raised inside the validation block are converted to
        a row-level problem rather than propagated.

    Notes:
        Checked or normalized values are not written back to the row
        and are not included in the return value.
        Additional named keys outside EXPECTED_COLUMNS are not rejected
        by this implementation.
        This function performs no logging.
    """
    try:
        # 1. Is it a record at all?
        if not hasattr(row, "get") or not hasattr(row, "keys"):
            return False, [("row", f"not a record: {type(row).__name__}")]

        # 2. DictReader stores surplus CSV values under None and fills
        #    missing trailing fields with None.
        if row.get(None):
            return False, [("row", "too many fields")]

        for column in EXPECTED_COLUMNS:
            if column not in row or row[column] is None:
                return False, [("row", "too few fields")]

        # 3. Check the three required columns.
        usable = True
        problems = []

        for column, check in REQUIRED_COLUMN_CHECKS:
            value, reasons = check(row[column])

            if value is None:
                usable = False
                problems.append(
                    (column, f"missing or unusable value {row[column]!r}")
                )
            elif reasons:
                problems.append(
                    (column, f"unexpected format {row[column]!r}")
                )

        return usable, problems

    except Exception as error:     # Convert validation failures to metadata.
        return False, [("row", f"could not be checked: {error}")]


def has_required_fields(row):
    """Return whether a row passes the usability checks.

    Args:
        row: Raw row supplied to validate_raw_row().

    Returns:
        The usable boolean from validate_raw_row().

    Notes:
        Checks expected fields and usable required identifiers/type.
        A flagged but nonblank identifier can still return True.
        Detailed validation problems are discarded by this convenience
        function. It performs no logging or row modification.
    """
    return validate_raw_row(row)[0]


def find_repeated_ids(numbered_rows):
    """Count raw transaction IDs that occur on two or more supplied rows.

    Args:
        numbered_rows: Iterable of (source_line, raw_row) pairs.

    Returns:
        Dictionary mapping each repeated raw transaction_id value to
        its occurrence count.

    Behavior:
        IDs are counted exactly as supplied, without whitespace
        normalization or identifier validation.
        Missing IDs, None, and blank strings are also counted if present.
        Rows whose get() access raises AttributeError are ignored.

    Notes:
        Passing all raw rows includes repetitions caused by exact
        duplicates. Passing unique raw rows after duplicate separation
        counts repetitions among rows with different duplicate keys.

        The reported Phase 1 figure of 1,680 refers to profiling the raw
        dataset and is not a guaranteed result for other inputs.

        This function does not drop rows or log issues. The pipeline
        uses the returned dictionary to flag repeated IDs.
        IDs must be hashable; other exceptions propagate.
    """
    counts = Counter()

    for _, row in numbered_rows:
        try:
            counts[row.get("transaction_id")] += 1
        except AttributeError:
            continue

    return {
        transaction_id: count
        for transaction_id, count in counts.items()
        if count > 1
    }
