"""Unit tests for src/viewscope/scene/target_report.py."""

import json

import numpy as np
import pytest
import trimesh

import viewscope_core as vc
from viewscope.data import SceneData
from viewscope.scene import (
    ANGLE,
    DISTANCE,
    EVEN,
    Observer,
    TargetReports,
    build_report,
    summarise_sectors,
)

# A target at the origin looking straight up. tangent_basis puts e1 along x
# and e2 along y for this normal, so an azimuth of zero points along +x.
ORIGIN = np.zeros(3)
UP = np.array([0.0, 0.0, 1.0])

#: Distance and incidence that both score a factor of one.
IDEAL_RHO = vc.constants.MU_RHO_M
IDEAL_THETA = vc.constants.MU_THETA_DEG


def camera_at(azimuth_deg, theta_deg=IDEAL_THETA, rho=IDEAL_RHO):
    """A camera `rho` metres off the origin target, at a known compass bearing."""
    azimuth = np.radians(azimuth_deg)
    theta = np.radians(theta_deg)
    tangent = np.array([np.cos(azimuth), np.sin(azimuth), 0.0])

    return rho * (np.sin(theta) * tangent + np.cos(theta) * UP)


def observer(camera_index=0, weight=0.5, f_rho=0.7, f_theta=0.7, sector=0, best=False):
    return Observer(camera_index, weight, f_rho, f_theta, sector, best)


# -----------------------------------------------------------------------------
# Which of the two factors is holding a camera back
# -----------------------------------------------------------------------------


@pytest.mark.parametrize(
    ("f_rho", "f_theta", "expected"),
    [
        (0.2, 0.9, DISTANCE),
        (0.9, 0.2, ANGLE),
        (0.8, 0.8, EVEN),
        (0.80, 0.81, EVEN),  # inside the margin, so neither is blamed
    ],
)
def test_limited_by_names_the_weaker_factor(f_rho, f_theta, expected):
    assert observer(f_rho=f_rho, f_theta=f_theta).limited_by == expected


# -----------------------------------------------------------------------------
# Sector summaries
# -----------------------------------------------------------------------------


def test_summarise_reports_every_sector_occupied_or_not():
    """Empty wedges are the point of the decomposition, so they get a row too."""
    sectors = summarise_sectors([observer(sector=0), observer(sector=0)], 8)

    assert len(sectors) == 8
    assert sectors[0].observers == 2
    assert sectors[0].occupied
    assert [s.occupied for s in sectors[1:]] == [False] * 7
    assert sectors[3].best_camera is None
    assert sectors[3].best_weight == 0.0


def test_summarise_picks_the_heaviest_camera_in_each_sector():
    observers = [
        observer(camera_index=1, weight=0.2, sector=3),
        observer(camera_index=2, weight=0.9, sector=3),
        observer(camera_index=3, weight=0.4, sector=5),
    ]

    sectors = summarise_sectors(observers, 8)

    assert (sectors[3].best_camera, sectors[3].best_weight) == (2, 0.9)
    assert (sectors[5].best_camera, sectors[5].best_weight) == (3, 0.4)


# -----------------------------------------------------------------------------
# Reports built from geometry
# -----------------------------------------------------------------------------


def test_cameras_land_in_the_wedge_their_bearing_points_at():
    """Eight wedges of 45 degrees each, numbered anticlockwise from +x."""
    bearings = [10.0, 100.0, 190.0, 280.0]
    positions = np.array([camera_at(bearing) for bearing in bearings])

    report = build_report(0, ORIGIN, UP, positions, np.arange(4), 8)

    assert {o.camera_index: o.sector for o in report.observers} == {0: 0, 1: 2, 2: 4, 3: 6}


def test_weight_is_the_product_of_its_two_factors():
    positions = np.array([camera_at(0.0), camera_at(90.0, theta_deg=75.0, rho=20.0)])

    report = build_report(0, ORIGIN, UP, positions, np.arange(2), 8)

    for observed in report.observers:
        assert observed.weight == pytest.approx(observed.f_rho * observed.f_theta)


def test_the_ideal_camera_scores_one_and_leads_its_sector():
    report = build_report(0, ORIGIN, UP, np.array([camera_at(0.0)]), np.array([7]), 8)

    only = report.observers[0]
    assert only.camera_index == 7
    assert only.weight == pytest.approx(1.0)
    assert only.best
    assert report.occupied_sectors == 1
    # One perfect camera in one of eight wedges is an eighth of the coverage.
    assert report.score == pytest.approx(1.0 / 8.0)


def test_observers_come_back_heaviest_first():
    positions = np.array(
        [camera_at(0.0, rho=20.0), camera_at(45.0), camera_at(90.0, theta_deg=60.0)]
    )

    report = build_report(0, ORIGIN, UP, positions, np.arange(3), 8)

    weights = [observed.weight for observed in report.observers]
    assert weights == sorted(weights, reverse=True)
    assert report.observers[0].camera_index == 1


def test_only_the_heaviest_camera_in_a_sector_is_flagged_best():
    """Two cameras in one wedge see the same thing; only one of them wins it."""
    positions = np.array([camera_at(5.0, rho=20.0), camera_at(40.0)])

    report = build_report(0, ORIGIN, UP, positions, np.arange(2), 8)

    assert {o.camera_index for o in report.best_observers} == {1}
    assert report.sectors[0].observers == 2


def test_four_sectors_merge_the_wedges_eight_separates():
    bearings = [10.0, 55.0]
    positions = np.array([camera_at(bearing) for bearing in bearings])

    eight = build_report(0, ORIGIN, UP, positions, np.arange(2), 8)
    four = build_report(0, ORIGIN, UP, positions, np.arange(2), 4)

    assert eight.occupied_sectors == 2
    assert four.occupied_sectors == 1
    assert len(four.sectors) == 4


def test_a_camera_too_far_to_score_is_left_out():
    """The bundle drops pairs whose weight underflows float32, so we do too."""
    positions = np.array([camera_at(0.0), camera_at(180.0, rho=400.0)])

    report = build_report(0, ORIGIN, UP, positions, np.arange(2), 8)

    assert [o.camera_index for o in report.observers] == [0]


def test_a_target_nobody_can_see_reports_nothing():
    report = build_report(4, ORIGIN, UP, np.zeros((0, 3)), np.zeros(0, dtype=int), 8)

    assert report.observers == ()
    assert report.occupied_sectors == 0
    assert (report.score, report.diversity) == (0.0, 0.0)
    assert len(report.sectors) == 8


def test_stored_factors_are_used_as_given():
    """A report off the bundle shows the bundle's numbers, not fresh ones."""
    report = build_report(
        0,
        ORIGIN,
        UP,
        np.array([camera_at(0.0)]),
        np.array([0]),
        8,
        weights=(np.array([0.25]), np.array([0.5]), np.array([0.5])),
    )

    assert report.observers[0].weight == pytest.approx(0.25)
    assert report.observers[0].f_rho == pytest.approx(0.5)


# -----------------------------------------------------------------------------
# TargetReports, over a scene
# -----------------------------------------------------------------------------


def scene_with(plan_positions, *, scores=None, visibility=None):
    """A two target scene, both at the origin plane, both facing up."""
    targets = np.array([[0.0, 0.0, 0.0], [50.0, 0.0, 0.0]])
    normals = np.array([UP, UP])
    plan = vc.Plan(
        camera={"width": 640, "height": 480, "yfov_deg": 53.0},
        ids=tuple(f"vp{i}" for i in range(len(plan_positions))),
        positions=np.asarray(plan_positions, dtype=float),
        yaws_deg=np.zeros(len(plan_positions)),
        pitches_deg=np.zeros(len(plan_positions)),
    )

    return SceneData(
        mesh=trimesh.Trimesh(),
        targets=targets,
        normals=normals,
        plan=plan,
        scores=scores,
        visibility=visibility,
    )


def stored_scores(camera_count, camera_index, weight, f_rho, f_theta, sector_8, best_8):
    """A one row score table for target 0, shaped the way the loader returns one."""
    size = len(camera_index)

    return vc.Scores(
        offsets=np.array([0, size, size], dtype=np.int64),
        camera_index=np.asarray(camera_index, dtype=np.int32),
        weight=np.asarray(weight, dtype=np.float32),
        f_rho=np.asarray(f_rho, dtype=np.float32),
        f_theta=np.asarray(f_theta, dtype=np.float32),
        sector_8=np.asarray(sector_8, dtype=np.int8),
        sector_4=np.asarray(sector_8, dtype=np.int8) // 2,
        best_8=np.asarray(best_8, dtype=bool),
        best_4=np.asarray(best_8, dtype=bool),
        diversity_8=np.array([0.25, 0.0], dtype=np.float32),
        diversity_4=np.array([0.5, 0.0], dtype=np.float32),
        score_8=np.array([0.125, 0.0], dtype=np.float32),
        score_4=np.array([0.25, 0.0], dtype=np.float32),
        meta=json.loads(json.dumps({"version": 1, "camera_count": camera_count})),
    )


def test_a_scored_bundle_is_read_rather_than_recomputed():
    scores = stored_scores(
        camera_count=2,
        camera_index=[0, 1],
        weight=[0.9, 0.3],
        f_rho=[1.0, 0.5],
        f_theta=[0.9, 0.6],
        sector_8=[2, 5],
        best_8=[True, True],
    )
    scene = scene_with([camera_at(100.0), camera_at(250.0)], scores=scores)

    report = TargetReports(scene).report(0, 8)
    assert report is not None

    assert not report.live
    assert [o.sector for o in report.observers] == [2, 5]
    assert report.observers[0].weight == pytest.approx(0.9, abs=1e-6)
    assert report.score == pytest.approx(0.125)
    assert report.diversity == pytest.approx(0.25)


def test_an_unstored_sector_count_is_derived_from_the_stored_weights():
    """Six wedges is nobody's column, but the weights on disk still stand."""
    scores = stored_scores(
        camera_count=1,
        camera_index=[0],
        weight=[0.42],
        f_rho=[0.6],
        f_theta=[0.7],
        sector_8=[0],
        best_8=[True],
    )
    scene = scene_with([camera_at(190.0)], scores=scores)

    report = TargetReports(scene).report(0, 6)
    assert report is not None

    assert len(report.sectors) == 6
    assert report.observers[0].weight == pytest.approx(0.42, abs=1e-6)
    assert report.observers[0].sector == 3  # 190 degrees, in wedges of 60
    assert report.score == pytest.approx(0.42 / 6, abs=1e-6)


def test_a_plan_the_bundle_never_scored_is_recomputed():
    scores = stored_scores(
        camera_count=1,
        camera_index=[0],
        weight=[0.42],
        f_rho=[0.6],
        f_theta=[0.7],
        sector_8=[0],
        best_8=[True],
    )
    # Two cameras against a table that only ever covered one of them.
    scene = scene_with([camera_at(0.0), camera_at(180.0)], scores=scores)
    reports = TargetReports(scene)

    assert not reports.stored

    report = reports.report(0, 8)
    assert report is not None
    assert report.live
    assert len(report.observers) == 2
    assert report.observers[0].weight == pytest.approx(1.0)


def test_the_shipped_visibility_matrix_decides_who_observes():
    visible = np.array([[True, False], [False, True]])
    scene = scene_with([camera_at(0.0), camera_at(180.0)], visibility=visible)

    report = TargetReports(scene).report(0, 8)
    assert report is not None

    assert [o.camera_index for o in report.observers] == [0]
    assert not report.assumed_visibility


def test_a_camera_with_no_visibility_data_is_assumed_to_see_the_target():
    """Better an approximate row, clearly flagged, than a blank panel."""
    visible = np.array([[True, False]])  # one row for two cameras
    scene = scene_with([camera_at(0.0), camera_at(180.0)], visibility=visible)

    report = TargetReports(scene).report(0, 8)
    assert report is not None

    assert [o.camera_index for o in report.observers] == [0, 1]
    assert report.assumed_visibility


def test_reports_are_cached_per_target_and_sector_count():
    scene = scene_with([camera_at(0.0)])
    reports = TargetReports(scene)

    assert reports.report(0, 8) is reports.report(0, 8)
    assert reports.report(0, 8) is not reports.report(0, 4)

    reports.forget()
    assert reports.report(0, 8) is not None


def test_an_index_that_is_not_a_target_reports_nothing():
    reports = TargetReports(scene_with([camera_at(0.0)]))

    assert reports.report(99, 8) is None
    assert reports.report(-1, 8) is None


# -----------------------------------------------------------------------------
# The single best observer, and the weights by camera
# -----------------------------------------------------------------------------


def test_the_top_observer_is_the_heaviest_of_them_all():
    """Not the same as a sector winner: one per target, not one per wedge."""
    positions = np.array([camera_at(0.0), camera_at(90.0), camera_at(180.0)])
    report = build_report(0, ORIGIN, UP, positions, np.arange(3), 8)

    top = report.top_observer
    assert top is not None
    assert top is report.observers[0]
    assert top.weight == max(observer.weight for observer in report.observers)


def test_a_target_nobody_observes_has_no_top_observer():
    report = build_report(0, ORIGIN, UP, np.zeros((0, 3)), np.zeros(0, dtype=np.int64), 8)

    assert report.top_observer is None


def test_the_weights_map_is_keyed_by_plan_row_not_by_position():
    """Colouring things that are not rows needs the camera's own index."""
    positions = np.array([camera_at(0.0), camera_at(120.0)])
    report = build_report(0, ORIGIN, UP, positions, np.array([4, 9]), 8)

    weights = report.weights()

    assert set(weights) == {4, 9}
    assert weights == {observer.camera_index: observer.weight for observer in report.observers}


def test_the_weights_map_is_empty_when_nothing_observes():
    report = build_report(0, ORIGIN, UP, np.zeros((0, 3)), np.zeros(0, dtype=np.int64), 8)

    assert report.weights() == {}


# -----------------------------------------------------------------------------
# Sectors that fall outside the compass
# -----------------------------------------------------------------------------


def test_an_observer_in_no_such_sector_is_left_out_of_the_summary():
    """A four sector summary must not be handed an eight sector index."""
    summary = summarise_sectors([observer(sector=6), observer(sector=1)], sector_count=4)

    assert [wedge.observers for wedge in summary] == [0, 1, 0, 0]


def test_a_negative_sector_is_left_out_too():
    summary = summarise_sectors([observer(sector=-1)], sector_count=4)

    assert all(wedge.observers == 0 for wedge in summary)


def test_an_added_camera_is_asked_of_the_live_visibility_rather_than_assumed():
    """The shipped matrix stops at the plan it was built for; past that the
    recomputed mask is what decides, and the report is not flagged."""

    class Live:
        """Stands in for TargetVisibility: camera 1 sees only the far target."""

        def mask_for(self, camera):
            return np.array([False, True])

    visible = np.array([[True, False]])  # one row, for camera 0 only
    scene = scene_with([camera_at(0.0), camera_at(180.0)], visibility=visible)

    near = TargetReports(scene, visibility=Live()).report(0, 8)
    far = TargetReports(scene, visibility=Live()).report(1, 8)
    assert near is not None and far is not None

    assert [o.camera_index for o in near.observers] == [0]
    assert [o.camera_index for o in far.observers] == [1]
    assert not near.assumed_visibility and not far.assumed_visibility
