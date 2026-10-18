from budgetwise.errorlog import Reason


def normalize_payment_mode(raw: str | None) -> tuple[str, str | None]:
    """
    Normalize a raw payment mode.

    Returns:
        (normalized_payment_mode, reason_code)
    """

    if raw is None or raw.strip() == "":
        return "Unknown", Reason.PAYMENT_MODE_UNKNOWN

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

        # One-letter misspellings found in budgetwise_synthetic_dirty.csv.
        # Values one letter from both Cash and Card (cah, cahs, cas, car,
        # cad, cadr) are left out on purpose and stay Unknown.
        "pi": "UPI",
        "pui": "UPI",
        "ui": "UPI",
        "uip": "UPI",
        "up": "UPI",
        "upii": "UPI",
        "uppi": "UPI",
        "uupi": "UPI",
        "acrd": "Card",
        "ard": "Card",
        "caard": "Card",
        "cardd": "Card",
        "carrd": "Card",
        "ccard": "Card",
        "crad": "Card",
        "acsh": "Cash",
        "ash": "Cash",
        "caash": "Cash",
        "cashh": "Cash",
        "cassh": "Cash",
        "ccash": "Cash",
        "csah": "Cash",
        "abnk transfer": "Bank Transfer",
        "ank transfer": "Bank Transfer",
        "baank transfer": "Bank Transfer",
        "bak transfer": "Bank Transfer",
        "ban transfer": "Bank Transfer",
        "bank rtansfer": "Bank Transfer",
        "bank tarnsfer": "Bank Transfer",
        "bank traansfer": "Bank Transfer",
        "bank tranfser": "Bank Transfer",
        "bank trannsfer": "Bank Transfer",
        "bank transefr": "Bank Transfer",
        "bank transer": "Bank Transfer",
        "bank transfe": "Bank Transfer",
        "bank transfeer": "Bank Transfer",
        "bank transferr": "Bank Transfer",
        "bank transffer": "Bank Transfer",
        "bank transsfer": "Bank Transfer",
        "bank trasfer": "Bank Transfer",
        "bank trasnfer": "Bank Transfer",
        "bank trnasfer": "Bank Transfer",
        "bank trnsfer": "Bank Transfer",
        "bank trransfer": "Bank Transfer",
        "bank ttransfer": "Bank Transfer",
        "bankk transfer": "Bank Transfer",
        "bankt ransfer": "Bank Transfer",
        "bnk transfer": "Bank Transfer",
    }

    if cleaned in mapping:
        normalized = mapping[cleaned]

        # Any change from the canonical value counts as normalization.
        # This includes capitalization, misspellings, variants, and whitespace.
        if raw != normalized:
            return normalized, Reason.PAYMENT_MODE_NORMALIZED

        return normalized, None

    return "Unknown", Reason.PAYMENT_MODE_UNKNOWN
