import csv
import os
import tempfile
import unittest

from budgetwise.pipeline import run_cleaning


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


class TestCleaningPipeline(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp_dir.cleanup)

        self.csv_path = os.path.join(
            self.temp_dir.name,
            "transactions.csv"
        )
        self.log_path = os.path.join(
            self.temp_dir.name,
            "errors.log"
        )

    def make_row(self, **changes):
        row = {
            "transaction_id": "T0001",
            "user_id": "U001",
            "date": "2023-01-01",
            "transaction_type": "Expense",
            "category": "Food",
            "amount": "100",
            "payment_mode": "Cash",
            "location": "Pune",
            "notes": "Lunch"
        }
        row.update(changes)
        return [row[column] for column in HEADER]

    def run_rows(self, rows):
        with open(
            self.csv_path,
            "w",
            newline="",
            encoding="utf-8"
        ) as file:
            writer = csv.writer(file)
            writer.writerow(HEADER)
            writer.writerows(rows)

        result = run_cleaning(
            self.csv_path,
            log_path=self.log_path
        )

        counts = result.counts
        self.assertEqual(
            counts["input"],
            counts["retained"]
            + counts["skipped"]
            + counts["exact_duplicates"]
        )
        self.assertEqual(
            counts["retained"],
            len(result.records)
        )

        return result

    def read_log(self):
        with open(self.log_path, encoding="utf-8") as file:
            return file.read()

    def test_cleaners_and_logger_work_together(self):
        result = self.run_rows([
            self.make_row(
                date="01/02/2023",
                category=" Food ",
                amount="-$1,000",
                payment_mode="Crd",
                location=" Pune ",
                notes="  Lunch with friends  "
            )
        ])

        record = result.records[0]

        self.assertEqual(record["date"], "2023-01-02")
        self.assertEqual(record["category"], "Food")
        self.assertEqual(record["amount"], 1000.0)
        self.assertEqual(record["currency_label"], "$")
        self.assertEqual(record["payment_mode"], "Card")
        self.assertEqual(record["location"], "Pune")
        self.assertEqual(
            record["notes"],
            "  Lunch with friends  "
        )
        self.assertEqual(record["source_line"], 2)

        log = self.read_log()

        for reason in [
            "DATE_NORMALIZED",
            "CATEGORY_NORMALIZED",
            "amount_negative_to_magnitude",
            "amount_format_normalized",
            "PAYMENT_MODE_NORMALIZED",
            "LOCATION_NORMALIZED"
        ]:
            self.assertIn(f"reason={reason} ", log)

        self.assertIn("line=2 field=amount", log)
        self.assertIn("raw='-$1,000'", log)

    def test_duplicates_are_checked_before_normalization(self):
        first = self.make_row()

        result = self.run_rows([
            first,
            first.copy(),
            self.make_row(category=" food ")
        ])

        self.assertEqual(
            result.counts,
            {
                "input": 3,
                "retained": 2,
                "skipped": 0,
                "exact_duplicates": 1
            }
        )

        # Different raw rows remain even when their cleaned values match.
        self.assertEqual(
            [row["category"] for row in result.records],
            ["Food", "Food"]
        )
        self.assertEqual(
            result.issue_counts["DUPLICATE_RAW_ROW"],
            1
        )
        self.assertEqual(
            result.issue_counts["REPEATED_TRANSACTION_ID"],
            2
        )

    def test_missing_date_and_unknown_values_are_retained(self):
        result = self.run_rows([
            self.make_row(
                date="",
                category="",
                payment_mode="",
                location="N/A",
                notes="test"
            )
        ])

        self.assertEqual(result.counts["retained"], 1)

        record = result.records[0]

        self.assertIsNone(record["date"])
        self.assertEqual(record["category"], "Uncategorized")
        self.assertEqual(record["payment_mode"], "Unknown")
        self.assertEqual(record["location"], "Unknown")
        self.assertEqual(record["notes"], "test")
        self.assertEqual(
            record["notes_quality"],
            "low_information"
        )

    def test_unusable_amounts_and_types_are_skipped(self):
        result = self.run_rows([
            self.make_row(
                transaction_id="T0001",
                amount="1-2"
            ),
            self.make_row(
                transaction_id="T0002",
                amount="100000000"
            ),
            self.make_row(
                transaction_id="T0003",
                transaction_type="Refund"
            )
        ])

        self.assertEqual(result.counts["skipped"], 3)
        self.assertEqual(result.records, [])

        log = self.read_log()
        self.assertIn("reason=unrecognized_amount_format ", log)
        self.assertIn("reason=sentinel_amount ", log)
        self.assertIn("reason=MALFORMED_ROW ", log)

    def test_malformed_rows_are_skipped(self):
        short_row = self.make_row()[:4]
        extra_row = self.make_row(
            transaction_id="T0002"
        ) + ["unexpected value"]

        result = self.run_rows([short_row, extra_row])

        self.assertEqual(result.counts["skipped"], 2)
        self.assertEqual(result.records, [])
        self.assertEqual(
            result.issue_counts["MALFORMED_ROW"],
            2
        )

    def test_direction_comes_from_transaction_type(self):
        result = self.run_rows([
            self.make_row(
                transaction_id="T0001",
                transaction_type="Income",
                amount="-100"
            ),
            self.make_row(
                transaction_id="T0002",
                transaction_type="Expense",
                amount="100"
            )
        ])

        self.assertEqual(
            [row["transaction_type"] for row in result.records],
            ["Income", "Expense"]
        )
        self.assertEqual(
            [row["amount"] for row in result.records],
            [100.0, 100.0]
        )


if __name__ == "__main__":
    unittest.main()
