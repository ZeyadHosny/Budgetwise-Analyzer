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
    """Check for missing, unexpected, or duplicate column names."""

    if header is None:
        raise ValueError("Invalid CSV header; header is missing")

    missing = [
        column
        for column in EXPECTED_COLUMNS
        if column not in header
    ]

    unexpected = [
        column
        for column in header
        if column not in EXPECTED_COLUMNS
    ]

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

    if problems:
        raise ValueError(
            "Invalid CSV header; " + "; ".join(problems)
        )
