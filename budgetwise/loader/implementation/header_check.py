"""Validate CSV column names before loading transaction records.

A valid header contains each of the nine expected dataset columns exactly
once. Column order may vary.

Names are compared exactly, including capitalization and whitespace.
This module does not normalize headers, validate row values, or log errors.
"""

from collections import Counter


EXPECTED_COLUMNS = [
    "transaction_id",
    "user_id",
    "date",
    "transaction_type",
    "category",
    "amount",
    "payment_mode",
    "location",
    "notes"
]


def validate_header(header):
    """Check for missing, unexpected, or duplicate column names.

    Args:
        header: List of column-name strings supplied by csv.DictReader,
            or None when no header is available.

    Returns:
        None when every expected column appears exactly once and no
        unexpected column names are present.

    Raises:
        ValueError: If the header is missing or contains missing,
            unexpected, or duplicate column names. When several kinds
            of problems are found, they are included in one message.

    Validation:
        Missing columns are reported in EXPECTED_COLUMNS order.
        Unexpected names are reported in their input order and may
        appear more than once.
        Duplicate names are reported once per name, in first-appearance
        order.

    Notes:
        Column order is not enforced because downstream access uses
        column names.

        Names are not stripped or case-normalized. For example,
        "Amount" and " amount " do not match "amount".

        The input header is not modified. File-level error handling
        and user-facing reporting belong to the caller.
    """

    if header is None:
        raise ValueError("Invalid CSV header; header is missing")

    # Identify required names that are absent from the input header.
    missing = [
        column
        for column in EXPECTED_COLUMNS
        if column not in header
    ]

    # Reject names outside the agreed nine-column dataset schema.
    unexpected = [
        column
        for column in header
        if column not in EXPECTED_COLUMNS
    ]

    # Duplicate names could cause DictReader to overwrite field values.
    duplicates = [
        column
        for column, count in Counter(header).items()
        if count > 1
    ]

    problems = []

    if missing:
        problems.append(f"missing columns: {missing}")

    if unexpected:
        problems.append(f"unexpected columns: {unexpected}")

    if duplicates:
        problems.append(f"duplicate columns: {duplicates}")

    # Report all detected header problems together.
    if problems:
        raise ValueError(
            "Invalid CSV header; " + "; ".join(problems)
        )
