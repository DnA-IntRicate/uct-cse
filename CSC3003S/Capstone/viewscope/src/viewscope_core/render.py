import numpy as np
import pyrender


class SceneRenderer:
    def __init__(self, mesh, width, height, yfov_deg):
        self.width = int(width)
        self.height = int(height)
        self.yfov_deg = float(yfov_deg)
        diagonal = float(np.linalg.norm(mesh.bounds[1] - mesh.bounds[0]))
        self._scene = pyrender.Scene(bg_color=[0.03, 0.03, 0.05], ambient_light=[0.35, 0.35, 0.35])
        self._scene.add(pyrender.Mesh.from_trimesh(mesh, smooth=False))
        camera = pyrender.PerspectiveCamera(
            yfov=np.radians(self.yfov_deg),
            aspectRatio=self.width / self.height,
            znear=0.1,
            zfar=max(100.0, 10.0 * diagonal),
        )
        self._camera_node = self._scene.add(camera, pose=np.eye(4))
        light = pyrender.DirectionalLight(color=np.ones(3), intensity=3.0)
        self._light_node = self._scene.add(light, pose=np.eye(4))
        self._renderer = pyrender.OffscreenRenderer(self.width, self.height)

    def render_depth(self, pose):
        self._scene.set_pose(self._camera_node, pose)
        return self._renderer.render(self._scene, flags=pyrender.RenderFlags.DEPTH_ONLY)

    def render_color(self, pose):
        self._scene.set_pose(self._camera_node, pose)
        self._scene.set_pose(self._light_node, pose)
        color, _ = self._renderer.render(self._scene)
        return color

    def close(self):
        self._renderer.delete()
