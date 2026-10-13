class Reason:
    # Canonical error-log codes
    MISSING_DATE                = "missing_date"
    UNRECOGNIZED_DATE_FORMAT    = "unrecognized_date_format"
    IMPOSSIBLE_DATE             = "impossible_date"

    # Amount codes
    MISSING_AMOUNT              = "missing_amount"
    UNRECOGNIZED_AMOUNT_FORMAT  = "unrecognized_amount_format"
    SENTINEL_AMOUNT             = "sentinel_amount"

    # Category codes
    MISSING_CATEGORY            = "missing_category"
    UNKNOWN_CATEGORY            = "unknown_category"

    # Row codes
    DUPLICATE_ROW               = "duplicate_row"
    MISSING_REQUIRED_FIELD      = "missing_required_field"

    # Cleaner return codes retain their public uppercase spelling. The
    # pipeline lowercases them before writing to errors.log.
    DATE_NORMALIZED             = "DATE_NORMALIZED"
    DATE_MISSING                = "MISSING_DATE"
    INVALID_DATE                = "INVALID_DATE"
    CATEGORY_NORMALIZED         = "CATEGORY_NORMALIZED"
    CATEGORY_UNCATEGORIZED      = "CATEGORY_UNCATEGORIZED"
    CATEGORY_UNKNOWN            = "UNKNOWN_CATEGORY"
    LOCATION_NORMALIZED         = "LOCATION_NORMALIZED"
    LOCATION_UNKNOWN            = "LOCATION_UNKNOWN"
    PAYMENT_MODE_NORMALIZED     = "PAYMENT_MODE_NORMALIZED"
    PAYMENT_MODE_UNKNOWN        = "PAYMENT_MODE_UNKNOWN"
    NOTES_MISSING               = "NOTES_MISSING"
    NOTES_LOW_INFORMATION      = "NOTES_LOW_INFORMATION"
    DUPLICATE_RAW_ROW           = "DUPLICATE_RAW_ROW"
    REPEATED_TRANSACTION_ID     = "REPEATED_TRANSACTION_ID"
    MALFORMED_ROW               = "MALFORMED_ROW"

    # Pipeline-only codes
    CURRENCY_LABEL_STRIPPED     = "currency_label_stripped"
    NEGATIVE_AMOUNT_MAGNITUDE   = "negative_amount_magnitude"
    FILE_NOT_LOADED             = "file_not_loaded"
    TRANSACTION_NOT_BUILT       = "transaction_not_built"