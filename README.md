# 🫒 Olive Harvest Optimization

This repository contains the code and data for the study:  
**"Sustainable Planning for Olive Harvest and Olive Mill Wastewater Valorization in Tunisia: An Integrated Optimization Framework"**

## 📦 Repository Contents

| File/Folder                | Description                                                                 |
|----------------------------|-----------------------------------------------------------------------------|
| `model/milp_model.py`      | MILP formulation for olive harvest and OMW management optimization.         |
| `model/epsilon_constraint.py` | ε-constraint method (AUGMECON2) for multi-objective optimization.           |
| `data_template.py`         | Generator for sample case study data (Henchir Chaal, Tunisia).              |
| `results/`                 | Generated Pareto front and figures (CSV + PNG).                            |

## 🔧 Installation

1. **Prerequisites**: Python 3.9+  
2. Install dependencies:  
   ```bash
   pip install -r requirements.txt
   ```  
   *(Optional)* For commercial use with Gurobi:  
   ```bash
   pip install gurobipy
   ```

## 🚀 Quick Start  

```bash
python model/epsilon_constraint.py --p2 5 --p3 10 --output results/pareto_front.csv
```  
*You can change p2 and p3 to control the grid granularity for quality (Z2) and profit (Z3).*

*Input data is generated via data_template.py.*  

## 📊 Output & Visualization
The script generates:

*results/pareto_front.csv — Pareto-optimal solutions.*

*results/pareto_front.png — Front Z2 (Quality) vs Z3 (Profit).*

*results/mill_P1_flow.png, mill_P2_flow.png, mill_P3_flow.png — Quantity processed per mill.*

*results/day_1_harvest.png to results/day_14_harvest.png — Harvested quantity per day.*

*These allow for visual analysis of environmental–economic trade-offs and system load.*

## 🧪 Data
This repository includes synthetic data representing the Henchir Chaal case study (18 plots, 3 mills, 14 days).
Parameters include olive quality attributes, capacities, waste coefficients, and cost structures.



## 📜 License  
MIT License. See [LICENSE](LICENSE).  

## 📚 Citation  

```bibtex
@article{argoubi2025,
  title={Optimizing Olive Harvest and Wastewater Valorization in Tunisia: A Sustainable Planning Framework for Circular Agri-Waste Management},  
  author={Argoubi, M. and Mili, K.},  
  year={2025},  
  doi={10.5281/zenodo.XXXXXXX}  
}
```  
