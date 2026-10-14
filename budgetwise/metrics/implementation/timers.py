"""
timers.py  -  time one phase of a run                    (task P3.8, Henrietta)

Section 5 asks for execution time for loading, cleaning and analysis,
measured, not estimated. timed() wraps a block of code and adds the elapsed
seconds to a RunMetrics object. Standard library only.
"""

import time
from contextlib import contextmanager


@contextmanager
def timed(metrics, phase):
    """
    Description:
    - Time the block inside the `with` statement with time.perf_counter()
      and add the seconds to metrics under `phase`.
    - The time is recorded even if the block raises, so a failed run still
      shows how long it took.

    Input arguments:
       metrics (RunMetrics): where the time is stored.
       phase (str): 'load', 'clean' or 'analysis'.

    Return:
        None (used as a context manager)

    Example:
        with timed(metrics, "analysis"):
            totals = totals_by_category(records)
    """
    started = time.perf_counter()
    try:
        yield
    finally:
        metrics.add_time(phase, time.perf_counter() - started)
