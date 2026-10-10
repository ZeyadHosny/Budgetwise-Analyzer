"""Connect the existing menu interface to the cleaning pipeline."""

from budgetwise.pipeline import run_cleaning


def run_for_menu(dataset_path, start=None, end=None, category=None):
    """Clean the dataset, then apply optional display filters.

    The 'transactions' key preserves the existing menu contract.
    Its values are cleaned dictionaries, not Transaction objects.
    """

    if (start is None) != (end is None):
        raise ValueError("Provide both start and end dates.")

    if start is not None and end < start:
        raise ValueError("End date must not be before start date.")

    cleaning_result = run_cleaning(dataset_path)

    all_records = cleaning_result.records
    selected_records = list(all_records)

    if start is not None:
        selected_records = [
            record
            for record in selected_records
            if (
                record["date"] is not None
                and start <= record["date"] <= end
            )
        ]

    if category is not None:
        selected_records = [
            record
            for record in selected_records
            if record["category"] == category
        ]

    # Keep cleaning counts separate from filtering counts.
    counts = cleaning_result.counts

    return {
        "transactions": selected_records,
        "records": selected_records,
        "all_records": all_records,
        "counts": {
            "input": counts["input"],
            "valid": counts["retained"],
            "duplicates": counts["exact_duplicates"],
            "skipped": counts["skipped"],
        },
        "selected_count": len(selected_records),
        "cleaning_counts": dict(counts),
        "issue_counts": dict(cleaning_result.issue_counts),
    }
