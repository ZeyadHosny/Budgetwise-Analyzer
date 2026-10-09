import csv

from .header_check import validate_header


def load_rows(filename):
    """Yield source line numbers and unmodified raw CSV rows."""

    with open(
        filename,
        "r",
        newline="",
        encoding="utf-8"
    ) as file:
        reader = csv.DictReader(file)

        if reader.fieldnames is None:
            raise ValueError("CSV file is empty")

        validate_header(reader.fieldnames)

        for row in reader:
            yield reader.line_num, row
