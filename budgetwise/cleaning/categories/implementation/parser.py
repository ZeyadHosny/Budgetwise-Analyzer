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


def normalize(raw: str | None) -> tuple[str, str | None]:
    """
    Normalize a raw category value.

    Returns:
        (normalized_category, error_reason)
    """

    if raw is None or raw.strip() == "":
        return "Uncategorized", "missing_category"

    cleaned = raw.strip().lower()

    if cleaned in CATEGORY_MAPPING:
        return CATEGORY_MAPPING[cleaned], None

    return "Uncategorized", "unknown_category"
