"""Date cleaning (P2.1, Sarah).

Converts each raw date to YYYY-MM-DD, or returns None with a reason code.
The separator and year length decide the format; the numbers are never used
to guess which part is the day. Rules are explained in README.md.
"""

import re
from datetime import datetime

from budgetwise.errorlog import Reason

# (format name, exact shape, strptime pattern). Shapes are strict, so
# "8/5/2022" or "2022/08/05" match nothing and are reported, not guessed.
DATE_FORMATS = (
    ("YYYY-MM-DD", re.compile(r"\d{4}-\d{2}-\d{2}"), "%Y-%m-%d"),
    ("MM/DD/YYYY", re.compile(r"\d{2}/\d{2}/\d{4}"), "%m/%d/%Y"),
    ("DD-MM-YY",   re.compile(r"\d{2}-\d{2}-\d{2}"), "%d-%m-%y"),
    ("DD-MM-YYYY", re.compile(r"\d{2}-\d{2}-\d{4}"), "%d-%m-%Y"),
)

MISSING_VALUES = ("", "n/a")


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
    """Return (date as 'YYYY-MM-DD' or None, reasons). Never raises."""
    raw = raw_date
    if raw is None:
        return None, [Reason.MISSING_DATE]
    if not isinstance(raw, str):
        return None, [Reason.INVALID_DATE]
    text = raw.strip()
    if text.lower() in MISSING_VALUES:
        return None, [Reason.MISSING_DATE]

    for name, shape, read_format in DATE_FORMATS:
        if shape.fullmatch(text):
            try:
                parsed = datetime.strptime(text, read_format)
            except ValueError:
                # Right shape but not a real date, e.g. 31-02-23.
                return None, [Reason.INVALID_DATE]
            value = parsed.strftime("%Y-%m-%d")
            if value == raw:
                return value, []          # already standard
            return value, [Reason.DATE_NORMALIZED]

    return None, [Reason.INVALID_DATE]    # no format matched


def is_ambiguous_date(raw):
    """Return True if a valid slash or hyphen date has day and month both 1 to 12.

    Used only for report counts. Parsing does not depend on it.
    """
    if find_date_format(raw) in (None, "YYYY-MM-DD"):
        return False
    if parse_date(raw)[0] is None:        # not a real date
        return False
    text = raw.strip()
    first, second = int(text[0:2]), int(text[3:5])
    return 1 <= first <= 12 and 1 <= second <= 12
