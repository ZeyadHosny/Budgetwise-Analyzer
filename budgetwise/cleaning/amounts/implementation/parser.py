import math
import re

from budgetwise.errorlog import Reason


def parse_amount(
    raw: str | None
) -> tuple[float | None, str | None, str | None]:
    """
    Return (amount magnitude, original currency label, error reason).

    Supported formats:
    - Plain integers and decimals
    - Correctly grouped thousands separators
    - Currency prefixes: ₹, $, Rs.
    - Currency suffix: INR
    - One optional positive or negative sign

    No currency conversion is performed.
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

    # Reject conflicting currency labels.
    if prefix and suffix:
        return None, None, Reason.UNRECOGNIZED_AMOUNT_FORMAT

    # Reject multiple signs, such as --100 or -$-100.
    if leading_sign and number.startswith(("+", "-")):
        return None, None, Reason.UNRECOGNIZED_AMOUNT_FORMAT

    # 3. Convert the validated number.
    try:
        amount = float(leading_sign + number.replace(",", ""))
    except ValueError:
        return None, None, Reason.UNRECOGNIZED_AMOUNT_FORMAT

    if not math.isfinite(amount):
        return None, None, Reason.UNRECOGNIZED_AMOUNT_FORMAT

    # 4. Store unsigned magnitude.
    # Income/expense direction comes from transaction_type.
    amount = abs(amount)

    # 5. Exclude sentinel/outlier amounts.
    if amount >= 100_000_000:
        return None, None, Reason.SENTINEL_AMOUNT

    symbol = prefix or suffix

    return amount, symbol, None
