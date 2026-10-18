"""Write cleaned transactions as an Excel-friendly CSV file."""

import csv
from datetime import date, datetime
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[4]
OUTPUT_ROOT = PROJECT_ROOT / "output"
CSV_FIELDS = (
    "transaction_id",
    "user_id",
    "date",
    "transaction_type",
    "category",
    "amount",
    "original_currency",
)


def export_cleaned(transactions, dataset: str, when=None) -> Path:
    """Write cleaned transaction rows and return the dated output path."""
    dataset_filename, dataset_stem = _dataset_names(dataset)
    run_time = _coerce_datetime(when)
    output_dir = OUTPUT_ROOT / "cleaned"
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / (
        f"cleaned_{dataset_stem}_{run_time:%Y-%m-%d}.csv"
    )

    with output_path.open("w", encoding="utf-8-sig", newline="") as csv_file:
        writer = csv.DictWriter(
            csv_file,
            fieldnames=CSV_FIELDS,
            extrasaction="ignore",
            lineterminator="\n",
        )
        writer.writeheader()
        for transaction in transactions:
            record = _as_record(transaction)
            writer.writerow({
                field: _csv_value(field, record.get(field))
                for field in CSV_FIELDS
            })
    return output_path


def _as_record(transaction):
    if isinstance(transaction, dict):
        return transaction
    to_dict = getattr(transaction, "to_dict", None)
    if callable(to_dict):
        record = to_dict()
        if isinstance(record, dict):
            return record
    raise TypeError("transactions must be cleaned dictionaries or model objects")


def _csv_value(field, value):
    if value is None:
        return ""
    if field == "amount":
        return f"{float(value):.2f}"
    return str(value)


def _dataset_names(dataset):
    if not isinstance(dataset, (str, Path)):
        raise TypeError("dataset must be a string or path")
    filename = Path(dataset).name
    if not filename:
        raise ValueError("dataset must name a file")
    if not Path(filename).suffix:
        filename += ".csv"
    return filename, Path(filename).stem


def _coerce_datetime(when):
    if when is None:
        return datetime.now()
    if isinstance(when, datetime):
        return when
    if isinstance(when, date):
        return datetime.combine(when, datetime.min.time())
    if isinstance(when, str):
        try:
            return datetime.fromisoformat(when)
        except ValueError:
            try:
                parsed_date = date.fromisoformat(when)
            except ValueError:
                raise ValueError("when must be an ISO date or datetime") from None
            return datetime.combine(parsed_date, datetime.min.time())
    raise TypeError("when must be a date, datetime, ISO string, or None")