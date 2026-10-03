import os

class ErrorLog:
    def __init__(self, filename="output/logs/errors.log"):
        self.filename = filename

        # Create output/logs if it doesn't exist
        os.makedirs(os.path.dirname(filename), exist_ok=True)

        # Open the file once
        self.file = open(
            filename,
            "a",
            encoding="utf-8"
        )

        self._counts = {}

    def record(self, line, field, reason, raw):
        """Record one error event."""

        entry = (
            f"line={line} "
            f"field={field} "
            f"reason={reason} "
            f"raw={raw!r}\n"
        )

        self.file.write(entry)
        self.file.flush()

        # Keep counts in memory
        self._counts[reason] = self._counts.get(reason, 0) + 1

    def counts(self):
        """Return the number of occurrences of each reason."""
        return self._counts.copy()

    def read(self):
        """Return the lines currently in the error log."""
        self.file.flush()

        with open(self.filename, "r", encoding="utf-8") as file:
            return file.readlines()

    def close(self):
        """Close the log file."""
        self.file.close()