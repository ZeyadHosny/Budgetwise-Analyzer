from budgetwise.cleaning.amounts import clean_amount
from budgetwise.errorlog import ErrorLog


def clean_and_log_amount(
    raw: str | None,
    line: int,
    logger: ErrorLog
) -> tuple[float | None, str | None, list[str]]:
    """Clean one amount and log its issues with the source row."""
    amount, symbol, issues = clean_amount(raw)

    for reason in issues:
        logger.record(
            line=line,
            field="amount",
            reason=reason,
            raw=raw
        )

    return amount, symbol, issues
