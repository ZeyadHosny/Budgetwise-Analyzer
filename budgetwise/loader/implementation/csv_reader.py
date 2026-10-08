import csv

from .header_check import validate_header


def load_rows(filename):
    """Yield (line_number, row) for each data row in the CSV."""

    with open(filename, "r", newline="", encoding="utf-8") as file:
        reader = csv.reader(file)

        try:
            header = next(reader)
        except StopIteration:
            raise ValueError("CSV file is empty")
        
        validate_header(header)

        for line_no, values in enumerate(reader, start=2):
            row = {}

            for index, column in enumerate(header):
                if index < len(values):
                    row[column] = values[index]
                else:
                    row[column] = ""

            yield line_no, row