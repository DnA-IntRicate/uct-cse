"""Unit tests for src/viewscope/data/flight_path.py."""

import numpy as np
import pytest
import trimesh

import viewscope.data.flight_path as fp
from viewscope.data import Obstacle, plan_path

# -----------------------------------------------------------------------------
# Fixtures
# -----------------------------------------------------------------------------


@pytest.fixture
def grid():
    """An 8x8 unit grid, whose shortest path is known to be exactly 63."""
    return np.array([[float(x), float(y), 0.0] for x in range(8) for y in range(8)])


@pytest.fixture
def cloud():
    """A repeatable scatter, for the cases where only the shape matters."""
    return np.random.default_rng(7).uniform(0.0, 100.0, size=(60, 3))


@pytest.fixture
def block():
    """A solid 20 m cube at the origin, as something to fly around."""
    return Obstacle.from_mesh(trimesh.creation.box(extents=[20.0, 20.0, 20.0]))


@pytest.fixture
def ring():
    """Eight viewpoints in a circle round the cube, at its waist."""
    angles = np.linspace(0.0, 2.0 * np.pi, 9)[:-1]

    return np.column_stack([18.0 * np.cos(angles), 18.0 * np.sin(angles), np.zeros(8)])


def fouls(obstacle: Obstacle, path) -> int:
    """How many segments of a planned path pass through the building."""
    return int(obstacle.blocks(path.points[:-1], path.points[1:]).sum())


def flies_through(path, position) -> bool:
    """Whether the drawn line actually passes through this viewpoint."""
    return bool(np.isclose(path.points, position).all(axis=1).any())


@pytest.fixture
def unpulled():
    """Plan one path without taking the slack out, to measure what pulling saves.

    Scoped to the single call, so a test can plan it both ways and compare.
    """

    def plan(positions, obstacle):
        with pytest.MonkeyPatch.context() as patched:
            patched.setattr(
                fp, "_string_pull", lambda line, stops, obstacle: np.asarray(line).reshape(-1, 3)
            )

            return plan_path(positions, obstacle)

    return plan


@pytest.fixture
def opposite_faces():
    """Two viewpoints on opposite faces of the block, with the block between."""
    return np.array([[-18.0, 0.0, 0.0], [18.0, 0.0, 0.0]])


@pytest.fixture
def long_wall():
    """A wall too long to walk round, so a hop across it has to climb."""
    return Obstacle.from_mesh(trimesh.creation.box(extents=[2.0, 120.0, 30.0]))


@pytest.fixture
def either_side():
    """One viewpoint each side of the long wall."""
    return np.array([[-10.0, -45.0, 0.0], [10.0, -45.0, 0.0]])


# -----------------------------------------------------------------------------
# What comes back
# -----------------------------------------------------------------------------


def test_every_viewpoint_is_flown_exactly_once(cloud):
    assert sorted(plan_path(cloud).order) == list(range(len(cloud)))


def test_an_empty_route_has_no_path():
    assert plan_path(np.zeros((0, 3))).order == ()


def test_one_viewpoint_is_a_path_of_one():
    assert plan_path(np.array([[1.0, 2.0, 3.0]])).order == (0,)


def test_two_viewpoints_have_only_one_path_between_them():
    """There is nothing to choose, so they come back the way they went in."""
    pair = np.array([[9.0, 9.0, 9.0], [0.0, 0.0, 0.0]])

    assert plan_path(pair).order == (0, 1)


def test_viewpoints_in_a_line_are_flown_along_it():
    """Shuffled into the plan; the path has to put them back in order."""
    line = np.array([[4.0, 0.0, 0.0], [0.0, 0.0, 0.0], [3.0, 0.0, 0.0], [1.0, 0.0, 0.0]])

    path = plan_path(line)

    assert path.length == pytest.approx(4.0)
    assert path.order in {(1, 3, 2, 0), (0, 2, 3, 1)}


def test_a_path_planned_against_nothing_does_not_claim_to_be_clear(cloud):
    """`clear` is a promise about a building, not a default."""
    path = plan_path(cloud)

    assert not path.checked
    assert not path.clear


# -----------------------------------------------------------------------------
# How good the path is
# -----------------------------------------------------------------------------


def test_a_grid_is_flown_by_its_shortest_path(grid):
    """Row by row, 63 unit hops. Anything longer means a hop was wasted."""
    assert plan_path(grid).length == pytest.approx(63.0)


def test_the_path_is_far_shorter_than_flying_the_plan_in_order(cloud):
    in_order = float(np.linalg.norm(np.diff(cloud, axis=0), axis=1).sum())

    assert plan_path(cloud).length < 0.5 * in_order


def test_two_clusters_are_crossed_between_once():
    """The path visits one cluster, crosses, and stays: never back and forth."""
    rng = np.random.default_rng(3)
    near = rng.uniform(0.0, 5.0, size=(20, 3))
    far = rng.uniform(0.0, 5.0, size=(20, 3)) + np.array([500.0, 0.0, 0.0])
    both = np.vstack([near, far])

    flown = both[list(plan_path(both).order)]

    assert np.count_nonzero(np.abs(np.diff(flown[:, 0])) > 100.0) == 1


# -----------------------------------------------------------------------------
# Staying out of the building
# -----------------------------------------------------------------------------


def test_a_hop_straight_through_the_building_is_blocked(block):
    across = block.blocks([[-18.0, 0.0, 0.0]], [[18.0, 0.0, 0.0]])

    assert bool(across[0])


def test_a_hop_that_misses_the_building_is_not_blocked(block):
    past = block.blocks([[-18.0, 40.0, 0.0]], [[18.0, 40.0, 0.0]])

    assert not bool(past[0])


def test_a_viewpoint_above_the_building_is_not_inside_it(block):
    """The grid stops at the model; beyond it is open air, not a wall.

    Read the other way round - anything off the grid clipped onto its face -
    a viewpoint over the roof is walled in and reaches nothing.
    """
    overhead = block.blocks([[0.0, 0.0, 40.0]], [[18.0, 0.0, 40.0]])

    assert not bool(overhead[0])


def test_a_viewpoint_pressed_against_the_building_still_reaches_its_neighbours():
    """Kept clear of, a survey viewpoint can sit inside the grown surface.

    Counting that as a wall would strike out every hop it has and strand it,
    so the cell at either end of a hop has no say in whether it is blocked.
    """
    wall = Obstacle.from_mesh(trimesh.creation.box(extents=[20.0, 20.0, 20.0]))
    against = np.array([[10.2, 0.0, 0.0], [10.2, 4.0, 0.0]])

    assert not bool(wall.blocks(against[:1], against[1:])[0])


def test_the_path_round_a_block_never_goes_through_it(block, ring):
    path = plan_path(ring, block)

    assert path.clear
    assert fouls(block, path) == 0
    assert sorted(path.order) == list(range(len(ring)))


def test_avoiding_the_building_beats_ignoring_it(block):
    """Two viewpoints on opposite faces: straight across is through it."""
    across = np.array([[-18.0, 0.0, 0.0], [18.0, 0.0, 0.0], [0.0, 18.0, 0.0]])

    assert fouls(block, plan_path(across)) > 0
    assert fouls(block, plan_path(across, block)) == 0


def test_a_hop_with_no_way_round_climbs_over_the_top():
    """A wall too long to walk round is flown over instead."""
    wall = Obstacle.from_mesh(trimesh.creation.box(extents=[2.0, 120.0, 30.0]))
    either_side = np.array(
        [[-10.0, y, 0.0] for y in (-55.0, -45.0, -35.0)]
        + [[10.0, y, 0.0] for y in (-55.0, -45.0, -35.0)]
    )

    path = plan_path(either_side, wall)

    assert path.clear
    assert path.climbs == 1
    assert fouls(wall, path) == 0
    assert path.points[:, 2].max() >= wall.ceiling


def test_viewpoints_walled_into_a_courtyard_are_still_all_flown():
    """Inside a ring wall and outside it, with no gate between them."""
    walls = Obstacle.from_mesh(trimesh.creation.annulus(r_min=12.0, r_max=14.0, height=20.0))
    angles = np.linspace(0.0, 2.0 * np.pi, 9)[:-1]
    inside = np.column_stack([8.0 * np.cos(angles), 8.0 * np.sin(angles), np.zeros(8)])
    outside = np.column_stack([20.0 * np.cos(angles), 20.0 * np.sin(angles), np.zeros(8)])
    yard = np.vstack([inside, outside])

    path = plan_path(yard, walls)

    assert path.clear
    assert fouls(walls, path) == 0
    assert sorted(path.order) == list(range(len(yard)))


def test_going_round_costs_distance_and_says_so(block):
    """The promise is a clear path, not the shortest one; both are reported."""
    across = np.array([[-18.0, 0.0, 0.0], [18.0, 0.0, 0.0], [0.0, 18.0, 0.0]])

    straight = plan_path(across)
    round_it = plan_path(across, block)

    assert round_it.length > straight.length
    assert round_it.avoidances == round_it.detours + round_it.climbs
    assert round_it.avoidances >= 1


def test_a_route_of_one_viewpoint_is_clear_by_default(block):
    assert plan_path(np.array([[18.0, 0.0, 0.0]]), block).clear


# -----------------------------------------------------------------------------
# Pulling the line taut
# -----------------------------------------------------------------------------


def test_pulling_shortens_the_way_over_a_building(unpulled, block, opposite_faces):
    """The box the search finds is not the way a pilot would fly it.

    Two viewpoints on opposite faces with nothing else in the route to go
    round by: straight up, across the top, straight down. Pulled, the climb
    leans over the corner instead.
    """
    box = unpulled(opposite_faces, block)
    pulled = plan_path(opposite_faces, block)

    assert box.climbs == 1
    assert pulled.length < 0.9 * box.length


def test_a_pulled_line_is_still_clear_of_the_building(
    long_wall, either_side, block, opposite_faces
):
    """Shorter is only worth having if every segment left was checked."""
    over_a_wall = plan_path(either_side, long_wall)
    round_a_block = plan_path(opposite_faces, block)

    assert fouls(long_wall, over_a_wall) == 0 and over_a_wall.clear
    assert fouls(block, round_a_block) == 0 and round_a_block.clear


def test_pulling_never_lengthens_a_path(unpulled, block, ring):
    """Cutting a corner off cannot make the way round longer."""
    across = np.vstack([ring, [[0.0, 0.0, 40.0]]])

    assert plan_path(across, block).length <= unpulled(across, block).length + 1e-9


def test_pulling_does_not_skip_a_viewpoint(block):
    """A shorter line that misses a viewpoint is not a saving, it is a bug."""
    angles = np.linspace(0.0, 2.0 * np.pi, 7)[:-1]
    ring = np.column_stack([18.0 * np.cos(angles), 18.0 * np.sin(angles), np.zeros(6)])

    path = plan_path(ring, block)

    assert sorted(path.order) == list(range(len(ring)))
    for row in path.order:
        assert flies_through(path, ring[row])


def test_a_route_flown_entirely_straight_is_left_alone(unpulled, block):
    """No detour, no slack: pulling has nothing to do and must not fidget."""
    clear_of_it = np.array([[40.0, 0.0, 0.0], [40.0, 10.0, 0.0], [40.0, 20.0, 0.0]])

    path = plan_path(clear_of_it, block)

    assert path.detours == 0 and path.climbs == 0
    assert np.array_equal(path.points, unpulled(clear_of_it, block).points)


def test_pulling_bends_the_line_at_the_building_not_at_right_angles(block, opposite_faces):
    """The climb leaves at a lean, rather than going straight up and along."""
    first = plan_path(opposite_faces, block).points[1] - opposite_faces[0]

    assert not np.isclose(first[0], 0.0), "the first leg is still a vertical climb"
    assert first[2] > 0.0, "and it is still a climb"


def test_resampling_keeps_both_ends_of_a_stretch():
    """The ends are the viewpoints; everything between them is negotiable."""
    stretch = np.array([[0.0, 0.0, 0.0], [0.0, 0.0, 10.0], [10.0, 0.0, 10.0]])

    walked = fp._resample(stretch, 1.0)

    assert np.allclose(walked[0], stretch[0])
    assert np.allclose(walked[-1], stretch[-1])
    assert len(walked) > len(stretch)


def test_resampling_a_stretch_that_never_moves_keeps_its_ends():
    """A degenerate stretch must still hand back something to fly to."""
    still = np.repeat([[3.0, 4.0, 5.0]], 4, axis=0)

    assert len(fp._resample(still, 1.0)) == 2


def test_a_pull_that_would_foul_the_building_is_thrown_away(block, opposite_faces):
    """The sweep is checked over before it is kept, so its output is clear.

    Whatever the shortcut sweep hands back, what comes out of planning never
    fouls: the sweep is verified with the same test the rest of the module
    uses, and a sweep that fails it is discarded for the way round as found.
    """
    with pytest.MonkeyPatch.context() as patched:
        # A sweep that "shortcuts" straight through the middle of the block.
        patched.setattr(fp, "_shortcut", lambda stretch, obstacle: stretch[[0, -1]])

        path = plan_path(opposite_faces, block)

    assert fouls(block, path) == 0
    assert path.clear


def test_a_hop_is_judged_the_same_whatever_it_is_asked_alongside(block):
    """Sampling is measured from the start of each hop, not across the batch.

    Judged as a fraction of the longest hop in hand, the same hop moves its
    own sample points about and can come back clear one time and blocked the
    next, which leaves the drawn line disagreeing with the check on it.
    """
    start = np.array([-18.0, 0.0, 0.0])
    end = np.array([18.0, 0.0, 0.0])
    direction = (end - start) / np.linalg.norm(end - start)

    alone = bool(block.blocks([start], [end])[0])
    alongside = [
        bool(block.blocks([start, start], [end, start + direction * span])[0])
        for span in (10.0, 40.0, 90.0, 250.0)
    ]

    assert all(verdict == alone for verdict in alongside)


# -----------------------------------------------------------------------------
# An obstacle built cell by cell, where the geometry has to be exact
# -----------------------------------------------------------------------------


def walled(shape=(9, 9, 4)) -> Obstacle:
    """A wall straight across the middle of a box of cells, floor to ceiling."""
    filled = np.zeros(shape, dtype=bool)
    filled[:, shape[1] // 2, :] = True

    return Obstacle(filled, origin=(0.0, 0.0, 0.0), pitch=1.0)


def roofed() -> Obstacle:
    """A wall with a lid on it, so there is no way over the top either."""
    filled = np.zeros((9, 9, 4), dtype=bool)
    filled[:, 4, :] = True
    filled[:, :, -1] = True

    return Obstacle(filled, origin=(0.0, 0.0, 0.0), pitch=1.0)


def test_a_hop_can_climb_over_a_wall():
    obstacle = walled()

    way = obstacle.over_the_top([4.5, 1.5, 0.5], [4.5, 7.5, 0.5])

    assert way is not None
    assert len(way) == 2
    assert way[0][2] == way[1][2] > obstacle.ceiling - 1e-9


def test_a_hop_under_a_lid_cannot_climb_over_it():
    """The crossing leg is clear by definition; the climbs are not."""
    assert roofed().over_the_top([4.5, 1.5, 0.5], [4.5, 7.5, 0.5]) is None


# -----------------------------------------------------------------------------
# Degenerate inputs
# -----------------------------------------------------------------------------


def test_nothing_to_check_blocks_nothing():
    blocked = walled().blocks(np.zeros((0, 3)), np.zeros((0, 3)))

    assert blocked.shape == (0,)
    assert not blocked.any()


def test_a_single_viewpoint_has_no_pairs_to_block():
    blocked = walled().blocked_pairs(np.array([[1.0, 1.0, 1.0]]))

    assert blocked.shape == (1, 1)
    assert not blocked.any()


def test_no_viewpoints_at_all_has_no_pairs():
    assert walled().blocked_pairs(np.zeros((0, 3))).shape == (0, 0)


def test_a_line_of_one_point_fouls_nothing():
    assert fp._fouls(np.array([[1.0, 1.0, 1.0]]), walled()) is False


# -----------------------------------------------------------------------------
# Path length
# -----------------------------------------------------------------------------


def test_a_length_can_be_measured_in_a_given_order():
    """The order is what the planner works in; the points never get sorted."""
    square = np.array([[0.0, 0.0, 0.0], [3.0, 0.0, 0.0], [3.0, 4.0, 0.0]])

    assert fp.path_length(square, order=[0, 2, 1]) == pytest.approx(5.0 + 4.0)


def test_one_point_is_no_distance():
    assert fp.path_length(np.array([[1.0, 2.0, 3.0]])) == 0.0


def test_no_points_are_no_distance():
    assert fp.path_length(np.zeros((0, 3))) == 0.0


def test_one_point_in_a_given_order_is_no_distance():
    assert fp.path_length(np.array([[1.0, 2.0, 3.0]]), order=[0]) == 0.0


# -----------------------------------------------------------------------------
# Hops that cannot be flown straight
# -----------------------------------------------------------------------------


def gapped() -> Obstacle:
    """A wall with a gap at one end, under a lid so nothing can climb over.

    The only way from one side to the other is round through the gap, which
    is what makes a hop take other viewpoints on its way.
    """
    filled = np.zeros((9, 9, 4), dtype=bool)
    filled[:7, 4, :] = True
    filled[:, :, -1] = True

    return Obstacle(filled, origin=(0.0, 0.0, 0.0), pitch=1.0)


def test_a_hop_across_a_wall_goes_round_by_way_of_other_viewpoints():
    """Four viewpoints either side of the wall, with the gap the only way over."""
    positions = np.array(
        [[7.21, 1.45, 0.5], [1.81, 3.52, 0.5], [4.65, 4.57, 0.5], [8.17, 5.72, 0.5]]
    )

    path = plan_path(positions, gapped())

    assert path.checked
    assert path.detours == 1
    assert path.crossings == 0
    assert path.avoidances == 1


def test_a_detour_flies_every_viewpoint_it_goes_by():
    positions = np.array(
        [[7.21, 1.45, 0.5], [1.81, 3.52, 0.5], [4.65, 4.57, 0.5], [8.17, 5.72, 0.5]]
    )

    path = plan_path(positions, gapped())

    assert sorted(path.order) == [0, 1, 2, 3]
    assert len(path.points) > len(positions)


def test_a_hop_over_a_wall_climbs_when_there_is_no_way_round():
    """Nothing is above the model, so the sky is always the last resort."""
    positions = np.array([[1.5, 1.5, 0.5], [1.5, 7.5, 0.5], [3.5, 1.5, 0.5], [3.5, 7.5, 0.5]])

    path = plan_path(positions, walled())

    assert path.climbs >= 1
    assert path.crossings == 0
    assert path.clear


def test_a_hop_with_no_way_round_or_over_is_flown_and_reported():
    """Better a route that says it crosses than one that drops a viewpoint."""
    positions = np.array([[4.5, 1.5, 0.5], [4.5, 7.5, 0.5]])

    path = plan_path(positions, roofed())

    assert path.crossings >= 1
    assert not path.clear
    assert len(path.order) == 2


def test_a_crossing_still_leaves_every_viewpoint_on_the_route():
    positions = np.array([[4.5, 1.5, 0.5], [4.5, 7.5, 0.5]])

    path = plan_path(positions, roofed())

    assert sorted(path.order) == [0, 1]


# -----------------------------------------------------------------------------
# The way between two viewpoints
# -----------------------------------------------------------------------------


def test_a_way_through_other_viewpoints_is_read_back_in_flying_order():
    previous = np.array([[-1, 0, 1], [-1, -1, -1], [-1, -1, -1]], dtype=np.int64)

    assert fp._between(previous, 0, 1) == [1]
    assert fp._between(previous, 0, 2) == [1, 2]


def test_no_way_between_two_viewpoints_reads_back_as_none():
    previous = np.full((3, 3), -1, dtype=np.int64)

    assert fp._between(previous, 0, 2) is None


# -----------------------------------------------------------------------------
# Resampling a stretch that goes nowhere
# -----------------------------------------------------------------------------


def test_a_stretch_that_never_moves_is_left_as_its_two_ends():
    same = np.tile([1.0, 2.0, 3.0], (4, 1))

    assert fp._resample(same, spacing=0.5).shape == (2, 3)


# -----------------------------------------------------------------------------
# The budgets the search is held to
# -----------------------------------------------------------------------------


def test_a_very_large_plan_is_ordered_without_uncrossing_it():
    """Past the matrix limit 2-opt is skipped: the ordering still has to come
    back complete, just not optimised."""
    points = np.column_stack(
        [
            np.arange(fp.MATRIX_LIMIT + 1, dtype=float),
            np.zeros(fp.MATRIX_LIMIT + 1),
            np.zeros(fp.MATRIX_LIMIT + 1),
        ]
    )

    order = fp._order(points, fp._distances(points))

    assert sorted(order) == list(range(len(points)))


def test_uncrossing_stops_when_its_passes_run_out(monkeypatch):
    """A budget, not a convergence test: it must return a usable tour either way."""
    monkeypatch.setattr(fp, "MAX_PASSES", 1)
    crossed = np.array([[0.0, 0.0, 0.0], [10.0, 0.0, 0.0], [1.0, 1.0, 0.0], [9.0, 1.0, 0.0]])

    order = fp._two_opt(np.arange(4), fp._distances(crossed))

    assert sorted(order) == [0, 1, 2, 3]


def test_pulling_stops_when_its_passes_run_out(monkeypatch):
    """The line still has to be clear when the budget is what ends the loop."""
    monkeypatch.setattr(fp, "PULL_PASSES", 1)
    obstacle = walled()
    slack = np.array([[1.5, 1.5, 0.5], [1.5, 6.5, 0.5], [6.5, 6.5, 0.5], [6.5, 1.5, 0.5]])

    pulled = fp._taut(slack, obstacle)

    assert len(pulled) >= 2
    assert not fp._fouls(pulled, obstacle)
