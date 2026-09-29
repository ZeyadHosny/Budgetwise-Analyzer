# cleaning/amounts/implementation

Patrick · `P2.3` · domain reviewer Bahareh

## Write this

```python
parse_amount(raw: str) -> tuple[float | None, str | None, str | None]
    success → (5891.0, "₹", None)
    failure → (None, None, "reason_code")
```

Three values: the number, the symbol it carried, and why it failed.

## Must handle — counts are from the real dataset

| Shape | Count | Rule |
|---|---|---|
| `5891` | 12,313 | plain |
| `₹5891` | 1,550 | strip prefix, remember `₹` |
| `$5891` | 786 | strip prefix, remember `$` |
| `Rs.5891` | 498 | strip prefix — **including the dot** |
| `5891 INR` | 309 | strip **suffix**, remember `INR` |
| `-5891` and variants | 153 | discard the sign, return the magnitude |
| blank | 291 | `(None, None, "missing_amount")` |
| `999999999` | 80 | `(None, None, "sentinel_amount")` |

## Two traps

**`Rs.` contains a period.** Stripping non-digits with a regex that keeps `.`
turns `Rs.5638` into `.5638` — which parses as `0.5638`. Every `Rs.` row then
reads as under a rupee and all your totals shift. Strip the `Rs.` prefix as a
string before touching the number.

**`INR` is a suffix, the rest are prefixes.** Check the end of the string, not
the start.

## Rules

- Never convert currency. §4.5 forbids it — the symbols are cosmetic labels on a
  single unit, as the medians (5,900 / 5,891 / 5,863 / 5,638 / 6,602) show.
- Threshold is `>= 100_000_000`. All 80 sentinel rows are exactly `999999999`,
  but code the threshold, not the literal.
- Return the magnitude. Direction comes from `transaction_type` in `models/`.
- Always return the symbol. §4.5 requires it logged.

## Do not

- Multiply by an exchange rate, ever
- Use the sign of the amount to decide income versus expense
- Import pandas or numpy — violates §2
