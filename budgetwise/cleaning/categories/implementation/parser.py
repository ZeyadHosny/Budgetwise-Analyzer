import csv
from pathlib import Path


def _load_mapping() -> dict[str, str]:
    """Load category mappings from config/category_mapping.csv."""

    mapping = {}

    project_root = Path(__file__).resolve().parents[4]
    mapping_file = project_root / "config" / "category_mapping.csv"

    with mapping_file.open("r", encoding="utf-8", newline="") as file:
        reader = csv.DictReader(file)

        for row in reader:
            raw = row["raw"].strip().lower()
            normalized = row["normalized"].strip()

            mapping[raw] = normalized

    return mapping


CATEGORY_MAPPING = _load_mapping()


def normalize_category(raw: str | None) -> tuple[str, str | None]:
    """
    Normalize a raw category value.

    Returns:
        (normalized_category, reason_code)
    """

    # Missing category
    if raw is None or raw.strip() == "":
        return "Uncategorized", "CATEGORY_UNCATEGORIZED"

    # Remove surrounding spaces and ignore capitalization for lookup
    cleaned = raw.strip().lower()

    # Known category
    if cleaned in CATEGORY_MAPPING:
        normalized = CATEGORY_MAPPING[cleaned]

        # The raw value had to be changed
        if raw.strip() != normalized:
            return normalized, "CATEGORY_NORMALIZED"

        # Already in the correct form
        return normalized, None

    # Unknown category
    return "Uncategorized", "UNKNOWN_CATEGORY"
