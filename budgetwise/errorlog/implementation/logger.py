"""Append source-traceable cleaning issues to a text log.

Each entry contains the source-line identifier, field name, reason code,
and repr() of the original value.

Issue counts are maintained in memory for each ErrorLog instance.
Existing entries in an earlier log file are not included in those counts.
"""

import os


class ErrorLog:
    """Write cleaning issue events and track counts by reason code.

    Attributes:
        filename: Destination log path.
        file: Open text stream used to append log entries.
        _counts: In-memory event counts grouped by reason code.

    Notes:
        The pipeline calls record() using issue metadata returned by
        cleaners. This class does not clean or validate transactions.

        Counts represent log events, not unique affected rows. One row
        may produce several events.

        The caller is responsible for closing the logger.
    """

    def __init__(self, filename="output/logs/errors.log"):
        """Create the parent directory and open the log in append mode.

        Args:
            filename: Log destination. Defaults to
                "output/logs/errors.log".

        Side Effects:
            Creates the parent directory if it does not exist.
            Opens or creates the log file without removing existing text.

        Raises:
            OSError: If directory creation or file opening fails.

        Notes:
            Counts start empty for every new instance.
            This implementation requires a nonempty parent-directory
            component; a bare filename such as "errors.log" fails during
            directory creation.
        """
        self.filename = filename

        # Create output/logs if it doesn't exist.
        os.makedirs(os.path.dirname(filename), exist_ok=True)

        # Open the file once.
        self.file = open(
            filename,
            "a",
            encoding="utf-8"
        )

        self._counts = {}

    def record(self, line, field, reason, raw):
        """Record one error event.

        Args:
            line: Source-line identifier supplied by the pipeline.
            field: Name of the affected field, or "row" for row issues.
            reason: Hashable reason code used as the event-count key.
            raw: Original value or row context to include in the entry.

        Returns:
            None.

        Side Effects:
            Appends an entry, flushes the stream, and increments the
            in-memory count for the reason.

        Notes:
            repr(raw) preserves a textual representation of values,
            including whitespace, currency labels, and None.

            Inputs are not validated. File-operation errors propagate.
            The count is incremented only after write() and flush()
            complete successfully.
        """
        entry = (
            f"line={line} "
            f"field={field} "
            f"reason={reason} "
            f"raw={raw!r}\n"
        )

        self.file.write(entry)
        self.file.flush()

        # Keep counts in memory.
        self._counts[reason] = self._counts.get(reason, 0) + 1

    def counts(self):
        """Return the number of occurrences of each reason.

        Returns:
            A shallow copy of this instance's reason-to-count dictionary.

        Notes:
            Changing the returned dictionary does not change _counts.
            Counts exclude entries written by earlier logger instances.
        """
        return self._counts.copy()

    def read(self):
        """Return the lines currently in the error log.

        Returns:
            A list of text lines, including their newline characters,
            from the complete log file.

        Side Effects:
            Flushes the append stream before opening a separate reader.

        Notes:
            Includes existing entries from previous runs, whereas
            counts() reports only this instance's events.
            Requires the append stream to remain open.
            File-access and decoding errors propagate to the caller.
        """
        self.file.flush()

        with open(self.filename, "r", encoding="utf-8") as file:
            return file.readlines()

    def close(self):
        """Close the log file.

        Returns:
            None.

        Notes:
            Closing flushes buffered output and releases the file.
            Calling close() again on an already closed stream is allowed.
            Subsequent record() or read() calls fail because they use
            the closed append stream.
        """
        self.file.close()
