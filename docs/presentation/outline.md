# Presentation outline

20 minutes total, **including Q&A**. Budget roughly 15 speaking, 5 for questions.

## Speaking split — decide and record this

Even participation is graded (§7). Fill this in before the first rehearsal.

| Section | Minutes | Speaker |
|---|---|---|
| Problem and dataset | 3 | |
| Cleaning pipeline | 4 | |
| Design and OOP choices | 3 | |
| Findings and budget analysis | 3 | |
| Limitations and conclusion | 2 | |
| **Live demo** | 2 | |
| Q&A | 5 | all |

Three minutes each is the fair split for five people across 15 minutes. Adjust,
but do not let one person carry it — the criterion is explicit.

---

## 1. Problem and dataset  ~3 min

What the data is, and what is wrong with it. Lead with the concrete numbers:
15,900 rows, 900 exact duplicates, 47 spellings of about 12 categories, five
date formats, five currency labels, 80 sentinel amounts.

Real numbers hold an audience. "The data was messy" does not.

## 2. Cleaning pipeline  ~4 min

The flow from raw CSV to transaction objects. Spend the time on the two
decisions that are genuinely interesting:

- Duplicate detection **before** normalization, and what breaks otherwise
- Ambiguous dates resolved by separator, not by value

## 3. Design and OOP choices  ~3 min

The class structure, the inheritance relationship, and how encapsulation is
enforced. Explain the departure from the suggested `Account` hierarchy — the
data has no account types, and inventing them is what the assignment warns
against.

A deliberate, explained departure is stronger than silent compliance.

## 4. Findings and budget analysis  ~3 min

Income, expenses, net balance, top five categories, top five expenses, budget vs
actual. Show the text bar chart — it is the one visual the audience can read
instantly.

## 5. Limitations and conclusion  ~2 min

No merchant column, so §4.2's merchant sets are not possible. Currency labels
are cosmetic. What you would do with more time.

## 6. Live demo  ~2 min

Run the menu. Load a date range. Show the error log.

**Rehearse this on the actual machine that will be used.** Have a screen
recording as a fallback — a demo that fails live costs more than one that is
merely watched.

## 7. Q&A  ~5 min

See [`qa_preparation.md`](qa_preparation.md).
