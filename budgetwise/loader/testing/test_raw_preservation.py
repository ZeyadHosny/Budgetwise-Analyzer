import csv
import os
import tempfile
import unittest

from budgetwise.loader import load_rows


HEADER = [
    "transaction_id",
    "user_id",
    "date",
    "transaction_type",
    "category",
    "amount",
    "payment_mode",
    "location",
    "notes"
]


class TestRawPreservation(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp_dir.cleanup)

        self.filename = os.path.join(
            self.temp_dir.name,
            "test_data.csv"
        )

    def write_csv(self, rows):
        with open(
            self.filename,
            "w",
            newline="",
            encoding="utf-8"
        ) as file:
            writer = csv.writer(file)
            writer.writerow(HEADER)
            writer.writerows(rows)

    def test_extra_values_are_preserved(self):
        values = [
            "T001", "U001", "2023-01-01", "Expense",
            "Food", "25", "Cash", "Pune", "Lunch",
            "extra value"
        ]
        self.write_csv([values])

        line, row = list(load_rows(self.filename))[0]

        self.assertEqual(line, 2)
        self.assertEqual(row[None], ["extra value"])

        for column, original in zip(HEADER, values[:9]):
            self.assertEqual(row[column], original)

    def test_raw_text_is_not_normalized(self):
        values = [
            "T001", "U001", "01/02/2023", "Expense",
            " Food ", "-$1,000", " Crd ", " Pune ",
            "  Lunch, with friends  "
        ]
        self.write_csv([values])

        _, row = list(load_rows(self.filename))[0]

        self.assertEqual(
            row,
            dict(zip(HEADER, values))
        )

    def test_empty_value_differs_from_absent_field(self):
        self.write_csv([
            ["T001", "U001", "2023-01-01", "Expense", ""],
            ["T002", "U001", "2023-01-01", "Expense"]
        ])

        rows = list(load_rows(self.filename))

        self.assertEqual(rows[0][1]["category"], "")
        self.assertIsNone(rows[1][1]["category"])

    def test_header_only_file_yields_no_rows(self):
        self.write_csv([])

        self.assertEqual(
            list(load_rows(self.filename)),
            []
        )

    def test_multiline_notes_keep_source_line_numbers(self):
        self.write_csv([
            [
                "T001", "U001", "2023-01-01", "Expense",
                "Food", "25", "Cash", "Pune",
                "First line\nSecond line"
            ],
            [
                "T002", "U001", "2023-01-02", "Expense",
                "Food", "30", "Cash", "Pune", "Lunch"
            ]
        ])

        rows = list(load_rows(self.filename))

        # DictReader reports the last physical line of each record.
        self.assertEqual(rows[0][0], 3)
        self.assertEqual(rows[1][0], 4)
        self.assertEqual(
            rows[0][1]["notes"],
            "First line\nSecond line"
        )


if __name__ == "__main__":
    unittest.main()
