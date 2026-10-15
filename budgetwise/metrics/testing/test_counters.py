import time
import unittest

from budgetwise.metrics import RunMetrics, timed


def pipeline_result():
    """A clean_file() result with the shape and counts of a real run."""
    return {
        "counts": {"input": 15900, "duplicates": 900, "skipped": 349, "valid": 14651,
                   "corrected": 14587, "flagged": 6768, "categories_normalized": 10955},
        "timings": {"load": 0.0438, "clean": 0.5572},
    }


class TestCounts(unittest.TestCase):

    def test_new_metrics_start_at_zero(self):
        metrics = RunMetrics()
        self.assertEqual(set(metrics.report()["counts"].values()), {0})
        self.assertEqual(metrics.total_time(), 0.0)

    def test_record_methods_add_to_each_count(self):
        metrics = RunMetrics()
        metrics.record_input(10)
        metrics.record_valid(7)
        metrics.record_corrected(4)
        metrics.record_skipped(2)
        metrics.record_duplicate()
        metrics.record_category_normalized(3)
        self.assertEqual(
            metrics.report()["counts"],
            {"input": 10, "valid": 7, "corrected": 4, "skipped": 2,
             "duplicates": 1, "categories_normalized": 3},
        )

    def test_negative_or_fractional_counts_are_refused(self):
        metrics = RunMetrics()
        for bad in (-1, 1.5, "3", True):
            with self.subTest(count=bad):
                with self.assertRaises(ValueError):
                    metrics.record_input(bad)


class TestReconciliation(unittest.TestCase):

    def test_reconciles_when_every_row_is_accounted_for(self):
        metrics = RunMetrics()
        metrics.record_input(10)
        metrics.record_valid(7)
        metrics.record_skipped(2)
        metrics.record_duplicate(1)
        self.assertTrue(metrics.reconciles())

    def test_does_not_reconcile_when_a_row_is_missing(self):
        metrics = RunMetrics()
        metrics.record_input(10)
        metrics.record_valid(7)
        self.assertFalse(metrics.reconciles())
        self.assertIn("WARNING", metrics.format_report())

    def test_corrected_is_not_part_of_reconciliation(self):
        # Corrected rows are valid rows; counting them again would double count.
        metrics = RunMetrics()
        metrics.record_input(5)
        metrics.record_valid(5)
        metrics.record_corrected(5)
        self.assertTrue(metrics.reconciles())


class TestTimings(unittest.TestCase):

    def test_timed_records_elapsed_seconds(self):
        metrics = RunMetrics()
        with timed(metrics, "analysis"):
            time.sleep(0.01)
        self.assertGreater(metrics.get_time("analysis"), 0.0)

    def test_timed_records_even_when_block_raises(self):
        metrics = RunMetrics()
        with self.assertRaises(RuntimeError):
            with timed(metrics, "clean"):
                raise RuntimeError("boom")
        self.assertGreater(metrics.get_time("clean"), 0.0)

    def test_phases_are_kept_separate(self):
        metrics = RunMetrics()
        metrics.add_time("load", 0.5)
        metrics.add_time("clean", 1.0)
        metrics.add_time("analysis", 0.25)
        self.assertEqual(metrics.get_time("load"), 0.5)
        self.assertEqual(metrics.total_time(), 1.75)

    def test_unknown_phase_or_negative_time_is_refused(self):
        metrics = RunMetrics()
        with self.assertRaises(ValueError):
            metrics.add_time("export", 1.0)
        with self.assertRaises(ValueError):
            metrics.add_time("load", -1.0)


class TestFromPipeline(unittest.TestCase):

    def test_copies_the_six_counts(self):
        counts = RunMetrics.from_pipeline(pipeline_result()).report()["counts"]
        self.assertEqual(
            counts,
            {"input": 15900, "valid": 14651, "corrected": 14587, "skipped": 349,
             "duplicates": 900, "categories_normalized": 10955},
        )

    def test_copies_load_and_clean_timings(self):
        metrics = RunMetrics.from_pipeline(pipeline_result())
        self.assertEqual(metrics.get_time("load"), 0.0438)
        self.assertEqual(metrics.get_time("clean"), 0.5572)
        self.assertEqual(metrics.get_time("analysis"), 0.0)

    def test_real_run_counts_reconcile(self):
        self.assertTrue(RunMetrics.from_pipeline(pipeline_result()).reconciles())

    def test_missing_keys_default_to_zero(self):
        metrics = RunMetrics.from_pipeline({})
        self.assertEqual(metrics.get_count("input"), 0)


class TestReport(unittest.TestCase):

    def test_report_holds_all_seven_measurements(self):
        report = RunMetrics.from_pipeline(pipeline_result()).report()
        self.assertEqual(len(report["counts"]), 6)
        self.assertEqual(set(report["timings_seconds"]), {"load", "clean", "analysis", "total"})
        self.assertTrue(report["reconciles"])

    def test_format_report_lists_every_label_in_order(self):
        text = RunMetrics.from_pipeline(pipeline_result()).format_report()
        labels = ["Input records", "Valid records", "Corrected records",
                  "Invalid / skipped records", "Duplicates detected",
                  "Categories normalized", "Loading", "Cleaning", "Analysis", "Total"]
        positions = [text.index(label) for label in labels]
        self.assertEqual(positions, sorted(positions))
        self.assertIn("15,900", text)

    def test_format_report_returns_string(self):
        self.assertIsInstance(RunMetrics().format_report(), str)


if __name__ == "__main__":
    unittest.main()
