from budgetwise.errorlog import Reason
from .parser import parse_amount


def clean_amount(
    raw: str | None
) -> tuple[float | None, str | None, list[str]]:
    """Return amount, original currency label, and issue codes."""
    amount, symbol, error = parse_amount(raw)

    # Invalid or missing amounts keep their existing error reason.
    if error is not None:
        return amount, symbol, [error]

    issues = []
    value = raw.strip()

    # The parser has already validated the input.
    if "-" in value:
        issues.append(Reason.AMOUNT_NEGATIVE_TO_MAGNITUDE)

    formatting_changed = (
        raw != value
        or symbol is not None
        or "," in value
        or "+" in value
        or any(character.isspace() for character in value)
    )

    if formatting_changed:
        issues.append(Reason.AMOUNT_FORMAT_NORMALIZED)

    return amount, symbol, issues
