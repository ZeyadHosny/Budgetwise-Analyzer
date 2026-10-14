import unittest

from budgetwise.interface.charts import bar_chart


def bars(chart):
    """Star count on each line of a chart with no title."""
    return [line.count("*") for line in chart.splitlines()]


class TestBarChart(unittest.TestCase):

    def test_largest_value_gets_exactly_width_stars(self):
        chart = bar_chart({"Food": 500.0, "Rent": 1000.0}, width=40)
        self.assertEqual(max(bars(chart)), 40)

    def test_half_size_value_gets_half_the_stars(self):
        chart = bar_chart({"Rent": 1000.0, "Food": 500.0}, width=40)
        self.assertEqual(bars(chart), [40, 20])

    def test_tiny_value_still_gets_one_star(self):
        chart = bar_chart({"Rent": 1_000_000.0, "Tiny": 1.0}, width=40)
        self.assertEqual(bars(chart)[1], 1)

    def test_zero_value_has_no_stars_but_keeps_label(self):
        chart = bar_chart({"Rent": 100.0, "Savings": 0.0}, width=10)
        last = chart.splitlines()[1]
        self.assertTrue(last.startswith("Savings"))
        self.assertEqual(last.count("*"), 0)

    def test_empty_dict_returns_empty_string(self):
        self.assertEqual(bar_chart({}), "")

    def test_all_values_equal_gives_equal_bars(self):
        chart = bar_chart({"A": 5.0, "B": 5.0, "C": 5.0}, width=12)
        self.assertEqual(bars(chart), [12, 12, 12])

    def test_all_zero_values_do_not_divide_by_zero(self):
        chart = bar_chart({"A": 0.0, "B": 0.0}, width=12)
        self.assertEqual(bars(chart), [0, 0])

    def test_tuple_month_keys_render_as_year_month(self):
        chart = bar_chart({("2023", "07"): 10.0, ("2023", "08"): 20.0})
        lines = chart.splitlines()
        self.assertTrue(lines[0].startswith("2023-07"))
        self.assertTrue(lines[1].startswith("2023-08"))

    def test_every_line_is_the_same_length(self):
        chart = bar_chart(
            {"Food": 38_410_740.0, "Rent": 48_822_528.0, "Healthcare": 5_824_809.0,
             "Uncategorized": 3_104_685.0},
            width=30,
        )
        lengths = {len(line) for line in chart.splitlines()}
        self.assertEqual(len(lengths), 1)

    def test_numbers_are_right_aligned_with_commas(self):
        chart = bar_chart({"Rent": 48_822_528.0, "Food": 950.0}, width=10)
        lines = chart.splitlines()
        self.assertTrue(lines[0].endswith("48,822,528"))
        self.assertTrue(lines[1].endswith("       950"))

    def test_keeps_dictionary_order_by_default(self):
        chart = bar_chart({"B": 1.0, "A": 3.0, "C": 2.0})
        self.assertEqual([line[0] for line in chart.splitlines()], ["B", "A", "C"])

    def test_sort_by_value_puts_largest_first(self):
        chart = bar_chart({"B": 1.0, "A": 3.0, "C": 2.0}, sort_by_value=True)
        self.assertEqual([line[0] for line in chart.splitlines()], ["A", "C", "B"])

    def test_title_is_first_line(self):
        chart = bar_chart({"Food": 1.0}, title="Spending by category")
        self.assertEqual(chart.splitlines()[0], "Spending by category")

    def test_long_labels_are_shortened(self):
        chart = bar_chart({"A very long category name indeed": 1.0})
        self.assertTrue(chart.startswith("A very long cate "))

    def test_width_below_one_raises(self):
        with self.assertRaises(ValueError):
            bar_chart({"Food": 1.0}, width=0)

    def test_returns_string_and_does_not_print(self):
        self.assertIsInstance(bar_chart({"Food": 1.0}), str)


if __name__ == "__main__":
    unittest.main()
