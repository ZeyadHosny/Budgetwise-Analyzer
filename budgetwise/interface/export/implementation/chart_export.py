from pathlib import Path
from budgetwise.interface.charts.implementation.bar_chart import bar_chart
from .csv_export import OUTPUT_ROOT, _coerce_datetime, _dataset_names

def export_charts(
    total_breakdown: dict,
    monthly_breakdown: dict,
    dataset: str,
    when=None,
) -> Path:
    """Export spending bar charts to a dated text file."""
    dataset_filename, dataset_stem = _dataset_names(dataset)
    run_time = _coerce_datetime(when)

    output_dir = OUTPUT_ROOT / "summaries"
    output_dir.mkdir(parents=True, exist_ok=True)

    output_path = output_dir / (
        f"charts_{dataset_stem}_{run_time:%Y-%m-%d}.txt"
    )

    sections = [
        f"Budgetwise Spending Charts",
        f"Dataset: {dataset_filename}",
        f"Generated: {run_time.isoformat(timespec='seconds')}",
        "",
        bar_chart(
            {
                item["category"]: item["expenses"]
                for item in total_breakdown
            },
            title="Expenses by Category",
            sort_by_value=True,
        ),
        "",
        bar_chart(
            {
                (item["month"][:4], item["month"][5:]):
                    item["expenses"]
                for item in monthly_breakdown
            },
            title="Expenses by Month",
        ),
    ]

    with output_path.open("w", encoding="utf-8", newline="\n") as text_file:
        text_file.write("\n\n".join(sections))
        text_file.write("\n")

    return output_path