from algo.value_iteration import run_value_iteration
from algo.q_learning import run_q_learning
from env.grid_world import GridWorld
from utils import simulate_path
import numpy as np

if __name__ == "__main__":
    env = GridWorld()
    # V_or_Q, pi_star = run_value_iteration(env)
    V_or_Q, pi_star = run_q_learning(env)
    print(V_or_Q.shape) # (H, W, n_actions) for Q-learning, (H, W) for value iteration
    print("--- State Values ---")
    print(np.round(V_or_Q, 2)) # V(s) stores one value per state, while Q(s,a) stores one value per state-action pair, so Q needs more memory.
    print("\n--- Optimal Policy ---")
    for row in pi_star:
        print("  ".join(row))
    print("\n--- Simulation ---")
    simulate_path(env, pi_star, start=(4,0))
