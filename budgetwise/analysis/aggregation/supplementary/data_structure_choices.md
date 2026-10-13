# Data structure choices — analysis/aggregation

Henrietta · `P3.2` · evidence for §4.2 and §7

## Which structure is used where, and why

| Structure | Where | Why this one |
|---|---|---|
| `list` | The transactions passed in | Ordered, walked once per aggregation. The pipeline already produces a list, so nothing is copied. |
| `dict` | `totals_by_category`, `count_by_category`, `totals_by_month` | Keyed accumulation: each transaction adds to the total under its key in one step, without searching. `collections.defaultdict` removes the "is the key there yet" check. |
| `set` | `unique_categories` | The question is "which categories exist", so membership and de-duplication are the whole job. A list would keep duplicates and imply an order that means nothing. |
| `tuple` | The month key `("2023", "07")` | Immutable, so it can be a dictionary key. Zero-padded strings in a tuple sort chronologically, so the monthly results come out in date order without parsing any dates. |
| nested `dict` | `totals_by_month_and_category` | Month → category → total, for budget comparison by month. |

## Dated versus undated transactions

§4.5: a row with a missing date is *"excluded from date-based analysis (it may still count toward category totals)"*.

- `totals_by_category` **includes** undated transactions.
- `totals_by_month` **skips** them.

So the two totals legitimately differ, by exactly the amount of the undated transactions. On the full dataset (provisional run, before `G4`):

| | Expense total |
|---|---|
| Sum of `totals_by_category(kind="expense")` | 165,749,066 |
| Sum of `totals_by_month(kind="expense")` | 162,224,605 |
| Difference = undated expense transactions | 3,524,461 |

This is the expected result, not a bug.

## Two input shapes, one set of functions

Each function accepts either:

- `Transaction` objects from `budgetwise.models`, read through their getters (`get_category()`, `get_amount()`, `get_transaction_type()`, `get_month()`), or
- the cleaned record dictionaries from `budgetwise.pipeline.clean_file()`.

`implementation/fields.py` is the only place that knows the difference. The tests run every total against both shapes and get identical results.

## Direction

Totals sum the unsigned `amount`. Whether a transaction is an expense or income comes from `transaction_type`, selected with `kind="expense"` or `kind="income"`, never from the sign of the amount (§4.5).
