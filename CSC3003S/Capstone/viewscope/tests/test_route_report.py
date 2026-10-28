"""Unit tests for src/viewscope/route_report.py.

What the report says is built as text by `report_html`, away from any window,
so what it says is what is checked here: every viewpoint in it, in flying
order, by name and by co-ordinate, and every figure the panel would have
shown. Drawing it onto a page is Qt's, and is not re-tested.
"""

from dataclasses import replace
from typing import Any

import numpy as np
import pytest

import viewscope.route_report as rr
from viewscope.data.flight_metrics import Drone, estimate_flight, sharpest_turn
from viewscope.data.flight_path import FlightPath
from viewscope.data.route import RouteStatus
from viewscope.route_report import CHART_URLS, report_html

IDS = ("vp000", "vp001", "vp002", "vp003")
POSITIONS = np.array(
    [
        [0.0, 0.0, 10.0],
        [30.0, 0.0, 10.0],
        [30.0, 40.0, 12.5],
        [0.0, 40.0, 10.0],
    ]
)


@pytest.fixture
def path():
    """A route flown 0 -> 2 -> 1, which turns a right angle in the middle."""
    points = np.array([[0.0, 0, 0], [40, 0, 0], [40, 30, 0]])

    return FlightPath(
        order=(0, 2, 1),
        points=points,
        length=70.0,
        detours=1,
        climbs=0,
        crossings=0,
        checked=True,
    )


@pytest.fixture
def status():
    return RouteStatus(
        planning=True,
        selected=(0, 1, 2),
        labels=("vp000", "vp001", "vp002"),
        camera_count=4,
        observed=4_200,
        targets=9_000,
        sectors=(2, 0, 1, 0, 0, 0, 0, 0),
    )


@pytest.fixture
def html(status, path):
    def build(**overrides):
        drone = overrides.pop("drone", Drone())
        settings: dict[str, Any] = {
            "name": "north_face",
            "bundle": "kiri",
            "status": status,
            "path": path,
            "ids": IDS,
            "positions": POSITIONS,
            "turn": sharpest_turn(path.points),
            "flight": estimate_flight(path.points, stops=len(path.order), drone=drone),
            "drone": drone,
        }
        settings.update(overrides)

        return report_html(**settings)

    return build


# -----------------------------------------------------------------------------
# What the route is
# -----------------------------------------------------------------------------


def test_the_route_is_named(html):
    assert "north_face" in html()
    assert "kiri" in html()


def test_a_name_with_markup_in_it_is_written_as_text(html):
    """A file can be called anything; a document that took it as a tag could not."""
    document = html(name="<b>north</b> & south")

    assert "&lt;b&gt;north&lt;/b&gt; &amp; south" in document
    assert "<b>north</b>" not in document


def test_the_coverage_the_panel_shows_is_in_it(html):
    document = html()

    assert "4,200 of 9,000" in document
    assert "46.7%" in document


# -----------------------------------------------------------------------------
# The path, twice over
# -----------------------------------------------------------------------------


def test_the_path_is_given_as_viewpoints_in_flying_order(html):
    document = html()

    assert "vp000 &rarr; vp002 &rarr; vp001" in document


def test_every_viewpoint_flown_is_given_as_a_co_ordinate(html):
    document = html()

    for row in (0, 2, 1):
        x, y, z = POSITIONS[row]
        assert f"{x:,.2f}" in document
        assert f"{y:,.2f}" in document
        assert f"{z:,.2f}" in document


def test_a_viewpoint_left_out_of_the_route_is_left_out_of_the_report(html):
    """vp003 is in the plan and not in the path, so it is not a stop."""
    assert "vp003" not in html()


def test_the_length_is_the_path_is_own(html, path):
    assert f"{path.length:,.0f} m" in html()


def test_the_sharpest_turn_is_reported_with_its_place(html):
    document = html()

    assert "90&deg; at stop 1" in document
    assert "straight on is 180" in document


def test_a_path_with_no_corner_says_so(html, path, status):
    straight = FlightPath(
        order=(0, 1),
        points=np.array([[0.0, 0, 0], [10, 0, 0]]),
        length=10.0,
        detours=0,
        climbs=0,
        crossings=0,
        checked=True,
    )

    assert "no corner to turn at" in html(path=straight, turn=sharpest_turn(straight.points))


def test_an_empty_route_says_there_is_nothing_to_fly(html):
    empty = FlightPath(
        order=(),
        points=np.zeros((0, 3)),
        length=0.0,
        detours=0,
        climbs=0,
        crossings=0,
        checked=False,
    )

    assert "no path to fly" in html(path=empty, turn=None)


# -----------------------------------------------------------------------------
# What it would cost to fly
# -----------------------------------------------------------------------------


def test_the_energy_is_given_in_watt_hours_and_in_joules(html, path):
    flight = estimate_flight(path.points, stops=3)
    document = html()

    assert f"{flight.energy_wh:,.1f} Wh" in document
    assert f"{flight.energy_kj:,.0f} kJ" in document


def test_the_share_of_a_battery_is_given(html):
    assert "of a 74 Wh pack" in html()


def test_a_flight_needing_more_than_a_pack_says_so(html):
    assert "more than one battery" in html(drone=Drone(battery_wh=0.001))


def test_every_assumption_behind_the_figure_is_printed(html):
    """An estimate whose assumptions are not stated cannot be argued with."""
    document = html(drone=Drone(mass_kg=2.4, cruise_speed_ms=7.0, dwell_s=3.0))

    assert "2.4 kg" in document
    assert "7 m/s" in document
    assert "3 s held at each" in document
    assert "momentum theory" in document


# -----------------------------------------------------------------------------
# The charts
# -----------------------------------------------------------------------------


def test_both_charts_are_in_the_document(html):
    document = html()

    assert CHART_URLS["coverage"] in document
    assert CHART_URLS["sectors"] in document


def test_the_sectors_are_said_in_words_as_well_as_drawn(html):
    """A chart is no use to a reader who cannot see it, and none to a grep."""
    document = html()

    assert "2 of the 8 sectors" in document
    assert "S1 2 (67%)" in document
    assert "S3 1 (33%)" in document


def test_a_document_without_charts_leaves_the_images_out(html):
    document = html(charts=False)

    assert CHART_URLS["coverage"] not in document
    assert "The path, by viewpoint" in document


# -----------------------------------------------------------------------------
# The lines the report is built out of
# -----------------------------------------------------------------------------


def test_an_empty_route_stands_nowhere():
    empty = RouteStatus(planning=True, selected=(), labels=(), camera_count=4, sectors=(0,) * 8)

    assert "nothing to stand anywhere" in rr._sector_note(empty)


def test_a_route_measured_against_no_plan_stands_nowhere():
    """Sectors are empty when there was no plan to measure."""
    none = RouteStatus(planning=True, selected=(), labels=(), camera_count=0)

    assert "nothing to stand anywhere" in rr._sector_note(none)


def test_hops_left_crossing_the_model_are_owned_up_to(path):
    crossed = replace(path, crossings=2, detours=0)

    assert "2 hops cross the model" in rr._clearance(crossed)
    assert "no way round or over was found" in rr._clearance(crossed)


def test_a_single_crossing_is_not_pluralised(path):
    assert "1 hop cross" in rr._clearance(replace(path, crossings=1))


def test_a_path_that_climbed_says_how_many_hops_went_over(path):
    line = rr._clearance(replace(path, detours=0, climbs=3))

    assert "nothing flies through the model" in line
    assert "3 flown over" in line


def test_a_path_that_both_went_round_and_climbed_says_both(path):
    line = rr._clearance(replace(path, detours=2, climbs=3))

    assert "2 flown round, 3 flown over" in line


def test_a_straight_clear_path_says_only_that(path):
    line = rr._clearance(replace(path, detours=0, climbs=0))

    assert line == "nothing flies through the model"


def test_an_unmeasured_path_says_so(path):
    assert "not measured" in rr._clearance(replace(path, checked=False))


# -----------------------------------------------------------------------------
# Times as a pilot would say them
# -----------------------------------------------------------------------------


def test_under_a_minute_is_said_in_seconds():
    assert rr._clock(42.4) == "42 s"


def test_a_minute_or_more_is_said_in_minutes_and_seconds():
    assert rr._clock(75.0) == "1 min 15 s"
    assert rr._clock(3600.0) == "60 min 00 s"


def test_the_seconds_are_padded_so_the_times_line_up():
    assert rr._clock(65.0) == "1 min 05 s"


def test_a_negative_time_is_no_time_at_all():
    assert rr._clock(-5.0) == "0 s"


# -----------------------------------------------------------------------------
# Writing the document out
# -----------------------------------------------------------------------------


def test_a_report_is_written_as_a_pdf(app, tmp_path, status, path):
    """End to end, through Qt: the charts are drawn and the page is printed."""
    out = tmp_path / "report.pdf"

    written = rr.write_report(
        out,
        name="north_face",
        bundle="kiri",
        status=status,
        path=path,
        ids=IDS,
        positions=POSITIONS,
    )

    assert written == out
    assert out.exists()
    assert out.read_bytes().startswith(b"%PDF")


def test_the_report_carries_the_panels_own_charts(app, status):
    images = rr._chart_images(status)

    assert set(images) == set(CHART_URLS)
    assert all(not image.isNull() for image in images.values())


def test_the_charts_are_drawn_on_paper_rather_than_on_the_dock(app, status):
    """A dark surround would print as a black frame round the chart."""
    from PySide6.QtCore import Qt

    images = rr._chart_images(status)

    corner = images["coverage"].pixelColor(1, 1)
    assert corner == Qt.GlobalColor.white


def test_a_report_can_be_written_for_a_drone_that_is_not_the_default(app, tmp_path, status, path):
    from dataclasses import replace as replaced

    out = tmp_path / "report.pdf"

    rr.write_report(
        out,
        name="north_face",
        bundle="kiri",
        status=status,
        path=path,
        ids=IDS,
        positions=POSITIONS,
        drone=replaced(Drone(), cruise_speed_ms=3.0),
    )

    assert out.exists()
