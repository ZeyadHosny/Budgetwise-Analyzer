# interface/export/testing

Sarah · domain reviewer Bahareh

## Required cases

- [ ] CSV is written with the correct dated filename
- [ ] JSON is written with the correct dated filename
- [ ] Missing output folders are created
- [ ] The exported CSV reads back with `csv.DictReader` and matches
- [ ] Row count in the CSV equals the transactions exported
- [ ] `original_currency` survives the round trip
- [ ] The JSON names the source dataset
- [ ] The JSON parses with `json.load`
- [ ] A `₹` in the data survives and reopens correctly
- [ ] Empty input writes a header-only file, not a crash

Write to a temporary directory in tests — `tempfile.TemporaryDirectory` is
standard library. Never write into the real `output/` from a test.

## Run

```bash
python -m unittest discover
```

Check how many tests ran, not just that it said `OK`.
