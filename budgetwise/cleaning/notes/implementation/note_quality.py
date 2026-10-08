"""
note_quality.py  -  column: notes        (task P2.7, owner: Sarah)

WHAT THE PHASE 2 SPEC SAYS (sections 2, 4 and 5)
  * Meaningful notes: "Preserve meaningful free text exactly as observed."
  * Low-information notes: "Flag blank, N/A, and known placeholders; do not
    replace meaningful text."
  * Known placeholders: ...  !!!  xyz123  test  misc  asdfgh
  * notes is free text, NOT a closed category, so nothing is mapped.

WHAT PHASE 1 FOUND (15,900 rows)
  * 10,072 meaningful, 2,335 blank, 486 "N/A", 3,007 placeholders

REASON CODES AND FUNCTION NAME
  NOTES_MISSING          flagged: note is blank or N/A
  NOTES_LOW_INFORMATION  flagged: known placeholder

Returns THREE things (spec: "preserved note + quality flag / reason metadata"):
    (note, quality, reasons)
note is the text exactly as it was ('' if there was none).
"""

# Quality flags
MEANINGFUL = "meaningful"
MISSING = "missing"                    # blank
NOT_AVAILABLE = "not_available"        # the text N/A
LOW_INFORMATION = "low_information"    # known placeholder

# Closed list of placeholders found in Phase 1 (compared in lowercase).
PLACEHOLDER_NOTES = ("...", "!!!", "xyz123", "test", "misc", "asdfgh")

# Reason codes (both are flags; the row is always kept)
NOTES_MISSING = "NOTES_MISSING"
NOTES_LOW_INFORMATION = "NOTES_LOW_INFORMATION"


def classify_note_quality(raw_note):
    """Return (note text unchanged, quality, reasons). Never crashes."""
    if raw_note is None:
        return "", MISSING, [NOTES_MISSING]
    if not isinstance(raw_note, str):
        raw_note = str(raw_note)

    # Compare the WHOLE note, ignoring capitals and outer spaces, so that
    # "test" is a placeholder but "test drive fee" is a real note.
    comparable = raw_note.strip().lower()

    if comparable == "":
        return raw_note, MISSING, [NOTES_MISSING]
    if comparable == "n/a":
        # Same reason code as blank, but a separate quality flag, so the
        # blank and N/A counts can each be reconciled with Phase 1.
        return raw_note, NOT_AVAILABLE, [NOTES_MISSING]
    if comparable in PLACEHOLDER_NOTES:
        return raw_note, LOW_INFORMATION, [NOTES_LOW_INFORMATION]
    return raw_note, MEANINGFUL, []
