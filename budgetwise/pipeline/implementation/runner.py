"""
runner.py  -  the cleaning pipeline            (task P2.10, owner: Sarah)

WHAT THIS FILE DOES
  It does not clean anything itself. It calls each teammate's function in
  the required order and joins the results together.

  clean_file(path)  loads the CSV and cleans every row.
                    Returns plain cleaned records. Needs no classes.
  run(path, ...)    calls clean_file(), then turns each cleaned record into
                    a transaction object. This is what the menu calls.

THE ORDER (Project-1.pdf section 4.5: "duplicate detection must be
performed on the original raw rows before data normalization")

    1. load_rows()               loader      every raw row, numbered
    2. is_duplicate()            rows        on the RAW row, before anything else
    3. has_required_fields()     rows        skip rows that cannot be used
    4. parse_amount()            amounts     no usable amount -> skip the row
    5. parse_date()              dates       no date -> row is KEPT, date is None
       normalize_category()      categories
       normalize_payment_mode()  payment_modes
       normalize_location()      locations
       classify_note_quality()   notes
    6. Transaction.create()      models      builds the Expense/Income object
    7. date-range and category filters from the menu

RULES THIS FILE FOLLOWS
  * Standard library only.
  * Every teammate's function is imported from its feature's __init__.py,
    never from an implementation/ folder.
  * A bad row is logged and skipped. It never stops the program (4.1).
  * A missing date does not remove the row. It is only left out of
    date-based analysis, and still counts toward category totals (4.5).
  * An amount of 100,000,000 or more is not a real transaction (4.5).
  * Direction comes from transaction_type, never from the sign (4.5).
  * input rows = valid + skipped + duplicates, always.
"""

import math
import time
from collections import Counter

from budgetwise.cleaning.amounts import parse_amount
from budgetwise.cleaning.categories import normalize_category
from budgetwise.cleaning.dates import parse_date
from budgetwise.cleaning.locations import normalize_location
from budgetwise.cleaning.notes import classify_note_quality
from budgetwise.cleaning.payment_modes import normalize_payment_mode
from budgetwise.cleaning.rows import has_required_fields, is_duplicate
from budgetwise.errorlog import ErrorLog, Reason
from budgetwise.loader import load_rows

# The classes are Zeyad's task. Until they are merged, cleaning still works
# and run() explains why it has no objects to return.
try:
    from budgetwise.models import Transaction
except ImportError:
    Transaction = None

# Reason codes this file creates itself, written in the same lowercase style
# as errorlog's Reason list. The cleaners return their own.
REPEATED_TRANSACTION_ID = "repeated_transaction_id"
CURRENCY_LABEL_STRIPPED = "currency_label_stripped"
NEGATIVE_AMOUNT_MAGNITUDE = "negative_amount_magnitude"
FILE_NOT_LOADED = "file_not_loaded"
OBJECT_NOT_BUILT = "transaction_not_built"

# Reasons that mean "a value was changed to its standard form" (corrected).
# Any other reason on a row we keep means "kept, but with a concern" (flagged).
CORRECTED_REASONS = {
    "date_normalized", "category_normalized", "category_uncategorized",
    "payment_mode_normalized", "payment_mode_unknown",
    "location_normalized", "location_unknown",
    CURRENCY_LABEL_STRIPPED, NEGATIVE_AMOUNT_MAGNITUDE,
}

NO_CURRENCY_LABEL = "plain"


# ==========================================================================
# PART 1: CLEANING  (steps 1 to 5)
# ==========================================================================
def clean_file(path, error_log=None):
    """Load the CSV and clean every row.

    path       the CSV file to read
    error_log  an ErrorLog to write to. If none is given, one is opened on
               output/logs/errors.log and closed again at the end.

    Returns a dictionary:
        "records"  list of dictionaries, one per valid row (cleaned values)
        "counts"   totals for the report (see _empty_counts)
        "timings"  {"load": seconds, "clean": seconds}
        "issues"   list of (line_number, field, reason, raw_value)
        "error"    None, or a message if the file could not be read
    """
    owns_log = error_log is None
    if owns_log:
        error_log = ErrorLog()
    try:
        return _clean_rows(path, error_log)
    finally:
        if owns_log:
            error_log.close()


def _clean_rows(path, error_log):
    records = []
    counts = _empty_counts()
    issues = []
    result = {
        "records": records, "counts": counts,
        "timings": {"load": 0.0, "clean": 0.0}, "issues": issues, "error": None,
    }

    def record_issue(line_number, field, reasons, raw_value):
        """Keep each reason in memory and send it to errors.log."""
        for reason in _reason_list(reasons):
            issues.append((line_number, field, reason, raw_value))
            error_log.record(line_number, field, reason, raw_value)

    # ---- STEP 1: load every raw row -------------------------------------
    started = time.perf_counter()
    try:
        numbered_rows = list(load_rows(path))
    except Exception as error:       # missing file, bad header, bad encoding
        result["error"] = f"could not load {path}: {error}"
        record_issue(0, "file", FILE_NOT_LOADED, str(error))
        return result
    loaded = time.perf_counter()
    result["timings"]["load"] = round(loaded - started, 4)
    counts["input"] = len(numbered_rows)

    # ---- STEPS 2 to 5: one row at a time --------------------------------
    seen_rows = set()        # a NEW set for every call, so loading twice is safe
    for line_number, raw in numbered_rows:
        issues_before = len(issues)

        # STEP 2: exact duplicate? Checked on the untouched raw row.
        if is_duplicate(raw, seen_rows):
            counts["duplicates"] += 1
            record_issue(line_number, "row", Reason.DUPLICATE_ROW, _row_id(raw))
            continue

        # STEPS 3 to 5. Anything unexpected is caught, so one bad row can
        # never stop the run.
        try:
            record = _clean_one_row(line_number, raw, record_issue)
        except Exception as error:
            record = None
            record_issue(line_number, "row", Reason.MISSING_REQUIRED_FIELD, str(error))

        if record is None:
            counts["skipped"] += 1
            continue

        counts["valid"] += 1
        records.append(record)
        if record["category"] != raw["category"]:
            counts["categories_normalized"] += 1

        # Was anything on this row corrected or flagged?
        row_reasons = {reason for _, _, reason, _ in issues[issues_before:]}
        if row_reasons & CORRECTED_REASONS:
            counts["corrected"] += 1
        if row_reasons - CORRECTED_REASONS:
            counts["flagged"] += 1

    # A repeated transaction_id is NOT a duplicate (4.5). The rows are kept;
    # they are only noted in the log so they can be traced.
    id_counts = Counter(record["transaction_id"] for record in records)
    for record in records:
        if id_counts[record["transaction_id"]] > 1:
            record_issue(record["line_number"], "transaction_id",
                         REPEATED_TRANSACTION_ID, record["transaction_id"])
    counts["repeated_ids"] = sum(1 for count in id_counts.values() if count > 1)

    counts["by_reason"] = dict(Counter(reason for _, _, reason, _ in issues))
    result["timings"]["clean"] = round(time.perf_counter() - loaded, 4)
    return result


def _clean_one_row(line_number, raw, record_issue):
    """Clean one raw row. Return a dictionary of cleaned values, or None to skip it."""

    # STEP 3: is there enough here to build a transaction at all?
    if not has_required_fields(raw):
        record_issue(line_number, "row", Reason.MISSING_REQUIRED_FIELD, _row_id(raw))
        return None

    # STEP 4: amount. Without a usable amount there is no transaction.
    raw_amount = raw["amount"]
    amount, symbol, amount_reason = parse_amount(raw_amount)
    if amount is None or not math.isfinite(amount):
        record_issue(line_number, "amount",
                     amount_reason or Reason.UNRECOGNIZED_AMOUNT_FORMAT, raw_amount)
        return None
    # The parser strips the currency label and the minus sign without saying
    # so. Section 4.5 wants the original label logged, so it is noted here.
    if symbol:
        record_issue(line_number, "amount", CURRENCY_LABEL_STRIPPED, raw_amount)
    if "-" in raw_amount:
        record_issue(line_number, "amount", NEGATIVE_AMOUNT_MAGNITUDE, raw_amount)

    # STEP 5: the other columns. None of these can make the row invalid.
    date, date_reasons = parse_date(raw["date"])            # date may be None
    record_issue(line_number, "date", date_reasons, raw["date"])

    category, category_reason = normalize_category(raw["category"])
    record_issue(line_number, "category", category_reason, raw["category"])

    payment_mode, payment_reason = normalize_payment_mode(raw["payment_mode"])
    record_issue(line_number, "payment_mode", payment_reason, raw["payment_mode"])

    location, location_reason = normalize_location(raw["location"])
    record_issue(line_number, "location", location_reason, raw["location"])

    notes, notes_quality, note_reasons = classify_note_quality(raw["notes"])
    record_issue(line_number, "notes", note_reasons, raw["notes"])

    return {
        "line_number": line_number,
        "transaction_id": raw["transaction_id"].strip(),
        "user_id": raw["user_id"].strip(),
        "transaction_type": raw["transaction_type"].strip().capitalize(),
        "date": date,
        "category": category,
        "amount": amount,
        "original_currency": symbol or NO_CURRENCY_LABEL,
        "payment_mode": payment_mode,
        "location": location,
        "notes": notes,
        "notes_quality": notes_quality,
    }


# ==========================================================================
# PART 2: BUILDING THE OBJECTS  (steps 6 and 7)
# ==========================================================================
def run(path, start=None, end=None, category=None, error_log=None):
    """Load, clean and build transaction objects. The function the menu calls.

    path      the CSV file to read
    start     optional 'YYYY-MM-DD'. Keep only transactions on or after it.
    end       optional 'YYYY-MM-DD'. Keep only transactions on or before it.
    category  optional normalized category name, for example 'Food'.

    Returns everything clean_file() returns, plus:
        "transactions"  list of ExpenseTransaction / IncomeTransaction objects
    """
    owns_log = error_log is None
    if owns_log:
        error_log = ErrorLog()
    try:
        result = _clean_rows(path, error_log)
        result["transactions"] = []
        if result["error"]:
            return result
        if Transaction is None:
            result["error"] = "rows were cleaned, but budgetwise.models has no Transaction class yet"
            return result

        counts = result["counts"]
        for record in result["records"]:
            # STEP 6: Transaction.create() picks ExpenseTransaction or
            # IncomeTransaction from transaction_type.
            try:
                transaction = Transaction.create(
                    record["transaction_type"], record["transaction_id"],
                    record["user_id"], record["date"], record["category"],
                    record["amount"], record["payment_mode"],
                    record["original_currency"],
                )
            except Exception as error:      # the class refused the values
                counts["valid"] -= 1
                counts["skipped"] += 1
                result["issues"].append((record["line_number"], "row", OBJECT_NOT_BUILT, str(error)))
                error_log.record(record["line_number"], "row", OBJECT_NOT_BUILT, str(error))
                continue

            # STEP 7: the menu's filters, applied to cleaned values.
            if _passes_filters(record, start, end, category):
                result["transactions"].append(transaction)

        counts["returned"] = len(result["transactions"])
        return result
    finally:
        if owns_log:
            error_log.close()


def _passes_filters(record, start, end, category):
    """True if the row is inside the date range and category asked for."""
    if start or end:
        # A row with no date cannot be inside a date range (4.5).
        if record["date"] is None:
            return False
        if start and record["date"] < start:        # 'YYYY-MM-DD' text sorts
            return False                            # in date order
        if end and record["date"] > end:
            return False
    if category:
        # Compared AFTER normalizing, so 'food', 'Fod' and 'FOOD' rows all match.
        if record["category"].lower() != category.strip().lower():
            return False
    return True


# ==========================================================================
# SMALL HELPERS
# ==========================================================================
def _reason_list(reasons):
    """Turn whatever a cleaner returned into a list of lowercase text codes.

    The cleaners do not all return reasons the same way: one code, a list of
    codes, or None, some in capitals and some not. This makes them uniform,
    in the lowercase style of errorlog's Reason list.
    """
    if reasons is None:
        return []
    if not isinstance(reasons, (list, tuple, set)):
        reasons = [reasons]
    return [str(getattr(reason, "value", reason)).lower() for reason in reasons if reason]


def _row_id(raw):
    """The row's transaction_id for the log, or its text if it has none."""
    try:
        return raw.get("transaction_id") or repr(raw)
    except AttributeError:
        return repr(raw)


def _empty_counts():
    return {
        "input": 0,                  # rows read from the file
        "duplicates": 0,             # exact duplicate raw rows removed
        "skipped": 0,                # rows that could not become a transaction
        "valid": 0,                  # rows that did
        "corrected": 0,              # valid rows with a value standardized
        "flagged": 0,                # valid rows kept with a concern
        "categories_normalized": 0,  # valid rows whose category text changed
        "repeated_ids": 0,           # ids shared by different rows (all kept)
        "returned": 0,               # objects left after the menu's filters
        "by_reason": {},             # how many times each reason was logged
    }
