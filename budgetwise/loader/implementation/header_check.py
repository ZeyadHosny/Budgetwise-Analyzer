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


def check_header(header):
    """Check that the CSV contains exactly the expected columns."""

    missing = [column for column in EXPECTED_COLUMNS if column not in header]
    unexpected = [column for column in header if column not in EXPECTED_COLUMNS]

    if missing or unexpected:
        problems = []

        if missing:
            problems.append(f"missing columns: {missing}")

        if unexpected:
            problems.append(f"unexpected columns: {unexpected}")

        raise ValueError("Invalid CSV header; " + "; ".join(problems))