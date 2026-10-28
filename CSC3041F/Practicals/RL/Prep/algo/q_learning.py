import numpy as np
import random

# Hyperparameters
GAMMA = 0.9
ALPHA = 0.1
EPSILON = 0.1
EPISODES = 500
START_CELL = (4, 0)

def run_q_learning(env):
    action_list = list(env.ACTIONS.keys())
    n_actions = len(action_list)

    # Initialize Q-table: H x W x n_actions
    Q = np.zeros((env.H, env.W, n_actions))

    for ep in range(EPISODES):
        s = START_CELL
        while s not in env.terminals:
            x, y = s

            # ε-greedy action selection
            if random.random() < EPSILON:
                a_idx = random.randint(0, n_actions - 1)
            else:
                a_idx = np.argmax(Q[x, y, :])
            a = action_list[a_idx]

            # Take action
            ns, r = env.step(s, a)
            nx, ny = ns

            # Q-learning update
            # Find max over next actions manually
            max_q = -float("inf")
            for a in range(len(env.ACTIONS)):  # number of actions
                if Q[nx, ny, a] > max_q:
                    max_q = Q[nx, ny, a]

            # Q-learning update
            Q[x, y, a_idx] += ALPHA * (r + GAMMA * max_q - Q[x, y, a_idx]) # updating with the maximum Q-value of the next state, not the current action's Q-value. This is the key difference from SARSA.

            # Move to next state
            s = ns

    # Extract policy
    policy = np.full((env.H, env.W), " ")
    for x in range(env.H):
        for y in range(env.W):
            if (x, y) in env.terminals:
                policy[x, y] = "T"
            else:
                policy[x, y] = action_list[np.argmax(Q[x, y, :])]

    return Q, policy
