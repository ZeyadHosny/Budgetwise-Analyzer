# cleaning/amounts/testing

Patrick · domain reviewer Bahareh

## Required cases

- [ ] `5891` → `5891.0`, symbol `plain`
- [ ] `₹5891` → `5891.0`, symbol `₹`
- [ ] `$5863` → `5863.0`, symbol `$`
- [ ] **`Rs.5638` → `5638.0`, symbol `Rs.`** — not `0.5638`
- [ ] `6602 INR` → `6602.0`, symbol `INR` — suffix, not prefix
- [ ] `-5891` → `5891.0` — positive magnitude
- [ ] `₹-5891` → `5891.0`, symbol `₹`
- [ ] `999999999` → `(None, None, "sentinel_amount")`
- [ ] `100000000` → `sentinel_amount` — the boundary is inclusive
- [ ] `99999999` → parses fine — just below the boundary
- [ ] `""` → `(None, None, "missing_amount")`
- [ ] `abc` → `(None, None, "unrecognized_amount_format")`
- [ ] Never raises, for any input

The `Rs.` case and the two boundary cases are the ones that catch real bugs.

## Sanity check against the real data

After implementing, group the parsed values by symbol and take the median. All
five should land between about 5,600 and 6,600. If `Rs.` comes out near zero, the
period trap has you.

## Fixtures

`fixtures/amount_cases.csv` — one row per case above with its expected output.

## Run

```bash
python -m unittest discover
```

A run collecting 0 tests is not a pass.
