def normalize_payment_mode(raw: str | None) -> tuple[str, str | None]:
    """
    Normalize a raw payment mode.

    Returns:
        (normalized_payment_mode, reason_code)
    """

    if raw is None or raw.strip() == "":
        return "Unknown", "PAYMENT_MODE_UNKNOWN"

    cleaned = raw.strip().lower()

    mapping = {
        "upi": "UPI",

        "card": "Card",
        "crd": "Card",

        "cash": "Cash",
        "csh": "Cash",

        "bank transfer": "Bank Transfer",
        "banktransfer": "Bank Transfer",
        "bank_transfer": "Bank Transfer",
        "bank transfr": "Bank Transfer",
    }

    if cleaned in mapping:
        normalized = mapping[cleaned]

        if raw.strip() != normalized:
            return normalized, "PAYMENT_MODE_NORMALIZED"

        return normalized, None

    return "Unknown", "PAYMENT_MODE_UNKNOWN"
