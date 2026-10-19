# Presentation outline

20 minutes total, **including Q&A**. Roughly 15 minutes speaking and 5 for
questions. All figures are from the dirty dataset (decision D01) and match the
report.

## Speaking split

| Slide | Topic | Presenter |
|---|---|---|
| 2 | Purpose and Scope | Bahareh |
| 3 | System Context and Data Scope | Bahareh |
| 4 | Key Problems and Our Solutions | Bahareh |
| 5 | Component Architecture | Patrick |
| 6 | Pipeline Overview | Sarah |
| 7 | Cleaning Flow and Reconciliation | Sarah |
| 8 | Record Flow | Sarah |
| 9 | Object Model | Zeyad |
| 10 | Key Design Choices | Zeyad |
| 11 | Data Organization | Henrietta |
| 12 | Effectiveness: Cleaning Outcomes | Sarah |
| 13 | Financial Results | Bahareh |
| 14 | Spending Patterns | Henrietta |
| 15 | Budget vs Actual | Patrick |
| 16 | Efficiency: Runtime and Scaling | Henrietta |
| 17 | Key Findings | Bahareh |
| 18 | Limitations and Conclusion | Patrick |
| | Live demo | Zeyad |
| | Q&A | all |

---

## 1. Problem and dataset (slides 2 to 4)

What the data is and what is wrong with it. Lead with real numbers: 15,836
rows, 804 exact duplicates, 163 transaction IDs shared by 328 rows, many
spellings of each category, several date formats, and 170 rows with a blank
amount.

## 2. Pipeline (slides 5 to 8)

The flow from raw CSV to transaction objects, through `run()`. The two
decisions worth the time:

- Duplicate detection on raw rows **before** cleaning, so copies are compared
  exactly as written
- Ambiguous dates decided by the separator, never by the numbers

The reconciliation: 15,836 = 14,862 kept + 170 skipped + 804 duplicates.

## 3. Design and OOP (slides 9 to 11)

`ExpenseTransaction` and `IncomeTransaction` inherit from `Transaction` and
override `get_signed_amount()`. `CashAccount`, `BankAccount` and
`UnknownAccount` inherit from `Account` and group transactions by payment
mode; they are not real bank accounts, because the data has no account IDs.
Private attributes are read through getters, and the amount setter rejects
bad values. `Budget` compares monthly spending with a limit.

## 4. Findings (slides 12 to 17)

Total income 134,553,045; total expenses 53,348,034; net balance 81,205,011.
Top five categories, the 999,999 expenses, monthly expenses in 2022, budget vs
actual for January 2022, and the runtime (median 423.1 ms for the full
pipeline).

## 5. Limitations (slide 18)

334 records have no usable date, so they are left out of monthly figures.
Some categories and payment modes stay Unknown or Uncategorized. Large
999,999 expenses dominate the totals. Account groups are payment methods, not
bank accounts. Timings come from one laptop.

## 6. Live demo

Run `python3 main.py`. Load the full dataset, then a date range, then show the
error log. Have a screen recording as a fallback.

## 7. Q&A

See [`qa_preparation.md`](qa_preparation.md).
