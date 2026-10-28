def update_q(Q, N, episode, gamma):
    """
    Update Q-values and visit counts N for each first-visit state-action pair in a single episode.

    Args:
        Q (dict of dicts): Q[state][action] = value
        N (dict of dicts): N[state][action] = count
        episode (dict): {'states': [...], 'actions': [...], 'rewards': [...]}
        gamma (float): discount factor

    Returns:
        None: updates Q and N in-place
    """

    visited = set()
    states, actions, rewards = episode["states"], episode["actions"], episode["rewards"]

    for i in range(len(states)):
        state = states[i]
        action = actions[i]

        N[state][action] += 1
        if (state, action) in visited:
            continue    # Skip

        visited.add((state, action)) # Add state-action tuple to visited set

        g0 = 0.0
        for j in range(len(rewards)):
            g0 += rewards[j] * (gamma ** j)

        visit_count = N[state][action]
        prev_g = Q[state][action]
        Q[state][action] = (g0 + prev_g) / visit_count


def extract_policy(Q):
    """
    Derive a deterministic greedy policy from a fully defined Q-table.

    Args:
        Q (dict of dicts): Q[state][action] = value

    Returns:
        dict: mapping state -> action with the highest Q-value
        In case of ties, use lexicographical (alphabetical) order.
    """
    policy = {}

    for state in Q.keys():
        actions = Q[state]

        # Find max Q-value
        best_action = None
        for a in sorted(actions.keys()):
            if best_action is None:
                best_action = a
                continue

            q_v = actions[a]
            if actions[best_action] < q_v:
                best_action = a

        policy[state] = best_action

    return policy
