# 🫒 Olive Harvest Optimization  

This repository contains the code and data for the study:  
**"Sustainable Planning for Olive Harvest and Olive Mill Wastewater Valorization in Tunisia: An Integrated Optimization Framework"**  

## 📦 Repository Contents  

| File/Folder          | Description                                                                 |
|----------------------|-----------------------------------------------------------------------------|
| `model/milp_model.py` | MILP formulation for olive harvest and OMW management optimization.         |
| `model/epsilon_constraint.py` | ε-constraint method implementation for multi-objective optimization.        |
| `data/`              | Sample dataset (CSV/XLSX) for simulations.                                  |
| `results/`           | Pre-computed optimization outputs (tables/figures).                        |

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
python model/epsilon_constraint.py --input data/olive_data.csv --output results/
```  
*Modify parameters in `config.yaml` for custom scenarios.*  

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
