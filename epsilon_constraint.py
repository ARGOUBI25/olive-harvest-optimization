# epsilon_constraint.py

import csv
import itertools
from pulp import LpStatusOptimal
from milp_model import build_model

# Placeholder function to extract objective values from a solved model
def extract_objectives(model, data, z, v, w, e, r):
    Z1 = sum(data['alpha'] * z[d, f, p].varValue - v[d, f, p].varValue for d in data['D'] for f in data['F'] for p in data['P'])
    Z2 = sum((data['omega1'] * data['O'][d][f] - data['omega2'] * data['A'][d][f] -
              data['omega3'] * data['P'][d][f] - data['omega4'] * data['H'][d][f]) * z[d, f, p].varValue
              for d in data['D'] for f in data['F'] for p in data['P'])
    Z3 = (sum(data['V'][d][p] * data['ATR'][d][f] * z[d, f, p].varValue for d in data['D'] for f in data['F'] for p in data['P'])
          - sum(data['CP'][d][f][p] * z[d, f, p].varValue for d in data['D'] for f in data['F'] for p in data['P'])
          - sum(data['CR'][f] * r[d, f].varValue for d in data['D'] for f in data['F'])
          - sum(data['CL'][p] * (w[d, f, p].varValue - v[d, f, p].varValue) + data['CE'][f] * e[d, f, p].varValue
                for d in data['D'] for f in data['F'] for p in data['P']))
    return Z1, Z2, Z3

# Solve individual objective optima
def solve_individual_optima(data):
    results = {}
    for obj in ['quality', 'profit']:
        model = build_model(data, objective=obj)
        status = model.solve()
        if status == LpStatusOptimal:
            results[obj] = model.objective.value()
        else:
            results[obj] = None
    return results['quality'], results['profit']

# Explore epsilon grid and build Pareto front
def generate_pareto_front(data, p2=5, p3=10, output_csv='pareto_front.csv'):
    q_min, q_max = 0, 0
    g_min, g_max = 0, 0

    q_opt, g_opt = solve_individual_optima(data)
    q_min, q_max = 0.9 * q_opt, q_opt
    g_min, g_max = 0.9 * g_opt, g_opt

    eps_q_values = [q_min + i * (q_max - q_min) / p2 for i in range(p2 + 1)]
    eps_g_values = [g_min + j * (g_max - g_min) / p3 for j in range(p3 + 1)]

    pareto_solutions = []

    for eps_q, eps_g in itertools.product(eps_q_values, eps_g_values):
        model = build_model(data, objective='environment')

        # Add epsilon constraints
        model += (lpSum((data['omega1'] * data['O'][d][f] - data['omega2'] * data['A'][d][f] -
                         data['omega3'] * data['P'][d][f] - data['omega4'] * data['H'][d][f]) * model.variablesDict()[f"z_{d}_{f}_{p}"]
                         for d in data['D'] for f in data['F'] for p in data['P']) >= eps_q, f"Eps_Quality_{eps_q}")

        model += (lpSum(data['V'][d][p] * data['ATR'][d][f] * model.variablesDict()[f"z_{d}_{f}_{p}"]
                         - data['CP'][d][f][p] * model.variablesDict()[f"z_{d}_{f}_{p}"]
                         - data['CL'][p] * (model.variablesDict()[f"w_{d}_{f}_{p}"] - model.variablesDict()[f"v_{d}_{f}_{p}"])
                         - data['CE'][f] * model.variablesDict()[f"e_{d}_{f}_{p}"]
                         for d in data['D'] for f in data['F'] for p in data['P']
                         ) - sum(data['CR'][f] * model.variablesDict()[f"r_{d}_{f}"] for d in data['D'] for f in data['F']) >= eps_g,
                   f"Eps_Profit_{eps_g}")

        status = model.solve()
        if status == LpStatusOptimal:
            z, v, w, e, r = {}, {}, {}, {}, {}
            for var in model.variables():
                if var.name.startswith("z_"):
                    key = tuple(map(int, var.name[2:].split("_")))
                    z[key] = var
                elif var.name.startswith("v_"):
                    key = tuple(map(int, var.name[2:].split("_")))
                    v[key] = var
                elif var.name.startswith("w_"):
                    key = tuple(map(int, var.name[2:].split("_")))
                    w[key] = var
                elif var.name.startswith("e_"):
                    key = tuple(map(int, var.name[2:].split("_")))
                    e[key] = var
                elif var.name.startswith("r_"):
                    key = tuple(map(int, var.name[2:].split("_")))
                    r[key] = var

            Z1, Z2, Z3 = extract_objectives(model, data, z, v, w, e, r)
            pareto_solutions.append({'Z1': Z1, 'Z2': Z2, 'Z3': Z3})

    # Export to CSV
    with open(output_csv, 'w', newline='') as csvfile:
        fieldnames = ['Z1', 'Z2', 'Z3']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for row in pareto_solutions:
            writer.writerow(row)

    print(f"Pareto front exported to {output_csv}")

# Example usage (requires data dictionary)
# from data_template import load_data
# data = load_data()
# generate_pareto_front(data)
