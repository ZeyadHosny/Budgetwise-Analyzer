"""Generate config-backed monthly limits and their data-based justification."""

import argparse
import json
import math
from datetime import datetime
from pathlib import Path
from statistics import median

from budgetwise.analysis.aggregation import totals_by_month_and_category
from budgetwise.analysis.budgets.implementation.limits import load_limits
from budgetwise.pipeline import clean_file


PROJECT_ROOT = Path(__file__).resolve().parents[4]
DEFAULT_DATASET = PROJECT_ROOT / "data" / "raw" / "budgetwise_synthetic_dirty.csv"
DEFAULT_CONFIG = PROJECT_ROOT / "config" / "monthly_budgets.json"
DEFAULT_JUSTIFICATION = (
    PROJECT_ROOT / "budgetwise" / "analysis" / "budgets" / "supplementary"
    / "budget_justification.md"
)
ROUNDING_INCREMENT = 500


class _DiscardErrorLog:
    def record(self, line, field, reason, raw):
        pass


def calculate_evidence(transactions, categories, increment=ROUNDING_INCREMENT):
    """Calculate median, 75th percentile, maximum, and proposed limits.

    The month range spans the earliest through latest dated transaction,
    including calendar months with zero spending for a category.
    """
    if isinstance(increment, bool) or not isinstance(increment, (int, float)):
        raise TypeError("increment must be a positive number")
    if not math.isfinite(increment) or increment <= 0:
        raise ValueError("increment must be a positive finite number")

    categories = sorted(set(categories))
    if len(categories) < 5:
        raise ValueError("at least five budget categories are required")
    if any(not isinstance(category, str) or not category.strip()
           for category in categories):
        raise ValueError("budget categories must be nonempty strings")

    all_months = sorted(
        month for transaction in transactions
        if (month := _transaction_month(transaction)) is not None
    )
    if not all_months:
        raise ValueError("no dated transactions are available")
    months = _month_range(all_months[0], all_months[-1])
    totals = totals_by_month_and_category(transactions, kind="expense")

    evidence = []
    for category in categories:
        spends = [totals.get(month, {}).get(category, 0.0) for month in months]
        if not any(spends):
            raise ValueError(
                f"configured category has no dated expense spending: {category}"
            )
        monthly_median = median(spends)
        proposed_limit = math.ceil(monthly_median / increment) * increment
        evidence.append({
            "category": category,
            "median": monthly_median,
            "p75": _percentile(spends, 0.75),
            "maximum": max(spends),
            "limit": int(proposed_limit)
            if float(proposed_limit).is_integer() else proposed_limit,
        })
    return months, evidence


def _transaction_month(transaction):
    date = (transaction.get("date") if isinstance(transaction, dict)
            else transaction.get_date())
    if not isinstance(date, str):
        return None
    try:
        parsed = datetime.strptime(date, "%Y-%m-%d")
    except ValueError:
        return None
    return parsed.strftime("%Y-%m")


def _month_range(first, last):
    first_year, first_month = (int(part) for part in first.split("-"))
    last_year, last_month = (int(part) for part in last.split("-"))
    first_index = first_year * 12 + first_month - 1
    last_index = last_year * 12 + last_month - 1
    return [
        (str(index // 12).zfill(4), str(index % 12 + 1).zfill(2))
        for index in range(first_index, last_index + 1)
    ]


def _percentile(values, percentile):
    ordered = sorted(values)
    position = (len(ordered) - 1) * percentile
    lower = math.floor(position)
    upper = math.ceil(position)
    if lower == upper:
        return float(ordered[lower])
    fraction = position - lower
    return ordered[lower] + (ordered[upper] - ordered[lower]) * fraction


def _render_justification(months, evidence, dataset_path, increment):
    rows = [
        "# Monthly Budget Justification",
        "",
        "## Method",
        "",
        f"Limits use cleaned expense transactions from `{dataset_path.name}`. "
        f"The observed month window is {months[0][0]}-{months[0][1]} through "
        f"{months[-1][0]}-{months[-1][1]} ({len(months)} calendar months). "
        "Undated transactions are excluded. Months with no spending in a "
        "category are included as zero, so every category uses the same "
        "window.",
        "",
        f"For each configured category, the limit is its median monthly "
        f"spend rounded up to the next {increment:g} dataset units. The median "
        "is less sensitive to one unusually expensive month than the mean. "
        "The 75th percentile and maximum are shown as context, not used to "
        "set the limit. No currency conversion is performed.",
        "",
        "These are historical spending-based planning limits, not a claim "
        "that the amounts are affordable or financially advisable for every "
        "household. The team should revise them if its goals or circumstances "
        "differ from the historical pattern.",
        "",
        "## Proposed Limits",
        "",
        "| Category | Median monthly spend | 75th percentile | Highest month | Proposed limit |",
        "|---|---:|---:|---:|---:|",
    ]
    for item in evidence:
        rows.append(
            f"| {item['category']} | {item['median']:,.2f} | "
            f"{item['p75']:,.2f} | {item['maximum']:,.2f} | "
            f"{item['limit']:,.2f} |"
        )
    rows.extend([
        "",
        "The configured categories are retained from `monthly_budgets.json`. "
        "Categories with spending but no configured limit are reported as "
        "`unbudgeted` by the comparison function.",
        "",
    ])
    return "\n".join(rows)


def generate(dataset_path=DEFAULT_DATASET, config_path=DEFAULT_CONFIG,
             justification_path=DEFAULT_JUSTIFICATION,
             increment=ROUNDING_INCREMENT):
    """Update the configured limits and write the accompanying evidence."""
    dataset_path = Path(dataset_path)
    config_path = Path(config_path)
    justification_path = Path(justification_path)

    with config_path.open("r", encoding="utf-8") as config_file:
        config = json.load(config_file)
    limits = load_limits(config_path)

    cleaned = clean_file(dataset_path, error_log=_DiscardErrorLog())
    if cleaned["error"]:
        raise RuntimeError(cleaned["error"])
    months, evidence = calculate_evidence(
        cleaned["records"], limits.keys(), increment
    )

    config["limits"] = {item["category"]: item["limit"] for item in evidence}
    config["_comment"] = (
        "Generated from cleaned monthly expense history; each limit is the "
        f"category median rounded up to {increment:g} dataset units. See "
        "budgetwise/analysis/budgets/supplementary/budget_justification.md."
    )
    config_path.write_text(
        json.dumps(config, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )

    justification_path.parent.mkdir(parents=True, exist_ok=True)
    justification_path.write_text(
        _render_justification(months, evidence, dataset_path, increment),
        encoding="utf-8",
    )
    return evidence


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dataset", type=Path, default=DEFAULT_DATASET)
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    parser.add_argument("--justification", type=Path, default=DEFAULT_JUSTIFICATION)
    parser.add_argument("--increment", type=float, default=ROUNDING_INCREMENT)
    arguments = parser.parse_args()

    evidence = generate(
        arguments.dataset,
        arguments.config,
        arguments.justification,
        arguments.increment,
    )
    for item in evidence:
        print(f"{item['category']}: {item['limit']:,.2f}")


if __name__ == "__main__":
    main()