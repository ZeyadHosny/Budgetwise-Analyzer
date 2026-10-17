## 6. October 13 — Real-model and account integration review

This entry supplements the historical October 11 results above.
The earlier model-integration pending statement is superseded by this
preliminary review. Final validation after G2 remains pending.

### Execution details

- Review date: October 13, 2026.
- Python: 3.12.14.
- Source snapshot: `Budgetwise-Analyzer-feature-P3.7-exports.zip`.
- Local review change: added `test_account_summaries.py`.
- Exact commit SHA: not available from the supplied ZIP.
- Summary calculation files were not changed.

Command from the repository root:

```bash
python -m unittest budgetwise.analysis.summaries.testing.test_account_summaries budgetwise.analysis.summaries.testing.test_totals budgetwise.analysis.summaries.testing.test_rankings -v
```

Observed in the local review copy:

```text
Ran 39 tests

OK
```

The 27 existing dictionary tests and 12 new integration tests passed.
The committed integration branch must be verified separately.

### Real-model fixture expectations

The integration sample uses actual ExpenseTransaction and IncomeTransaction
objects stored in CashAccount, BankAccount and UnknownAccount.

| Scope | Income | Expenses | Net | January expenses | February expenses | Undated expenses |
|---|---:|---:|---:|---:|---:|---:|
| Cash | 500 | 350 | 150 | 300 | 0 | 50 |
| Bank | 1,000 | 380 | 620 | 300 | 80 | 0 |
| Unknown | 60 | 330 | -270 | 100 | 200 | 30 |
| Overall | 1,560 | 1,060 | 500 | 700 | 280 | 80 |

Overall expense categories:

| Category | Expense total |
|---|---:|
| Rent | 600 |
| Food | 350 |
| Utilities | 80 |
| Other | 30 |

Expected top expense IDs:
`T0002`, `T0007`, `T0011`, `T0001`, `T0005`.

All six outputs are checked against hand-calculated expectations.
Additional checks cover:
- Dictionary/model equivalence.
- Exactly-once fixture account membership using object identity.
- Undated transactions.
- Stable ranking ties and original-object identity.
- Repeated IDs without additional deduplication.
- Empty accounts.
- Unchanged objects and account order.
- Shared amount updates without stale cached totals.

These tests verify summary integration. They do not independently prove
that the pipeline routes every dataset record into the correct account.

## 7. Separate full-dataset review findings

Re-measured 2026-10-17 on the retained records from
`data/raw/budgetwise_synthetic_dirty.csv`, the D01 dataset. The earlier
October 13 figures, taken on `budgetwise_finance_dataset.csv`, are kept in the
second column.

These findings are distinct from the 39 fixture tests and are preliminary
review evidence, not final validation on a G2-approved revision.

| Measure | Observed (D01) | finance (old) |
|---|---:|---:|
| Retained records | 14,862 | 14,651 |
| Model objects | 14,862 | 14,651 |
| Total income | 134,553,045 | 144,624,974 |
| Total expenses | 53,348,034 | 165,749,066 |
| Net balance | **+81,205,011** | -21,124,092 |
| Sum of monthly expenses | 44,579,968 | 162,224,605 |
| Undated expense difference | **8,768,066** | 3,524,461 |
| Cash objects | 3,563 | 3,502 |
| Bank objects | 10,591 | 10,425 |
| Unknown objects | 708 | 724 |

All six summaries matched independently calculated results for the
complete selected model list and for each account list.

The returned model objects appeared in exactly one payment-group account.

Two differences change how the results read, and both belong in the report
rather than in this file alone.

**The net balance flips sign.** It is +81,205,011 here against -21,124,092 on
the earlier dataset. Any narrative written around "expenses exceed income" no
longer holds.

**The undated expense difference is 8,768,066, or 16.4% of total expenses**,
against 3,524,461 and 2.1% before. That is the gap between total expenses and
the sum of the monthly figures, and it exists because 2,259 date values match
no parsing rule. `total_expenses()` includes undated rows while
`monthly_expenses()` excludes them, so the two will not reconcile unless the
split is reported. Nothing stores this figure: it has to be derived as total
expenses minus the sum of the monthly rows.

### Full-dataset spending categories

| Rank | Category | Expense total |
|---|---|---:|
| 1 | Food | 15,059,930 |
| 2 | Rent | 10,364,133 |
| 3 | Utilities | 8,970,763 |
| 4 | Transportation | 8,110,333 |
| 5 | Entertainment | 3,852,311 |

The same five categories hold the top five places on both datasets, which is
why decision `D06` did not have to change which categories are budgeted. Only
the order and the amounts moved: Food and Rent swap first and second place.

The five largest individual expense amounts were each 999,999.
Their order was checked against the retained input order.
These amounts are below the exclusion threshold of 100,000,000.

**999,999 is a ceiling in the source data, not a real transaction.** It is the
largest value either dataset contains, and the five largest expenses are all
exactly equal to it. Report them as an artefact of the data rather than as a
finding about spending.

## 8. Caller responsibilities and final validation

For overall reports, pass the ordered master transaction list.
For an account report, pass that account's `get_transactions()` result.

Accounts share the same objects as the master list.
Do not add master totals to account totals.

Menu account selection and export formatting belong to their respective
features. Monthly tuple keys require a JSON-compatible representation;
individual expense objects require explicit record serialization.

Remaining final work:
- Verify the committed integration branch.
- Rerun after the cleaning baseline fixes.
- Record the exact revision, dataset identity and execution commands.
- Verify the final menu/report/export flow.
- Add the dated/undated expense split to the reported results, since the
  monthly figures exclude 16.4% of expenses on this dataset and nothing in the
  summary output states that.

No commit SHA or final gate approval is inferred from an uploaded ZIP.
