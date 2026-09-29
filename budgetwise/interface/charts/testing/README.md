# interface/charts/testing

Sarah · domain reviewer Bahareh

## Required cases

- [ ] The largest value gets exactly `width` stars
- [ ] A half-size value gets about half the stars
- [ ] A tiny non-zero value still gets at least one star
- [ ] A zero value gets no stars but still shows its label
- [ ] An empty dict returns an empty string, not an error
- [ ] All values equal produces equal bars, no division error
- [ ] Tuple month keys render as `2023-07`
- [ ] Every line is the same length — alignment holds

Assert on the returned string. That is the advantage of returning rather than
printing.

## Run

```bash
python -m unittest discover
```

Check how many tests ran, not just that it said `OK`.
