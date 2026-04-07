import pulp

def get_optimal_team(df):
    prob = pulp.LpProblem("Fantasy_Optimizer", pulp.LpMaximize)
    player_vars = pulp.LpVariable.dicts("P", df.index, cat=pulp.LpBinary)

    # Objective: Maximize Points
    prob += pulp.lpSum([df.loc[i, 'points'] * player_vars[i] for i in df.index])

    # Basic Constraints
    prob += pulp.lpSum([player_vars[i] for i in df.index]) == 11
    prob += pulp.lpSum([df.loc[i, 'credits'] * player_vars[i] for i in df.index]) <= 100

    # Role Constraints
    prob += pulp.lpSum([player_vars[i] for i in df.index if df.loc[i, 'role'] == 'WK']) >= 1
    prob += pulp.lpSum([player_vars[i] for i in df.index if df.loc[i, 'role'] == 'BOWL']) >= 3
    
    prob.solve(pulp.PULP_CBC_CMD(msg=0))
    return df.loc[[i for i in df.index if player_vars[i].varValue == 1]]