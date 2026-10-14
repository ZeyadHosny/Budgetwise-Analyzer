"""
bar_chart.py  -  text bar chart of spending              (task P3.6, Henrietta)

Section 4.4: "a simple text-based visualization of spending by month or
category (e.g., bar chart using * characters)".

bar_chart() takes the dictionary analysis/aggregation already produces and
returns the chart as a string. It never prints, so the tests can check the
exact output and the menu decides where it goes. Standard library only.
"""

# Character used to draw the bars.
BAR_CHARACTER = "*"
# Default number of characters the largest bar is drawn with.
DEFAULT_WIDTH = 40
# Longest label shown before it is shortened.
MAX_LABEL_WIDTH = 16


def format_label(key):
    """
    Description:
    - Turn a dictionary key into a chart label.
    - A (year, month) tuple key becomes 'YYYY-MM'; anything else becomes text.
    - Labels longer than MAX_LABEL_WIDTH are cut short.

    Input arguments:
       key (str or tuple): e.g. 'Food' or ('2023', '07').

    Return:
        str: e.g. 'Food' or '2023-07'.
    """
    if isinstance(key, tuple):
        label = "-".join(str(part) for part in key)
    else:
        label = str(key)
    return label[:MAX_LABEL_WIDTH]


def bar_length(value, max_value, width):
    """
    Description:
    - Number of bar characters for one value, scaled so the largest value
      gets exactly `width`.
    - Any value above zero gets at least one character, so a small total is
      still visible. Zero or negative gets none.

    Input arguments:
       value (float): this row's total.
       max_value (float): the largest total in the chart.
       width (int): characters for the largest bar.

    Return:
        int: between 0 and width.
    """
    if value <= 0 or max_value <= 0:
        return 0
    return max(1, round(value / max_value * width))


def bar_chart(totals, width=DEFAULT_WIDTH, title="", sort_by_value=False):
    """
    Description:
    - Draw one bar per key, scaled to the largest value.
    - Labels are left-aligned and numbers right-aligned, so every line has
      the same length.
    - Tuple month keys render as 'YYYY-MM'. Rows keep the dictionary's order
      (chronological for totals_by_month) unless sort_by_value is True.

    Input arguments:
       totals (dict): e.g. totals_by_category(...) or totals_by_month(...).
       width (int): characters for the largest bar. Must be at least 1.
       title (str): optional heading line.
       sort_by_value (bool): largest first when True.

    Return:
        str: the chart, lines joined with newlines. '' for an empty dict.
    """
    if width < 1:
        raise ValueError(f"width must be at least 1, not {width}")
    if not totals:
        return ""

    items = list(totals.items())
    if sort_by_value:
        items.sort(key=lambda item: item[1], reverse=True)

    labels = [format_label(key) for key, _ in items]
    numbers = [f"{value:,.0f}" for _, value in items]
    label_width = max(len(label) for label in labels)
    number_width = max(len(number) for number in numbers)
    max_value = max(value for _, value in items)

    lines = []
    if title:
        lines.append(title)
    for label, number, (_, value) in zip(labels, numbers, items):
        bar = BAR_CHARACTER * bar_length(value, max_value, width)
        lines.append(f"{label:<{label_width}}  {bar:<{width}}  {number:>{number_width}}")
    return "\n".join(lines)
