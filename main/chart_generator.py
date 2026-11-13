"""Builds the chart and opens it in the default browser."""
import os
import webbrowser

import pygal

SERIES = ["open", "high", "low", "close"]


def create_chart(df, symbol, chart_type, function, start_date, end_date,
                 filename="chart.svg"):
    """Render the data as a line or bar chart, save it, and open it."""
    title = (f"{symbol} - {function.replace('_', ' ').title()}: "
             f"{start_date} to {end_date}")

    chart_class = pygal.Bar if chart_type == "bar" else pygal.Line
    chart = chart_class(
        title=title,
        x_label_rotation=45,
        show_minor_x_labels=False,
        width=1100,
        height=600,
    )
    chart.x_labels = [d.strftime("%Y-%m-%d") for d in df.index]
    # Only label ~12 dates so the axis stays readable.
    step = max(1, len(df) // 12)
    chart.x_labels_major = chart.x_labels[::step]

    for name in SERIES:
        chart.add(name.capitalize(), df[name].tolist())

    chart.render_to_file(filename)
    path = os.path.abspath(filename)
    webbrowser.open("file://" + path)
    print(f"\nChart saved to {path} and opened in your browser.")
    return path
