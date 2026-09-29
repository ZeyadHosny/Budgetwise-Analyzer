# cleaning/amounts

Turns messy amount strings into plain unsigned numbers.

| | |
|---|---|
| **Responsible** | Patrick |
| **Domain reviewer** | Henrieta (`P1.3`) · Bahareh (`P2.3`) |
| **PR approval** | Zeyad or Patrick — see `CONTRIBUTING.md` |
| **Tasks** | `P1.3` profiling · `P2.3` implementation |
| **Status** | Not started |

## 1. What this folder does

The amount column mixes five currency labels, negative signs, blanks, and a
sentinel value. Eleven shapes in the main dataset:

| Shape | Count | Shape | Count |
|---|---|---|---|
| `5891` | 12,313 | `-5891` | 127 |
| `₹5891` | 1,550 | `₹-5891` | 11 |
| `$5891` | 786 | `Rs.-5891` | 6 |
| `Rs.5891` | 498 | `$-5891` | 6 |
| `5891 INR` | 309 | `-5891 INR` | 3 |
| blank | 291 | | |

Plus **80 rows holding `999999999`**, the sentinel §4.5 requires excluding.

**No currency conversion.** §4.5 explains why: the median is ~5,600–6,600 across
every symbol, so the labels are cosmetic, not real currencies. Applying an
exchange rate would distort the totals rather than fix them.

## 2. How other modules use it

```python
from budgetwise.cleaning.amounts import parse_amount

value, symbol, reason = parse_amount("Rs.5638")   # (5638.0, "Rs.", None)
value, symbol, reason = parse_amount("999999999") # (None, None, "sentinel_amount")
```

Only `pipeline/` calls this.

## 3. What it produces

| Input | Value | Symbol | Reason |
|---|---|---|---|
| `5891` | `5891.0` | `plain` | — |
| `₹5891` | `5891.0` | `₹` | — |
| `$5863` | `5863.0` | `$` | — |
| `Rs.5638` | `5638.0` | `Rs.` | — |
| `6602 INR` | `6602.0` | `INR` | — |
| `-5891` | `5891.0` | `plain` | — sign discarded, unsigned magnitude |
| `999999999` | `None` | — | `sentinel_amount` |
| `""` | `None` | — | `missing_amount` |
| `abc` | `None` | — | `unrecognized_amount_format` |

The symbol is returned, not discarded — §4.5 requires logging which symbol each
row originally carried.

## 4. Requirements and tasks covered

| Requirement | Source | Task |
|---|---|---|
| Normalize currency symbols into a single numeric representation | §4.1 | `P2.3` |
| Strip `₹`, `$`, `Rs.`, trailing `INR`; attempt no conversion | §4.5 | `P2.3` |
| Log which currency symbol each row originally had | §4.5 | `P2.3` |
| Amounts ≥ 100,000,000 invalid — excluded and logged | §4.5 | `P2.3` |
| Treat amount as an unsigned magnitude | §4.5 | `P2.3` |
| Direction from `transaction_type`, never the sign | §4.5 | `P2.3` `P2.5` |
| Unrecognized formats logged and skipped, never crash | §4.5 | `P2.3` |

## 5. Folders

| Folder | Contents |
|---|---|
| `implementation/` | `parser.py`, `currency.py` |
| `testing/` | `test_parser.py`, `fixtures/amount_cases.csv` |
| `supplementary/` | `amount_profile.md`, `currency_symbol_log.md` |

## 6. Done when

- [ ] All eleven shapes above parse correctly
- [ ] All 80 sentinel rows excluded and logged
- [ ] The original symbol returned for every parsed row
- [ ] Negative inputs return a positive magnitude
- [ ] Never raises, for any input
