"""Write a precomputed run summary as JSON with dataset provenance."""

import json
from datetime import date, datetime
from pathlib import Path

from .csv_export import OUTPUT_ROOT, _coerce_datetime, _dataset_names


def export_summary(summary: dict, dataset: str, when=None) -> Path:
    """Write a summary dictionary and return the dated output path.

    Summary calculations belong to analysis callers; this function only
    records the supplied figures and adds the dataset and generation time.
    """
    if not isinstance(summary, dict):
        raise TypeError("summary must be a dictionary")

    dataset_filename, dataset_stem = _dataset_names(dataset)
    run_time = _coerce_datetime(when)
    output_dir = OUTPUT_ROOT / "summaries"
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / (
        f"summary_{dataset_stem}_{run_time:%Y-%m-%d}.json"
    )

    document = dict(summary)
    document["dataset"] = dataset_filename
    document["generated"] = run_time.isoformat(timespec="seconds")
    with output_path.open("w", encoding="utf-8") as json_file:
        json.dump(document, json_file, indent=2, ensure_ascii=False,
                  default=_json_default)
        json_file.write("\n")
    return output_path


def _json_default(value):
    if isinstance(value, (date, datetime)):
        return value.isoformat()
    if isinstance(value, Path):
        return str(value)
    raise TypeError(f"cannot serialize {type(value).__name__} to JSON")