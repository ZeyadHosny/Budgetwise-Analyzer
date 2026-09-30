def parse_amount(raw: str) -> tuple[float | None, str | None, str | None]:
    """Parse a raw amount string into a tuple of (value, currency, unit)."""

    # Missing amount
    if raw is None or raw.strip() == "":
        return None, None, "missing_amount"

    value = raw.strip()
    symbol = None

    # Negative sign
    if value.startswith('-'):
        value = value[1:].strip()

    # Currency prefixes
    if value.startswith("₹"):
        symbol = "₹"
        value = value[1:].strip()

    elif value.startswith("$"):
        symbol = "$"
        value = value[1:].strip()

    elif value.startswith("Rs."):
        symbol = "Rs."
        value = value[3:].strip()

    # INR suffix
    elif value.endswith("INR"):
        symbol = "INR"
        value = value[:-3].strip()

    # Convert the remaining text to a number
    try:
        amount = float(value)
    except ValueError:
        return None, None, "invalid_amount"

    # Sentinel amount
    if amount >= 100_000_000:
        return None, None, "sentinel_amount"

    return amount, symbol, None