"""Coordinate CSV loading, raw duplicate detection, cleaning, and logging.

The pipeline performs the following steps:

1. Load numbered raw rows from the CSV loader.
2. Separate exact duplicates before normalizing any field.
3. Identify repeated transaction IDs among the remaining raw rows.
4. Validate each remaining row and log structural problems.
5. Normalize transaction type and clean the transaction fields.
6. Record corrections, flags, and exclusions through ErrorLog.
7. Return retained cleaned dictionaries and processing counts.

Exact duplicate comparison is delegated to split_exact_duplicates().
That helper must compare all nine original dataset fields to satisfy the
project's duplicate policy. Repeated transaction IDs alone do not cause
records to be removed.

Rows with unusable amounts are excluded. Missing or invalid dates may
remain in retained records; downstream date-based analysis must exclude
those records.

This module returns dictionaries. It does not construct Transaction
objects, route transactions to payment collections, or perform analysis.
"""

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
    """Store cleaned records and the counts reported by one pipeline run.

    Attributes:
        records: Retained transaction dictionaries in processing order.
            Each dictionary contains the copied raw fields, updated with
            cleaned values, plus source_line, currency_label, and
            notes_quality. An unavailable date may be None.
        counts: Row-level counts with the following keys:
            input: Number of rows returned by the loader.
            retained: Number of cleaned records included in records.
            skipped: Number of unique rows excluded by row validation
                or an unusable amount.
            exact_duplicates: Number of rows classified as exact
                duplicates and excluded from further cleaning.
        issue_counts: Issue counts supplied by ErrorLog.counts().
            Their precise keys and counting behavior are defined by
            the logger implementation.

    For a successfully completed run, row counts should satisfy:
        input = retained + skipped + exact_duplicates

    A row may produce several log entries, so issue counts are not
    necessarily equal to the number of affected rows.
    """

    records: list[dict]
    counts: dict[str, int]
    issue_counts: dict[str, int]


def run_cleaning(path, log_path="output/logs/errors.log"):
    """Load and clean CSV rows, log issues, and return a CleaningResult.

    Args:
        path: CSV input location accepted by load_rows().
        log_path: Log destination passed to ErrorLog. Defaults to
            "output/logs/errors.log".

    Returns:
        CleaningResult containing retained cleaned dictionaries,
        row-processing counts, and issue counts reported by the logger.

    Processing:
        Exact duplicate detection runs on raw rows before field
        normalization. Repeated IDs are flagged separately and do not
        independently exclude records.

        validate_raw_row() decides whether a row can be processed.
        Transaction type is normalized using strip().title(); this
        function relies on row validation to reject unsupported types.
        Transaction direction is never inferred from the amount sign.

        Date, amount, category, payment mode, location, and notes are
        processed through their respective helpers. The amount helper
        receives the logger to coordinate amount-related logging.

        Structurally unusable rows and rows whose cleaned amount is None
        are skipped. An unavailable date does not independently cause a
        row to be skipped.

    Side Effects:
        Reads the input CSV and writes issues through ErrorLog.
        Field issues may be logged even for a row subsequently excluded
        because its amount is unusable.

    Error Handling:
        This function does not catch unexpected loader, cleaner, or
        logger exceptions; they propagate to the caller. Once the logger
        has been constructed, its close() method runs in a finally block
        when processing returns or raises an exception.

        Loading and duplicate detection occur before logger creation,
        so failures during those stages are not logged by this function.

    Notes:
        Downstream monthly or date-range analysis must filter out records
        with unavailable dates. This function does not perform that
        filtering or construct domain objects.
    """

    # Materialize numbered raw rows before any field is normalized.
    raw_rows = list(load_rows(path))

    # Detect exact duplicates before any normalization.
    # The helper is responsible for comparing all nine raw fields.
    unique_rows, duplicates = split_exact_duplicates(raw_rows)

    # Track repeated IDs separately from exact duplicate rows.
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
        """Record each supplied issue reason for one source field.

        Args:
            line: Source-line identifier provided by the loader.
            field: Name of the field associated with the issues.
            reasons: Iterable of reason codes returned by a cleaner.
                An empty iterable produces no log entries.
            raw: Original field value included as logging context.

        Returns:
            None.

        Logger exceptions propagate to run_cleaning().
        """
        for reason in reasons:
            logger.record(line, field, reason, raw)

    try:
        # Log duplicate exclusions using the original row as context.
        for line, raw in duplicates:
            logger.record(
                line,
                "row",
                DUPLICATE_RAW_ROW,
                raw
            )

        for line, raw in unique_rows:
            # Validate the raw row before accessing required fields.
            usable, problems = validate_raw_row(raw)

            # Record each reported problem, including problems that do
            # not necessarily make the row unusable.
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

            # Copy the row so cleaning does not overwrite the raw values
            # used for duplicate detection and logging.
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

            # Keep the date helper's result, including None when a date
            # is unavailable, and log each reported reason.
            date, reasons = parse_date(raw["date"])
            record["date"] = date
            log_reasons(line, "date", reasons, raw["date"])

            # Delegate amount processing and associated logging to the
            # pipeline's amount-step helper. Its third return value is
            # not used by this function.
            amount, currency, _ = clean_and_log_amount(
                raw["amount"],
                line,
                logger
            )

            record["amount"] = amount
            record["currency_label"] = currency

            # These field cleaners return a value and one optional
            # reason. The pipeline records the reason when present.
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

            # Preserve the processed note and its quality classification.
            note, quality, reasons = classify_note_quality(
                raw["notes"]
            )

            record["notes"] = note
            record["notes_quality"] = quality
            log_reasons(line, "notes", reasons, raw["notes"])

            # An unusable amount excludes the row.
            # Other field issues have already been processed and logged.
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
        # Release logger resources on normal completion and on errors.
        logger.close()
