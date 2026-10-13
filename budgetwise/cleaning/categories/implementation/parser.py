import csv
from pathlib import Path

from budgetwise.errorlog import Reason


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
        return "Uncategorized", Reason.CATEGORY_UNCATEGORIZED

    # Remove surrounding spaces and ignore capitalization for lookup
    cleaned = raw.strip().lower()

    # Known category
    if cleaned in CATEGORY_MAPPING:
        normalized = CATEGORY_MAPPING[cleaned]

        # Any difference from the canonical value counts as normalization.
        if raw != normalized:
            return normalized, Reason.CATEGORY_NORMALIZED

        return normalized, None

    # Unknown nonblank category
    return "Uncategorized", Reason.CATEGORY_UNKNOWN
