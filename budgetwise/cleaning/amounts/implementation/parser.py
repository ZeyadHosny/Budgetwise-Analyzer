def parse_amount(raw: str) -> tuple[float | None, str | None, str | None]:

    # 1. Missing
    if raw is None or raw.strip() == "":
        return None, None, "missing_amount"

    value = raw.strip()

    # 2. Remove formatting
    value = value.replace(",", "")
    value = value.replace("-", "")

    # 3. Identify/remove currency
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

    # 4. Convert
    try:
        amount = float(value)
    except ValueError:
        return None, None, "invalid_amount"

    # 5. Sentinel
    if amount >= 100_000_000:
        return None, None, "sentinel_amount"

    return amount, symbol, None