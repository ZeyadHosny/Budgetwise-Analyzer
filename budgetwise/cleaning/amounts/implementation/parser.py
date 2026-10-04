"""Parse formatted amount strings into unsigned numeric magnitudes."""

import math

from budgetwise.errorlog.implementation.reason_codes import Reason


def parse_amount(raw: str | None) -> tuple[float | None, str | None, str | None]:
    """Return the amount magnitude, original currency label, and failure reason."""
    if raw is None or raw.strip() == "":
        return None, None, Reason.MISSING_AMOUNT

    value = raw.strip().replace(",", "")
    symbol = "plain"

    if value.startswith("₹"):
        symbol = "₹"
        value = value[1:]
    elif value.startswith("$"):
        symbol = "$"
        value = value[1:]
    elif value.startswith("Rs."):
        symbol = "Rs."
        value = value[3:]

    value = value.strip()
    if value.endswith("INR"):
        symbol = "INR"
        value = value[:-3].strip()

    if value.startswith("-"):
        value = value[1:]

    try:
        amount = float(value)
    except ValueError:
        return None, None, Reason.UNRECOGNIZED_AMOUNT_FORMAT

    if not math.isfinite(amount) or amount < 0:
        return None, None, Reason.UNRECOGNIZED_AMOUNT_FORMAT
    if amount >= 100_000_000:
        return None, None, Reason.SENTINEL_AMOUNT

    return amount, symbol, None
