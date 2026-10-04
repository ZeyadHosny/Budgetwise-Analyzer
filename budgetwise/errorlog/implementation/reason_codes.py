"""Shared reason codes emitted by data-cleaning modules."""


class Reason:
    MISSING_DATE = "missing_date"
    UNRECOGNIZED_DATE_FORMAT = "unrecognized_date_format"
    IMPOSSIBLE_DATE = "impossible_date"
    MISSING_AMOUNT = "missing_amount"
    UNRECOGNIZED_AMOUNT_FORMAT = "unrecognized_amount_format"
    SENTINEL_AMOUNT = "sentinel_amount"
    MISSING_CATEGORY = "missing_category"
    UNKNOWN_CATEGORY = "unknown_category"
    DUPLICATE_ROW = "duplicate_row"
    MISSING_REQUIRED_FIELD = "missing_required_field"
