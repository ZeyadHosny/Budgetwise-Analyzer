# Agreed interfaces

**Status: outstanding.** Owner: Zeyad · Task: `P1.5` · Agreed at: `G1`

The function signatures every module depends on. Written **before** Phase 2
implementation starts, so four people building cleaners in parallel are building
against something already settled.

This closes flag `F04` — the plan requires agreed interfaces but no task produces
a concrete contract.

## Where the contracts actually live

Each feature's `__init__.py` is the enforceable version of this document:

```python
# budgetwise/cleaning/dates/__init__.py
from .implementation.parser import parse_date
```

This file records the signatures and the reasoning; `__init__.py` is what Python
checks. **They must agree.** See `CONTRIBUTING.md` §6.

## To be filled in at P1.5

| Module | Function | Signature | Owner |
|---|---|---|---|
| `loader` | `load_rows` | `(path) -> Iterator[tuple[int, dict]]` | unassigned |
| `cleaning/dates` | `parse_date` | `(raw) -> tuple[str \| None, str \| None]` | Bahareh |
| `cleaning/categories` | `normalize` | `(raw) -> tuple[str, str \| None]` | Henrieta |
| `cleaning/amounts` | `parse_amount` | `(raw) -> tuple[float \| None, str \| None, str \| None]` | Patrick |
| `cleaning/rows` | `is_duplicate` | `(raw_row) -> bool` | Sarah |
| `cleaning/rows` | `has_required_fields` | `(raw_row) -> tuple[bool, str \| None]` | Sarah |
| `errorlog` | `ErrorLog.record` | `(line, field, reason, raw) -> None` | Sarah |
| `models` | `Transaction` | see `budgetwise/models/README.md` | Zeyad |
| `pipeline` | `run` | `(path, **filters) -> LoadResult` | Sarah, Zeyad |

The signatures above are proposals drawn from each feature's README. Confirm,
amend, or replace them at `G1`, then uncomment the matching `__init__.py` lines.

## Shapes that need agreeing

- **Raw row** — a `dict[str, str]` of the nine columns, exactly as read
- **Reason code** — the vocabulary in `budgetwise/errorlog/`
- **LoadResult** — what `pipeline.run` returns, and which counts it carries
- **Retained vs skipped** — which counts must reconcile, and how
