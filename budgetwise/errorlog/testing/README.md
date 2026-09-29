# errorlog/testing

Sarah · domain reviewer Henrieta

## Required cases

- [ ] A recorded entry appears in the file with all four fields
- [ ] The log folder is created if it does not exist
- [ ] `counts()` totals correctly across several reasons
- [ ] Reading back returns every line written
- [ ] A raw value containing a comma or newline does not break the format
- [ ] Two cleaners writing to the same log do not interleave a single line

## Run

```bash
python -m unittest discover
```

A run collecting 0 tests is not a pass.
