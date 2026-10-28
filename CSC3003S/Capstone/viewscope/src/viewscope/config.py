"""Constants for the ViewScope viewer.

Nothing here imports Qt or VTK, so any module can pull from it freely.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

# Relative to the working directory. Pass an explicit path to MainWindow if
# you need to run from somewhere else.
DATA_DIR = Path("data/kiri")

YFOV_DEG = 53.1301

MODE_TEXTURED = "Textured mesh"
MODE_GEOMETRY = "Geometry (.obj)"
MODE_TARGETS = "Target values"
MODE_ALL = "All three"
MODES = [MODE_TEXTURED, MODE_GEOMETRY, MODE_TARGETS, MODE_ALL]

SCALAR_FIELDS = ["score_8", "score_4", "diversity_8", "diversity_4"]

ORG_NAME = "ViewScope"
APP_NAME = "viewer"

BACKGROUND = (0.03, 0.03, 0.05)
GEOMETRY_COLOUR = (0.62, 0.64, 0.70)
EDGE_COLOUR = (0.15, 0.16, 0.20)

# Occlusion highlighting: what the selected camera can and cannot see.
VISIBLE_COLOUR = (0.90, 0.11, 0.14)
OCCLUDED_COLOUR = (0.42, 0.43, 0.47)

# The camera view draws the full-resolution textured model, not the
# simplified scene.obj the main viewport runs on: the viewport is the half
# that has to animate on a laptop without much GPU, while a simulated
# photograph is worth looking at only for the detail in it. Bundles that
# carry one keep it in this subfolder, beside its .mtl and textures.
PHOTO_MESH_DIR = "Mesh"

# An exported still is the camera view blown up, not the camera view at the
# size the dock happens to be: the dock is a few hundred pixels across, and a
# simulated photograph is worth having at something nearer print size. VTK
# renders it in tiles, so this width costs render time and memory rather than
# screen, and the shot keeps the aspect the dock is showing.
STILL_WIDTH = 3840

# A ceiling on that blow-up. A dock dragged narrow would otherwise ask for a
# grid of tiles deep enough to stall the window for the length of a coffee.
STILL_MAX_SCALE = 12

# -- the drone the route is costed against ---------------------------------

# The energy figure in the route report is an estimate, and an estimate is
# only as good as what it assumes, so everything it assumes is here rather
# than buried in the arithmetic. These are a small survey quadrotor: change
# them and the report changes with them, because the report prints them.

#: All-up mass, in kilograms: airframe, battery and camera.
DRONE_MASS_KG = 1.5

#: How many rotors, and how long each blade is, in metres. Together they give
#: the disc the thrust is made over, which is what sets the hover power.
DRONE_ROTORS = 4
DRONE_ROTOR_RADIUS_M = 0.12

#: Air density at sea level, in kg/m^3.
AIR_DENSITY = 1.225

#: What the rotors make of the power they are given, and what the motors and
#: speed controllers make of the power the battery gives them. Momentum
#: theory gives the ideal; these are what a real aircraft gets for it.
DRONE_FIGURE_OF_MERIT = 0.70
DRONE_DRIVE_EFFICIENCY = 0.80

#: Everything that draws power without lifting anything: flight controller,
#: radio, camera, gimbal. In watts.
DRONE_AVIONICS_W = 12.0

#: How fast it flies between viewpoints and how hard it accelerates, in m/s
#: and m/s^2. Survey speeds, not sport ones.
DRONE_CRUISE_SPEED_MS = 5.0
DRONE_ACCELERATION_MS2 = 2.0

#: How long it holds still at each viewpoint to take the photograph, in
#: seconds. A survey shot is taken stopped, not on the fly.
DRONE_DWELL_S = 2.0

#: A typical pack, in watt-hours: 4 cells at 5,000 mAh. The report says what
#: share of one the flight would take, which is the number a pilot plans by.
DRONE_BATTERY_WH = 74.0

# -- target inspection -----------------------------------------------------

# Sector counts the inspector offers. Eight is the default; four is the
# coarser decomposition the bundle also stores a column for.
SECTOR_COUNTS = (8, 4)

COLOUR_BY_WEIGHT = "Weight"
COLOUR_BY_SECTOR = "Sector"
TARGET_COLOUR_MODES = [COLOUR_BY_WEIGHT, COLOUR_BY_SECTOR]

# The hue the weight ramp is built on, as an HSV fraction, and the saturation
# and value it runs between. Weight is a magnitude, so it is read as depth of
# one blue rather than as a walk around the wheel: a weak camera is a wash, a
# strong one is ink. The dark end stops where it does because below that it
# sinks into BACKGROUND (3.0:1 against it, measured, not guessed).
WEIGHT_HUE = 0.59
WEIGHT_SATURATION_RANGE = (0.10, 0.82)
WEIGHT_VALUE_RANGE = (0.98, 0.655)

# One colour per sector, worn by the ray and by the camera glyph it runs to:
# four shades of blue and four of orange. Sector is an identity, not a
# magnitude, so these are a fixed set read in order and never generated, and
# the colour a wedge wears does not move when a neighbour appears or goes away.
#
# The order is not the order they were designed in, and not arbitrary either.
# Neighbouring wedges sit side by side on screen, so every arrangement of these
# eight was measured against this viewport's background and this is the one
# that holds neighbours furthest apart: around the full eight-wedge cycle, and
# among the first four on their own, which is what the coarser decomposition
# uses. Running them pale-to-dark instead reads tidily in this list and costs
# half the separation. Reordering by eye undoes it, so measure again if these
# ever change.
SECTOR_COLOURS = (
    (0.678, 0.804, 0.969),  # pale blue
    (0.173, 0.502, 0.882),  # blue
    (0.957, 0.569, 0.431),  # light orange
    (0.627, 0.259, 0.122),  # dark orange
    (0.424, 0.655, 0.949),  # light blue
    (0.847, 0.365, 0.176),  # orange
    (0.976, 0.800, 0.737),  # pale orange
    (0.118, 0.365, 0.655),  # dark blue
)

# The single heaviest observer of the picked target, in weight mode only. Red
# is off the weight ramp on purpose: it is not a weight, it is one camera
# singled out, so it must not read as another step of the blue. Measured 22.8
# away from the nearest step of that ramp, and 6.2:1 against BACKGROUND.
TOP_OBSERVER_COLOUR = (0.902, 0.404, 0.404)

# The picked target itself. Its radius is a fraction of the scene diagonal,
# because bundles differ in scale by an order of magnitude and a marker fixed
# in metres would be a speck on one and a boulder on the next.
TARGET_MARKER_COLOUR = (1.00, 0.84, 0.10)
TARGET_MARKER_FRACTION = 0.0024

# -- route planning --------------------------------------------------------

# A viewpoint in the route, and one the user has taken out of it. Only ever
# worn while planning is on; outside it the glyphs keep their own colours.
# Cyan reads off the model at a glance where a blue sat against the shadowed
# side of it; the one taken out stays grey and out of the way.
ROUTE_SELECTED_COLOUR = (0.15, 0.85, 1.00)
ROUTE_UNSELECTED_COLOUR = (0.34, 0.35, 0.39)

#: What a saved route is called, before the user renames it.
ROUTE_FILENAME = "route.json"

# -- targets nothing can see -----------------------------------------------

# Magenta, and magenta for a reason: the score colouring is a hue ramp from
# blue through green and yellow to red, so magenta is the one hue it can
# never produce. These are the only targets on screen while they are up, but
# they are up against the model behind them, and nothing on it is this colour.
UNOBSERVED_COLOUR = (1.00, 0.10, 0.80)

# Drawn larger than the cloud they were picked out of. With the rest of the
# targets gone what is left can be sparse and far off, and a gap worth seeing
# should not come down to a single pixel.
UNOBSERVED_POINT_GROWTH = 3.0


# -- camera glyphs ---------------------------------------------------------

# How solid a frustum is drawn when it is not the one being looked at and not
# an observer of the picked target - which is to say, nearly all of them.
#
# The two representations want different numbers for the same result. A
# wireframe is a few thin lines and already reads clearly when it is faint;
# filling one in at the same strength leaves a smudge with no edge to it,
# which is what made the solid frustums so hard to make out.
GLYPH_SOLID_OPACITY = 0.85
GLYPH_WIREFRAME_OPACITY = 0.2


# -- flight path -----------------------------------------------------------

#: The line drawn from frustum to frustum through the route, in the order it
#: would be flown. Red, to sit apart from everything else in the scene: the
#: route blues, the gold of the selected camera and the target colours.
FLIGHT_PATH_COLOUR = (0.94, 0.15, 0.18)
FLIGHT_PATH_WIDTH = 3.0


# How far a click may travel, in total, before it counts as a drag of the
# view rather than a pick. Device-independent pixels, summed over the whole
# gesture, so a little hand tremor still reads as a click.
PICK_DRAG_SLOP_PX = 8

# How near the cursor a target has to sit to count as the thing that was
# clicked. Device-independent pixels, measured on screen rather than in
# metres, so the reach is the same however far the view is zoomed out.
PICK_TARGET_RADIUS_PX = 14


@dataclass(frozen=True)
class OverlayOptions:
    """How the picked target is drawn. Plain display state, no VTK in sight."""

    rays: bool = True
    colour_by: str = COLOUR_BY_WEIGHT

    def marker_radius(self, diagonal: float) -> float:
        """The radius of the marker on the picked target, in metres."""
        return float(diagonal) * TARGET_MARKER_FRACTION


# -- startup screen --------------------------------------------------------

# Hex strings, because these are Qt stylesheet values. The VTK colours above
# are 0-1 floats and the two are not interchangeable. Pitched dark, a shade
# above BACKGROUND, so the page and the viewport read as one application.
PAGE = "#121116"
INK = "#F2EFE9"
MUTED = "#918C99"
HAIRLINE = "#2A2831"
CARD = "#1B1A21"
CARD_HOVER = "#232229"
CARD_BORDER = "#2A2831"
CARD_BORDER_HOVER = "#4A4553"
ACCENT = "#8FC5E8"
TRACK = "#26242C"

# Tooltips are top-level windows of their own, so they do not inherit a
# window's stylesheet and come up in the platform's own colours - a pale slab
# against a dark application. Applied once to the QApplication in main, this
# puts them in the same palette as everything else.
TOOLTIP_STYLE = f"""
QToolTip {{
    background: {CARD};
    border: 1px solid {CARD_BORDER_HOVER};
    border-radius: 6px;
    color: {INK};
    font-size: 11px;
    padding: 7px 9px;
}}
"""


TOOLTIP_WIDTH = 290


def tooltip(headline: str, detail: str, width: int = TOOLTIP_WIDTH) -> str:
    """
    A two-part tooltip: what a setting costs, then what it gives you.

    Rich text rather than plain, because Qt lays a long plain tooltip out as a
    single wide slab - the longest of the quality tooltips measured 541px -
    where the same words as rich text wrap to a readable column. The headline
    carries the weight and the detail is dropped to MUTED, so a glance gets the
    gist and a read gets the rest.

    The table is what holds the width: Qt's rich text honours a width on a
    table but not on a div, and without one each tooltip sizes itself to its
    own longest line. Hovering along a row of them then means watching the box
    jump from 255px to 402px and back.
    """
    return (
        f"<table width='{width}' cellspacing='0' cellpadding='0'><tr><td>"
        f"<p style='margin:0'><b>{headline}</b></p>"
        f"<p style='margin:5px 0 0 0; color:{MUTED}'>{detail}</p>"
        "</td></tr></table>"
    )


@dataclass(frozen=True)
class Project:
    """One bundle the startup screen can open."""

    name: str
    subtitle: str
    data_dir: Path
    # The plan size a bundle we ship is known to hold, checked while loading.
    # Projects the user adds bring their own plan, so they leave this None.
    expected_viewpoints: int | None = None

    def as_dict(self) -> dict:
        """The form the startup screen saves an added project in."""
        return {"name": self.name, "subtitle": self.subtitle, "data_dir": str(self.data_dir)}

    @classmethod
    def from_dict(cls, raw: dict) -> Project:
        return cls(
            name=str(raw["name"]),
            subtitle=str(raw.get("subtitle", raw["data_dir"])),
            data_dir=Path(raw["data_dir"]),
        )


PROJECTS = (
    Project(
        name="Kiri Vehera",
        subtitle="Kiri Vehera mesh, targets and viewpoint plan",
        data_dir=DATA_DIR,
        expected_viewpoints=185,
    ),
    Project(
        name="SeaHawk Helicopter",
        subtitle="SH-60 airframe, targets and viewpoint plan",
        data_dir=Path("data/SeaHawk"),
        expected_viewpoints=120,
    ),
    Project(
        name="Formula One",
        subtitle="Formula One car mesh, targets and viewpoint plan",
        data_dir=Path("data/Formula1"),
        expected_viewpoints=120,
    ),
    Project(
        name="The World Trade Center",
        subtitle="WTC mesh, targets and viewpoint plan",
        data_dir=Path("data/WorldTradeCenter"),
        expected_viewpoints=120,
    ),
)
