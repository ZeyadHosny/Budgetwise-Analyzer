"""Read and validate monthly category limits from the config file."""

import json
from pathlib import Path

from budgetwise.models import Budget


DEFAULT_LIMITS_PATH = (
    Path(__file__).resolve().parents[4] / "config" / "monthly_budgets.json"
)


def load_limits(path=None):
    """Return {category: monthly_limit} from the budgets JSON file."""
    limits_path = Path(path) if path is not None else DEFAULT_LIMITS_PATH
    with limits_path.open("r", encoding="utf-8") as config_file:
        config = json.load(config_file)

    if not isinstance(config, dict) or not isinstance(config.get("limits"), dict):
        raise ValueError("monthly budget config must contain a limits object")

    limits = {}
    for category, monthly_limit in config["limits"].items():
        budget = Budget(category, monthly_limit)
        normalized_category = budget.get_category()
        if normalized_category in limits:
            raise ValueError(f"duplicate budget category: {normalized_category}")
        limits[normalized_category] = budget.get_monthly_limit()
    return limits