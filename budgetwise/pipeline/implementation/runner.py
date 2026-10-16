"""Cleaning pipeline (P2.10, Sarah).

Calls each teammate's cleaner in the required order and joins the results.
  clean_file(path)  loads the CSV and cleans every row
  run(path, ...)    cleans, then builds transaction objects and accounts;
                    this is what the menu calls
The step order, counts and use of the model classes are explained in README.md.
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
from budgetwise.cleaning.rows import find_repeated_ids, is_duplicate, validate_raw_row
from budgetwise.errorlog import ErrorLog, Reason
from budgetwise.loader import load_rows

# If the model classes are missing, cleaning still works and run() says why
# it has no objects.
try:
    from budgetwise.models import (BankAccount, CashAccount, ExpenseTransaction,
                                   IncomeTransaction, Transaction, UnknownAccount)
except ImportError:
    Transaction = ExpenseTransaction = IncomeTransaction = None
    CashAccount = BankAccount = UnknownAccount = None

# Payment mode -> account. Anything else (e.g. Unknown) goes to UnknownAccount.
CASH_MODES = {"Cash"}
BANK_MODES = {"Card", "UPI", "Bank Transfer"}

# Reasons meaning a value was standardised (corrected). Any other reason on
# a kept row means it was kept with a concern (flagged).
CORRECTED_REASONS = {
    Reason.DATE_NORMALIZED.lower(),
    Reason.CATEGORY_NORMALIZED.lower(),
    Reason.CATEGORY_UNCATEGORIZED.lower(),
    Reason.PAYMENT_MODE_NORMALIZED.lower(),
    Reason.PAYMENT_MODE_UNKNOWN.lower(),
    Reason.LOCATION_NORMALIZED.lower(),
    Reason.LOCATION_UNKNOWN.lower(),
    Reason.CURRENCY_LABEL_STRIPPED,
    Reason.NEGATIVE_AMOUNT_MAGNITUDE,
}

NO_CURRENCY_LABEL = "plain"
REQUIRED_COLUMNS = ("transaction_id", "user_id", "transaction_type")


# Part 1: cleaning (steps 1 to 6)

def clean_file(path, error_log=None):
    """Load the CSV and clean every row.

    If no error_log is given, one is opened on output/logs/errors.log and
    closed at the end. Returns a dictionary with "records", "counts",
    "timings", "issues" and "error".
    """
    owns_log = error_log is None
    if owns_log:
        error_log = ErrorLog()
    try:
        result = _clean_rows(path, error_log)
        _summarise(result)
        return result
    finally:
        if owns_log:
            error_log.close()


def _record_issue(result, error_log, line_number, field, reasons, raw_value):
    """Store each reason in memory and write it to errors.log, so both match."""
    for reason in _reason_list(reasons):
        result["issues"].append((line_number, field, reason, raw_value))
        error_log.record(line_number, field, reason, raw_value)


def _clean_rows(path, error_log):
    records = []
    counts = _empty_counts()
    result = {
        "records": records, "counts": counts,
        "timings": {"load": 0.0, "clean": 0.0}, "issues": [], "error": None,
    }

    def record_issue(line_number, field, reasons, raw_value):
        _record_issue(result, error_log, line_number, field, reasons, raw_value)

    # Step 1: load every raw row.
    started = time.perf_counter()
    try:
        numbered_rows = list(load_rows(path))
    except Exception as error:       # missing file, bad header or encoding
        result["error"] = f"could not load {path}: {error}"
        record_issue(0, "file", Reason.FILE_NOT_LOADED, str(error))
        return result
    loaded = time.perf_counter()
    result["timings"]["load"] = round(loaded - started, 4)
    counts["input"] = len(numbered_rows)

    # Steps 2 to 5, one row at a time.
    seen_rows = set()                # new set per call, so reloading is safe
    for line_number, raw in numbered_rows:
        # Any error on one row is logged and the run continues.
        try:
            # Step 2: exact duplicate, checked on the raw row (section 4.5).
            if is_duplicate(raw, seen_rows):
                counts["duplicates"] += 1
                record_issue(line_number, "row", Reason.DUPLICATE_ROW, _row_id(raw))
                continue
            record = _clean_one_row(line_number, raw, record_issue)
        except Exception as error:
            record = None
            record_issue(line_number, "row", Reason.MALFORMED_ROW,
                         f"could not be processed: {type(error).__name__}: {error}")

        if record is None:
            counts["skipped"] += 1
            continue

        counts["valid"] += 1
        records.append(record)
        if record["category"] != raw["category"]:
            counts["categories_normalized"] += 1

    # Step 6: repeated IDs are not duplicates. Rows are kept and flagged.
    repeated = find_repeated_ids((record["line_number"], record) for record in records)
    for record in records:
        if record["transaction_id"] in repeated:
            record_issue(record["line_number"], "transaction_id",
                         Reason.REPEATED_TRANSACTION_ID, record["transaction_id"])
    counts["repeated_ids"] = len(repeated)

    result["timings"]["clean"] = round(time.perf_counter() - loaded, 4)
    return result


def _clean_one_row(line_number, raw, record_issue):
    """Clean one raw row. Return a dictionary of cleaned values, or None to skip it."""

    # Step 3: required fields. Unusable required column -> missing_required_field;
    # any other problem -> malformed_row.
    usable, problems = validate_raw_row(raw)
    for column, detail in problems:
        if not usable and column in REQUIRED_COLUMNS:
            record_issue(line_number, column, Reason.MISSING_REQUIRED_FIELD, detail)
        else:
            record_issue(line_number, column, Reason.MALFORMED_ROW, detail)
    if not usable:
        return None

    # Step 4: amount. No usable amount means the row is skipped.
    raw_amount = raw["amount"]
    amount, symbol, amount_reason = parse_amount(raw_amount)
    if amount is None or not math.isfinite(amount):
        record_issue(line_number, "amount",
                     amount_reason or Reason.UNRECOGNIZED_AMOUNT_FORMAT,
                     raw_amount)
        return None
    # Log the stripped currency label and minus sign (section 4.5), unless
    # the parser already returned its own reason.
    if amount_reason:
        record_issue(line_number, "amount", amount_reason, raw_amount)
    else:
        if symbol and symbol != NO_CURRENCY_LABEL:
            record_issue(line_number, "amount", Reason.CURRENCY_LABEL_STRIPPED, raw_amount)
        if "-" in raw_amount:
            record_issue(line_number, "amount", Reason.NEGATIVE_AMOUNT_MAGNITUDE, raw_amount)

    # Step 5: other columns. None of these removes the row.
    date, date_reasons = parse_date(raw["date"])            # may be None
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


def _summarise(result):
    """Count reasons, and corrected and flagged rows, once all issues are in.

    Each valid row counts at most once as corrected and once as flagged.
    """
    counts = result["counts"]
    issues = result["issues"]
    counts["by_reason"] = dict(Counter(reason for _, _, reason, _ in issues))

    reasons_by_line = {}
    for line_number, _, reason, _ in issues:
        reasons_by_line.setdefault(line_number, set()).add(reason)

    corrected = flagged = 0
    for record in result["records"]:
        reasons = reasons_by_line.get(record["line_number"], ())
        if not reasons:
            continue
        if not CORRECTED_REASONS.isdisjoint(reasons):
            corrected += 1
        if any(reason not in CORRECTED_REASONS for reason in reasons):
            flagged += 1
    counts["corrected"] = corrected
    counts["flagged"] = flagged


# Part 2: building the objects (steps 7 to 9)

def run(path, start=None, end=None, category=None, error_log=None):
    """Clean the file, then build transaction objects and accounts.

    start and end are optional 'YYYY-MM-DD' limits (inclusive); category is
    an optional category name. Returns everything clean_file() returns, plus
    "transactions" (objects that pass the filters) and "accounts"
    ({"cash", "bank", "unknown"}). Filters never change the cleaning counts.
    """
    owns_log = error_log is None
    if owns_log:
        error_log = ErrorLog()
    try:
        result = _clean_rows(path, error_log)
        result["transactions"] = []
        result["accounts"] = {}
        if result["error"]:
            pass
        elif Transaction is None:
            result["error"] = "rows were cleaned, but budgetwise.models has no Transaction class yet"
        else:
            _build_objects(result, error_log, start, end, category)
        _summarise(result)
        return result
    finally:
        if owns_log:
            error_log.close()


def _build_objects(result, error_log, start, end, category):
    """Build, filter and file each cleaned record, in one pass."""
    counts = result["counts"]
    transactions = result["transactions"]

    cash, bank, unknown = CashAccount(), BankAccount(), UnknownAccount()
    result["accounts"] = {"cash": cash, "bank": bank, "unknown": unknown}

    for record in result["records"]:
        # Step 7: build an ExpenseTransaction or IncomeTransaction.
        try:
            transaction = _build_transaction(record)
        except Exception as error:      # the class refused a value
            counts["objects_failed"] += 1
            _record_issue(result, error_log, record["line_number"], "row",
                          Reason.TRANSACTION_NOT_BUILT,
                          f"{type(error).__name__}: {error}")
            continue
        counts["objects_built"] += 1

        # Step 8: the menu's filters.
        if not _passes_filters(record, start, end, category):
            continue
        transactions.append(transaction)

        # Step 9: add to its account (add_transaction is inherited from Account).
        if record["payment_mode"] in CASH_MODES:
            cash.add_transaction(transaction)
        elif record["payment_mode"] in BANK_MODES:
            bank.add_transaction(transaction)
        else:
            unknown.add_transaction(transaction)

    counts["returned"] = len(transactions)


def _build_transaction(record):
    """Return an ExpenseTransaction or IncomeTransaction for one record.

    Uses Transaction.create() if it exists. Any other type raises ValueError,
    so it is never treated as income by mistake.
    """
    values = (record["transaction_id"], record["user_id"], record["date"],
              record["category"], record["amount"], record["payment_mode"],
              record["original_currency"])
    if callable(getattr(Transaction, "create", None)):
        return Transaction.create(record["transaction_type"], *values)

    kind = (record["transaction_type"] or "").strip()
    if kind == "Expense":
        return ExpenseTransaction(*values)
    if kind == "Income":
        return IncomeTransaction(*values)
    raise ValueError(f"unknown transaction_type: {kind!r}")


def _passes_filters(record, start, end, category):
    """Return True if the record is inside the date range and category."""
    if start or end:
        if record["date"] is None:                  # undated rows have no range
            return False
        if start and record["date"] < start:        # ISO dates sort as text
            return False
        if end and record["date"] > end:
            return False
    if category:
        # Compared after cleaning, so 'food' and 'Fod' rows both match Food.
        if record["category"].lower() != category.strip().lower():
            return False
    return True


# Helpers

def _reason_list(reasons):
    """Return the cleaner's reason(s) as a list of lowercase codes."""
    if reasons is None:
        return []
    if not isinstance(reasons, (list, tuple, set)):
        reasons = [reasons]
    return [str(getattr(reason, "value", reason)).lower() for reason in reasons if reason]


def _row_id(raw):
    """Return the row's transaction_id for the log, or its text if it has none."""
    try:
        return raw.get("transaction_id") or repr(raw)
    except AttributeError:
        return repr(raw)


def _empty_counts():
    return {
        # Cleaning counts (the same for every filter)
        "input": 0,                  # rows read
        "duplicates": 0,             # exact duplicates removed
        "skipped": 0,                # rows that could not be cleaned
        "valid": 0,                  # rows cleaned
        "corrected": 0,              # valid rows with a value standardised
        "flagged": 0,                # valid rows kept with a concern
        "categories_normalized": 0,  # valid rows whose category changed
        "repeated_ids": 0,           # distinct IDs on 2+ valid rows
        "by_reason": {},             # times each reason was logged
        # Object counts (run() only)
        "objects_built": 0,          # records turned into objects
        "objects_failed": 0,         # records the classes refused
        "returned": 0,               # objects left after filters
    }
