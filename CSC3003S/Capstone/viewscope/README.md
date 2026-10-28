# ViewScope-2026 ~ By Swapchain

Viewpoint planning studio.

## Authors

- Adam Foflonker
- Kira Webb
- Azaam Holdman

---

## Running the Project

Run the setup script found in the `scripts/` folder. Then run the following command to build & run the program:

``` text
uv run viewscope 
```

The startup screen lists the projects. "Add a project..." takes a folder that already holds a bundle; "Build a project from a model..." turns an `.obj` into one. The viewer's toolbar has "<- Projects" (`Ctrl+Shift+P`) to come back.

---

## The Viewer

- **3D viewport**: *orbit/pan/dolly* around the model with the mouse (look-at
  camera, pivoting on whatever you're viewing rather than the scene's
  bounding box), or switch to trackball mode from the gizmo in the corner.
  The camera orientation widget snaps to axis-aligned views.
- **Display modes**: textured, geometry, targets, or all of it; point size,
  grid, and glyph visibility are adjustable from the Display panel.
- **Viewpoints**: each planned camera is a frustum glyph in the scene.
  Click one to select it (or use the Viewpoints panel), step through them
  with `N`/`P` or the arrow keys, and drag it into place with the move gizmo.
  "Overview" (`O`) returns to free-look.
- **Targets**: click a point on the surface to see which cameras observe
  it, from what angle and distance, and how its visibility is spread across
  sectors around it. Occlusion mode paints the surface by what the selected
  camera (or the whole planned route) can actually see.
- **Route planning**: pick a subset of viewpoints, see their combined
  coverage, and save the result as a route file to load again later.
- **Full-resolution model**: if a bundle ships one, the camera-view panel
  (and, optionally, the main viewport) swaps the simplified mesh for the
  full-quality textured model the bundle was built from. Reading it once is
  cached to disk, so later loads skip re-parsing the source `OBJ`.
- **Render Still** (`Ctrl+R`): save a pyrender image of whatever the viewport
  is currently looking at, shaded the same way the planning results were
  computed.

---

## Building a bundle from a model

3D models (`obj` format) can be imported into the project by building it into a scene bundle, which can be done from the command line as seen below:

``` text
uv run viewscope-build data/SeaHawk/Seahawk.obj data/SeaHawk --length 19.76 --up y
```

This same functionality is also present through the **GUI** in the **startup window**.

It writes the six files a project needs:

- `scene.obj`
- `targets.ply`
- `plan.json`
- `visibility.npz`
- `scores.npz`
- `flyable.npz`

It produces every number through `viewscope_core`, the way `data/kiri` was made. The model is baked to vertex colours, turned `+Z` up, and scaled so its longest side measure (`--length` metres parameter).

---
