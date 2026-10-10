"""Read CSV records for validation and cleaning by the pipeline.

The loader validates the header and yields each parsed record with its
source-line number. Field values are not stripped, normalized, or converted
to numeric or date types.

CSV syntax, such as quoting and delimiters, is interpreted by DictReader.
The returned values are original field contents, not literal file bytes.

This module does not clean fields, detect duplicates, or write log entries.
"""

import csv

from .header_check import validate_header


def load_rows(filename):
    """Yield source line numbers and unmodified raw CSV rows.

    Args:
        filename: Path to a CSV file accepted by open().
            The file is read using UTF-8 encoding.

    Yields:
        A (source_line, raw_row) tuple for each record:
            source_line: Physical line number at which the CSV record
                ends, as reported by reader.line_num.
            raw_row: Dictionary mapping header names to parsed field
                strings, without application-level normalization.

        For records with too few fields, DictReader supplies None for
        missing values. For records with too many fields, surplus values
        are stored as a list under the key None.

    Validation:
        Raises ValueError when no header is available.
        Delegates header validation to validate_header().
        Row-level validation is left to the cleaning pipeline.

    Error Handling:
        File-access, decoding, CSV parsing, and header-validation errors
        propagate to the caller. This function does not log them.

    Resource Handling:
        The file is opened when iteration begins. The context manager
        closes it when the generator is exhausted, explicitly closed,
        or exits because of an exception.

    Notes:
        A header-only file produces no records after header validation.
        Completely empty lines are skipped by DictReader.
        For a quoted record spanning multiple physical lines,
        source_line identifies the ending line, not the starting line.

        Duplicate detection must use these field values before cleaning.
        No date-range or category filtering is performed here.
    """

    # newline="" lets the csv module handle CSV newline conventions.
    with open(
        filename,
        "r",
        newline="",
        encoding="utf-8"
    ) as file:
        reader = csv.DictReader(file)

        if reader.fieldnames is None:
            raise ValueError("CSV file is empty")

        # Validate column names before yielding any transaction records.
        validate_header(reader.fieldnames)

        # Preserve parsed field contents and malformed row structure
        # for duplicate detection and validation in the pipeline.
        for row in reader:
            yield reader.line_num, row
