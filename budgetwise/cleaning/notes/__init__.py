"""Notes quality flagging. Classifies notes; never rewrites them.

Public contract (Phase 2 specification, section 5):
    classify_note_quality(raw_note) -> (note unchanged, quality flag, list of reason codes)
"""

from .implementation.note_quality import (
    LOW_INFORMATION,
    MEANINGFUL,
    MISSING,
    NOT_AVAILABLE,
    NOTES_LOW_INFORMATION,
    NOTES_MISSING,
    PLACEHOLDER_NOTES,
    classify_note_quality,
)
