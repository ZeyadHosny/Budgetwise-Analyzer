# cleaning/categories

Maps messy raw category strings onto a fixed, documented set of names.

| | |
|---|---|
| **Responsible** | Henrieta |
| **Domain reviewer** | Bahareh (`P1.2`) · Sarah (`P2.2`) |
| **PR approval** | Zeyad or Patrick — see `CONTRIBUTING.md` |
| **Tasks** | `P1.2` profiling · `P2.2` implementation |
| **Status** | Not started |

## 1. What this folder does

The main dataset holds **47 distinct category strings** for what are really
about a dozen categories. The damage is case variation and typos:

```
FOOD 583 · Food 579 · food 567 · Foods 567 · Fod 535 · Foodd 525
RENT 574 · Rent 571 · rent 534 · Rentt 517 · Rnt 516
TRAVEL 403 · Travel 422 · travel 381 · Traval 411 · Travl 368
```

plus 285 blank values.

§4.5 requires a **closed** mapping: every raw string maps to a known name, and
the mapping is documented in the report. Closed means no silent pass-through —
an unrecognized string is a decision, not a default.

## 2. How other modules use it

```python
from budgetwise.cleaning.categories import normalize

name, reason = normalize("Foodd")      # ("Food", None)
name, reason = normalize("")           # ("Uncategorized", "missing_category")
```

Only `pipeline/` calls this.

## 3. What it produces

| Input | Returns | Reason |
|---|---|---|
| `Food` | `"Food"` | — |
| `FOOD` | `"Food"` | — case variant |
| `Foodd` | `"Food"` | — typo in the mapping |
| `Rnt` | `"Rent"` | — typo in the mapping |
| `""` | `"Uncategorized"` | `missing_category` |
| `Wobble` | `"Uncategorized"` | `unknown_category` |

A missing category is **never** dropped — §4.5 requires `"Uncategorized"`.

## 4. Requirements and tasks covered

| Requirement | Source | Task |
|---|---|---|
| Missing category assigned `"Uncategorized"`, never dropped | §4.5 | `P2.2` |
| A documented, closed raw-to-normalized mapping | §4.5 | `P1.2` `P2.2` |
| The mapping included in the report | §4.5 | `P4.4` |
| Use sets to identify unique categories | §4.2 | `P3.1` |
| Number of categories normalized | §5 | `P3.5` |

## 5. Folders

| Folder | Contents |
|---|---|
| `implementation/` | `normalizer.py`, `mapping.py` |
| `testing/` | `test_normalizer.py`, `fixtures/category_variants.csv` |
| `supplementary/` | `category_profile.md`, `mapping_rationale.md` |

## 6. Done when

- [ ] All 47 raw variants map to a name — none fall through
- [ ] Blank maps to `"Uncategorized"` with the right reason code
- [ ] The canonical set agreed at `G1` and written in `mapping_rationale.md`
- [ ] `config/category_mapping.csv` matches the code exactly
- [ ] `category_profile.md` written — report material
