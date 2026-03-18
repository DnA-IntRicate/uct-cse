import numpy as np

# Hyperparameters
GAMMA = 0.9
THETA = 1e-4
START_CELL = (4, 0)

def run_value_iteration(env):
    V = np.zeros((env.H, env.W))
    
    # 1. Value Estimation Loop
    while True:
        delta = 0
        for x in range(env.H):
            for y in range(env.W):
                s = (x, y)
                if s in env.terminals:
                    continue
                
                v_old = V[x, y]
                
                # Bellman Optimality Update: V(s) = max_a [r + gamma * V(s')]
                action_values = []
                for a in env.ACTIONS:
                    ns, r = env.step(s, a)
                    action_values.append(r + GAMMA * V[ns])
                
                V[x, y] = max(action_values)
                delta = max(delta, abs(v_old - V[x, y]))
        if delta < THETA:
            break

    # 2. Policy Extraction
    policy = np.full((env.H, env.W), " ")
    for x in range(env.H):
        for y in range(env.W):
            s = (x, y)
            if s in env.terminals:
                policy[x, y] = "T"
                continue
            
            best_action = None
            max_val = float('-inf')
            for a in env.ACTIONS:
                ns, r = env.step(s, a)
                val = r + GAMMA * V[ns]
                if val > max_val:
                    max_val = val
                    best_action = a #argmax
            policy[x, y] = best_action

    return V, policy

