"""Unit tests for the frustums and the flight path line drawn in the scene.

Actors only: building a CameraGlyphs needs no render window, so what each
frustum is told to wear can be read straight off its properties.
"""

import numpy as np
import pytest
import vtk

import viewscope_core as vc
from viewscope.config import (
    GLYPH_SOLID_OPACITY,
    GLYPH_WIREFRAME_OPACITY,
    ROUTE_SELECTED_COLOUR,
    ROUTE_UNSELECTED_COLOUR,
    UNOBSERVED_COLOUR,
    UNOBSERVED_POINT_GROWTH,
)
from viewscope.scene import FlightPathLine, UnobservedTargets
from viewscope.scene.gizmos import CameraGlyphs


@pytest.fixture
def plan():
    """Four viewpoints, which is enough to have some in a route and some out."""
    return vc.Plan(
        camera={"width": 1368, "height": 912, "yfov_deg": 53.13},
        ids=("vp000", "vp001", "vp002", "vp003"),
        positions=np.array([[0.0, 0.0, 5.0], [1.0, 0.0, 5.0], [2.0, 0.0, 5.0], [3.0, 0.0, 5.0]]),
        yaws_deg=np.array([0.0, 90.0, 180.0, -90.0]),
        pitches_deg=np.array([-10.0, -20.0, -30.0, -40.0]),
    )


def glyph(glyphs: CameraGlyphs, index: int):
    """The actor drawing one camera, by its row in the plan."""
    return next(actor for actor, row in glyphs.glyphs.items() if row == index)


def worn(glyphs: CameraGlyphs, index: int):
    """What that camera is wearing: representation, opacity and colour."""
    prop = glyph(glyphs, index).GetProperty()

    return prop.GetRepresentationAsString(), prop.GetOpacity(), prop.GetColor()


# -----------------------------------------------------------------------------
# How solid a frustum is drawn
# -----------------------------------------------------------------------------


def test_a_wireframe_frustum_is_drawn_exactly_as_it_always_was(plan):
    """The wireframe is the one people read the scene by; it does not move."""
    glyphs = CameraGlyphs(plan)
    glyphs.wireframe_enabled = True
    glyphs._refresh()

    representation, opacity, _ = worn(glyphs, 0)

    assert representation == "Wireframe"
    assert opacity == pytest.approx(GLYPH_WIREFRAME_OPACITY)
    assert GLYPH_WIREFRAME_OPACITY == 0.2, "the value wireframes have always worn"


def test_a_solid_frustum_is_drawn_strongly_enough_to_make_out(plan):
    """Filled in, a frustum needs far more than a wireframe to read at all."""
    glyphs = CameraGlyphs(plan)
    glyphs.wireframe_enabled = False
    glyphs._refresh()

    representation, opacity, _ = worn(glyphs, 0)

    assert representation == "Surface"
    assert opacity == pytest.approx(GLYPH_SOLID_OPACITY)
    assert GLYPH_SOLID_OPACITY > GLYPH_WIREFRAME_OPACITY


def test_the_two_representations_do_not_share_an_opacity(plan):
    """One number for both is what left the solid frustums a smudge."""
    assert GLYPH_SOLID_OPACITY != GLYPH_WIREFRAME_OPACITY


def test_the_camera_being_looked_at_is_drawn_solid_whatever_the_mode(plan):
    for wireframe in (True, False):
        glyphs = CameraGlyphs(plan)
        glyphs.wireframe_enabled = wireframe
        glyphs.set_selected(2)

        representation, opacity, _ = worn(glyphs, 2)

        assert representation == "Surface"
        assert opacity == pytest.approx(1.0)


# -----------------------------------------------------------------------------
# What a frustum wears
# -----------------------------------------------------------------------------


def test_a_camera_in_the_route_wears_cyan(plan):
    glyphs = CameraGlyphs(plan)
    glyphs.set_route({0, 2})

    _, _, colour = worn(glyphs, 0)
    red, green, blue = colour

    assert colour == pytest.approx(ROUTE_SELECTED_COLOUR)
    assert green > 0.7 and blue > 0.7, "cyan is green and blue together"
    assert red < 0.3, "and very little red"


def test_a_camera_taken_out_of_the_route_stays_grey(plan):
    glyphs = CameraGlyphs(plan)
    glyphs.set_route({0, 2})

    _, _, colour = worn(glyphs, 1)

    assert colour == pytest.approx(ROUTE_UNSELECTED_COLOUR)


def test_the_route_colours_tell_each_other_apart(plan):
    """In and out of the route has to be readable at a glance, not squinted at."""
    apart = np.abs(np.array(ROUTE_SELECTED_COLOUR) - np.array(ROUTE_UNSELECTED_COLOUR))

    assert apart.max() > 0.5


def test_a_camera_out_of_the_route_is_dimmed_never_hidden(plan):
    """Out of the route is a colour, not an absence.

    A loaded route used to switch off every viewpoint its file did not name,
    which left the rest of the plan unclickable: you cannot put a camera back
    into a route when it is not on screen to be clicked.
    """
    glyphs = CameraGlyphs(plan)
    glyphs.set_route({0, 2})

    assert all(glyph(glyphs, index).GetVisibility() == 1 for index in range(4))
    assert worn(glyphs, 1)[2] == pytest.approx(ROUTE_UNSELECTED_COLOUR)


def test_the_only_frustum_hidden_is_the_one_you_are_sitting_inside(plan):
    """That one fills the view; every other camera stays drawn."""
    glyphs = CameraGlyphs(plan)
    glyphs.set_route({0})
    glyphs.set_active(3)

    assert glyph(glyphs, 3).GetVisibility() == 0
    assert all(glyph(glyphs, index).GetVisibility() == 1 for index in (0, 1, 2))


def test_switching_the_glyphs_off_still_hides_them_all(plan):
    """The one deliberate way to clear the frustums out has to keep working."""
    glyphs = CameraGlyphs(plan)
    glyphs.set_route({0, 2})
    glyphs.set_visible(False)

    assert all(glyph(glyphs, index).GetVisibility() == 0 for index in range(4))


def test_the_camera_being_looked_at_outranks_the_route(plan):
    """Gold wins: it says where you are, which the route colour does not."""
    glyphs = CameraGlyphs(plan)
    glyphs.set_route({0, 2})
    glyphs.set_selected(0)

    _, _, colour = worn(glyphs, 0)

    assert colour == pytest.approx(CameraGlyphs.COLOUR_ACTIVE)


# -----------------------------------------------------------------------------
# A plan that grows is drawn by a whole new set of frustums
# -----------------------------------------------------------------------------


@pytest.fixture
def bigger_plan(plan):
    """The same plan with one more viewpoint, as adding a camera makes."""
    return vc.Plan(
        camera=plan.camera,
        ids=(*plan.ids, "vp004"),
        positions=np.vstack([plan.positions, [[4.0, 0.0, 5.0]]]),
        yaws_deg=np.append(plan.yaws_deg, 45.0),
        pitches_deg=np.append(plan.pitches_deg, -15.0),
    )


def test_a_new_set_keeps_the_representation_the_old_one_was_shown_in(plan, bigger_plan):
    """Adding a camera used to quietly put the frustums back into wireframe."""
    before = CameraGlyphs(plan)
    before.wireframe_enabled = False
    before._refresh()

    after = CameraGlyphs(bigger_plan)
    after.adopt_display(before)

    assert after.wireframe_enabled is False
    assert worn(after, 0)[0] == "Surface"
    assert worn(after, 4)[0] == "Surface", "the camera just added too"


def test_a_new_set_keeps_the_frustums_switched_off(plan, bigger_plan):
    """Show camera frustum is the viewer's setting, not the plan's."""
    before = CameraGlyphs(plan)
    before.set_visible(False)

    after = CameraGlyphs(bigger_plan)
    after.adopt_display(before)

    assert all(glyph(after, index).GetVisibility() == 0 for index in range(5))


def test_a_new_set_keeps_the_frustum_you_are_sitting_inside_hidden(plan, bigger_plan):
    before = CameraGlyphs(plan)
    before.set_active(2)

    after = CameraGlyphs(bigger_plan)
    after.adopt_display(before)

    assert glyph(after, 2).GetVisibility() == 0
    assert glyph(after, 4).GetVisibility() == 1


def test_a_new_set_left_alone_is_drawn_the_way_it_always_was(bigger_plan):
    """Nothing to adopt from, so the defaults stand: visible, solid.

    Solid because that is what the display panel's wireframe box is unchecked
    at: the two say the same thing about a scene nobody has touched yet.
    """
    glyphs = CameraGlyphs(bigger_plan)
    glyphs._refresh()

    assert glyphs.wireframe_enabled is False
    assert all(glyph(glyphs, index).GetVisibility() == 1 for index in range(5))


# -----------------------------------------------------------------------------
# What the flight path line does to everything else
# -----------------------------------------------------------------------------


def test_drawing_a_flight_path_leaves_every_other_mapper_alone():
    """Coincident-topology resolution is static on vtkMapper, not per mapper.

    One mapper asking for it turns it on for every mapper in the process, and
    the floor grid then draws over the ground the model stands on rather than
    being hidden by it - the grid lines come up through the building.
    """
    before = vtk.vtkMapper.GetResolveCoincidentTopology()

    FlightPathLine().show(
        vtk.vtkRenderer(), np.array([[0.0, 0.0, 0.0], [1.0, 1.0, 1.0], [2.0, 0.0, 1.0]])
    )

    assert vtk.vtkMapper.GetResolveCoincidentTopology() == before
    assert vtk.vtkPolyDataMapper().GetResolveCoincidentTopology() == before


def test_the_flight_path_is_drawn_as_one_line_through_its_points():
    line = FlightPathLine()
    line.show(vtk.vtkRenderer(), np.array([[0.0, 0.0, 0.0], [1.0, 0.0, 0.0], [2.0, 1.0, 0.0]]))

    assert line.actor is not None
    drawn = line.actor.GetMapper().GetInput()
    assert drawn.GetNumberOfPoints() == 3
    assert drawn.GetNumberOfLines() == 1


def test_a_path_of_one_point_draws_nothing():
    """One viewpoint is not a path, and half a line is worse than none."""
    line = FlightPathLine()
    line.show(vtk.vtkRenderer(), np.array([[1.0, 2.0, 3.0]]))

    assert line.actor is None


# -----------------------------------------------------------------------------
# Targets nothing can see
# -----------------------------------------------------------------------------


@pytest.fixture
def missed():
    """Three targets that no camera observes."""
    return np.array([[0.0, 0.0, 0.0], [1.0, 2.0, 3.0], [4.0, 5.0, 6.0]])


def drawn(flags: UnobservedTargets) -> vtk.vtkActor:
    """The actor doing the flagging, once there is something to flag."""
    actor = flags.actor
    assert actor is not None, "nothing was flagged"

    return actor


def test_flagged_targets_are_drawn_where_they_are(missed):
    flags = UnobservedTargets()
    flags.show(vtk.vtkRenderer(), missed)

    points = drawn(flags).GetMapper().GetInput()

    assert points.GetNumberOfPoints() == len(missed)
    assert np.allclose(points.GetPoint(1), missed[1])


def test_flags_wear_one_flat_colour_of_their_own(missed):
    """Whatever the cloud underneath is coloured by, a flag looks the same."""
    flags = UnobservedTargets()
    flags.show(vtk.vtkRenderer(), missed)

    assert drawn(flags).GetProperty().GetColor() == pytest.approx(UNOBSERVED_COLOUR)
    assert not drawn(flags).GetMapper().GetScalarVisibility()


def test_a_flag_is_drawn_larger_than_the_target_it_marks(missed):
    """One flagged target among well covered ones still has to be findable."""
    flags = UnobservedTargets(point_size=2.0)
    flags.show(vtk.vtkRenderer(), missed)

    assert drawn(flags).GetProperty().GetPointSize() == pytest.approx(2.0 + UNOBSERVED_POINT_GROWTH)


def test_flags_follow_the_point_size_of_the_cloud(missed):
    flags = UnobservedTargets(point_size=2.0)
    flags.show(vtk.vtkRenderer(), missed)
    flags.set_point_size(7.0)

    assert drawn(flags).GetProperty().GetPointSize() == pytest.approx(7.0 + UNOBSERVED_POINT_GROWTH)


def test_nothing_is_drawn_when_every_target_has_an_observer():
    """The good case draws no actor at all, rather than an empty one."""
    flags = UnobservedTargets()
    flags.show(vtk.vtkRenderer(), np.zeros((0, 3)))

    assert flags.actor is None


def test_flags_can_be_hidden_with_the_target_cloud_and_shown_again(missed):
    """A mode that draws no targets draws no flags floating in front of it."""
    renderer = vtk.vtkRenderer()
    flags = UnobservedTargets()
    flags.show(renderer, missed)

    flags.set_visible(False)
    assert drawn(flags).GetVisibility() == 0

    flags.set_visible(True)
    assert drawn(flags).GetVisibility() == 1


def test_hiding_before_anything_is_flagged_is_remembered(missed):
    """The switch is state, not a call: what is drawn next has to obey it."""
    flags = UnobservedTargets()
    flags.set_visible(False)
    flags.show(vtk.vtkRenderer(), missed)

    assert drawn(flags).GetVisibility() == 0


def test_flagging_again_replaces_what_was_flagged_before(missed):
    """Otherwise every route change would leave its flags behind on the scene."""
    renderer = vtk.vtkRenderer()
    flags = UnobservedTargets()
    flags.show(renderer, missed)
    first = drawn(flags)

    flags.show(renderer, missed[:1])

    assert drawn(flags) is not first
    assert drawn(flags).GetMapper().GetInput().GetNumberOfPoints() == 1
    assert renderer.HasViewProp(first) == 0


def test_taking_the_flags_off_leaves_nothing_behind(missed):
    renderer = vtk.vtkRenderer()
    flags = UnobservedTargets()
    flags.show(renderer, missed)
    actor = drawn(flags)

    flags.remove_from(renderer)

    assert flags.actor is None
    assert renderer.HasViewProp(actor) == 0


def test_the_flag_colour_is_one_the_score_ramp_cannot_produce():
    """The cloud runs blue to red through green and yellow; magenta is not on it."""
    red, green, blue = UNOBSERVED_COLOUR

    assert red > 0.5 and blue > 0.5, "magenta is red and blue together"
    assert green < 0.3, "with no green, which the ramp is full of"


# -----------------------------------------------------------------------------
# Putting the frustums on a renderer and taking them off
# -----------------------------------------------------------------------------


def test_every_frustum_is_an_actor(plan):
    glyphs = CameraGlyphs(plan)

    assert len(glyphs.actors) == len(plan.ids)
    assert set(glyphs.actors) == set(glyphs.glyphs)


def test_adding_puts_every_frustum_on_the_renderer(plan):
    glyphs, renderer = CameraGlyphs(plan), vtk.vtkRenderer()

    glyphs.add_to(renderer)

    assert renderer.GetActors().GetNumberOfItems() == len(plan.ids)


def test_removing_takes_them_all_off_and_forgets_them(plan):
    glyphs, renderer = CameraGlyphs(plan), vtk.vtkRenderer()
    glyphs.add_to(renderer)

    glyphs.remove_from(renderer)

    assert renderer.GetActors().GetNumberOfItems() == 0
    assert glyphs.glyphs == {}
    assert glyphs.actors == []


# -----------------------------------------------------------------------------
# Looking a frustum up
# -----------------------------------------------------------------------------


def test_an_actor_reports_the_camera_it_draws(plan):
    glyphs = CameraGlyphs(plan)

    assert glyphs.camera_id_of_actor(glyph(glyphs, 2)) == 2


def test_an_actor_that_is_not_a_frustum_names_no_camera(plan):
    """The picker hands over whatever was under the cursor, model included."""
    glyphs = CameraGlyphs(plan)

    assert glyphs.camera_id_of_actor(vtk.vtkActor()) is None


def test_a_camera_reports_the_actor_that_draws_it(plan):
    glyphs = CameraGlyphs(plan)

    assert glyphs.actor_of_id(2) is glyph(glyphs, 2)


def test_a_camera_that_is_not_in_the_plan_has_no_actor(plan):
    glyphs = CameraGlyphs(plan)

    assert glyphs.actor_of_id(99) is None


# -----------------------------------------------------------------------------
# The observers of the picked target
# -----------------------------------------------------------------------------


def test_an_observer_wears_the_colour_it_is_given(plan):
    glyphs = CameraGlyphs(plan)

    glyphs.set_observer_colours({1: (0.5, 0.25, 0.75)})

    assert worn(glyphs, 1)[2] == pytest.approx((0.5, 0.25, 0.75))


def test_dropping_the_target_takes_the_observer_colours_off(plan):
    glyphs = CameraGlyphs(plan)
    glyphs.set_observer_colours({1: (0.5, 0.25, 0.75)})

    glyphs.set_observer_colours(None)

    assert worn(glyphs, 1)[2] != pytest.approx((0.5, 0.25, 0.75))


def test_the_selected_camera_outranks_the_observer_colouring(plan):
    """Gold means "this is the one you picked" and nothing may take it."""
    glyphs = CameraGlyphs(plan)
    glyphs.set_observer_colours({1: (0.5, 0.25, 0.75)})

    glyphs.set_selected(1)

    assert worn(glyphs, 1)[2] == pytest.approx(CameraGlyphs.COLOUR_ACTIVE)


# -----------------------------------------------------------------------------
# Cameras the user added
# -----------------------------------------------------------------------------


def test_a_camera_the_user_added_is_drawn_in_its_own_colour(plan):
    glyphs = CameraGlyphs(plan)

    glyphs.set_new_cameras({"vp002"})
    glyphs._refresh()

    assert worn(glyphs, 2)[2] == pytest.approx(CameraGlyphs.COLOUR_NEW)
    assert worn(glyphs, 0)[2] != pytest.approx(CameraGlyphs.COLOUR_NEW)


def test_clearing_the_new_cameras_puts_their_own_colours_back(plan):
    glyphs = CameraGlyphs(plan)
    glyphs.set_new_cameras({"vp002"})

    glyphs.set_new_cameras(None)
    glyphs._refresh()

    assert glyphs.new_ids == set()
    assert worn(glyphs, 2)[2] != pytest.approx(CameraGlyphs.COLOUR_NEW)


def test_the_route_outranks_the_new_camera_colouring(plan):
    """While planning, in or out of the route is the only thing worth seeing."""
    glyphs = CameraGlyphs(plan)
    glyphs.set_new_cameras({"vp002"})

    glyphs.set_route({2})

    assert worn(glyphs, 2)[2] == pytest.approx(ROUTE_SELECTED_COLOUR)


# -----------------------------------------------------------------------------
# Showing only what a loaded plan names
# -----------------------------------------------------------------------------


def test_showing_only_some_ids_switches_the_rest_off(plan):
    glyphs = CameraGlyphs(plan)

    glyphs.show_only({"vp000", "vp002"})

    assert glyph(glyphs, 0).GetVisibility() == 1
    assert glyph(glyphs, 1).GetVisibility() == 0
    assert glyph(glyphs, 2).GetVisibility() == 1


def test_showing_everything_again_switches_them_all_back_on(plan):
    glyphs = CameraGlyphs(plan)
    glyphs.show_only({"vp000"})

    glyphs.show_only(None)

    assert all(actor.GetVisibility() == 1 for actor in glyphs.actors)
