# Report outline

The structure the final report follows, mapped to §5's required content.
All figures come from the dirty dataset (decision D01).

Target: **10 pages maximum**, excluding references and peer assessment.
Suggested split is indicative, not a rule.

---

## 1. Introduction and key problems studied  ~1 page

What the BudgetWise dataset is, and what makes it hard: 15,836 rows with
several date formats, currency labels, many spellings of each category, 804
exact duplicates alongside 163 repeated transaction IDs, and 170 blank
amounts.

*Evidence: `evidence/` profiling files from `P1.1`–`P1.4`.*

## 2. Solutions proposed  ~2 pages

Theory, algorithms, and systems. The cleaning rules and why each is correct , 
particularly the ones where a plausible alternative is wrong:

- Why duplicate detection must precede normalization
- Why the separator, not the values, resolves ambiguous dates
- Why currency symbols are stripped rather than converted

*Evidence: `ambiguity_decision.md`, `mapping_rationale.md`, `duplicate_profile.md`.*

## 3. Implementation details  ~2 pages

Datasets used and their provenance. Python version, standard library only, and
why no pandas or NumPy. Module structure and what each is responsible for.

*Evidence: `data/README.md`, `budgetwise/README.md`, `data_structure_choices.md`.*

## 4. Design flow diagram  ~1 page

**Required by §5**: "based on important subroutines". The pipeline from raw CSV
through the four cleaners to transaction objects, analysis, and output. Show the
menu paths too.

*Evidence: `class_diagram.md`, `menu_flow.md`.*

## 5. Key experimental results  ~2 pages

### Effectiveness

Input records · valid · corrected · invalid/skipped · duplicates detected ·
categories normalized. **Measured, not estimated.**

### Efficiency

Execution time for loading, cleaning, and analysis, with the machine stated.

### Findings

Total income, total expenses, net balance, monthly expenses, top 5 categories,
top 5 largest expenses, budget vs actual. Include the text bar chart.

Say what the monthly figures show over time: §2 asks for **trends** and §4.4
never defines one, so this is where that requirement is met.

*Evidence: `measured_results.md`, `manual_verification.md`, `chart_samples.md`,
`budget_justification.md`.*

## 6. Limitations and future work  ~1 page

Honest ones. 334 records have no usable date, so they are left out of monthly
figures. Some categories and payment modes stay Uncategorized or Unknown. The
data has no account IDs, so the `Account` classes group transactions by
payment method rather than representing bank accounts. Currency labels are
removed without conversion, and large 999,999 expenses dominate the totals.
The dataset has no merchant column, so §4.2's merchant sets cannot be
produced (D07).

Naming a limitation you chose deliberately, with the reasoning, is stronger than
claiming full coverage.

*Evidence: `design_justification.md`, `interface_conflicts.md`.*

## 7. Conclusion  ~0.5 page

**Required by §5**, and easy to forget: it appears only at the very end of the
deliverables paragraph.

## References

Does not count toward the 10 pages.

## Peer assessment

Does not count toward the 10 pages. Goes at the end, signed by all members.
See [`../peer_assessment.md`](../peer_assessment.md).
