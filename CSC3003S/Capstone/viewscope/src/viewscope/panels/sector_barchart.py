"""The Bar-chart for the sector. Every bar represents a sector(so either 4 or 8 bars).
The Y-axis represents the best weight. There's also a line drawn across screen.
I looked at the official PyQt6 docs for an example and took inspiration from it:
https://doc.qt.io/qtforpython-6/examples/example_charts_barchart.html"""

from __future__ import annotations

from PySide6.QtCharts import (
    QBarCategoryAxis,
    QBarSeries,
    QBarSet,
    QChart,
    QChartView,
    QLineSeries,
    QValueAxis,
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QPainter
from PySide6.QtWidgets import QVBoxLayout, QWidget

from viewscope.scene import TargetReport


class SectorBarChart(QWidget):
    """Bar Chart for best weight per sector, and a line for the average."""

    def __init__(self):
        super().__init__()

        self.chart = QChart()
        self.chart.setTitle("Best Weight Per Sector")
        self.chart.legend().setVisible(True)

        self.view = QChartView(self.chart)  #
        self.view.setRenderHint(QPainter.RenderHint.Antialiasing)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.view)
        self.setMinimumHeight(250)  # 180

    def update_chart(self, report: TargetReport | None):
        """Update the bar chart with the latest report.
        This should be called whenever a new target is picked."""

        self.chart.removeAllSeries()  # clear chart
        for axis in list(self.chart.axes()):
            self.chart.removeAxis(axis)

        if report is None:
            self.chart.setTitle("No target selected")
            return
        self.chart.setTitle(f"Best Weight Per Sector\nTarget: {report.index}")

        # Draw bars
        heights = [s.best_weight for s in report.sectors]  # weights
        categories = [str(s.index) for s in report.sectors]  # sectors

        bar_set = QBarSet("Best weight")
        bar_set.append(heights)

        series = QBarSeries()
        series.append(bar_set)
        self.chart.addSeries(series)

        axis_x = QBarCategoryAxis()
        axis_x.append(categories)
        self.chart.addAxis(axis_x, Qt.AlignmentFlag.AlignBottom)
        axis_x.setTitleText("Sectors")
        series.attachAxis(axis_x)

        axis_y = QValueAxis()
        axis_y.setRange(0.0, 1.0)
        axis_y.setTitleText("Best weight")
        self.chart.addAxis(axis_y, Qt.AlignmentFlag.AlignLeft)
        series.attachAxis(axis_y)

        # Used Claude to help with drawing the average line
        occupied = [h for h in heights if h > 0]  # exlcude the empty sectors from average calc.
        average = sum(occupied) / len(occupied) if occupied else None
        self.draw_average_line(average, categories, axis_y)

    def draw_average_line(self, average, categories, axis_y):
        """Drawing the line that represents the average weight.
        Claude recommended a QLineSeries. The BarSeries and LineSeries don't share
        the same axis coordinate cleanly, so this Line overlays ontop of the BarSeries."""
        if average is None:
            return  # nothing observes this target, so there is no average to draw

        line = QLineSeries()
        line.append(0.0, average)  # first category centre
        line.append(len(categories) - 1.0, average)
        self.chart.addSeries(line)

        line_axis_x = QValueAxis()  # separate numeric axis
        line_axis_x.setRange(-0.5, len(categories) - 0.5)
        line_axis_x.setVisible(False)  # hidden, just to place the line
        self.chart.addAxis(line_axis_x, Qt.AlignmentFlag.AlignBottom)
        line.attachAxis(line_axis_x)

        line.attachAxis(axis_y)  # share the y-axis with the bars
