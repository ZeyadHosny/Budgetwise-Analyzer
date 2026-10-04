"""Amount parser implementation requested for this package."""

from budgetwise.errorlog.implementation.reason_codes import Reason


def parse_amount(raw: str) -> tuple[float | None, str | None, str | None]:
    if raw is None or raw.strip() == "":
        return None, None, Reason.MISSING_AMOUNT

    value = raw.strip()
    value = value.replace(",", "")
    value = value.replace("-", "")

    symbol = None

    if value.startswith("₹"):
        symbol = "₹"
        value = value[1:]
    elif value.startswith("$"):
        symbol = "$"
        value = value[1:]
    elif value.startswith("Rs."):
        symbol = "Rs."
        value = value[3:]
    elif value.endswith("INR"):
        symbol = "INR"
        value = value[:-3]

    try:
        amount = float(value)
    except ValueError:
        return None, None, Reason.UNRECOGNIZED_AMOUNT_FORMAT

    if amount >= 100_000_000:
        return None, None, Reason.SENTINEL_AMOUNT

    return amount, symbol, None


__all__ = ["parse_amount"]
