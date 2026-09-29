# Report outline

A skeleton mapped to §5's required content. Fill each section; delete nothing.

Target: **10 pages maximum**, excluding references and peer assessment.
Suggested split is indicative, not a rule.

---

## 1. Introduction and key problems studied  ~1 page

What the BudgetWise dataset is, and what makes it hard. The concrete problems:
multi-format dates, cosmetic currency labels, 47 category spellings for ~12
categories, exact duplicates alongside deliberately repeated transaction ids,
sentinel amounts, and roughly 30% of records carrying some defect.

*Evidence: `evidence/` profiling files from `P1.1`–`P1.4`.*

## 2. Solutions proposed  ~2 pages

Theory, algorithms, and systems. The cleaning rules and why each is correct —
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

**Required by §5** — "based on important subroutines". The pipeline from raw CSV
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

Say what the monthly figures show over time — §2 asks for **trends** and §4.4
never defines one, so this is where that requirement is met.

*Evidence: `measured_results.md`, `manual_verification.md`, `chart_samples.md`,
`budget_justification.md`.*

## 6. Limitations and future work  ~1 page

Honest ones. The dataset has no merchant column, so §4.2's merchant sets cannot
be produced. The data has no account types, so the suggested `Account` hierarchy
was not built. Currency labels are cosmetic and cannot be interpreted as real
currencies.

Naming a limitation you chose deliberately, with the reasoning, is stronger than
claiming full coverage.

*Evidence: `design_justification.md`, `interface_conflicts.md`.*

## 7. Conclusion  ~0.5 page

**Required by §5**, and easy to forget — it appears only at the very end of the
deliverables paragraph.

## References

Does not count toward the 10 pages.

## Peer assessment

Does not count toward the 10 pages. Goes at the end, signed by all members.
See [`../peer_assessment.md`](../peer_assessment.md).
