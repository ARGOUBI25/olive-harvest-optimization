# epsilon_constraint.py

import csv
import itertools
import argparse
import multiprocessing
import matplotlib.pyplot as plt
from pulp import LpStatusOptimal
from milp_model import build_model
from data_template import load_data

# Extract objectives from solved model
def extract_objectives(model, data, z, v, w, e, r):
    Z1 = sum(data['alpha'] * z[k].varValue - v[k].varValue for k in z)
    Z2 = sum((data['omega1'] * data['O'][d][f] - data['omega2'] * data['A'][d][f] -
              data['omega3'] * data['P'][d][f] - data['omega4'] * data['H'][d][f]) * z[d, f, p].varValue
              for (d, f, p) in z)
    Z3 = (
        sum(data['V'][d][p] * data['ATR'][d][f] * z[d, f, p].varValue for (d, f, p) in z)
        - sum(data['CP'][d][f][p] * z[d, f, p].varValue for (d, f, p) in z)
        - sum(data['CL'][p] * (w[d, f, p].varValue - v[d, f, p].varValue) + data['CE'][f] * e[d, f, p].varValue
              for (d, f, p) in z)
        - sum(data['CR'][f] * r[d, f].varValue for (d, f) in r)
    )
    return Z1, Z2, Z3

# Solve optima for quality and profit
def solve_individual_optima(data):
    from pulp import LpStatusOptimal
    q_model = build_model(data, objective='quality')
    g_model = build_model(data, objective='profit')
    q_model.solve()
    g_model.solve()
    return q_model.objective.value(), g_model.objective.value()

# Solve one instance
def solve_instance(args):
    data, eps_q, eps_g = args
    model = build_model(data, objective='environment')

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

    model += extract_objectives(model, data, z, v, w, e, r)[1] >= eps_q
    model += extract_objectives(model, data, z, v, w, e, r)[2] >= eps_g
    status = model.solve()

    if status == LpStatusOptimal:
        Z1, Z2, Z3 = extract_objectives(model, data, z, v, w, e, r)
        return {'Z1': Z1, 'Z2': Z2, 'Z3': Z3}
    return None

def generate_pareto_front(data, p2=5, p3=10, output_csv='pareto_front.csv'):
    q_opt, g_opt = solve_individual_optima(data)
    eps_q_vals = [q_opt * (0.9 + 0.1 * i / p2) for i in range(p2 + 1)]
    eps_g_vals = [g_opt * (0.9 + 0.1 * j / p3) for j in range(p3 + 1)]

    grid = list(itertools.product(eps_q_vals, eps_g_vals))
    args = [(data, q, g) for q, g in grid]

    with multiprocessing.Pool() as pool:
        results = pool.map(solve_instance, args)

    pareto_solutions = [res for res in results if res is not None]

    with open(output_csv, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=['Z1', 'Z2', 'Z3'])
        writer.writeheader()
        writer.writerows(pareto_solutions)

    # Visualisation
    Z2_vals = [r['Z2'] for r in pareto_solutions]
    Z3_vals = [r['Z3'] for r in pareto_solutions]
    plt.scatter(Z2_vals, Z3_vals, c='green')
    plt.xlabel('Olive Quality (Z2)')
    plt.ylabel('Economic Profit (Z3)')
    plt.title('Pareto Front: Quality vs Profit under Environmental Constraints')
    plt.grid(True)
    plt.tight_layout()
    plt.savefig('pareto_front.png')
    plt.show()
    print(f"Pareto front saved to {output_csv} and plot to pareto_front.png")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Generate Pareto front using epsilon-constraint method")
    parser.add_argument('--p2', type=int, default=5, help='Number of grid intervals for Z2')
    parser.add_argument('--p3', type=int, default=10, help='Number of grid intervals for Z3')
    parser.add_argument('--output', type=str, default='pareto_front.csv', help='Output CSV filename')
    args = parser.parse_args()

    data = load_data()
    generate_pareto_front(data, p2=args.p2, p3=args.p3, output_csv=args.output)
