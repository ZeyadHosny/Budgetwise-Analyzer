# metrics/testing

Zeyad · domain reviewer Patrick

## Required cases

- [ ] Each counter increments independently
- [ ] `report()` returns all seven measurements
- [ ] `input = valid + skipped + duplicates` holds on a fixture
- [ ] The `timed` context manager records a positive duration
- [ ] Timing survives an exception raised inside the block
- [ ] Nested phases do not double-count
- [ ] A run with zero rows reports zeros, not a division error
- [ ] Corrections to two fields on one row follow the agreed rule

## Run

```bash
python -m unittest discover
```

Check how many tests ran, not just that it said `OK`.
