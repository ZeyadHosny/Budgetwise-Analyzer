"""
runner.py  -  the cleaning pipeline            (task P2.10, owner: Sarah)

WHAT THIS FILE DOES
  It does not clean anything itself. It calls each teammate's function in
  the required order and joins the results together.

  clean_file(path)  loads the CSV and cleans every row.
                    Returns plain cleaned records. Needs no classes.
  run(path, ...)    does the same cleaning, then turns each cleaned record
                    into a transaction object and places it in an account.
                    This is what the menu calls.

THE ORDER (Project-1.pdf section 4.5: "duplicate detection must be
performed on the original raw rows before data normalization")

    1. load_rows()               loader      every raw row, numbered
    2. is_duplicate()            rows        on the RAW row, before anything else
    3. validate_raw_row()        rows        skip unusable rows, flag odd ones
    4. parse_amount()            amounts     no usable amount -> skip the row
    5. parse_date()              dates       no date -> row is KEPT, date is None
       normalize_category()      categories
       normalize_payment_mode()  payment_modes
       normalize_location()      locations
       classify_note_quality()   notes
    6. find_repeated_ids()       rows        repeated IDs are flagged, rows KEPT
    7. ExpenseTransaction(...)   models      or IncomeTransaction(...), by type
    8. date-range and category filters from the menu
    9. add_transaction()         models      cash, bank or unknown account

HOW THE CLASSES ARE USED (budgetwise.models, Zeyad)
  Transaction          the parent. Never built directly: its
                       get_transaction_type() and get_signed_amount() only
                       work in a child. It has no create() factory, so the
                       pipeline picks the child from transaction_type.
  ExpenseTransaction   one object per cleaned row whose type is Expense.
  IncomeTransaction    one object per cleaned row whose type is Income.
  Account              the parent. Never built directly. Its
                       add_transaction() method is what stores a transaction
                       in an account, and all three children inherit it.
  CashAccount          one per load. Holds the Cash transactions.
  BankAccount          one per load. Holds Card, UPI and Bank Transfer.
  UnknownAccount       one per load. Holds rows whose payment mode is Unknown.
  Budget               NOT used here. It compares monthly totals to limits,
                       which is analysis (task P3.4), after the pipeline.
  Every value on an object is private and read through a getter, for
  example transaction.get_amount() or account.get_transaction_count().

TWO SETS OF COUNTS, KEPT SEPARATE
  Cleaning counts   input, duplicates, skipped, valid, corrected, flagged...
                    These describe the cleaning only. They are the same
                    whatever filter the menu asks for, and
                    input = valid + skipped + duplicates always holds.
  Object counts     objects_built, objects_failed, returned.
                    These describe steps 7 to 9 only.
  result["records"] is every cleaned row, UNFILTERED.
  result["transactions"] is the objects left after the menu's filters.

CORRECTED AND FLAGGED
  corrected = valid rows where a value was changed to its standard form.
  flagged   = valid rows kept with a concern (no date, repeated ID, ...).
  Each row is counted at most once in each, however many reasons it has.
  A row can be in both.

RULES THIS FILE FOLLOWS
  * Standard library only.
  * Every teammate's function is imported from its feature's __init__.py,
    never from an implementation/ folder.
  * A bad row is logged and skipped. It never stops the program (4.1).
  * A missing date does not remove the row. It is only left out of
    date-based analysis, and still counts toward category totals (4.5).
  * An amount of 100,000,000 or more is not a real transaction (4.5).
  * Direction comes from transaction_type, never from the sign (4.5).
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

# The classes are Zeyad's task. Until they are merged, cleaning still works
# and run() explains why it has no objects to return.
try:
    from budgetwise.models import (BankAccount, CashAccount, ExpenseTransaction,
                                   IncomeTransaction, Transaction, UnknownAccount)
except ImportError:
    Transaction = ExpenseTransaction = IncomeTransaction = None
    CashAccount = BankAccount = UnknownAccount = None

# Which account a payment mode belongs to (Zeyad's design: cash in hand
# versus money held at a bank). Any other value, such as 'Unknown' for a
# blank payment mode, goes to the UnknownAccount, which Zeyad's model
# provides for exactly those rows.
CASH_MODES = {"Cash"}
BANK_MODES = {"Card", "UPI", "Bank Transfer"}

# --------------------------------------------------------------------------
# REASON CODES
# All in one place, in the lowercase style of errorlog's Reason list, so the
# team can change the vocabulary here once it is agreed. The cleaners return
# their own codes; _reason_list() puts those in the same style.
# --------------------------------------------------------------------------
DUPLICATE_ROW = Reason.DUPLICATE_ROW                    # row skipped
MISSING_REQUIRED_FIELD = Reason.MISSING_REQUIRED_FIELD  # row skipped
UNRECOGNIZED_AMOUNT = Reason.UNRECOGNIZED_AMOUNT_FORMAT  # row skipped
MALFORMED_ROW = "malformed_row"                         # skipped or flagged
REPEATED_TRANSACTION_ID = "repeated_transaction_id"     # flagged, row kept
CURRENCY_LABEL_STRIPPED = "currency_label_stripped"     # corrected
NEGATIVE_AMOUNT_MAGNITUDE = "negative_amount_magnitude"  # corrected
FILE_NOT_LOADED = "file_not_loaded"
OBJECT_NOT_BUILT = "transaction_not_built"              # flagged

# Reasons that mean "a value was changed to its standard form" (corrected).
# Any other reason on a row we keep means "kept, but with a concern" (flagged).
CORRECTED_REASONS = {
    "date_normalized", "category_normalized", "category_uncategorized",
    "payment_mode_normalized", "payment_mode_unknown",
    "location_normalized", "location_unknown",
    CURRENCY_LABEL_STRIPPED, NEGATIVE_AMOUNT_MAGNITUDE,
}

NO_CURRENCY_LABEL = "plain"
REQUIRED_COLUMNS = ("transaction_id", "user_id", "transaction_type")


# ==========================================================================
# PART 1: CLEANING  (steps 1 to 6)
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
        result = _clean_rows(path, error_log)
        _summarise(result)
        return result
    finally:
        if owns_log:
            error_log.close()


def _record_issue(result, error_log, line_number, field, reasons, raw_value):
    """Keep each reason in memory and send it to errors.log.

    Every issue in the program goes through here, so the list in memory and
    the log file can never disagree.
    """
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
        # Anything unexpected on a row is caught here, INCLUDING a failure
        # in the duplicate check, so one bad row can never stop the run.
        try:
            # STEP 2: exact duplicate? Checked on the untouched raw row.
            if is_duplicate(raw, seen_rows):
                counts["duplicates"] += 1
                record_issue(line_number, "row", DUPLICATE_ROW, _row_id(raw))
                continue
            # STEPS 3 to 5.
            record = _clean_one_row(line_number, raw, record_issue)
        except Exception as error:
            record = None
            record_issue(line_number, "row", MALFORMED_ROW,
                         f"could not be processed: {type(error).__name__}: {error}")

        if record is None:
            counts["skipped"] += 1
            continue

        counts["valid"] += 1
        records.append(record)
        if record["category"] != raw["category"]:
            counts["categories_normalized"] += 1

    # ---- STEP 6: repeated transaction IDs -------------------------------
    # A repeated transaction_id is NOT a duplicate (4.5). The rows are kept;
    # they are only flagged in the log so they can be traced. The rows
    # feature does the counting, so its rule (blank IDs never count) and
    # this one are the same rule.
    repeated = find_repeated_ids((record["line_number"], record) for record in records)
    for record in records:
        if record["transaction_id"] in repeated:
            record_issue(record["line_number"], "transaction_id",
                         REPEATED_TRANSACTION_ID, record["transaction_id"])
    counts["repeated_ids"] = len(repeated)

    result["timings"]["clean"] = round(time.perf_counter() - loaded, 4)
    return result


def _clean_one_row(line_number, raw, record_issue):
    """Clean one raw row. Return a dictionary of cleaned values, or None to skip it."""

    # STEP 3: is there enough here to build a transaction at all?
    # validate_raw_row() returns (usable, problems). Every problem is logged
    # with the column it belongs to, so nothing it found is lost:
    #   a required column that cannot be used -> missing_required_field
    #   anything else (odd ID, wrong field count) -> malformed_row
    usable, problems = validate_raw_row(raw)
    for column, detail in problems:
        if not usable and column in REQUIRED_COLUMNS:
            record_issue(line_number, column, MISSING_REQUIRED_FIELD, detail)
        else:
            record_issue(line_number, column, MALFORMED_ROW, detail)
    if not usable:
        return None            # skipped. A usable row with a problem carries on.

    # STEP 4: amount. Without a usable amount there is no transaction.
    raw_amount = raw["amount"]
    amount, symbol, amount_reason = parse_amount(raw_amount)
    if amount is None or not math.isfinite(amount):
        record_issue(line_number, "amount", amount_reason or UNRECOGNIZED_AMOUNT, raw_amount)
        return None
    # The parser strips the currency label and the minus sign without saying
    # so. Section 4.5 wants the original label logged, so it is noted here.
    # If the parser starts returning a reason for an accepted amount, that
    # reason is logged instead, so nothing is reported twice.
    if amount_reason:
        record_issue(line_number, "amount", amount_reason, raw_amount)
    else:
        # Only a real label counts as stripped. If the parser ever reports
        # "plain" for an amount with no label, nothing was stripped.
        if symbol and symbol != NO_CURRENCY_LABEL:
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


def _summarise(result):
    """Work out the counts that depend on EVERY issue having been collected.

    This runs once, at the very end, after the repeated-ID flags and after
    any object that could not be built. Doing it earlier is what made a
    repeated ID miss the flagged count.
    """
    counts = result["counts"]
    issues = result["issues"]
    counts["by_reason"] = dict(Counter(reason for _, _, reason, _ in issues))

    # Gather the reasons on each line, then look at the valid rows only.
    reasons_by_line = {}
    for line_number, _, reason, _ in issues:
        reasons_by_line.setdefault(line_number, set()).add(reason)

    corrected = flagged = 0
    for record in result["records"]:
        reasons = reasons_by_line.get(record["line_number"], ())
        if not reasons:
            continue
        if not CORRECTED_REASONS.isdisjoint(reasons):
            corrected += 1                      # once, however many reasons
        if any(reason not in CORRECTED_REASONS for reason in reasons):
            flagged += 1                        # once, however many reasons
    counts["corrected"] = corrected
    counts["flagged"] = flagged


# ==========================================================================
# PART 2: BUILDING THE OBJECTS  (steps 7 to 9)
# ==========================================================================
def run(path, start=None, end=None, category=None, error_log=None):
    """Load, clean and build transaction objects. The function the menu calls.

    path      the CSV file to read
    start     optional 'YYYY-MM-DD'. Keep only transactions on or after it.
    end       optional 'YYYY-MM-DD'. Keep only transactions on or before it.
    category  optional normalized category name, for example 'Food'.

    Returns everything clean_file() returns, plus:
        "transactions"  list of ExpenseTransaction / IncomeTransaction objects
                        that pass the filters
        "accounts"      {"cash": CashAccount, "bank": BankAccount,
                         "unknown": UnknownAccount} holding those same objects
    The cleaning counts and "records" are not changed by the filters.
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
    """Steps 7 to 9, in ONE pass over the cleaned records."""
    counts = result["counts"]
    transactions = result["transactions"]

    # One ledger of each kind over whatever the menu loaded. All three are
    # children of Account.
    cash, bank, unknown = CashAccount(), BankAccount(), UnknownAccount()
    result["accounts"] = {"cash": cash, "bank": bank, "unknown": unknown}

    for record in result["records"]:
        # STEP 7: build the object. The result is always a CHILD class:
        # ExpenseTransaction or IncomeTransaction, chosen from transaction_type.
        try:
            transaction = _build_transaction(record)
        except Exception as error:      # the class refused the values
            counts["objects_failed"] += 1
            _record_issue(result, error_log, record["line_number"], "row",
                          OBJECT_NOT_BUILT, f"{type(error).__name__}: {error}")
            continue
        counts["objects_built"] += 1

        # STEP 8: the menu's filters, applied to cleaned values.
        if not _passes_filters(record, start, end, category):
            continue
        transactions.append(transaction)

        # STEP 9: the same object also goes into its account.
        # add_transaction() is defined once on the parent Account and
        # inherited by all three children.
        if record["payment_mode"] in CASH_MODES:
            cash.add_transaction(transaction)
        elif record["payment_mode"] in BANK_MODES:
            bank.add_transaction(transaction)
        else:
            unknown.add_transaction(transaction)

    counts["returned"] = len(transactions)


def _build_transaction(record):
    """Turn one cleaned record into an ExpenseTransaction or IncomeTransaction.

    Zeyad's merged Transaction class has no create() factory, so the
    subclass is picked here. If a factory is added later, it is used
    instead. Any type other than Expense or Income raises an error, so
    it is never silently treated as income.
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
        # ---- cleaning counts: the same for every filter ------------------
        "input": 0,                  # rows read from the file
        "duplicates": 0,             # exact duplicate raw rows removed
        "skipped": 0,                # rows that could not be cleaned
        "valid": 0,                  # rows that could (= len of "records")
        "corrected": 0,              # valid rows with a value standardized
        "flagged": 0,                # valid rows kept with a concern
        "categories_normalized": 0,  # valid rows whose category text changed
        "repeated_ids": 0,           # distinct IDs shared by 2+ valid rows
        "by_reason": {},             # how many times each reason was logged
        # ---- object counts: steps 7 to 9, run() only ---------------------
        "objects_built": 0,          # cleaned records that became objects
        "objects_failed": 0,         # cleaned records the classes refused
        "returned": 0,               # objects left after the menu's filters
    }
