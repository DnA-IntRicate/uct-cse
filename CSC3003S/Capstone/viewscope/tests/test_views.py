"""Unit tests for src/viewscope/scene/views.py.

The mesh, the target cloud and the unobserved markers, all against a real
vtkRenderer. No window is needed: what each actor is told to wear can be read
straight back off its properties.
"""

import numpy as np
import pytest
import trimesh
import trimesh.visual
import vtk
from PIL import Image
from vtkmodules.util import numpy_support as vtknp

from viewscope.config import (
    GEOMETRY_COLOUR,
    OCCLUDED_COLOUR,
    UNOBSERVED_COLOUR,
    UNOBSERVED_POINT_GROWTH,
    VISIBLE_COLOUR,
)
from viewscope.scene.views import MeshView, TargetCloudView, UnobservedTargets

TARGETS = np.array([[0.0, 0.0, 0.0], [1.0, 0.0, 0.0], [2.0, 0.0, 0.0]])


@pytest.fixture
def renderer():
    return vtk.vtkRenderer()


def plain_mesh():
    mesh = trimesh.creation.box(extents=(2.0, 2.0, 2.0))
    mesh.visual = trimesh.visual.ColorVisuals(
        mesh, vertex_colors=np.tile([200, 180, 160, 255], (len(mesh.vertices), 1))
    )
    return mesh


def textured_mesh():
    mesh = trimesh.creation.box(extents=(2.0, 2.0, 2.0))
    mesh.visual = trimesh.visual.TextureVisuals(
        uv=np.zeros((len(mesh.vertices), 2)), image=Image.new("RGB", (4, 4), (10, 20, 30))
    )
    return mesh


class Scores:
    """Stands in for the bundle's score table; only the columns are read."""

    score_8 = np.array([0.1, 0.5, 0.9], dtype=np.float32)
    diversity_8 = np.array([0.0, 0.25, 1.0], dtype=np.float32)


# -----------------------------------------------------------------------------
# The mesh
# -----------------------------------------------------------------------------


def test_the_mesh_goes_on_and_comes_off_the_renderer(renderer):
    view = MeshView(plain_mesh())

    view.add_to(renderer)
    assert renderer.GetActors().GetNumberOfItems() == 1

    view.remove_from(renderer)
    assert renderer.GetActors().GetNumberOfItems() == 0


def test_a_textured_mesh_carries_its_texture(renderer):
    view = MeshView(textured_mesh())

    assert view.texture is not None
    assert view.actor.GetTexture() is not None


def test_an_untextured_mesh_has_no_texture(renderer):
    view = MeshView(plain_mesh())

    assert view.texture is None
    assert view.actor.GetTexture() is None


def test_the_mesh_can_be_hidden_and_shown():
    view = MeshView(plain_mesh())

    view.set_visible(False)
    assert view.actor.GetVisibility() == 0

    view.set_visible(True)
    assert view.actor.GetVisibility() == 1


def test_the_textured_view_paints_white_and_lets_the_scalars_through():
    view = MeshView(textured_mesh())

    view.show_geometry()
    view.show_textured()

    prop = view.actor.GetProperty()
    assert prop.GetColor() == (1.0, 1.0, 1.0)
    assert prop.GetEdgeVisibility() == 0
    assert view.actor.GetMapper().GetScalarVisibility() == 1
    assert view.actor.GetTexture() is not None


def test_the_textured_view_of_an_untextured_mesh_sets_no_texture():
    view = MeshView(plain_mesh())

    view.show_textured()

    assert view.actor.GetTexture() is None


def test_the_geometry_view_is_a_flat_colour_with_its_edges_drawn():
    view = MeshView(plain_mesh())

    view.show_geometry()

    prop = view.actor.GetProperty()
    assert prop.GetColor() == pytest.approx(GEOMETRY_COLOUR)
    assert prop.GetEdgeVisibility() == 1
    assert prop.GetLineWidth() == 1.0
    assert view.actor.GetMapper().GetScalarVisibility() == 0


# -----------------------------------------------------------------------------
# The targets nothing can see
# -----------------------------------------------------------------------------


def test_marking_targets_puts_a_cloud_of_them_on_the_renderer(renderer):
    marks = UnobservedTargets()

    marks.show(renderer, TARGETS)

    assert marks.actor is not None
    assert renderer.GetActors().GetNumberOfItems() == 1
    assert marks.actor is not None
    assert marks.actor.GetMapper().GetInput().GetNumberOfPoints() == 3


def test_the_marks_wear_their_own_colour_and_are_drawn_larger(renderer):
    """They have to be findable among the targets they were picked out of."""
    marks = UnobservedTargets(point_size=3.0)

    marks.show(renderer, TARGETS)

    assert marks.actor is not None
    prop = marks.actor.GetProperty()
    assert prop.GetColor() == pytest.approx(UNOBSERVED_COLOUR)
    assert prop.GetPointSize() == pytest.approx(3.0 + UNOBSERVED_POINT_GROWTH)
    assert marks.actor is not None
    assert marks.actor.GetMapper().GetScalarVisibility() == 0


def test_marking_nothing_draws_nothing(renderer):
    """An empty set is the answer that there are no gaps."""
    marks = UnobservedTargets()

    marks.show(renderer, np.zeros((0, 3)))

    assert marks.actor is None
    assert renderer.GetActors().GetNumberOfItems() == 0


def test_marking_again_replaces_what_was_marked(renderer):
    marks = UnobservedTargets()
    marks.show(renderer, TARGETS)

    marks.show(renderer, TARGETS[:1])

    assert renderer.GetActors().GetNumberOfItems() == 1
    assert marks.actor is not None
    assert marks.actor.GetMapper().GetInput().GetNumberOfPoints() == 1


def test_the_marks_follow_the_clouds_point_size(renderer):
    marks = UnobservedTargets(point_size=2.0)
    marks.show(renderer, TARGETS)

    marks.set_point_size(6.0)

    assert marks.actor is not None
    assert marks.actor.GetProperty().GetPointSize() == pytest.approx(6.0 + UNOBSERVED_POINT_GROWTH)


def test_a_point_size_set_before_anything_is_drawn_is_remembered(renderer):
    marks = UnobservedTargets()
    marks.set_point_size(6.0)

    marks.show(renderer, TARGETS)

    assert marks.actor is not None
    assert marks.actor.GetProperty().GetPointSize() == pytest.approx(6.0 + UNOBSERVED_POINT_GROWTH)


def test_the_marks_can_be_hidden(renderer):
    marks = UnobservedTargets()
    marks.show(renderer, TARGETS)

    marks.set_visible(False)

    assert marks.actor is not None
    assert marks.actor.GetVisibility() == 0


def test_marks_hidden_before_they_are_drawn_come_back_hidden(renderer):
    marks = UnobservedTargets()
    marks.set_visible(False)

    marks.show(renderer, TARGETS)

    assert marks.actor is not None
    assert marks.actor.GetVisibility() == 0


def test_hiding_marks_that_were_never_drawn_is_harmless():
    UnobservedTargets().set_visible(False)


def test_removing_marks_that_were_never_drawn_is_harmless(renderer):
    UnobservedTargets().remove_from(renderer)


# -----------------------------------------------------------------------------
# The target cloud
# -----------------------------------------------------------------------------


def test_a_bundle_without_scores_has_no_scale_to_explain(renderer):
    cloud = TargetCloudView(TARGETS)

    assert not cloud.has_scores
    assert cloud.scalar_bar is None
    assert cloud.lut is None


def test_a_scored_bundle_gets_a_scalar_bar(renderer):
    cloud = TargetCloudView(TARGETS, Scores())

    assert cloud.has_scores
    assert cloud.scalar_bar is not None


def test_the_cloud_and_its_scale_go_on_and_come_off_together(renderer):
    cloud = TargetCloudView(TARGETS, Scores())

    cloud.add_to(renderer)
    assert renderer.GetActors().GetNumberOfItems() == 1
    assert renderer.GetActors2D().GetNumberOfItems() == 1

    cloud.remove_from(renderer)
    assert renderer.GetActors().GetNumberOfItems() == 0
    assert renderer.GetActors2D().GetNumberOfItems() == 0


def test_an_unscored_cloud_goes_on_and_comes_off_without_a_scale(renderer):
    cloud = TargetCloudView(TARGETS)

    cloud.add_to(renderer)
    cloud.remove_from(renderer)

    assert renderer.GetActors().GetNumberOfItems() == 0


def test_hiding_the_cloud_hides_its_scale_too():
    cloud = TargetCloudView(TARGETS, Scores())

    cloud.set_visible(False)

    assert cloud.actor.GetVisibility() == 0
    assert cloud.scalar_bar is not None
    assert cloud.scalar_bar.GetVisibility() == 0


def test_hiding_an_unscored_cloud_is_harmless():
    cloud = TargetCloudView(TARGETS)

    cloud.set_visible(False)

    assert cloud.actor.GetVisibility() == 0


def test_the_point_size_can_be_changed():
    cloud = TargetCloudView(TARGETS, point_size=2.0)

    cloud.set_point_size(5.0)

    assert cloud.actor.GetProperty().GetPointSize() == pytest.approx(5.0)


# -----------------------------------------------------------------------------
# Colouring by a field
# -----------------------------------------------------------------------------


def test_colouring_by_a_field_reports_its_stats():
    cloud = TargetCloudView(TARGETS, Scores())

    stats = cloud.set_field("score_8")

    assert stats.field == "score_8"
    assert stats.minimum == pytest.approx(0.1)
    assert stats.maximum == pytest.approx(0.9)
    assert stats.mean == pytest.approx(0.5)


def test_an_unscored_cloud_has_no_field_to_colour_by():
    assert TargetCloudView(TARGETS).set_field("score_8") is None


def test_the_scale_is_titled_with_the_field_it_explains():
    cloud = TargetCloudView(TARGETS, Scores())

    cloud.set_field("diversity_8")

    assert cloud.scalar_bar is not None
    assert cloud.scalar_bar.GetTitle() == "diversity_8"


def test_the_values_land_on_the_points():
    cloud = TargetCloudView(TARGETS, Scores())

    cloud.set_field("score_8")

    scalars = cloud.polydata.GetPointData().GetScalars()
    assert vtknp.vtk_to_numpy(scalars) == pytest.approx([0.1, 0.5, 0.9])


def test_values_of_their_own_colour_themselves_when_no_range_is_given():
    cloud = TargetCloudView(TARGETS)

    cloud.set_values("route", np.array([2.0, 4.0, 6.0]))

    assert cloud.actor.GetMapper().GetScalarRange() == pytest.approx((2.0, 6.0))


def test_a_given_range_pins_the_scale_whatever_the_values_reach():
    """Rescaled per route, one camera would paint its patch the colour of full
    coverage and the next would repaint everything darker."""
    cloud = TargetCloudView(TARGETS)

    cloud.set_values("route", np.array([0.0, 0.1, 0.2]), (0.0, 1.0))

    assert cloud.actor.GetMapper().GetScalarRange() == pytest.approx((0.0, 1.0))


def test_an_empty_route_still_gets_a_scale():
    """A zero width range leaves the colours undefined."""
    cloud = TargetCloudView(TARGETS)

    cloud.set_values("route", np.zeros(3))

    low, high = cloud.actor.GetMapper().GetScalarRange()
    assert high > low


# -----------------------------------------------------------------------------
# Occlusion colouring
# -----------------------------------------------------------------------------


def test_occlusion_paints_what_the_camera_sees_and_what_it_does_not():
    cloud = TargetCloudView(TARGETS, Scores())

    cloud.set_occlusion(np.array([True, False, True]))

    assert cloud.occluding
    scalars = cloud.polydata.GetPointData().GetScalars()
    assert scalars.GetName() == "visible"
    assert vtknp.vtk_to_numpy(scalars) == pytest.approx([1.0, 0.0, 1.0])


def test_the_occlusion_colours_are_the_two_the_config_names():
    cloud = TargetCloudView(TARGETS)
    cloud.set_occlusion(np.array([True, False, True]))

    lut = cloud.actor.GetMapper().GetLookupTable()

    # The table stores colours as bytes, so a channel is only good to 1/255.
    assert lut.GetTableValue(0)[:3] == pytest.approx(OCCLUDED_COLOUR, abs=1 / 255)
    assert lut.GetTableValue(1)[:3] == pytest.approx(VISIBLE_COLOUR, abs=1 / 255)


def test_the_scale_is_hidden_while_occluding_because_it_explains_something_else():
    cloud = TargetCloudView(TARGETS, Scores())

    cloud.set_occlusion(np.array([True, False, True]))

    assert cloud.scalar_bar is not None
    assert cloud.scalar_bar.GetVisibility() == 0


def test_dropping_occlusion_puts_back_exactly_what_was_painted_before():
    """Not the bundle's column, which may be about other cameras entirely."""
    cloud = TargetCloudView(TARGETS, Scores())
    cloud.set_values("route", np.array([0.0, 0.1, 0.2]), (0.0, 1.0))
    cloud.set_occlusion(np.array([True, False, True]))

    cloud.set_occlusion(None)

    assert not cloud.occluding
    scalars = cloud.polydata.GetPointData().GetScalars()
    assert vtknp.vtk_to_numpy(scalars) == pytest.approx([0.0, 0.1, 0.2])
    assert cloud.actor.GetMapper().GetScalarRange() == pytest.approx((0.0, 1.0))


def test_dropping_occlusion_brings_the_scale_back():
    cloud = TargetCloudView(TARGETS, Scores())
    cloud.set_field("score_8")
    cloud.set_occlusion(np.array([True, False, True]))

    cloud.set_occlusion(None)

    assert cloud.scalar_bar is not None
    assert cloud.scalar_bar.GetVisibility() == 1
    assert cloud.actor.GetMapper().GetLookupTable() is cloud.lut


def test_dropping_occlusion_with_nothing_ever_painted_leaves_the_cloud_plain():
    cloud = TargetCloudView(TARGETS)
    cloud.set_occlusion(np.array([True, False, True]))

    cloud.set_occlusion(None)

    assert cloud.actor.GetMapper().GetScalarVisibility() == 0


def test_dropping_occlusion_that_was_never_on_does_nothing():
    """Route planning asks for this on every click; it must be free."""
    cloud = TargetCloudView(TARGETS, Scores())
    cloud.set_field("score_8")
    before = cloud.polydata.GetPointData().GetScalars()

    cloud.set_occlusion(None)

    assert cloud.polydata.GetPointData().GetScalars() is before


def test_a_field_set_while_occluding_is_remembered_but_not_painted():
    """Occlusion owns the scalars while it is on."""
    cloud = TargetCloudView(TARGETS, Scores())
    cloud.set_occlusion(np.array([True, False, True]))

    cloud.set_values("route", np.array([0.3, 0.4, 0.5]))

    assert cloud.polydata.GetPointData().GetScalars().GetName() == "visible"

    cloud.set_occlusion(None)
    assert vtknp.vtk_to_numpy(cloud.polydata.GetPointData().GetScalars()) == pytest.approx(
        [0.3, 0.4, 0.5]
    )
