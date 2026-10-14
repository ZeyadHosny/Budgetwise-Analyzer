"""
counters.py  -  the section 5 run measurements           (task P3.8, Henrietta)

Section 5 names seven measurements the report must contain:

    1. number of input records
    2. number of valid records
    3. number of corrected records
    4. number of invalid / skipped records
    5. number of duplicates detected
    6. number of categories normalized
    7. execution time for loading, cleaning and analysis

RunMetrics holds all seven. It can be filled one event at a time with the
record_* methods, or in one step from the cleaning pipeline's result with
RunMetrics.from_pipeline(), which copies the counts the pipeline already
made during its single pass instead of counting a second time.

Definitions follow the pipeline (budgetwise/pipeline, P2.10):
  * duplicates  exact copies of an earlier raw row, removed before cleaning
  * skipped     rows that could not be cleaned, e.g. no usable amount
  * valid       every other row; one cleaned record each
  * corrected   valid rows where at least one value was changed to its
                standard form. A row is counted once, however many fields
                changed.
  * so input = valid + skipped + duplicates must always hold.

Standard library only.
"""

# The three phases section 5 asks to be timed separately.
PHASES = ("load", "clean", "analysis")

# Labels used in the printed report, in the order section 5 lists them.
COUNT_LABELS = (
    ("input", "Input records"),
    ("valid", "Valid records"),
    ("corrected", "Corrected records"),
    ("skipped", "Invalid / skipped records"),
    ("duplicates", "Duplicates detected"),
    ("categories_normalized", "Categories normalized"),
)
PHASE_LABELS = (("load", "Loading"), ("clean", "Cleaning"), ("analysis", "Analysis"))


class RunMetrics:
    """
    Description:
    - The counts and timings of one program run, for the report (section 5).

    Attributes:
        __counts (dict): PRIVATE. Count name -> int.
        __timings (dict): PRIVATE. Phase name -> seconds (float).

    Methods:
        record_input, record_valid, record_corrected, record_skipped,
            record_duplicate, record_category_normalized: add to a count.
        add_time: add seconds to a phase.
        get_count, get_time, total_time: read values.
        reconciles: whether input = valid + skipped + duplicates.
        report: all seven measurements as a dictionary.
        format_report: the same as aligned text, for the menu or report.
        from_pipeline: CLASS METHOD. Build from a clean_file()/run() result.
    """

    # Constructor
    def __init__(self):
        """
        Description:
        - Start every count at zero and every phase at zero seconds.

        Input arguments:
           None

        Return:
            None
        """
        self.__counts = {key: 0 for key, _ in COUNT_LABELS}
        self.__timings = {phase: 0.0 for phase in PHASES}

    # Methods that add to the counts
    def record_input(self, count=1):
        """Add `count` raw rows read. Return: None."""
        self.__add("input", count)

    def record_valid(self, count=1):
        """Add `count` rows kept as cleaned records. Return: None."""
        self.__add("valid", count)

    def record_corrected(self, count=1):
        """Add `count` valid rows that had a value standardized. Return: None."""
        self.__add("corrected", count)

    def record_skipped(self, count=1):
        """Add `count` rows that could not be cleaned. Return: None."""
        self.__add("skipped", count)

    def record_duplicate(self, count=1):
        """Add `count` exact duplicate raw rows. Return: None."""
        self.__add("duplicates", count)

    def record_category_normalized(self, count=1):
        """Add `count` rows whose category was changed. Return: None."""
        self.__add("categories_normalized", count)

    def __add(self, key, count):
        """
        Description:
        - PRIVATE. Add to one count, refusing negative or non-whole numbers,
          so a count can never go down or become fractional.

        Input arguments:
           key (str): the count name.
           count (int): how many to add.

        Return:
            None (raises ValueError for a bad count)
        """
        if isinstance(count, bool) or not isinstance(count, int) or count < 0:
            raise ValueError(f"count must be a whole number of 0 or more, not {count!r}")
        self.__counts[key] += count

    # Method that adds to a timing
    def add_time(self, phase, seconds):
        """
        Description:
        - Add seconds to one of the three timed phases.

        Input arguments:
           phase (str): 'load', 'clean' or 'analysis'.
           seconds (float): elapsed time, 0 or more.

        Return:
            None (raises ValueError for an unknown phase or negative time)
        """
        if phase not in self.__timings:
            raise ValueError(f"phase must be one of {PHASES}, not {phase!r}")
        if seconds < 0:
            raise ValueError(f"seconds cannot be negative, not {seconds!r}")
        self.__timings[phase] += float(seconds)

    # Methods that read values
    def get_count(self, key):
        """Return one count, e.g. get_count('valid') -> 14651."""
        return self.__counts[key]

    def get_time(self, phase):
        """Return the seconds recorded for one phase."""
        return self.__timings[phase]

    def total_time(self):
        """Return the seconds across all three phases."""
        return sum(self.__timings.values())

    def reconciles(self):
        """
        Description:
        - Whether every input row is accounted for exactly once:
          input = valid + skipped + duplicates.

        Input arguments:
           None

        Return:
            bool: True when the counts add up.
        """
        counts = self.__counts
        return counts["input"] == counts["valid"] + counts["skipped"] + counts["duplicates"]

    def report(self):
        """
        Description:
        - All seven section 5 measurements as one dictionary, ready for the
          report, the menu or a JSON export.

        Input arguments:
           None

        Return:
            dict: {'counts': {...}, 'timings_seconds': {..., 'total': x},
                   'reconciles': bool}
        """
        timings = {phase: round(seconds, 4) for phase, seconds in self.__timings.items()}
        timings["total"] = round(self.total_time(), 4)
        return {
            "counts": dict(self.__counts),
            "timings_seconds": timings,
            "reconciles": self.reconciles(),
        }

    def format_report(self):
        """
        Description:
        - The seven measurements as aligned text. Returns a string; the
          caller decides whether to print it.

        Input arguments:
           None

        Return:
            str: e.g.
                Input records                15,900
                ...
                Loading                    0.0440 s
        """
        label_width = max(len(label) for _, label in COUNT_LABELS)
        lines = [f"{label:<{label_width}}  {self.__counts[key]:>10,}"
                 for key, label in COUNT_LABELS]
        lines.append("")
        for phase, label in PHASE_LABELS:
            lines.append(f"{label:<{label_width}}  {self.__timings[phase]:>8.4f} s")
        lines.append(f"{'Total':<{label_width}}  {self.total_time():>8.4f} s")
        if not self.reconciles():
            lines.append("")
            lines.append("WARNING: input != valid + skipped + duplicates")
        return "\n".join(lines)

    # Class method building the metrics from the pipeline's result
    @classmethod
    def from_pipeline(cls, result):
        """
        Description:
        - Build RunMetrics from the dictionary budgetwise.pipeline.clean_file()
          or run() returns. Copies result['counts'] and result['timings'],
          which the pipeline measured during its single pass.
        - The analysis phase is not timed by the pipeline; add it afterwards
          with timed(metrics, 'analysis').

        Input arguments:
           result (dict): the pipeline result.

        Return:
            RunMetrics: a new object holding the pipeline's counts and times.
        """
        metrics = cls()
        counts = result.get("counts", {})
        for key, _ in COUNT_LABELS:
            metrics.__add(key, int(counts.get(key, 0)))
        for phase, seconds in result.get("timings", {}).items():
            if phase in PHASES:
                metrics.add_time(phase, seconds)
        return metrics
