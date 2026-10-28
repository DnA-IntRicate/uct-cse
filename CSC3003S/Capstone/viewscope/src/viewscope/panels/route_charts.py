"""
The two charts the route panel reads itself through.

`CoverageBar` answers the question route planning is about - how much of the
model the cameras still in the route can see - as one bar filled to the share
of targets they observe between them. `SectorBars` answers the other half:
whether those cameras stand all around the model or bunched on one side of it,
as a bar per sector of the ground plane it sits on.

Both are fed a `RouteStatus` and nothing else. Each builds its series and its
axes once and then only rewrites the numbers in them: a chart that drops them
on every update draws the old ones over the new, and the route changes on
every click.

The sectors are one series, so they are one colour: which sector a bar is, is
said by where it stands on the axis and by the count written over it, and a
colour per sector would be eight hues carrying nothing the position does not.
Empty sectors keep their place on the axis rather than being left out, because
the gap in the route is the thing worth seeing.

Built with QtCharts, the way `sector_barchart.py` builds the target's chart.
"""

from __future__ import annotations

from PySide6.QtCharts import (
    QAbstractBarSeries,
    QBarCategoryAxis,
    QBarSeries,
    QBarSet,
    QChart,
    QChartView,
    QHorizontalStackedBarSeries,
    QValueAxis,
)
from PySide6.QtCore import QMargins, Qt
from PySide6.QtGui import QColor, QPainter, QPen
from PySide6.QtWidgets import QVBoxLayout, QWidget

from viewscope.data import SECTORS, RouteStatus

#: One series, so one colour. It is read on the panel's dark surface and again
#: on the white of a printed report, and holds up on both.
SECTOR_COLOUR = "#2a78d6"

#: The count written over each bar, and the line the bars stand on. Ink
#: rather than the series colour: the bar carries the colour, the number
#: carries the reading.
BAR_LABEL_COLOUR = "#3a3a3a"
AXIS_COLOUR = "#b8b6b0"

#: The two ends of the coverage bar: what the route sees, and what is left.
OBSERVED_COLOUR = "#e34948"
UNOBSERVED_COLOUR = "#ffffff"

#: White on a white chart is nothing at all, so the unobserved end is given
#: an edge to be read by. Without it the bar would look as though it simply
#: stopped where the coverage ended, with no whole to be a part of.
UNOBSERVED_EDGE = "#b8b6b0"

#: Room over the tallest bar for the count written above it.
BAR_HEADROOM = 1.18


class _ChartWidget(QWidget):
    """A chart filling the widget, with room for a dock this narrow."""

    def __init__(self, height: int):
        super().__init__()

        self.chart = QChart()
        self.chart.setMargins(QMargins(2, 2, 2, 2))

        self.view = QChartView(self.chart)
        self.view.setRenderHint(QPainter.RenderHint.Antialiasing)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.view)
        self.setMinimumHeight(height)


class CoverageBar(_ChartWidget):
    """One bar: the targets the route sees, against the targets there are."""

    def __init__(self):
        super().__init__(130)

        self.chart.legend().setVisible(True)
        self.chart.legend().setAlignment(Qt.AlignmentFlag.AlignBottom)

        self._observed = QBarSet("Observed")
        self._observed.setColor(QColor(OBSERVED_COLOUR))
        self._observed.setPen(QPen(Qt.PenStyle.NoPen))
        self._observed.append([0.0])

        self._unobserved = QBarSet("Not observed")
        self._unobserved.setColor(QColor(UNOBSERVED_COLOUR))
        self._unobserved.setPen(QPen(QColor(UNOBSERVED_EDGE), 1))
        self._unobserved.append([0.0])

        series = QHorizontalStackedBarSeries()
        series.append(self._observed)
        series.append(self._unobserved)
        self.chart.addSeries(series)

        # One nameless row: the bar is the whole chart, so a label down the
        # side would only repeat the title.
        self._axis_row = QBarCategoryAxis()
        self._axis_row.append([""])
        self.chart.addAxis(self._axis_row, Qt.AlignmentFlag.AlignLeft)
        series.attachAxis(self._axis_row)

        self._axis_targets = QValueAxis()
        self._axis_targets.setLabelFormat("%d")
        self.chart.addAxis(self._axis_targets, Qt.AlignmentFlag.AlignBottom)
        series.attachAxis(self._axis_targets)

        self.update_chart(None)

    def update_chart(self, status: RouteStatus | None):
        """Redraw for this route, or empty the bar when there is no scene."""
        targets = 0 if status is None else status.targets
        observed = 0 if status is None else min(status.observed, targets)

        self.chart.setTitle(
            "No targets to observe"
            if status is None or not targets
            else f"Observed {status.observed:,} of {targets:,} targets"
        )

        self._observed.replace(0, float(observed))
        self._unobserved.replace(0, float(targets - observed))
        # A scene with no targets would give a zero width axis, which draws as
        # a row of zeroes, so the bar keeps a nominal length with no scale on it.
        self._axis_targets.setRange(0.0, float(targets) if targets else 1.0)
        self._axis_targets.setLabelsVisible(bool(targets))


class SectorBars(_ChartWidget):
    """A bar per sector of the ground plane, holding the route's share."""

    def __init__(self):
        super().__init__(210)

        # One series: the bars are all the same thing counted in different
        # places, and a legend would only name the one thing twice.
        self.chart.legend().setVisible(False)

        self._counts = QBarSet("Cameras")
        self._counts.setColor(QColor(SECTOR_COLOUR))
        self._counts.setPen(QPen(Qt.PenStyle.NoPen))
        self._counts.setLabelColor(QColor(BAR_LABEL_COLOUR))
        self._counts.append([0.0] * SECTORS)

        self._series = QBarSeries()
        self._series.append(self._counts)
        # A bar wide enough to read in a dock this narrow, with the surface
        # showing between one and the next.
        self._series.setBarWidth(0.78)
        # Written over each bar, so the count is read off the bar itself
        # rather than tracked back to the axis.
        self._series.setLabelsVisible(True)
        self._series.setLabelsPosition(QAbstractBarSeries.LabelsPosition.LabelsOutsideEnd)
        # Counts, written as counts. The precision is significant digits, and
        # one of them turns a route of thirty cameras into "3e+01".
        self._series.setLabelsFormat("@value")
        self._series.setLabelsPrecision(6)
        self.chart.addSeries(self._series)

        self._axis_sectors = QBarCategoryAxis()
        self._axis_sectors.append([str(sector + 1) for sector in range(SECTORS)])
        # The bars are the thing; the lines between them are not.
        self._axis_sectors.setGridLineVisible(False)
        self._axis_sectors.setLinePen(QPen(QColor(AXIS_COLOUR), 1))
        self.chart.addAxis(self._axis_sectors, Qt.AlignmentFlag.AlignBottom)
        self._series.attachAxis(self._axis_sectors)

        # The count is written on the bars, so the scale behind them is there
        # to be glanced at rather than read: no labels, no grid to draw the
        # eye off the bars.
        self._axis_count = QValueAxis()
        self._axis_count.setLabelsVisible(False)
        self._axis_count.setGridLineVisible(False)
        self._axis_count.setLineVisible(False)
        self.chart.addAxis(self._axis_count, Qt.AlignmentFlag.AlignLeft)
        self._series.attachAxis(self._axis_count)

        self.update_chart(None)

    def update_chart(self, status: RouteStatus | None):
        """Redraw for this route, or empty the bars when there is no scene."""
        counts = () if status is None else status.sectors
        cameras = sum(counts)

        self.chart.setTitle(
            "Cameras by sector: --"
            if not cameras
            else f"Cameras by sector: {cameras} in {sum(1 for c in counts if c)} of {SECTORS}"
        )

        for sector in range(SECTORS):
            count = counts[sector] if sector < len(counts) else 0
            self._counts.replace(sector, float(count))

        # Room for the labels over the tallest bar, and a nominal scale while
        # there is nothing to scale to.
        tallest = max(counts, default=0)
        self._axis_count.setRange(0.0, float(tallest) * BAR_HEADROOM if tallest else 1.0)
