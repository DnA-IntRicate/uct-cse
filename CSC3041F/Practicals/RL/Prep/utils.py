def simulate_path(env, policy, start):
    s = start
    path = [s]
    while s not in env.terminals:
        a = policy[s]
        s, _ = env.step(s, a)
        path.append(s)
    print(f"Path: {path}")
