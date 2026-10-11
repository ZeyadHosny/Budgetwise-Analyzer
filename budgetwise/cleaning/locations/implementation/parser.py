def normalize_location(raw: str | None) -> tuple[str, str | None]:
    """
    Normalize a raw location value.

    Returns:
        (normalized_location, reason_code)
    """

    if raw is None or raw.strip() == "":
        return "Unknown", "LOCATION_UNKNOWN"

    cleaned = raw.strip().lower()

    if cleaned == "n/a":
        return "Unknown", "LOCATION_UNKNOWN"

    mapping = {
        "pune": "Pune",
        "pun": "Pune",

        "bangalore": "Bangalore",
        "ban": "Bangalore",

        "chennai": "Chennai",
        "che": "Chennai",

        "hyderabad": "Hyderabad",
        "hyd": "Hyderabad",

        "jaipur": "Jaipur",
        "jai": "Jaipur",

        "kolkata": "Kolkata",
        "kol": "Kolkata",

        "delhi": "Delhi",
        "del": "Delhi",

        "lucknow": "Lucknow",
        "luc": "Lucknow",

        "ahmedabad": "Ahmedabad",
        "ahm": "Ahmedabad",

        "mumbai": "Mumbai",
        "mum": "Mumbai",
    }

    if cleaned in mapping:
        normalized = mapping[cleaned]

        # Any difference from the canonical value counts as normalization.
        # This includes capitalization, abbreviations, and whitespace.
        if raw != normalized:
            return normalized, "LOCATION_NORMALIZED"

        return normalized, None

    return "Unknown", "LOCATION_UNKNOWN"
