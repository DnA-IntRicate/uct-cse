"""Unit tests for src/viewscope/data/route.py."""

import json

import numpy as np
import pytest

import viewscope_core as vc
from viewscope.data import ROUTE_VERSION, SECTORS, RoutePlan, count_sectors, load_route


@pytest.fixture
def plan():
    """A four viewpoint plan, the shape load_plan hands back."""
    return vc.Plan(
        camera={"width": 1368, "height": 912, "yfov_deg": 53.13},
        ids=("vp000", "vp001", "vp002", "vp003"),
        positions=np.array([[0.0, 0.0, 5.0], [1.0, 0.0, 5.0], [2.0, 0.0, 5.0], [3.0, 0.0, 5.0]]),
        yaws_deg=np.array([0.0, 90.0, 180.0, -90.0]),
        pitches_deg=np.array([-10.0, -20.0, -30.0, -40.0]),
    )


@pytest.fixture
def route():
    return RoutePlan()


# -----------------------------------------------------------------------------
# Selecting
# -----------------------------------------------------------------------------


def test_a_fresh_route_is_empty_and_not_planning(route):
    assert not route.planning
    assert route.selected == ()
    assert len(route) == 0


def test_planning_starts_with_every_camera_in(route):
    route.start(4)

    assert route.planning
    assert route.selected == (0, 1, 2, 3)


def test_toggling_takes_a_camera_out_and_puts_it_back(route):
    route.start(4)

    assert route.toggle(2) is False
    assert route.selected == (0, 1, 3)
    assert 2 not in route

    assert route.toggle(2) is True
    assert route.selected == (0, 1, 2, 3)
    assert 2 in route


def test_unselecting_all_empties_the_route_without_leaving_planning(route):
    route.start(4)

    route.clear()

    assert route.selected == ()
    assert route.planning


def test_select_all_puts_them_back(route):
    route.start(4)
    route.clear()

    route.select_all(4)

    assert route.selected == (0, 1, 2, 3)


def test_stopping_keeps_the_selection(route):
    """Stopping is for saving, not for throwing the route away."""
    route.start(4)
    route.toggle(0)

    route.stop()

    assert not route.planning
    assert route.selected == (1, 2, 3)


def test_rows_a_shrinking_plan_no_longer_has_are_dropped(route):
    route.start(6)

    route.forget_beyond(4)

    assert route.selected == (0, 1, 2, 3)


def test_selected_rows_come_back_ascending_however_they_went_in(route):
    for index in (3, 0, 2):
        route.toggle(index)

    assert route.selected == (0, 2, 3)


# -----------------------------------------------------------------------------
# Reporting
# -----------------------------------------------------------------------------


def test_status_labels_each_row_with_its_plan_id(route, plan):
    route.start(4)
    route.toggle(1)

    status = route.status(plan, observed=90, targets=100)

    assert status.selected == (0, 2, 3)
    assert status.labels == ("vp000", "vp002", "vp003")
    assert status.camera_count == 4
    assert status.coverage == pytest.approx(0.9)


def test_coverage_of_a_scene_with_no_targets_is_zero(route, plan):
    route.start(4)

    assert route.status(plan, observed=0, targets=0).coverage == 0.0


# -----------------------------------------------------------------------------
# Sectors of the ground plane
# -----------------------------------------------------------------------------


@pytest.fixture
def sector_plan():
    """Eight viewpoints, one squarely in the middle of each sector."""
    middles = np.arange(SECTORS) * (2.0 * np.pi / SECTORS) + np.pi / SECTORS
    positions = np.stack(
        [10.0 * np.cos(middles), 10.0 * np.sin(middles), np.full(SECTORS, 5.0)], axis=1
    )

    return vc.Plan(
        camera={"width": 1368, "height": 912, "yfov_deg": 53.13},
        ids=tuple(f"s{sector + 1}" for sector in range(SECTORS)),
        positions=positions,
        yaws_deg=np.zeros(SECTORS),
        pitches_deg=np.full(SECTORS, -20.0),
    )


def test_each_sector_takes_the_camera_standing_in_it(sector_plan):
    assert count_sectors(sector_plan.positions) == (1,) * SECTORS


def test_the_plane_is_cut_into_eighths(sector_plan):
    """Four quadrants hide a route that covers two faces of a building twice."""
    assert SECTORS == 8
    assert len(count_sectors(sector_plan.positions)) == 8


def test_a_camera_high_above_the_plane_is_still_in_its_own_sector():
    """Sectors are read off x and y; height has nothing to say about them."""
    low = count_sectors(np.array([[3.0, 4.0, 0.0]]))
    high = count_sectors(np.array([[3.0, 4.0, 500.0]]))

    assert low == high
    assert low[1] == 1, "53 degrees round, which is the second eighth"


def test_the_direction_from_the_model_is_what_picks_the_sector():
    positions = np.array(
        [
            [10.0, 1.0, 1.0],  # 6 degrees round -> 1
            [1.0, 10.0, 1.0],  # 84 -> 2
            [-10.0, 1.0, 1.0],  # 174 -> 4
            [1.0, -10.0, 1.0],  # 276 -> 7
            [9.0, 2.0, 1.0],  # 13 -> 1 again
        ]
    )

    assert count_sectors(positions) == (2, 1, 0, 1, 0, 0, 1, 0)


def test_a_camera_on_a_boundary_falls_in_the_sector_that_boundary_opens():
    """One camera on each of the eight lines, each counting in the wedge after it."""
    edges = np.array(
        [[1, 0], [1, 1], [0, 1], [-1, 1], [-1, 0], [-1, -1], [0, -1], [1, -1]], dtype=float
    )
    positions = np.concatenate([edges * 7.0, np.ones((SECTORS, 1))], axis=1)

    assert count_sectors(positions) == (1,) * SECTORS


def test_a_camera_on_the_origin_counts_in_the_first_sector():
    assert count_sectors(np.array([[0.0, 0.0, 5.0]])) == (1, 0, 0, 0, 0, 0, 0, 0)


def test_no_cameras_leaves_every_sector_empty():
    assert count_sectors(np.zeros((0, 3))) == (0,) * SECTORS


def test_sectors_are_measured_about_the_model_not_about_the_world():
    """A bundle carrying a larger survey's coordinates sits nowhere near 0, 0.

    Read from the world origin every one of these cameras is +x +y, which says
    only that the model is north east of it. Read from the model they surround
    it, which is the thing route planning is asking about.
    """
    ring = np.array(
        [
            [205.0, 125.0, 5.0],
            [165.0, 125.0, 5.0],
            [165.0, 95.0, 5.0],
            [205.0, 95.0, 5.0],
        ]
    )

    assert count_sectors(ring) == (4, 0, 0, 0, 0, 0, 0, 0)
    assert count_sectors(ring, (185.0, 110.0)) == (1, 0, 0, 1, 1, 0, 0, 1)


def test_a_three_component_centre_is_taken_as_its_ground_plane_part():
    """`SceneData.centre` is a point in space; only its x and y matter here."""
    camera = np.array([[9.0, 9.0, 1.0]])

    assert count_sectors(camera, np.array([10.0, 10.0, 500.0])) == (0, 0, 0, 0, 0, 1, 0, 0)


def test_a_camera_at_the_centre_counts_in_the_first_sector():
    assert count_sectors(np.array([[7.0, 3.0, 5.0]]), (7.0, 3.0)) == (1, 0, 0, 0, 0, 0, 0, 0)


def test_how_many_sectors_to_cut_into_can_be_asked_for():
    """Eight is what the panel draws; the count itself is not baked in."""
    quarters = count_sectors(np.array([[1.0, 1.0, 0.0], [-1.0, -1.0, 0.0]]), sectors=4)

    assert quarters == (1, 0, 1, 0)


def test_status_measures_from_the_origin_it_is_given(route, sector_plan):
    """The same plan, read from outside itself rather than from its middle.

    This is the shape of the bug it guards: seen from far enough away every
    camera falls in one sector, however well the route surrounds the model.
    """
    route.start(SECTORS)

    assert route.status(sector_plan).sectors == (1,) * SECTORS
    assert route.status(sector_plan, origin=(-1000.0, -414.0)).sectors == (8, 0, 0, 0, 0, 0, 0, 0)


def test_status_counts_only_the_cameras_left_in_the_route(route, sector_plan):
    route.start(SECTORS)
    for row in (1, 2, 3, 5, 6, 7):
        route.toggle(row)

    status = route.status(sector_plan)

    assert status.sectors == (1, 0, 0, 0, 1, 0, 0, 0)
    assert status.sector_shares == (0.5, 0.0, 0.0, 0.0, 0.5, 0.0, 0.0, 0.0)


def test_shares_of_an_empty_route_are_zero_rather_than_eight_equal_bars(route, sector_plan):
    status = route.status(sector_plan)

    assert status.sectors == (0,) * SECTORS
    assert status.sector_shares == (0.0,) * SECTORS


def test_a_route_with_no_plan_behind_it_has_no_sectors(route):
    assert route.status(None).sectors == ()
    assert route.status(None).sector_shares == ()


def test_rows_beyond_the_plan_are_left_out_of_the_sectors(route, sector_plan):
    """A route carried over from a longer plan still counts what it can."""
    route.start(SECTORS + 2)

    status = route.status(sector_plan)

    assert len(status.selected) == SECTORS + 2
    assert sum(status.sectors) == SECTORS


# -----------------------------------------------------------------------------
# Saving
# -----------------------------------------------------------------------------


def test_the_document_holds_only_the_chosen_viewpoints(route, plan):
    route.start(4)
    route.toggle(1)

    document = route.document(plan, observed=90, targets=100)

    assert document["version"] == ROUTE_VERSION
    assert [vp["id"] for vp in document["viewpoints"]] == ["vp000", "vp002", "vp003"]
    assert document["viewpoints"][1]["position"] == [2.0, 0.0, 5.0]
    assert document["viewpoints"][1]["yaw_deg"] == pytest.approx(180.0)
    assert document["coverage"] == {
        "targets": 100,
        "observed": 90,
        "fraction": pytest.approx(0.9),
        "cameras": 3,
        "cameras_available": 4,
    }


def test_a_saved_route_loads_straight_back_as_a_plan(route, plan, tmp_path):
    """The whole point of the format: the route is itself a plan.json."""
    route.start(4)
    route.toggle(3)

    written = route.save(tmp_path / "route.json", plan, observed=50, targets=60)

    reloaded = vc.load_plan(written)
    assert reloaded.ids == ("vp000", "vp001", "vp002")
    assert reloaded.camera == plan.camera
    np.testing.assert_allclose(reloaded.positions, plan.positions[:3])


def test_saving_an_empty_route_is_refused_by_the_plan_loader(route, plan, tmp_path):
    """A route with nothing in it is a file, but it is not a flyable plan."""
    written = route.save(tmp_path / "empty.json", plan)

    assert json.loads(written.read_text())["viewpoints"] == []
    with pytest.raises(ValueError, match="viewpoints must be a non empty list"):
        vc.load_plan(written)


# -----------------------------------------------------------------------------
# The file the route belongs to
# -----------------------------------------------------------------------------


def test_a_route_planned_from_scratch_belongs_to_no_file(route):
    assert route.path is None


def test_saving_makes_the_route_belong_to_what_it_was_written_to(route, plan, tmp_path):
    """So stopping again offers that file rather than starting the naming over."""
    route.start(4)

    written = route.save(tmp_path / "somewhere.json", plan)

    assert route.path == written


def test_a_route_read_out_of_a_file_belongs_to_it(route, tmp_path):
    route.came_from(tmp_path / "loaded.json")

    assert route.path == tmp_path / "loaded.json"


def test_a_loaded_route_saved_back_belongs_to_wherever_it_went(route, plan, tmp_path):
    """Save-as moves it: what is offered next is where it last went."""
    route.came_from(tmp_path / "loaded.json")
    route.start(4)

    route.save(tmp_path / "elsewhere.json", plan)

    assert route.path == tmp_path / "elsewhere.json"


def test_another_bundle_takes_the_file_away(route, tmp_path):
    """One bundle's route.json is not the next one's to overwrite."""
    route.came_from(tmp_path / "loaded.json")

    route.forget_file()

    assert route.path is None


def test_leaving_planning_keeps_the_file(route, plan, tmp_path):
    """Exit saves nothing, but the route is still the one that file holds."""
    route.came_from(tmp_path / "loaded.json")
    route.start(4)

    route.stop()

    assert route.path == tmp_path / "loaded.json"


# -----------------------------------------------------------------------------
# Loading
# -----------------------------------------------------------------------------


def _write(tmp_path, document, name="loaded.json"):
    path = tmp_path / name
    path.write_text(json.dumps(document))

    return path


def test_a_route_this_application_saved_loads_back(route, plan, tmp_path):
    """The round trip the Load route button rests on."""
    route.start(4)
    route.toggle(1)
    written = route.save(tmp_path / "route.json", plan, observed=50, targets=60)

    entries = load_route(written)

    assert [entry.id for entry in entries] == ["vp000", "vp002", "vp003"]
    np.testing.assert_allclose(entries[1].position, plan.positions[2])
    assert entries[1].yaw_deg == pytest.approx(180.0)
    assert entries[1].pitch_deg == pytest.approx(-30.0)


def test_a_plan_that_is_not_json_is_refused(tmp_path):
    path = tmp_path / "broken.json"
    path.write_text("{not json")

    with pytest.raises(ValueError, match="not valid json"):
        load_route(path)


def test_a_file_that_is_not_there_is_refused(tmp_path):
    with pytest.raises(ValueError, match="could not be read"):
        load_route(tmp_path / "missing.json")


def test_a_document_naming_no_viewpoints_is_refused(tmp_path):
    with pytest.raises(ValueError, match="names no viewpoints"):
        load_route(_write(tmp_path, {"version": 1, "viewpoints": []}))


def test_the_same_viewpoint_twice_is_refused(tmp_path):
    viewpoint = {"id": "vp000", "position": [0.0, 0.0, 5.0], "yaw_deg": 0.0, "pitch_deg": -10.0}

    with pytest.raises(ValueError, match="more than once"):
        load_route(_write(tmp_path, {"viewpoints": [viewpoint, dict(viewpoint)]}))


@pytest.mark.parametrize(
    ("viewpoint", "message"),
    [
        ({"position": [0.0, 0.0, 5.0], "yaw_deg": 0.0, "pitch_deg": 0.0}, "has no id"),
        (
            {"id": "vp000", "position": [0.0, 0.0], "yaw_deg": 0.0, "pitch_deg": 0.0},
            "three numbers",
        ),
        ({"id": "vp000", "position": [0.0, 0.0, 5.0], "pitch_deg": 0.0}, "not a finite number"),
        (
            {"id": "vp000", "position": [0.0, 0.0, 5.0], "yaw_deg": 0.0, "pitch_deg": 90.0},
            "too close to vertical",
        ),
    ],
)
def test_a_viewpoint_that_cannot_be_flown_is_refused(tmp_path, viewpoint, message):
    with pytest.raises(ValueError, match=message):
        load_route(_write(tmp_path, {"viewpoints": [viewpoint]}))


# -----------------------------------------------------------------------------
# Selecting and resuming
# -----------------------------------------------------------------------------


def test_select_replaces_the_route_with_exactly_those_rows():
    """Unlike toggle, this is not additive: what is passed in is the whole route."""
    plan = RoutePlan()
    plan.select([3, 1, 2])
    assert plan.selected == (1, 2, 3)

    plan.select([5])
    assert plan.selected == (5,)


def test_select_takes_any_integer_like_index():
    plan = RoutePlan()
    plan.select(np.array([2, 0]))
    assert plan.selected == (0, 2)


def test_resume_carries_on_with_what_is_already_there():
    """Reopening a saved route puts the user back into planning, rows intact."""
    plan = RoutePlan()
    plan.select([1, 4])
    assert not plan.planning

    plan.resume()

    assert plan.planning
    assert plan.selected == (1, 4)


# -----------------------------------------------------------------------------
# Route files that cannot be flown
# -----------------------------------------------------------------------------


def test_a_route_file_holding_a_bare_list_is_not_a_document(tmp_path):
    path = tmp_path / "route.json"
    path.write_text("[1, 2, 3]")

    with pytest.raises(ValueError, match="is not a route document"):
        load_route(path)


def test_a_viewpoint_that_is_not_an_object_is_refused(tmp_path):
    path = tmp_path / "route.json"
    path.write_text(json.dumps({"viewpoints": ["vp000"]}))

    with pytest.raises(ValueError, match="viewpoint 0 is not an object"):
        load_route(path)


def test_a_position_holding_something_non_numeric_is_refused(tmp_path):
    """Three entries, so the shape check passes and the float cast is what fails."""
    path = tmp_path / "route.json"
    path.write_text(
        json.dumps(
            {
                "viewpoints": [
                    {"id": "vp000", "position": [0, 0, "up"], "yaw_deg": 0, "pitch_deg": 0}
                ]
            }
        )
    )

    with pytest.raises(ValueError, match="pose that is not numeric"):
        load_route(path)
