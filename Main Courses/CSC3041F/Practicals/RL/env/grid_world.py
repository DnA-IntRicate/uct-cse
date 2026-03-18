import numpy as np

class GridWorld:
    def __init__(self):
        # Configuration
        self.W, self.H = 5, 5
        self.goal_cells = {(0, 4)}
        self.hole_cells = {(1, 0), (2, 2), (2, 4), (4, 2)}
        self.terminals = self.goal_cells | self.hole_cells

        self.goal_reward = 1
        self.hole_reward = -1
        self.step_reward = -0.001

        self.ACTIONS = {"U": (-1, 0), "D": (1, 0), "L": (0, -1), "R": (0, 1)}

    def step(self, s, a):
        """Deterministic transition: p(s', r | s, a)"""
        if s in self.terminals:
            return s, 0

        dx, dy = self.ACTIONS[a]
        x, y = s
        nx, ny = min(max(x + dx, 0), self.H - 1), min(max(y + dy, 0), self.W - 1)

        if (nx, ny) in self.goal_cells:
            reward = self.goal_reward
        elif (nx, ny) in self.hole_cells:
            reward = self.hole_reward
        else:
            reward = self.step_reward

        return (nx, ny), reward
