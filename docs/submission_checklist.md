# Submission checklist

| | |
|---|---|
| **Owner** | Bahareh (`G5`, `DUE`) · Sarah (`P6.2`) |
| **Deadline** | **Oct 19, 2026, 11:59 PM EST** |
| **Late work** | Not accepted |

Target an internal deadline earlier than Oct 19. Submitting on the day leaves no
room for a failed upload.

---

## G4 — freeze the results  · Oct 12 · Zeyad

- [ ] Fresh run from a clean clone, following `README.md` only
- [ ] Outputs match what the report will quote
- [ ] Final `cleaned_*.csv`, `summary_*.json`, and `errors.log` committed with `git add -f`
- [ ] Timings and counts recorded in `metrics/supplementary/measured_results.md`
- [ ] **No new features after this point**, except critical fixes

## G5 — final review · Oct 16 · Bahareh

### Report format — verified, not assumed

- [ ] Within **10 pages**, excluding references and peer assessment
- [ ] **Single column**
- [ ] **Arial**, **11pt**
- [ ] Exported as **PDF**

### Report content — all §5 sections present

- [ ] Key problems studied
- [ ] Solutions proposed — theory, algorithms, systems
- [ ] Implementation details — datasets, language, tools, code summary
- [ ] Design flow diagram based on important subroutines
- [ ] Key experimental results — all seven measurements
- [ ] Limitations and future work
- [ ] **Conclusion** — easy to forget
- [ ] GitHub link present and correct

### Peer assessment

- [ ] At the end of the report
- [ ] Every member named, described, and given a percentage
- [ ] Percentages total 100%
- [ ] **Signed by all five members**

### Repository

- [ ] Code present and runnable from a clean clone
- [ ] Input datasets present, or linked with download instructions
- [ ] Output datasets present
- [ ] `README.md` explains how to run **and how to interpret the outputs**
- [ ] No pandas or NumPy anywhere in the core pipeline — **grep and confirm**
- [ ] All five members have commits in the history

### Presentation

- [ ] Under 20 minutes including Q&A, timed twice
- [ ] Speaking time distributed evenly
- [ ] Demo rehearsed on the presentation machine
- [ ] Fallback recording saved

## P6.2 — final regression · Oct 17–18 · Sarah

- [ ] Only critical fixes applied, nothing new
- [ ] Full test suite passes — **check the count, not just `OK`**
- [ ] Full dataset run completes without error
- [ ] Final outputs archived
- [ ] Release tagged

## DUE — Oct 19 · Bahareh

- [ ] **Confirm who submits** and that they have Canvas access
- [ ] Verify the deadline and timezone in Canvas directly
- [ ] Report PDF uploaded
- [ ] GitHub link works when opened logged out
- [ ] Submission confirmation saved as evidence
- [ ] Present in class

---

## The cheapest marks to lose

Every one of these is avoidable in under five minutes:

| Risk | Check |
|---|---|
| Report is 11 pages | Count before `G5` |
| Wrong font or size | Check the exported PDF, not the editor |
| Conclusion missing | It is listed last in §5 and read past easily |
| Unsigned peer assessment | Collect signatures days ahead |
| GitHub link private | Open it in a logged-out browser |
| A stray `import pandas` | `grep -rn "import pandas\|import numpy" budgetwise/` |
