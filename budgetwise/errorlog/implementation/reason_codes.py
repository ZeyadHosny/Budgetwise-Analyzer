class Reason:
    # Date cleaning
    MISSING_DATE                = "missing_date"
    UNRECOGNIZED_DATE_FORMAT    = "unrecognized_date_format"
    IMPOSSIBLE_DATE             = "impossible_date"
    DATE_NORMALIZED             = "DATE_NORMALIZED"
    INVALID_DATE                = "INVALID_DATE"

    # Amount cleaning
    MISSING_AMOUNT              = "missing_amount"
    UNRECOGNIZED_AMOUNT_FORMAT  = "unrecognized_amount_format"
    SENTINEL_AMOUNT             = "sentinel_amount"
    CURRENCY_LABEL_STRIPPED     = "currency_label_stripped"
    NEGATIVE_AMOUNT_MAGNITUDE   = "negative_amount_magnitude"

    # Category cleaning
    MISSING_CATEGORY            = "missing_category"
    UNKNOWN_CATEGORY            = "unknown_category"
    CATEGORY_NORMALIZED         = "CATEGORY_NORMALIZED"
    CATEGORY_UNCATEGORIZED      = "CATEGORY_UNCATEGORIZED"

    # Payment-mode cleaning
    PAYMENT_MODE_NORMALIZED     = "PAYMENT_MODE_NORMALIZED"
    PAYMENT_MODE_UNKNOWN        = "PAYMENT_MODE_UNKNOWN"

    # Location cleaning
    LOCATION_NORMALIZED         = "LOCATION_NORMALIZED"
    LOCATION_UNKNOWN            = "LOCATION_UNKNOWN"

    # Notes cleaning
    NOTES_MISSING               = "NOTES_MISSING"
    NOTES_LOW_INFORMATION      = "NOTES_LOW_INFORMATION"

    # Row cleaning
    DUPLICATE_ROW               = "duplicate_row"
    MISSING_REQUIRED_FIELD      = "missing_required_field"
    DUPLICATE_RAW_ROW           = "DUPLICATE_RAW_ROW"
    REPEATED_TRANSACTION_ID     = "REPEATED_TRANSACTION_ID"
    MALFORMED_ROW               = "MALFORMED_ROW"

    # Pipeline orchestration
    FILE_NOT_LOADED             = "file_not_loaded"
    TRANSACTION_NOT_BUILT       = "transaction_not_built"