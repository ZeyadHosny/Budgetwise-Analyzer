# pipeline/supplementary

| File | Purpose | Feeds |
|---|---|---|
| `pipeline_evidence.md` | Counts on the full dataset, repeated-ID and payment-mode breakdowns, sample log entries, test results, and the open items owned by other features | report: results and implementation details; `G2` |

The evidence file states the command, dataset and populations behind each
figure. Fill in the Python version, branch and commit after running the tests
on the real branch.

`G2` is the first moment five people's code runs together. What went wrong
when the modules first met is recorded under "Open items owned by others" in
the evidence file. It is the most honest material the report will have, and
"limitations and future work" is a required section.

Still to write, if the team wants them as separate files:

| File | Purpose |
|---|---|
| `integration_notes.md` | What broke when the modules first met, and how it was fixed |
| `interface_conflicts.md` | Where two modules disagreed on a type or name, and what was agreed |
