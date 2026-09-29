# interface/export/implementation

Sarah · `P3.4` · domain reviewer Bahareh

## Write these

```python
export_cleaned(transactions, dataset: str, when=None) -> Path
export_summary(summary: dict, dataset: str, when=None) -> Path
```

Both return the path written, so the menu can tell the user where it went.

## Naming is fixed

```
output/cleaned/cleaned_<dataset>_<YYYY-MM-DD>.csv
output/summaries/summary_<dataset>_<YYYY-MM-DD>.json
```

Create the folders if they do not exist. `Path.mkdir(parents=True, exist_ok=True)`.

## Always record which dataset

Two CSVs are in `data/raw/`, and until the team settles which is official both
may be run. An output that does not name its source cannot be interpreted later,
and §3 requires the dataset be identified. Put it in the JSON, and in the CSV
filename.

## Two file-writing traps

**Excel and the BOM.** Write CSV with `encoding="utf-8-sig"` and
`newline=""`. Without `newline=""` every row gets a blank line between it on
Windows; without the BOM, Excel mangles the `₹` symbol.

**JSON and non-serialisable types.** `datetime` and `Path` objects raise
`TypeError`. Convert to strings before dumping. Use `indent=2` so the file can
be read in a pull request.

## Do not

- Recalculate anything — you receive finished figures
- Overwrite `data/raw/` — that data is never modified
- Import pandas or numpy — violates §2
