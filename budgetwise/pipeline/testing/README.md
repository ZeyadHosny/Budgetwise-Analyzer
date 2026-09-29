# pipeline/testing

Sarah with Zeyad · reviewed by all team

These are the tests `G2` is judged on.

## Required cases

- [ ] Full dataset runs end to end with no exception
- [ ] `counts["input"]` equals 15,900 for the main dataset
- [ ] `counts["duplicates"]` equals 900 for the main dataset
- [ ] Duplicate detection sees raw values — a file with `FOOD` and `Food` on
      otherwise-identical rows yields **two** transactions, not one
- [ ] A row with an unparseable date still counts toward category totals
- [ ] A row with a `999999999` amount is excluded and logged
- [ ] Every skipped row has a matching `errors.log` entry
- [ ] Date-range and category filters return the expected subset

## Fixtures

`fixtures/mini_dataset.csv` — about twenty rows, hand-built to contain one of
every problem: a duplicate pair, a case-variant pair that is *not* a duplicate, a
blank date, a blank category, a `999999999` amount, a `Rs.` amount, and a clean
row. Small enough to verify every expected number by hand.

## Run

```bash
python -m unittest discover
```

A run collecting 0 tests is not a pass.
