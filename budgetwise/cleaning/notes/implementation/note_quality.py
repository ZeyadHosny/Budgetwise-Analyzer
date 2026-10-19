"""Notes quality.

Labels each note's quality. The note text is never changed. Rules are
explained in README.md.
"""

from budgetwise.errorlog import Reason

# Quality labels
MEANINGFUL = "meaningful"
MISSING = "missing"                    # blank or None
NOT_AVAILABLE = "not_available"        # the text N/A
LOW_INFORMATION = "low_information"    # known placeholder

# Placeholders found when profiling the data, compared in lowercase.
PLACEHOLDER_NOTES = ("...", "!!!", "xyz123", "test", "misc", "asdfgh")


def classify_note_quality(raw_note):
    """Return (note unchanged, quality, reasons). Never raises."""
    if raw_note is None:
        return "", MISSING, [Reason.NOTES_MISSING]
    if not isinstance(raw_note, str):
        raw_note = str(raw_note)

    # Compare the whole note, so "test drive fee" stays meaningful.
    comparable = raw_note.strip().lower()

    if comparable == "":
        return raw_note, MISSING, [Reason.NOTES_MISSING]
    if comparable == "n/a":
        # Same reason as blank, separate label so each count can be checked.
        return raw_note, NOT_AVAILABLE, [Reason.NOTES_MISSING]
    if comparable in PLACEHOLDER_NOTES:
        return raw_note, LOW_INFORMATION, [Reason.NOTES_LOW_INFORMATION]
    return raw_note, MEANINGFUL, []
