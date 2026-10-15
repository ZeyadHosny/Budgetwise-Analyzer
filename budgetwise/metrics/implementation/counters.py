"""Counts and timings for one run of the program (section 5)."""

PHASES = ("load", "clean", "analysis")

COUNT_LABELS = (
    ("input", "Input records"),
    ("valid", "Valid records"),
    ("corrected", "Corrected records"),
    ("skipped", "Invalid / skipped records"),
    ("duplicates", "Duplicates detected"),
    ("categories_normalized", "Categories normalized"),
)

PHASE_LABELS = (("load", "Loading"), ("clean", "Cleaning"),
                ("analysis", "Analysis"))


class RunMetrics:
    """
    Stores the six counts and three timings required by section 5.

    Fill it one event at a time with the record_* methods, or all at once
    from the cleaning pipeline's result with RunMetrics.from_pipeline().
    """

    def __init__(self):
        self.__counts = {key: 0 for key, _ in COUNT_LABELS}
        self.__timings = {phase: 0.0 for phase in PHASES}

    def record_input(self, count=1):
        """Add rows read from the file."""
        self.__add("input", count)

    def record_valid(self, count=1):
        """Add rows kept after cleaning."""
        self.__add("valid", count)

    def record_corrected(self, count=1):
        """Add kept rows that had at least one value standardized."""
        self.__add("corrected", count)

    def record_skipped(self, count=1):
        """Add rows that could not be cleaned."""
        self.__add("skipped", count)

    def record_duplicate(self, count=1):
        """Add exact duplicate rows."""
        self.__add("duplicates", count)

    def record_category_normalized(self, count=1):
        """Add rows whose category was changed."""
        self.__add("categories_normalized", count)

    def __add(self, key, count):
        """Add to a count. Only whole numbers of 0 or more are accepted."""
        if isinstance(count, bool) or not isinstance(count, int) or count < 0:
            raise ValueError(
                f"count must be a whole number of 0 or more, not {count!r}")
        self.__counts[key] += count

    def add_time(self, phase, seconds):
        """Add seconds to 'load', 'clean' or 'analysis'."""
        if phase not in self.__timings:
            raise ValueError(f"phase must be one of {PHASES}, not {phase!r}")
        if seconds < 0:
            raise ValueError(f"seconds cannot be negative, not {seconds!r}")
        self.__timings[phase] += float(seconds)

    def get_count(self, key):
        """Return one count, for example get_count('valid')."""
        return self.__counts[key]

    def get_time(self, phase):
        """Return the seconds recorded for one phase."""
        return self.__timings[phase]

    def total_time(self):
        """Return the seconds across all phases."""
        return sum(self.__timings.values())

    def reconciles(self):
        """Return True if input = valid + skipped + duplicates."""
        counts = self.__counts
        return counts["input"] == counts["valid"] + counts["skipped"] + counts["duplicates"]

    def report(self):
        """Return all measurements as a dictionary."""
        timings = {phase: round(seconds, 4)
                   for phase, seconds in self.__timings.items()}
        timings["total"] = round(self.total_time(), 4)
        return {
            "counts": dict(self.__counts),
            "timings_seconds": timings,
            "reconciles": self.reconciles(),
        }

    def format_report(self):
        """Return all measurements as aligned text."""
        width = max(len(label) for _, label in COUNT_LABELS)
        lines = [
            f"{label:<{width}}  {self.__counts[key]:>10,}" for key, label in COUNT_LABELS]
        lines.append("")
        for phase, label in PHASE_LABELS:
            lines.append(f"{label:<{width}}  {self.__timings[phase]:>8.4f} s")
        lines.append(f"{'Total':<{width}}  {self.total_time():>8.4f} s")
        if not self.reconciles():
            lines.append("")
            lines.append("WARNING: input != valid + skipped + duplicates")
        return "\n".join(lines)

    @classmethod
    def from_pipeline(cls, result):
        """
        Build from the dictionary returned by clean_file() or run().

        Copies the pipeline's counts and its load and clean times. Add the
        analysis time afterwards with timed(metrics, "analysis").
        """
        metrics = cls()
        counts = result.get("counts", {})
        for key, _ in COUNT_LABELS:
            metrics.__add(key, int(counts.get(key, 0)))
        for phase, seconds in result.get("timings", {}).items():
            if phase in PHASES:
                metrics.add_time(phase, seconds)
        return metrics
