# Q&A preparation

**2 marks.** Owner: Patrick (`P5.3`)

Questions come from the audience and are not routed to whoever wrote that
module. Every member should be able to give each answer below. Figures are
from the dirty dataset (decision D01) and match the report.

## On cleaning

**How did you decide `07/08/2023` is July 8th and not August 7th?**
The separator decides, never the numbers. §4.5 says slash dates are month
first and hyphen dates with a two-digit year are day first. We added one rule
of our own: hyphen dates with a four-digit year are also day first (D10). A
date that does not exist, like 31 February, is rejected and logged, never
swapped around.

**Why detect duplicates before cleaning rather than after?**
After cleaning, two different raw rows could end up looking the same, for
example `food` and `Food`. Comparing the raw rows means we only remove true
copies. We make a tuple of all nine raw values and check it against a set.

**You have 163 repeated transaction IDs. Why keep them?**
The rows have the same ID but different values, so they may be separate real
transactions. Deleting them would lose data. We keep all 328 rows and flag
them. Only the 804 exact copies are removed.

**How do you know the counts are right?**
Every row ends in exactly one place: 15,836 = 14,862 kept + 170 skipped + 804
duplicates. Nothing is lost silently, and every skip or change is in
`errors.log` with a reason.

**What happens to a row with no date?**
It is kept with no date, logged, and still counts in overall and category
totals. It is left out of monthly figures. 334 rows are like this: 322 blank
and 12 invalid.

**How do you know your category mapping is complete?**
The mapping is closed: 14 standard names (D04). Anything not in it becomes
Uncategorized and is logged, so nothing is guessed. 3,718 values were mapped
and 251 became Uncategorized (154 blank, 97 unrecognized).

## On design

**Why are your Account classes not real bank accounts?**
The data has payment modes but no account IDs or balances. So `CashAccount`,
`BankAccount` and `UnknownAccount` group transactions by payment mode. That
uses information the data really has without inventing accounts.

**Where is encapsulation used, and what does it prevent?**
Every attribute is private and read through getters. The amount can only be
set through `set_amount()`, which rejects missing, non-numeric, non-finite
and negative values, so a bad amount can never get into an object.

**Why is the inheritance meaningful?**
An expense is a transaction and an income is a transaction. Each overrides
`get_signed_amount()`: expenses return a negative amount, income a positive
one. The same call gives the right answer for either type.

## On analysis

**How do you know the totals are right?**
Separate calculations over the cleaned CSV matched the object-based totals:
total expenses of 53,348,034 reconcile exactly.

**Why those five budget categories, and how were the limits chosen?**
They are the five highest-spending expense categories, 89.6% of all expenses.
Each limit is the median monthly spending from 2019 to 2021, rounded up to the
next 500 (D06). The median is not pulled up by one expensive month.

**Why are the category totals and the monthly totals different?**
Monthly totals leave out the 334 undated records. Category totals include
them. The difference in expenses is 243,341.

## On the data

**Why not convert the currencies?**
§4.5 says not to. We remove the label, record which one it was, and use the
number as it is.

**The top five expenses are all 999,999. Is that real?**
They are under the 100,000,000 limit, so the rules say they stay. There are
43 of them, 80.6% of expenses. The report names this as a limitation.

**You had two dataset files. Which did you use, and why?**
The dirty file, because it is the harder test of the cleaning (D01). The same
code cleans both, and the finance file reconciles too: 15,900 = 14,651 +
349 + 900.

## On process

**What broke when you first integrated the modules?**
The pipeline was written against method names from the plan, and the real
model classes used different ones (`add_transaction()` and getters), so
`run()` failed until the pipeline was updated. The tests caught it.

**What would you do differently?**
Agree the shared interfaces and reason codes earlier, before modules were
built in parallel.
