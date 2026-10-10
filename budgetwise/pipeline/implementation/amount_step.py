"""Connect amount cleaning to source-line issue logging.

This pipeline helper calls the amount cleaner, records each returned
issue through the supplied logger, and returns the cleaner's results.

Amount parsing, validation, and currency-label extraction belong to
clean_amount(). This helper does not implement those rules, perform
currency conversion, detect duplicates, or decide whether to retain
the transaction.
"""

from budgetwise.cleaning.amounts import clean_amount
from budgetwise.errorlog import ErrorLog


def clean_and_log_amount(
    raw: str | None,
    line: int,
    logger: ErrorLog
) -> tuple[float | None, str | None, list[str]]:
    """Clean one amount and log its issues with the source row.

    Args:
        raw: Original amount field, passed unchanged to clean_amount().
            May be None when the field is unavailable.
        line: Source-line identifier associated with the raw value.
        logger: Existing ErrorLog instance supplied by the pipeline.
            The caller is responsible for its creation and closure.

    Returns:
        A tuple containing:
            amount: Cleaned numeric value, or None when the cleaner
                cannot provide a usable amount.
            symbol: Currency label returned by the cleaner, or None
                when no label is available.
            issues: List of issue reason codes returned by the cleaner.

        The cleaner's results are returned without modification.

    Side Effects:
        Calls logger.record() once for each returned issue, using the
        source line, field name "amount", reason code, and original value.
        No log entries are created when the issue list is empty.

    Error Handling:
        Exceptions from clean_amount() or logger.record() propagate
        to the caller. If logging fails partway through, earlier issues
        may already have been recorded.

    Notes:
        Duplicate detection must occur elsewhere in the pipeline before
        this helper receives values for cleaning.

        The caller decides whether an amount of None excludes the row.
        This helper does not close the logger.
    """
    amount, symbol, issues = clean_amount(raw)

    # Preserve the original value and source line in every issue entry.
    for reason in issues:
        logger.record(
            line=line,
            field="amount",
            reason=reason,
            raw=raw
        )

    return amount, symbol, issues
