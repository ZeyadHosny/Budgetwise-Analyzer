"""Parse raw amount text without logging or currency conversion.

Accepted amounts are returned as finite, nonnegative magnitudes.
Transaction direction must be determined separately from transaction_type.

Currency labels are treated as cosmetic metadata. Supported labels are
the prefixes ₹, $, and Rs., or the suffix INR.

Missing, unsupported, malformed, nonfinite, and sentinel amounts return
an error reason for the pipeline to log. This module does not write logs,
detect duplicates, or decide how the complete transaction is stored.
"""

import math
import re

from budgetwise.errorlog import Reason


def parse_amount(
    raw: str | None
) -> tuple[float | None, str | None, str | None]:
    """Return amount magnitude, original currency label, and error reason.

    Args:
        raw: Original amount field as text, or None when unavailable.
            Non-string input is rejected rather than converted to text.

    Returns:
        A three-element tuple:
            amount: Finite, nonnegative float below 100,000,000 on
                success; otherwise None.
            symbol: Recognized currency label on success, or None for
                an unlabeled amount. All rejection paths currently
                return None for this element.
            error: None on success; otherwise MISSING_AMOUNT,
                UNRECOGNIZED_AMOUNT_FORMAT, or SENTINEL_AMOUNT.

    Supported Formats:
        Plain integers and decimals, including leading-dot decimals.
        Thousands separators in groups of three digits.
        Currency prefixes ₹, $, and Rs.
        Currency suffix INR.
        One optional positive or negative sign, either before the
        currency prefix or directly before the numeric portion.

        Examples:
            "1250"
            ".50"
            "1,250.75"
            "-$100"
            "Rs. -100"
            "100 INR"

        Surrounding whitespace and whitespace between the label and
        numeric portion are accepted. Whitespace inside the number is
        not accepted. Currency labels are case-sensitive.

    Rejected Formats:
        Blank or missing input.
        Non-string values, including numeric objects and booleans.
        Incorrect comma grouping.
        Multiple signs or simultaneous prefix and suffix labels.
        Unsupported labels, trailing text, scientific notation,
        NaN, and infinity.

    Processing:
        Validates the entire stripped string before removing commas.
        Converts the numeric portion to float and checks finiteness.
        Converts negative values to their unsigned magnitude.
        Rejects magnitudes greater than or equal to 100,000,000.

    Notes:
        No currency conversion is performed.
        Financial direction comes from transaction_type elsewhere.
        The original input is not modified.
        The caller is responsible for logging the returned error reason
        and retaining the original raw value for traceability.
    """

    # 1. Handle missing or unsupported input types.
    if raw is None:
        return None, None, Reason.MISSING_AMOUNT

    if not isinstance(raw, str):
        return None, None, Reason.UNRECOGNIZED_AMOUNT_FORMAT

    value = raw.strip()

    if value == "":
        return None, None, Reason.MISSING_AMOUNT

    # 2. Validate the entire input before removing formatting.
    # The numeric portion permits either correctly grouped commas or
    # an ungrouped integer/decimal, including a leading-dot decimal.
    pattern = (
        r"(?P<leading_sign>[+-]?)"
        r"(?P<prefix>₹|\$|Rs\.)?\s*"
        r"(?P<number>[+-]?(?:"
        r"[0-9]{1,3}(?:,[0-9]{3})+(?:\.[0-9]+)?"
        r"|[0-9]+(?:\.[0-9]+)?"
        r"|\.[0-9]+"
        r"))"
        r"\s*(?P<suffix>INR)?"
    )

    match = re.fullmatch(pattern, value)

    if match is None:
        return None, None, Reason.UNRECOGNIZED_AMOUNT_FORMAT

    prefix = match.group("prefix")
    suffix = match.group("suffix")
    number = match.group("number")
    leading_sign = match.group("leading_sign")

    # Reject simultaneous prefix and suffix labels, even when they
    # refer to the same currency.
    if prefix and suffix:
        return None, None, Reason.UNRECOGNIZED_AMOUNT_FORMAT

    # Reject multiple signs, such as --100 or -$-100.
    if leading_sign and number.startswith(("+", "-")):
        return None, None, Reason.UNRECOGNIZED_AMOUNT_FORMAT

    # 3. Convert the validated number after removing comma separators.
    try:
        amount = float(leading_sign + number.replace(",", ""))
    except ValueError:
        return None, None, Reason.UNRECOGNIZED_AMOUNT_FORMAT

    # Reject nonfinite results, including overflow to infinity.
    if not math.isfinite(amount):
        return None, None, Reason.UNRECOGNIZED_AMOUNT_FORMAT

    # 4. Store unsigned magnitude.
    # Income/expense direction comes from transaction_type.
    amount = abs(amount)

    # 5. Exclude sentinel/outlier amounts.
    # Checking after abs() also rejects large negative magnitudes.
    if amount >= 100_000_000:
        return None, None, Reason.SENTINEL_AMOUNT

    # Preserve the accepted label without currency conversion.
    symbol = prefix or suffix

    return amount, symbol, None
