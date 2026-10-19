"""Shared dataset and budget settings. Paths are relative to this repository."""

from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATASET_PATH = PROJECT_ROOT / "data" / "raw" / "budgetwise_synthetic_dirty.csv"

# Use complete months to set limits; reserve later data for comparison.
BUDGET_BASELINE_START = "2019-01-01"
BUDGET_BASELINE_END = "2021-12-31"
