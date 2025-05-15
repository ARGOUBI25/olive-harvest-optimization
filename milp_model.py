# model/milp_model.py

from pulp import LpProblem, LpVariable, LpMinimize, LpMaximize, lpSum, LpBinary, LpContinuous

def build_model(data, objective='profit'):
    """
    Builds the MILP model for sustainable olive harvest planning and OMW management.
    
    Parameters:
        data (dict): Dictionary containing all sets, parameters, and instance data.
        objective (str): Objective to use: 'profit', 'quality', or 'environment'.

    Returns:
        model (LpProblem): The optimization model.
    """
    model = LpProblem("Sustainable_Olive_Harvest_OMW_Optimization", LpMaximize)

    # Sets
    D, F, P, C = data['D'], data['F'], data['P'], data['C']

    # Variables
    z = LpVariable.dicts("z", ((d, f, p) for d in D for f in F for p in P), lowBound=0, cat=LpContinuous)
    v = LpVariable.dicts("v", ((d, f, p) for d in D for f in F for p in P), lowBound=0, cat=LpContinuous)
    w = LpVariable.dicts("w", ((d, f, p) for d in D for f in F for p in P), lowBound=0, cat=LpContinuous)
    e = LpVariable.dicts("e", ((d, f, p) for d in D for f in F for p in P), lowBound=0, cat=LpContinuous)
    x = LpVariable.dicts("x", ((f, p) for f in F for p in P), cat=LpBinary)
    r = LpVariable.dicts("r", ((d, f) for d in D for f in F), lowBound=0, cat=LpContinuous)
    y = LpVariable.dicts("y", ((i1, i2, c, f) for d in D for c in C for f in F for i1 in data['I_d'][d] for i2 in data['I_d'][d] if i1 <= i2), cat=LpBinary)
    o = LpVariable.dicts("o", ((i1, i2, c, f1, f2) for d in D for c in C for f1 in F for f2 in F for i1 in data['I_d'][d] for i2 in data['I_d'][d] if i1 < i2), cat=LpBinary)
    n = LpVariable.dicts("n", ((i, c, f) for d in D for c in C for f in F for i in data['I_d'][d]), cat=LpBinary)
    h = LpVariable.dicts("h", ((d, i, c, f) for d in D for i in data['I_d'][d] for c in C for f in F), cat=LpBinary)
    k = LpVariable.dicts("k", ((c, f, p) for c in C for f in F for p in P), cat=LpBinary)

    # Objective
    if objective == 'environment':
        model += lpSum(data['alpha'] * z[d, f, p] - v[d, f, p] for d in D for f in F for p in P)
    elif objective == 'quality':
        model += lpSum((data['omega1'] * data['O'][d][f] - data['omega2'] * data['A'][d][f] - data['omega3'] * data['P'][d][f] - data['omega4'] * data['H'][d][f]) * z[d, f, p] for d in D for f in F for p in P)
    else:
        model += (
            lpSum(data['V'][d][p] * data['ATR'][d][f] * z[d, f, p] for d in D for f in F for p in P)
            - lpSum(data['CP'][d][f][p] * z[d, f, p] for d in D for f in F for p in P)
            - lpSum(data['CR'][f] * r[d, f] for d in D for f in F)
            - lpSum(data['CL'][p] * (w[d, f, p] - v[d, f, p]) + data['CE'][f] * e[d, f, p] for d in D for f in F for p in P)
        )

    # Constraints
    for d in D:
        for f in F:
            for p in P:
                model += data['alpha'] * z[d, f, p] == v[d, f, p] + w[d, f, p] + e[d, f, p]
                model += v[d, f, p] <= data['alpha'] * z[d, f, p]
                model += v[d, f, p] <= data['Vmax'][d][f][p]
                model += e[d, f, p] <= data['E'][f]
            model += lpSum(w[d, f2, p] for f2 in F for p in P) <= data['B_total'][d]
        for p in P:
            model += lpSum((data['O'][d][f] - data['O_thresh'][d][p]) * z[d, f, p] for f in F) >= 0
            model += lpSum(data['A'][d][f] * z[d, f, p] for f in F) <= data['A_thresh'][d][p] * lpSum(z[d, f, p] for f in F)
            model += lpSum(data['P'][d][f] * z[d, f, p] for f in F) <= data['P_thresh'][d][p] * lpSum(z[d, f, p] for f in F)
            model += lpSum(data['H'][d][f] * z[d, f, p] for f in F) <= data['H_thresh'][d][p] * lpSum(z[d, f, p] for f in F)
            model += data['QP_min'][d][p] <= lpSum(z[d, f, p] for f in F) <= data['QP_max'][d][p]
            model += lpSum(z[d, f, p] for f in F) <= data['S'][p]
        for c in C:
            model += data['Q_min'][d][c] <= lpSum(data['R'][f] * (i2 - i1 + 1) * y[i1, i2, c, f] for f in F for i1 in data['I_d'][d] for i2 in data['I_d'][d] if i1 <= i2) <= data['Q_max'][d][c]
        for f in F:
            model += lpSum(z[d, f, p] for p in P) + r[d, f] == lpSum(data['R'][f] * (i2 - i1 + 1) * y[i1, i2, c, f] for c in C for i1 in data['I_d'][d] for i2 in data['I_d'][d] if i1 <= i2)
    for f in F:
        model += lpSum(y[i1, i2, c, f] for d in D for c in C for i1 in data['I_d'][d] for i2 in data['I_d'][d] if i1 <= i2) <= 1
        model += lpSum(x[f, p] for p in P) == 1
    for d in D:
        for f in F:
            for p in P:
                model += z[d, f, p] <= data['M'][f] * x[f, p]

    # Flow-based logistics (simplified conservation)
    for c in C:
        model += lpSum(y[i0, i2, c, f] + n[i0, c, f] + lpSum(o[i0, i2, c, f, f2] for f2 in F) + k[c, f, data['p_c'][c]] for f in F if i0 := data['I_c0'][c][0]) == 1
        for d in D:
            for i in data['I_d'][d]:
                for f in F:
                    inflow = (
                        lpSum(y[i1, i2, c, f] for i1 in data['I_d'][d] for i2 in data['I_d'][d] if i1 <= i <= i2) +
                        n[i - 1, c, f] +
                        lpSum(o[i1, i2, c, f2, f] for f2 in F for i1 in data['I_d'][d] for i2 in data['I_d'][d] if i1 < i == i2)
                    )
                    outflow = (
                        lpSum(y[i, i2, c, f] for i2 in data['I_d'][d] if i2 >= i) +
                        n[i, c, f] +
                        lpSum(o[i, i2, c, f, f2] for f2 in F for i2 in data['I_d'][d] if i2 > i)
                    )
                    model += inflow == outflow
            for i in data['I_c0'][c]:
                model += (
                    lpSum(y[i1, i, c, f] for f in F for i1 in data['I_d'][d] if i1 < i) +
                    lpSum(n[i - 1, c, f] for f in F) +
                    lpSum(o[i1, i, c, f2, f] for f in F for f2 in F for i1 in data['I_d'][d] if i1 < i)
                ) == lpSum(h[d, i, c, f] for f in F)
                for f in F:
                    model += h[d, i, c, f] == (
                        lpSum(y[i, i2, c, f] for i2 in data['I_d'][d] if i2 >= i) +
                        n[i, c, f] +
                        lpSum(o[i, i2, c, f, f2] for f2 in F for i2 in data['I_d'][d] if i2 > i)
                    )

    return model
