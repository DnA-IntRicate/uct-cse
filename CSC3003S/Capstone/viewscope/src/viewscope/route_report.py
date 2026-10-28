"""
The route as a document: what it covers, where it stands, and what it costs.

Everything the Plan Route panel shows is on screen and nowhere else. A survey
gets signed off away from the machine it was planned on, so this writes the
same answers out as a PDF: the two charts the panel reads itself through, the
order the viewpoints are flown in - by name and by co-ordinate - how far that
runs, how hard it turns and what a drone would take out of a battery flying it.

The text is built as a string by `report_html`, which takes plain data and
touches no window, so what the document says can be checked without one. Only
`write_report` needs Qt: it draws the two charts into images, hands them to
the same rich text engine the rest of the application draws its panels with,
and prints the result through `QPdfWriter`.
"""

from __future__ import annotations

from datetime import datetime
from pathlib import Path

import numpy as np
from PySide6.QtCore import QMarginsF, QSizeF, Qt, QUrl
from PySide6.QtGui import (
    QBrush,
    QFont,
    QPageLayout,
    QPageSize,
    QPdfWriter,
    QPen,
    QTextDocument,
)
from PySide6.QtWidgets import QFrame

from viewscope.data import (
    SECTORS,
    Drone,
    Flight,
    FlightPath,
    RouteStatus,
    Turn,
    estimate_flight,
    sharpest_turn,
)
from viewscope.panels import CoverageBar, SectorBars

#: The charts are drawn far larger than they are printed, so the print has
#: something to be sharp with. Pixels.
CHART_SIZE = {"coverage": (1560, 440), "sectors": (1560, 620)}

#: And laid out at this width, in the pixels the document is measured in:
#: A4 less its margins, at the 96 dpi rich text is written for.
CHART_WIDTH = 620

#: What the chart's own lettering is scaled by, so that shrinking the image
#: onto the page leaves it the size the rest of the report is set in.
CHART_FONT_SCALE = CHART_SIZE["coverage"][0] / CHART_WIDTH

#: How the images are named inside the document.
CHART_URLS = {"coverage": "viewscope:coverage", "sectors": "viewscope:sectors"}

#: Air above each heading and below it, in the pixels the document is
#: measured in. Written on the headings themselves rather than left to the
#: stylesheet, which the rich text engine reads for colour and size but not
#: for the space a table butting up against a heading needs.
HEADING_SPACE_ABOVE = 34
HEADING_SPACE_BELOW = 12

PAGE_MARGIN_MM = 16.0
PRINT_DPI = 300

#: The printable part of an A4 page at the 96 dpi rich text is measured in.
PAGE_WIDTH = 660.0
PAGE_HEIGHT = 990.0

STYLE = """
body { font-family: Helvetica, Arial, sans-serif; font-size: 10pt; color: #1a1a1a; }
h1 { font-size: 20pt; margin-bottom: 2pt; }
h2 { font-size: 12pt; color: #333333; }
p  { line-height: 135%; }
.sub { color: #666666; font-size: 9pt; margin-top: 0pt; }
.note { color: #666666; font-size: 8.5pt; }
.order { font-size: 9.5pt; line-height: 150%; }
td, th { padding-top: 3px; padding-bottom: 3px; padding-left: 8px; padding-right: 8px; }
th { background-color: #eeeeee; text-align: left; }
td.n { text-align: right; }
"""


def report_html(
    *,
    name: str,
    bundle: str,
    status: RouteStatus,
    path: FlightPath,
    ids,
    positions,
    turn: Turn | None,
    flight: Flight,
    drone: Drone,
    when: datetime | None = None,
    charts: bool = True,
) -> str:
    """The report as rich text. `charts` off leaves the two images out."""
    when = when or datetime.now()
    positions = np.asarray(positions, dtype=np.float64).reshape(-1, 3)
    order = tuple(path.order)

    parts = [
        f"<html><head><style>{STYLE}</style></head><body>",
        "<h1>Flight path report</h1>",
        f"<p class='sub'>{_escape(name)} &nbsp;&middot;&nbsp; {_escape(bundle)}"
        f" &nbsp;&middot;&nbsp; {when:%d %B %Y, %H:%M}</p>",
        _summary(status, path, turn, flight),
    ]

    if charts:
        parts += [
            _heading("What the route sees"),
            f"<p align='center'><img src='{CHART_URLS['coverage']}' width='{CHART_WIDTH}'></p>",
            _heading("Where the route stands"),
            f"<p align='center'><img src='{CHART_URLS['sectors']}' width='{CHART_WIDTH}'></p>",
            f"<p class='note'>{_sector_note(status)}</p>",
        ]

    parts += [
        _heading("The path, by viewpoint"),
        _flown_order(order, ids),
        _heading("The path, by co-ordinate"),
        _coordinates(order, ids, positions),
        _heading("The energy estimate"),
        _energy(flight, drone),
    ]
    parts.append("</body></html>")

    return "\n".join(parts)


def write_report(
    file,
    *,
    name: str,
    bundle: str,
    status: RouteStatus,
    path: FlightPath,
    ids,
    positions,
    drone: Drone | None = None,
) -> Path:
    """Write the report to `file` as a PDF. Returns the path written."""
    drone = drone or Drone()
    turn = sharpest_turn(path.points)
    flight = estimate_flight(path.points, stops=len(path.order), drone=drone)

    document = QTextDocument()
    images = _chart_images(status)
    for key, image in images.items():
        document.addResource(QTextDocument.ResourceType.ImageResource, QUrl(CHART_URLS[key]), image)

    document.setHtml(
        report_html(
            name=name,
            bundle=bundle,
            status=status,
            path=path,
            ids=ids,
            positions=positions,
            turn=turn,
            flight=flight,
            drone=drone,
            charts=bool(images),
        )
    )

    return _print_pdf(document, Path(file))


# -- the sections ----------------------------------------------------------


def _summary(status: RouteStatus, path: FlightPath, turn: Turn | None, flight: Flight) -> str:
    stops = len(path.order)
    rows = [
        ("Viewpoints flown", f"{stops:,} of {status.camera_count:,} in the plan"),
        ("Targets observed", f"{status.observed:,} of {status.targets:,} ({status.coverage:.1%})"),
        ("Path length", f"{path.length:,.0f} m"),
        ("Sharpest turn", _turn_line(turn)),
        ("Time in the air", _clock(flight.seconds)),
        ("Energy needed", f"{flight.energy_wh:,.1f} Wh ({flight.energy_kj:,.0f} kJ)"),
        ("Share of one battery", f"{flight.battery_share:.0%}"),
        ("Keeping off the model", _clearance(path)),
    ]

    return _table(
        ("", ""),
        [(f"<b>{label}</b>", value) for label, value in rows],
        headed=False,
        widths=("34%", "66%"),
    )


def _heading(text: str) -> str:
    """A section heading, standing clear of what is on either side of it."""
    return (
        f"<h2 style='margin-top: {HEADING_SPACE_ABOVE}px; "
        f"margin-bottom: {HEADING_SPACE_BELOW}px'>{text}</h2>"
    )


def _flown_order(order, ids) -> str:
    """The viewpoints in flying order, by the names the plan gave them."""
    if not order:
        return "<p>Nothing is in the route, so there is no path to fly.</p>"

    names = " &rarr; ".join(_escape(_name_of(row, ids)) for row in order)

    return f"<p class='order'>{names}</p>"


def _coordinates(order, ids, positions) -> str:
    """The same order again, as the places the drone actually flies to."""
    if not order:
        return "<p>--</p>"

    rows = []
    for stop, row in enumerate(order, start=1):
        x, y, z = positions[row] if row < len(positions) else (float("nan"),) * 3
        rows.append((f"{stop}", _escape(_name_of(row, ids)), f"{x:,.2f}", f"{y:,.2f}", f"{z:,.2f}"))

    return _table(
        ("Stop", "Viewpoint", "X (m)", "Y (m)", "Z (m)"),
        rows,
        widths=("10%", "26%", "21%", "21%", "22%"),
        aligns=("right", "left", "right", "right", "right"),
    )


def _energy(flight: Flight, drone: Drone) -> str:
    """The figure, and every assumption standing behind it."""
    battery = (
        "within one battery"
        if flight.within_one_battery
        else f"more than one battery: {flight.battery_share:.1f} packs"
    )

    return (
        f"<p>Flying this path takes an estimated <b>{flight.energy_wh:,.1f} Wh</b> "
        f"({flight.energy_kj:,.0f} kJ) over {_clock(flight.seconds)} in the air, which is "
        f"{flight.battery_share:.0%} of a {drone.battery_wh:,.0f} Wh pack &mdash; {battery}. "
        f"Of that time, {_clock(flight.flying_seconds)} is spent flying "
        f"{flight.distance_m:,.0f} m and {_clock(flight.dwelling_seconds)} holding still at "
        f"{flight.stops:,} viewpoint{'' if flight.stops == 1 else 's'} to take the photographs."
        "</p>"
        "<p class='note'>An estimate, and only as good as what it assumes. Hover power comes "
        "from momentum theory for a "
        f"{drone.mass_kg:,.1f} kg aircraft on {drone.rotors} rotors of "
        f"{drone.rotor_radius_m * 100:,.0f} cm radius, at a figure of merit of "
        f"{drone.figure_of_merit:.2f} behind a drive {drone.drive_efficiency:.0%} efficient, "
        f"plus {drone.avionics_w:,.0f} W of avionics: {flight.power_w:,.0f} W in all. Each hop "
        f"is flown from rest to rest at {drone.cruise_speed_ms:,.0f} m/s, accelerating at "
        f"{drone.acceleration_ms2:,.0f} m/s&sup2;, with {drone.dwell_s:,.0f} s held at each "
        "viewpoint. Forward flight is costed at hover power, which is a little pessimistic. "
        "Wind, temperature and the state of the pack are not modelled.</p>"
    )


def _sector_note(status: RouteStatus) -> str:
    """Say in words what the bars say in heights."""
    counts = status.sectors
    if not counts or not sum(counts):
        return "No viewpoints are in the route, so there is nothing to stand anywhere."

    filled = sum(1 for count in counts if count)
    shares = ", ".join(
        f"S{sector + 1} {count} ({share:.0%})"
        for sector, (count, share) in enumerate(zip(counts, status.sector_shares, strict=False))
    )

    return (
        f"The route stands in {filled} of the {SECTORS} sectors about the model's centre, "
        f"each an eighth of the way round it anticlockwise from +x: {shares}."
    )


# -- the small print -------------------------------------------------------


def _turn_line(turn: Turn | None) -> str:
    if turn is None:
        return "no corner to turn at"

    return (
        f"{turn.angle_deg:,.0f}&deg; at stop {turn.index}, {turn.distance_m:,.0f} m in "
        f"(of {turn.corners:,} corners; straight on is 180&deg;)"
    )


def _clearance(path: FlightPath) -> str:
    if not path.checked:
        return "the model was not measured, so nothing was kept off it"

    if path.crossings:
        return (
            f"{path.crossings:,} hop{'' if path.crossings == 1 else 's'} cross the model: "
            "no way round or over was found"
        )

    went = []
    if path.detours:
        went.append(f"{path.detours:,} flown round")
    if path.climbs:
        went.append(f"{path.climbs:,} flown over")

    clear = "nothing flies through the model"

    return f"{clear}; {', '.join(went)}" if went else clear


def _clock(seconds: float) -> str:
    """Seconds as a pilot would say them."""
    seconds = max(float(seconds), 0.0)
    if seconds < 60.0:
        return f"{seconds:,.0f} s"

    minutes, rest = divmod(int(round(seconds)), 60)

    return f"{minutes:,} min {rest:02d} s"


def _name_of(row: int, ids) -> str:
    return ids[row] if 0 <= row < len(ids) else f"#{row + 1}"


def _table(headings, rows, headed: bool = True, widths=(), aligns=()) -> str:
    """A plain bordered table, which is all the rich text engine draws."""
    out = ["<table border='1' cellspacing='0' cellpadding='8' width='100%'>"]

    def cell(tag, index, text):
        width = f" width='{widths[index]}'" if index < len(widths) else ""
        # Figures line up on the right, where a column of them can be read
        # down; words stay on the left.
        align = f" align='{aligns[index]}'" if index < len(aligns) else ""
        return f"<{tag}{width}{align}>{text}</{tag}>"

    if headed:
        out.append(
            "<tr>" + "".join(cell("th", i, text) for i, text in enumerate(headings)) + "</tr>"
        )

    for row in rows:
        out.append("<tr>" + "".join(cell("td", i, text) for i, text in enumerate(row)) + "</tr>")

    out.append("</table>")

    return "".join(out)


def _escape(text) -> str:
    return (
        str(text)
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


# -- the Qt end ------------------------------------------------------------


def _chart_images(status: RouteStatus) -> dict:
    """The panel's own two charts, drawn off screen at print size."""
    images = {}
    for key, chart in (("coverage", CoverageBar()), ("sectors", SectorBars())):
        width, height = CHART_SIZE[key]
        chart.update_chart(status)
        _scale_lettering(chart.chart)
        _whiten(chart)
        chart.resize(width, height)
        # The chart lays itself out when it is given a size, and draws when it
        # is asked for its pixels: neither needs it to have been on screen.
        layout = chart.layout()
        # Both charts lay themselves out in __init__, so this is only ever true.
        if layout is not None:  # pragma: no branch
            layout.activate()
        images[key] = chart.grab().toImage()
        chart.deleteLater()

    return images


def _whiten(widget):
    """Put the chart on paper rather than on the dock it is usually read in.

    The panel's charts sit on whatever the application's palette gives them,
    which on a dark theme is a dark surround the chart's own white background
    is an island in. On a printed page that surround is a black frame.
    """
    widget.view.setFrameShape(QFrame.Shape.NoFrame)
    widget.view.setBackgroundBrush(QBrush(Qt.GlobalColor.white))
    widget.chart.setBackgroundBrush(QBrush(Qt.GlobalColor.white))
    widget.chart.setBackgroundPen(QPen(Qt.PenStyle.NoPen))
    widget.chart.setBackgroundRoundness(0.0)


def _scale_lettering(chart):
    """Grow the chart's own words in step with the image they are drawn in.

    The image is shrunk onto the page, and everything in it shrinks with it.
    Left at the size a dock is read at, a title would print at two points.
    """

    def grown(font):
        bigger = QFont(font)
        bigger.setPointSizeF(max(font.pointSizeF(), 9.0) * CHART_FONT_SCALE)
        return bigger

    chart.setTitleFont(grown(chart.titleFont()))
    chart.legend().setFont(grown(chart.legend().font()))
    for axis in chart.axes():
        axis.setLabelsFont(grown(axis.labelsFont()))

    # And the figures written on the marks themselves, which are the chart's
    # own labels rather than any axis's.
    for series in chart.series():
        for bars in getattr(series, "barSets", list)():
            bars.setLabelFont(grown(bars.labelFont()))


def _print_pdf(document: QTextDocument, path: Path) -> Path:
    writer = QPdfWriter(str(path))
    writer.setPageSize(QPageSize(QPageSize.PageSizeId.A4))
    writer.setPageMargins(
        QMarginsF(PAGE_MARGIN_MM, PAGE_MARGIN_MM, PAGE_MARGIN_MM, PAGE_MARGIN_MM),
        QPageLayout.Unit.Millimeter,
    )
    writer.setResolution(PRINT_DPI)
    writer.setTitle("ViewScope flight path report")

    # The document is written in the pixels rich text is written in, and
    # `print_` is what puts those on a 300 dpi page: setting the page size in
    # printer pixels here would leave ten point type a tenth of the size.
    document.setPageSize(QSizeF(PAGE_WIDTH, PAGE_HEIGHT))
    document.print_(writer)

    return path
