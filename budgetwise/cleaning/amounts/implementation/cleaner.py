"""Add correction metadata to the amount parser's results.

parse_amount() performs parsing and validation. This module identifies
formatting changes in successfully parsed input and returns issue codes
for the pipeline to log.

This module does not write log entries, determine transaction direction,
perform currency conversion, or decide whether to retain a row.
"""

from budgetwise.errorlog import Reason
from .parser import parse_amount


def clean_amount(
    raw: str | None
) -> tuple[float | None, str | None, list[str]]:
    """Return the parsed amount, currency label, and issue codes.

    Args:
        raw: Original amount text, or None when unavailable.
            Passed unchanged to parse_amount().

    Returns:
        A tuple containing:
            amount: Numeric value returned by the parser, or None when
                the parser cannot provide a usable amount.
            symbol: Original currency label identified by the parser,
                or None when no label is available.
            issues: List of error or correction reason codes.

        If the parser returns an error, the result contains that single
        error code. Formatting corrections are not added in that case.

        For successfully parsed input, correction codes are returned
        in the following order when applicable:
            AMOUNT_NEGATIVE_TO_MAGNITUDE
            AMOUNT_FORMAT_NORMALIZED

    Correction Detection:
        A hyphen in successfully parsed text produces the negative-to-
        magnitude code. This function does not itself change the sign;
        magnitude conversion must be performed by the parser.

        Formatting normalization is reported when the input contains
        surrounding whitespace, a recognized currency label, commas,
        a plus sign, or any whitespace within the stripped text.

    Error Handling:
        Parser exceptions propagate to the caller.
        A successful parser result is expected to correspond to string
        input, because this function subsequently calls raw.strip().

    Notes:
        The parser's amount and currency label are returned unchanged.
        Financial direction must come from transaction_type elsewhere
        in the pipeline, rather than from the raw amount sign.

        Reason is a source of issue-code constants. Importing it does
        not perform logging; the pipeline records the returned issues.
    """
    amount, symbol, error = parse_amount(raw)

    # Invalid or missing amounts keep their existing error reason.
    if error is not None:
        return amount, symbol, [error]

    issues = []
    value = raw.strip()

    # The parser has already validated the input.
    # This detects a hyphen anywhere in accepted text.
    if "-" in value:
        issues.append(Reason.AMOUNT_NEGATIVE_TO_MAGNITUDE)

    formatting_changed = (
        raw != value
        or symbol is not None
        or "," in value
        or "+" in value
        or any(character.isspace() for character in value)
    )

    if formatting_changed:
        issues.append(Reason.AMOUNT_FORMAT_NORMALIZED)

    return amount, symbol, issues
