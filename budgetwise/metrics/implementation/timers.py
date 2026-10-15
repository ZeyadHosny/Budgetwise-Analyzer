"""Time one phase of a run."""

import time
from contextlib import contextmanager


@contextmanager
def timed(metrics, phase):
    """
    Time the code inside the `with` block and add the seconds to `metrics`.

    The time is recorded even if the block raises an error.

    Example:
        with timed(metrics, "analysis"):
            totals = totals_by_category(records)
    """
    started = time.perf_counter()
    try:
        yield
    finally:
        metrics.add_time(phase, time.perf_counter() - started)
