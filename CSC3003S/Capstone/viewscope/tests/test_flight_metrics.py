"""Unit tests for src/viewscope/data/flight_metrics.py.

The turn is geometry and is checked against angles that can be read off a
sketch. The energy is a model, so what is checked is that it is the model it
says it is: the arithmetic is redone here from the same physics rather than
compared against numbers copied out of a run.
"""

import math

import numpy as np
import pytest

from viewscope.data import (
    GRAVITY,
    SECONDS_PER_HOUR,
    Drone,
    Turn,
    estimate_flight,
    sharpest_turn,
)
from viewscope.data.flight_metrics import _hop_seconds


@pytest.fixture
def drone():
    return Drone()


def turn_in(line) -> Turn:
    """The sharpest turn in a line that has one, which every line here has."""
    turn = sharpest_turn(line)
    assert turn is not None, "this line has a corner to turn at"

    return turn


# -----------------------------------------------------------------------------
# The sharpest turn
# -----------------------------------------------------------------------------


def test_a_straight_line_never_turns():
    """Straight on is 180 degrees, which is the mildest corner there is."""
    line = np.array([[0.0, 0, 0], [5, 0, 0], [12, 0, 0]])

    assert turn_in(line).angle_deg == pytest.approx(180.0)


def test_a_right_angle_is_ninety_degrees():
    line = np.array([[0.0, 0, 0], [10, 0, 0], [10, 10, 0]])

    assert turn_in(line).angle_deg == pytest.approx(90.0)


def test_doubling_back_is_nothing_at_all():
    """The tightest corner a drone can be asked to fly: stop and return."""
    line = np.array([[0.0, 0, 0], [10, 0, 0], [0, 0, 0]])

    assert turn_in(line).angle_deg == pytest.approx(0.0, abs=1e-6)


def test_the_sharpest_of_several_is_the_one_reported():
    line = np.array([[0.0, 0, 0], [10, 0, 0], [10, 10, 0], [10.0, 10, 1]])

    turn = turn_in(line)

    assert turn.angle_deg == pytest.approx(90.0)
    assert turn.corners == 2


def test_the_turn_says_where_it_is_and_how_far_in():
    line = np.array([[0.0, 0, 0], [10, 0, 0], [10, 10, 0], [20, 10, 0]])

    turn = turn_in(line)

    assert turn.index == 1, "the first corner, which is as sharp as the second"
    assert turn.distance_m == pytest.approx(10.0)


def test_a_climb_turns_as_readily_as_a_corner_on_the_ground():
    """Nothing here is measured in the ground plane; a drone flies in three."""
    line = np.array([[0.0, 0, 0], [10, 0, 0], [10, 0, 10]])

    assert turn_in(line).angle_deg == pytest.approx(90.0)


@pytest.mark.parametrize(
    "line",
    [
        np.zeros((0, 3)),
        np.array([[1.0, 2, 3]]),
        np.array([[0.0, 0, 0], [1, 0, 0]]),
    ],
)
def test_a_line_with_no_corner_has_no_turn(line):
    assert sharpest_turn(line) is None


def test_a_point_repeated_is_not_a_corner():
    """A path round a building can leave one; a hop of no length has no way of facing."""
    line = np.array([[0.0, 0, 0], [10, 0, 0], [10, 0, 0], [10, 10, 0]])

    turn = turn_in(line)

    assert turn.corners == 1
    assert turn.angle_deg == pytest.approx(90.0)


# -----------------------------------------------------------------------------
# What it costs to fly
# -----------------------------------------------------------------------------


def test_hover_power_is_momentum_theory_and_the_losses_after_it(drone):
    thrust = drone.mass_kg * GRAVITY
    ideal = thrust**1.5 / math.sqrt(2.0 * drone.air_density * drone.disc_area_m2)
    expected = ideal / (drone.figure_of_merit * drone.drive_efficiency) + drone.avionics_w

    assert drone.hover_power_w == pytest.approx(expected)


def test_a_bigger_disc_costs_less_to_hold_up():
    """Momentum theory's one big claim, and a reason survey drones have big props."""
    small = Drone(rotor_radius_m=0.10)
    large = Drone(rotor_radius_m=0.20)

    assert large.hover_power_w < small.hover_power_w


def test_a_long_hop_cruises_between_its_ramps(drone):
    """Long enough to reach cruising speed: the ramps cost one speed-up in time."""
    far = 500.0
    line = np.array([[0.0, 0, 0], [far, 0, 0]])

    flight = estimate_flight(line, stops=0, drone=drone)

    expected = far / drone.cruise_speed_ms + drone.cruise_speed_ms / drone.acceleration_ms2
    assert flight.flying_seconds == pytest.approx(expected)


def test_a_short_hop_never_gets_up_to_speed(drone):
    """Half of it accelerating, half of it braking, and no cruise in between."""
    near = 1.0
    line = np.array([[0.0, 0, 0], [near, 0, 0]])

    flight = estimate_flight(line, stops=0, drone=drone)

    assert flight.flying_seconds == pytest.approx(2.0 * math.sqrt(near / drone.acceleration_ms2))


def test_every_stop_is_dwelt_at_for_its_photograph(drone):
    line = np.array([[0.0, 0, 0], [50, 0, 0], [50, 50, 0]])

    flight = estimate_flight(line, stops=3, drone=drone)

    assert flight.dwelling_seconds == pytest.approx(3 * drone.dwell_s)
    assert flight.seconds == pytest.approx(flight.flying_seconds + flight.dwelling_seconds)


def test_the_energy_is_the_power_over_the_time(drone):
    line = np.array([[0.0, 0, 0], [120, 0, 0], [120, 90, 0]])

    flight = estimate_flight(line, stops=3, drone=drone)

    assert flight.energy_wh == pytest.approx(
        drone.hover_power_w * flight.seconds / SECONDS_PER_HOUR
    )
    assert flight.energy_kj == pytest.approx(flight.energy_wh * 3.6)


def test_the_battery_share_is_of_one_pack(drone):
    line = np.array([[0.0, 0, 0], [400, 0, 0]])

    flight = estimate_flight(line, stops=2, drone=drone)

    assert flight.battery_share == pytest.approx(flight.energy_wh / drone.battery_wh)


def test_a_flight_longer_than_a_pack_says_so():
    """A route worth flagging: it cannot be flown without landing to swap."""
    thirsty = Drone(battery_wh=1.0)
    line = np.array([[0.0, 0, 0], [400, 0, 0]])

    flight = estimate_flight(line, stops=2, drone=thirsty)

    assert flight.battery_share > 1.0
    assert not flight.within_one_battery


def test_a_path_of_one_viewpoint_costs_only_its_dwell(drone):
    flight = estimate_flight(np.array([[1.0, 2, 3]]), stops=1, drone=drone)

    assert flight.distance_m == pytest.approx(0.0)
    assert flight.flying_seconds == pytest.approx(0.0)
    assert flight.seconds == pytest.approx(drone.dwell_s)


def test_the_distance_flown_is_the_line_as_given(drone):
    line = np.array([[0.0, 0, 0], [30, 0, 0], [30, 40, 0]])

    assert estimate_flight(line, drone=drone).distance_m == pytest.approx(70.0)


def test_stops_default_to_the_points_of_the_line(drone):
    line = np.array([[0.0, 0, 0], [30, 0, 0], [30, 40, 0]])

    assert estimate_flight(line, drone=drone).stops == 3


# -----------------------------------------------------------------------------
# Hops that cost nothing
# -----------------------------------------------------------------------------


def test_a_hop_of_no_length_takes_no_time(drone):
    """Repeated points are dropped upstream, but the arithmetic below would
    divide by a zero-length hop, so it is refused here rather than there."""
    assert _hop_seconds(0.0, drone) == 0.0


def test_a_negative_hop_takes_no_time(drone):
    assert _hop_seconds(-5.0, drone) == 0.0


def test_a_drone_that_cannot_move_is_costed_at_nothing_rather_than_forever(drone):
    """Zero speed would otherwise divide by zero and report an infinite flight."""
    from dataclasses import replace

    assert _hop_seconds(10.0, replace(drone, cruise_speed_ms=0.0)) == 0.0
    assert _hop_seconds(10.0, replace(drone, acceleration_ms2=0.0)) == 0.0


def test_a_standing_still_drone_still_reports_its_dwell_and_hover_cost(drone):
    """The battery drains while hovering even when nothing is flown."""
    from dataclasses import replace

    flight = estimate_flight(
        [[0.0, 0.0, 5.0], [10.0, 0.0, 5.0]], drone=replace(drone, cruise_speed_ms=0.0)
    )

    assert flight.flying_seconds == 0.0
    assert flight.dwelling_seconds > 0.0
    assert flight.energy_wh > 0.0
