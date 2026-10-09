"""Runs raw rows through the cleaners and builds the cleaned dataset."""

# Contract — uncomment once implementation/pipeline.py exists.
# from .implementation.pipeline import run, LoadResult

from .implementation.cleaning_pipeline import (
    run_cleaning,
    CleaningResult,
)
