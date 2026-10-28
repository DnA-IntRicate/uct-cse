"""Unit tests for src/viewscope/panels/sector_barchart.py.

The chart holds no numbers of its own; it restates a report. What is checked
is the series and axes it ends up with, which is what a reader sees.
"""

import numpy as np
import pytest
from PySide6.QtCharts import QBarSeries, QLineSeries

from viewscope.panels.sector_barchart import SectorBarChart
from viewscope.scene.target_report import build_report

ORIGIN = np.zeros(3)
UP = np.array([0.0, 0.0, 1.0])


@pytest.fixture
def chart(app):
    return SectorBarChart()


def report_over(azimuths_deg, sector_count=8):
    """A report whose observers sit at these azimuths about the target."""
    radians = np.radians(azimuths_deg)
    positions = np.column_stack(
        [10.0 * np.cos(radians), 10.0 * np.sin(radians), np.full(len(radians), 6.0)]
    )
    return build_report(3, ORIGIN, UP, positions, np.arange(len(radians)), sector_count)


def series_of(chart, kind):
    return [s for s in chart.chart.series() if isinstance(s, kind)]


# -----------------------------------------------------------------------------
# With no target picked
# -----------------------------------------------------------------------------


def test_the_chart_opens_empty(chart):
    assert chart.chart.series() == []
    assert chart.chart.title() == "Best Weight Per Sector"


def test_no_target_says_so_and_draws_nothing(chart):
    chart.update_chart(None)

    assert chart.chart.title() == "No target selected"
    assert chart.chart.series() == []


def test_going_back_to_no_target_clears_what_was_drawn(chart):
    chart.update_chart(report_over([0.0, 90.0, 180.0]))

    chart.update_chart(None)

    assert chart.chart.series() == []
    assert chart.chart.axes() == []


# -----------------------------------------------------------------------------
# With a target picked
# -----------------------------------------------------------------------------


def test_the_title_names_the_target(chart):
    chart.update_chart(report_over([0.0, 90.0]))

    assert "Target: 3" in chart.chart.title()


def test_there_is_one_bar_per_sector_occupied_or_not(chart):
    chart.update_chart(report_over([0.0, 90.0], sector_count=8))

    bars = series_of(chart, QBarSeries)
    assert len(bars) == 1
    assert bars[0].barSets()[0].count() == 8


def test_a_four_sector_report_draws_four_bars(chart):
    chart.update_chart(report_over([0.0, 90.0], sector_count=4))

    assert series_of(chart, QBarSeries)[0].barSets()[0].count() == 4


def test_the_bars_carry_the_best_weight_of_each_sector(chart):
    report = report_over([0.0, 90.0, 180.0])

    chart.update_chart(report)

    drawn = series_of(chart, QBarSeries)[0].barSets()[0]
    assert [drawn.at(i) for i in range(drawn.count())] == pytest.approx(
        [sector.best_weight for sector in report.sectors]
    )


def test_the_weight_axis_is_fixed_so_charts_can_be_compared(chart):
    """Rescaling per target would make a weak target look like a strong one."""
    chart.update_chart(report_over([0.0, 90.0]))

    weight_axis = [axis for axis in chart.chart.axes() if axis.isVisible()]
    ranges = [(axis.min(), axis.max()) for axis in weight_axis if hasattr(axis, "min")]
    assert (0.0, 1.0) in ranges


def test_redrawing_replaces_the_series_rather_than_adding_to_them(chart):
    chart.update_chart(report_over([0.0, 90.0]))
    chart.update_chart(report_over([180.0, 270.0]))

    assert len(series_of(chart, QBarSeries)) == 1


# -----------------------------------------------------------------------------
# The average line
# -----------------------------------------------------------------------------


def test_the_average_line_is_drawn_across_the_bars(chart):
    chart.update_chart(report_over([0.0, 90.0, 180.0]))

    lines = series_of(chart, QLineSeries)
    assert len(lines) == 1
    assert lines[0].count() == 2


def test_the_average_ignores_the_empty_sectors(chart):
    """Averaging the zeroes in would drag the line down with sector count."""
    report = report_over([0.0, 90.0])
    occupied = [sector.best_weight for sector in report.sectors if sector.best_weight > 0]

    chart.update_chart(report)

    line = series_of(chart, QLineSeries)[0]
    assert line.at(0).y() == pytest.approx(sum(occupied) / len(occupied), rel=1e-6)


def test_the_line_spans_every_sector(chart):
    chart.update_chart(report_over([0.0, 90.0], sector_count=8))

    line = series_of(chart, QLineSeries)[0]
    assert (line.at(0).x(), line.at(1).x()) == (0.0, 7.0)


def test_a_target_nobody_observes_draws_bars_but_no_average(chart):
    """There is no average of nothing, and the line must not claim one."""
    report = build_report(0, ORIGIN, UP, np.zeros((0, 3)), np.zeros(0, dtype=np.int64), 8)

    chart.update_chart(report)

    assert len(series_of(chart, QBarSeries)) == 1
    assert series_of(chart, QLineSeries) == []
