from dataclasses import dataclass

from budgetwise.loader import load_rows
from budgetwise.errorlog import ErrorLog
from budgetwise.cleaning.dates import parse_date
from budgetwise.cleaning.categories import normalize_category
from budgetwise.cleaning.payment_modes import normalize_payment_mode
from budgetwise.cleaning.locations import normalize_location
from budgetwise.cleaning.notes import classify_note_quality
from budgetwise.cleaning.rows import (
    split_exact_duplicates,
    find_repeated_ids,
    validate_raw_row,
    DUPLICATE_RAW_ROW,
    REPEATED_TRANSACTION_ID,
    MALFORMED_ROW,
)
from .amount_step import clean_and_log_amount


@dataclass
class CleaningResult:
    records: list[dict]
    counts: dict[str, int]
    issue_counts: dict[str, int]


def run_cleaning(path, log_path="output/logs/errors.log"):
    """Return cleaned records and counts; append issues to the log."""

    raw_rows = list(load_rows(path))

    # Detect exact duplicates before any normalization.
    unique_rows, duplicates = split_exact_duplicates(raw_rows)
    repeated_ids = find_repeated_ids(unique_rows)

    records = []
    counts = {
        "input": len(raw_rows),
        "retained": 0,
        "skipped": 0,
        "exact_duplicates": len(duplicates),
    }

    logger = ErrorLog(log_path)

    def log_reasons(line, field, reasons, raw):
        for reason in reasons:
            logger.record(line, field, reason, raw)

    try:
        for line, raw in duplicates:
            logger.record(
                line,
                "row",
                DUPLICATE_RAW_ROW,
                raw
            )

        for line, raw in unique_rows:
            usable, problems = validate_raw_row(raw)

            for field, detail in problems:
                source = (
                    raw if field == "row"
                    else raw.get(field)
                )

                logger.record(
                    line,
                    field,
                    MALFORMED_ROW,
                    {"value": source, "detail": detail}
                )

            if not usable:
                counts["skipped"] += 1
                continue

            # A repeated ID alone does not remove the row.
            if raw["transaction_id"] in repeated_ids:
                logger.record(
                    line,
                    "transaction_id",
                    REPEATED_TRANSACTION_ID,
                    raw["transaction_id"]
                )

            record = dict(raw)
            record["source_line"] = line

            # Direction comes from the validated transaction_type.
            record["transaction_type"] = (
                raw["transaction_type"].strip().title()
            )

            if record["transaction_type"] != raw["transaction_type"]:
                logger.record(
                    line,
                    "transaction_type",
                    "TRANSACTION_TYPE_NORMALIZED",
                    raw["transaction_type"]
                )

            date, reasons = parse_date(raw["date"])
            record["date"] = date
            log_reasons(line, "date", reasons, raw["date"])

            amount, currency, _ = clean_and_log_amount(
                raw["amount"],
                line,
                logger
            )

            record["amount"] = amount
            record["currency_label"] = currency

            for field, cleaner in (
                ("category", normalize_category),
                ("payment_mode", normalize_payment_mode),
                ("location", normalize_location),
            ):
                value, reason = cleaner(raw[field])
                record[field] = value

                if reason is not None:
                    logger.record(
                        line,
                        field,
                        reason,
                        raw[field]
                    )

            note, quality, reasons = classify_note_quality(
                raw["notes"]
            )

            record["notes"] = note
            record["notes_quality"] = quality
            log_reasons(line, "notes", reasons, raw["notes"])

            # An unusable amount excludes the row.
            if amount is None:
                counts["skipped"] += 1
                continue

            # Missing/invalid dates remain available for overall totals.
            records.append(record)
            counts["retained"] += 1

        return CleaningResult(
            records=records,
            counts=counts,
            issue_counts=logger.counts()
        )

    finally:
        logger.close()
