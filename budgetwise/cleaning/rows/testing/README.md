# cleaning/rows/testing

Sarah · domain reviewer Henrieta

## Required cases

- [ ] Two identical rows → second is a duplicate
- [ ] Same `transaction_id`, different `amount` → **not** a duplicate
- [ ] Same `transaction_id`, different `date` → **not** a duplicate
- [ ] Rows differing only by `FOOD` vs `Food` → **not** duplicates
- [ ] First occurrence of a row is never itself a duplicate
- [ ] Row missing `amount` → rejected
- [ ] Row missing `transaction_type` → rejected
- [ ] Row missing only `date` → **kept**
- [ ] Row missing only `category` → **kept**
- [ ] `"nan"` in `location` treated as blank
- [ ] Full dataset yields exactly **900** duplicates

That last one is the real check. The main dataset is known to hold 900 exact
duplicates and 1,900 repeated ids. A count of 1,900 means the key is wrong.

## Run

```bash
python -m unittest discover
```

A run collecting 0 tests is not a pass.
