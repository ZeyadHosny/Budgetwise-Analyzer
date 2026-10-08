"""
parser.py  -  column: date        (task P2.1, owner: Sarah)

WHAT THE PROJECT SAYS (Project-1.pdf 4.5)
  * Convert every valid date to YYYY-MM-DD.
  * If day and month are both 12 or less the date is ambiguous. Then:
        slash dates                  -> MM/DD/YYYY
        hyphen dates, 2-digit year   -> DD-MM-YY
  * A date that cannot be parsed is logged and left out of date-based
    analysis. It must never crash the program or be silently misread.
  * A missing date is logged and left out of date-based analysis. The row is
    kept, because it can still count toward category totals.

WHAT PHASE 1 FOUND (15,900 rows)
  * 6,091 YYYY-MM-DD, 4,676 MM/DD/YYYY, 3,044 DD-MM-YY, 1,603 DD-MM-YYYY
  * 486 missing, 0 in any other format, 1,865 ambiguous slash dates

TEAM CONVENTION
  * DD-MM-YYYY (hyphen, 4-digit year) is read day first, like DD-MM-YY.

HOW IT WORKS
  The separator ("/" or "-") and the position of the year tell us the format.
  We never look at the numbers to guess which one is the day.

Returns (cleaned_value, reasons), like every cleaner in this project.
cleaned_value is None when the date must be left out of date-based analysis.

REASON CODES AND FUNCTION NAME
  Taken from the Phase 2 Cleaning Decisions & Interface Specification
  (sections 4 and 5), so every module and errors.log use the same words.
"""

import re
from datetime import datetime

# Each format: (name, exact shape, how Python should read it).
# The shapes are strict about digit counts, so "8/5/2022" or "2022/08/05"
# match nothing and are reported instead of guessed.
DATE_FORMATS = (
    ("YYYY-MM-DD", re.compile(r"\d{4}-\d{2}-\d{2}"), "%Y-%m-%d"),
    ("MM/DD/YYYY", re.compile(r"\d{2}/\d{2}/\d{4}"), "%m/%d/%Y"),
    ("DD-MM-YY",   re.compile(r"\d{2}-\d{2}-\d{2}"), "%d-%m-%y"),
    ("DD-MM-YYYY", re.compile(r"\d{2}-\d{2}-\d{4}"), "%d-%m-%Y"),
)

MISSING_VALUES = ("", "n/a")

# Reason codes
DATE_NORMALIZED = "DATE_NORMALIZED"    # corrected: non-ISO date converted
MISSING_DATE = "MISSING_DATE"          # flagged: date is blank
INVALID_DATE = "INVALID_DATE"          # flagged: cannot be parsed by the rules


def find_date_format(raw):
    """Return the format name a raw date matches, or None."""
    if not isinstance(raw, str):
        return None
    text = raw.strip()
    for name, shape, _ in DATE_FORMATS:
        if shape.fullmatch(text):
            return name
    return None


def parse_date(raw_date):
    """Return (date as 'YYYY-MM-DD' or None, reasons). Never crashes."""
    # 1. Missing?
    raw = raw_date
    if raw is None:
        return None, [MISSING_DATE]
    if not isinstance(raw, str):
        return None, [INVALID_DATE]
    text = raw.strip()
    if text.lower() in MISSING_VALUES:
        return None, [MISSING_DATE]

    # 2. Find the format whose shape matches, then let Python read it.
    for name, shape, read_format in DATE_FORMATS:
        if shape.fullmatch(text):
            try:
                parsed = datetime.strptime(text, read_format)
            except ValueError:
                # Right shape but not a real date, e.g. 31-02-23, or a slash
                # date like 25/12/2023 where the "month" would be 25.
                return None, [INVALID_DATE]
            value = parsed.strftime("%Y-%m-%d")
            # Already in the target format: nothing to report.
            if value == raw:
                return value, []
            return value, [DATE_NORMALIZED]

    # 3. No format matched: report it, never guess.
    return None, [INVALID_DATE]


def is_ambiguous_date(raw):
    """True if a slash or hyphen date has day and month both 12 or less.

    Only used to count ambiguous dates for the report. Parsing does not need
    it, because the format alone decides how a date is read.
    """
    if find_date_format(raw) in (None, "YYYY-MM-DD"):
        return False
    text = raw.strip()
    return int(text[0:2]) <= 12 and int(text[3:5]) <= 12
