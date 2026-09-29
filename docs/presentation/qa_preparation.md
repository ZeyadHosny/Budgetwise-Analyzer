# Q&A preparation

**2 marks.** Owner: Patrick (`P5.3`)

Questions come from the audience and are not routed to whoever wrote that
module. `P5.3` requires that **every member can explain cleaning, OOP, analysis,
and outputs** — not only their own part.

## How to prepare

Each member writes the answer to one question about a module they **did not**
build, then the team reviews the answers together. This mirrors `G3`'s rule that
each member tests a module they did not own, and it surfaces gaps early.

## Likely questions

Draft an agreed answer to each.

### On cleaning

- How did you decide `07/08/2023` is July 8th and not August 7th?
- Why detect duplicates before normalizing rather than after?
- You have 1,900 repeated transaction ids but only removed 900 rows. Why?
- How do you know your category mapping is complete?
- What happens to a row with no date?

### On design

- Why no `Account` class hierarchy? The brief suggests one.
- Where is encapsulation actually used, and what does it prevent?
- Why is that inheritance relationship meaningful rather than decorative?

### On analysis

- How do you know the totals are right?
- Why those five budget categories, and how were the limits chosen?
- Why are the category totals and the monthly totals different?

### On the data

- Why not convert the currencies?
- Why is `999999999` excluded rather than treated as a large transaction?
- You had two dataset files. Which did you use, and why?

### On process

- What broke when you first integrated the modules?
- What would you do differently?

## Answers worth rehearsing

The strongest answers cite evidence: a number, a file, a measured result. "We
checked the medians across all five currency labels and they were all between
5,600 and 6,600, so the symbols are cosmetic" beats "the brief told us not to
convert."
