"""Unit tests for src/viewscope/data/store.py.

The store is the one piece of global state in the app, and what everything
else hangs off is its signals, so those are what is watched here.
"""

import pytest


@pytest.fixture
def listener(store):
    """Records every signal the store emits, in order."""
    seen = []
    store.scene_loaded.connect(lambda: seen.append(("loaded", None)))
    store.scene_unloaded.connect(lambda: seen.append(("unloaded", None)))
    store.scene_changed.connect(lambda: seen.append(("changed", None)))
    store.plan_changed.connect(lambda info: seen.append(("plan", info)))
    store.camera_moved.connect(lambda index: seen.append(("moved", index)))
    return seen


# -----------------------------------------------------------------------------
# Loading and clearing
# -----------------------------------------------------------------------------


def test_an_empty_store_holds_nothing():
    from viewscope.data.store import SceneStore

    fresh = SceneStore()

    assert fresh.scene is None
    assert fresh.loaded is False
    assert fresh.camera_count == 0


def test_loading_a_scene_announces_it(store, listener, make_scene):
    store.set_scene(make_scene())

    assert store.loaded is True
    assert store.camera_count == 2
    assert [name for name, _ in listener] == ["loaded", "changed", "plan"]


def test_clearing_puts_the_store_back_to_empty(store, listener, make_scene):
    store.set_scene(make_scene())
    listener.clear()

    store.clear()

    assert store.scene is None
    assert store.loaded is False
    assert store.camera_count == 0
    assert [name for name, _ in listener] == ["unloaded", "changed", "plan"]


def test_loading_a_second_scene_forgets_the_first_scenes_added_cameras(store, make_scene):
    store.set_scene(make_scene())
    store.add_camera((5.0, 5.0, 5.0), 0.0, 0.0)
    assert store.new_camera_ids

    store.set_scene(make_scene())

    assert store.new_camera_ids == set()


# -----------------------------------------------------------------------------
# Adding cameras
# -----------------------------------------------------------------------------


def test_an_added_camera_is_appended_and_named_past_the_highest_id(store, make_scene):
    store.set_scene(make_scene())

    store.add_camera((5.0, 6.0, 7.0), 30.0, -20.0)

    plan = store.scene.plan
    assert plan.ids == ("vp000", "vp001", "vp2")
    assert plan.positions[-1] == pytest.approx([5.0, 6.0, 7.0])
    assert plan.yaws_deg[-1] == 30.0
    assert plan.pitches_deg[-1] == -20.0
    assert store.camera_count == 3


def test_an_added_camera_is_remembered_as_one_the_user_made(store, make_scene):
    """The viewer draws these differently from the ones the bundle shipped."""
    store.set_scene(make_scene())

    store.add_camera((5.0, 6.0, 7.0), 0.0, 0.0)

    assert store.new_camera_ids == {"vp2"}


def test_adding_a_camera_announces_the_row_it_landed_at(store, listener, make_scene):
    store.set_scene(make_scene())
    listener.clear()

    store.add_camera((5.0, 6.0, 7.0), 0.0, 0.0)

    assert [name for name, _ in listener] == ["changed", "plan"]
    info = listener[-1][1]
    assert info.index == 2
    assert info.position == pytest.approx([5.0, 6.0, 7.0])


def test_adding_a_camera_with_no_scene_does_nothing(store, listener):
    store.add_camera((5.0, 6.0, 7.0), 0.0, 0.0)

    assert store.scene is None
    assert listener == []


# -----------------------------------------------------------------------------
# Moving and rotating
# -----------------------------------------------------------------------------


def test_moving_a_camera_changes_only_its_position(store, make_scene):
    store.set_scene(make_scene())
    before = store.scene.plan

    store.move_camera(0, (1.0, 2.0, 3.0))

    after = store.scene.plan
    assert after.positions[0] == pytest.approx([1.0, 2.0, 3.0])
    assert after.positions[1] == pytest.approx(before.positions[1])
    assert after.yaws_deg == pytest.approx(before.yaws_deg)
    assert after.ids == before.ids


def test_moving_a_camera_says_which_one_moved_and_nothing_more(store, listener, make_scene):
    """Deliberately not plan_changed: the plan's shape has not altered."""
    store.set_scene(make_scene())
    listener.clear()

    store.move_camera(1, (1.0, 2.0, 3.0))

    assert listener == [("moved", 1)]


def test_moving_a_camera_leaves_the_old_plan_untouched(store, make_scene):
    """The Plan is immutable, so a new one is built rather than edited."""
    store.set_scene(make_scene())
    original = store.scene.plan

    store.move_camera(0, (1.0, 2.0, 3.0))

    assert original.positions[0] == pytest.approx([0.0, 0.0, 12.0])
    assert store.scene.plan is not original


def test_moving_a_camera_with_no_scene_does_nothing(store, listener):
    store.move_camera(0, (1.0, 2.0, 3.0))

    assert listener == []


def test_rotating_a_camera_nudges_its_angles_in_place(store, make_scene):
    store.set_scene(make_scene())

    store.rotate_camera(1, delta_yaw_deg=15.0, delta_pitch_deg=-5.0)

    plan = store.scene.plan
    assert plan.yaws_deg[1] == pytest.approx(15.0)
    assert plan.pitches_deg[1] == pytest.approx(-50.0)
    assert plan.yaws_deg[0] == pytest.approx(0.0)


def test_rotating_a_camera_says_which_one_moved(store, listener, make_scene):
    store.set_scene(make_scene())
    listener.clear()

    store.rotate_camera(0)

    assert listener == [("moved", 0)]


def test_rotating_a_camera_with_no_scene_does_nothing(store, listener):
    store.rotate_camera(0, 10.0, 10.0)

    assert listener == []


# -----------------------------------------------------------------------------
# Making sure a route's cameras are all present
# -----------------------------------------------------------------------------


def entry(name, position=(1.0, 2.0, 3.0), yaw=10.0, pitch=-10.0):
    return (name, position, yaw, pitch)


def test_viewpoints_the_plan_already_has_are_left_exactly_as_they_were(store, make_scene):
    store.set_scene(make_scene())
    before = store.scene.plan

    rows, added = store.ensure_cameras([entry("vp001"), entry("vp000")])

    assert rows == (1, 0)
    assert added == 0
    assert store.scene.plan is before


def test_viewpoints_the_plan_lacks_are_appended_keeping_their_own_ids(store, make_scene):
    """A route names its cameras; those names have to survive the load."""
    store.set_scene(make_scene())

    rows, added = store.ensure_cameras([entry("routeA"), entry("vp000"), entry("routeB")])

    assert rows == (2, 0, 3)
    assert added == 2
    assert store.scene.plan.ids == ("vp000", "vp001", "routeA", "routeB")


def test_the_same_new_viewpoint_named_twice_is_only_appended_once(store, make_scene):
    store.set_scene(make_scene())

    rows, added = store.ensure_cameras([entry("routeA"), entry("routeA")])

    assert rows == (2, 2)
    assert added == 1
    assert store.scene.plan.ids == ("vp000", "vp001", "routeA")


def test_appending_announces_the_first_of_the_new_cameras(store, listener, make_scene):
    store.set_scene(make_scene())
    listener.clear()

    store.ensure_cameras([entry("routeA", position=(9.0, 8.0, 7.0), yaw=45.0, pitch=-30.0)])

    assert [name for name, _ in listener] == ["changed", "plan"]
    info = listener[-1][1]
    assert info.index == 2
    assert info.position == pytest.approx([9.0, 8.0, 7.0])
    assert info.yaw == 45.0
    assert info.pitch == -30.0


def test_appending_nothing_announces_nothing(store, listener, make_scene):
    store.set_scene(make_scene())
    listener.clear()

    store.ensure_cameras([entry("vp000")])

    assert listener == []


def test_ensuring_cameras_with_no_scene_reports_nothing_placed(store):
    assert store.ensure_cameras([entry("routeA")]) == ((), 0)


def test_the_appended_positions_and_angles_are_the_ones_given(store, make_scene):
    store.set_scene(make_scene())

    store.ensure_cameras([entry("routeA", position=(4.0, 5.0, 6.0), yaw=20.0, pitch=-15.0)])

    plan = store.scene.plan
    assert plan.positions[2] == pytest.approx([4.0, 5.0, 6.0])
    assert plan.yaws_deg[2] == pytest.approx(20.0)
    assert plan.pitches_deg[2] == pytest.approx(-15.0)


def test_an_empty_route_leaves_the_plan_alone(store, make_scene):
    store.set_scene(make_scene())
    before = store.scene.plan

    assert store.ensure_cameras([]) == ((), 0)
    assert store.scene.plan is before
