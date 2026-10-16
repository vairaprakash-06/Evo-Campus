# 🧬 Smart Campus Resource Optimizer

> **“Evolving Intelligence, Optimizing Tomorrow.”**  
> **Team EvoNex** &bull; College Evolutionary Computing (EC) Project

![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)
![Framework](https://img.shields.io/badge/Streamlit-1.30%2B-FF4B4B.svg)
![Optimization](https://img.shields.io/badge/Algorithm-Genetic%20Algorithm%20(From%20Scratch)-success.svg)
![Database](https://img.shields.io/badge/Database-SQLite3-003B57.svg)
![Tests](https://img.shields.io/badge/Tests-12%20Passed%20(pytest)-brightgreen.svg)

---

## 📌 Executive Summary

The **Smart Campus Resource Optimizer** is a production-grade web application engineered to solve the complex, multi-constrained resource scheduling challenges faced by academic institutions. Modern universities contend with limited lecture halls, computer terminals, specialized lab apparatus, and financial operating budgets while managing competing, high-demand academic sessions. 

Using an Evolutionary Computing approach, this application implements a **custom Genetic Algorithm (GA) from scratch** in pure Python/NumPy—featuring chromosome encoding, tournament selection, single-point crossover, gene mutation, elitism, and strict feasibility repair mechanisms to guarantee optimal, constraint-compliant resource distribution.

---

## 📂 Project Architecture & Directory Structure

```text
smart_campus_resource_optimizer/
├── .streamlit/
│   └── config.toml               # Modern dark navy visual theme & port settings
├── database.py                   # SQLite persistence, transactional schema, & CRUD operations
├── optimizer.py                  # Pure Python Genetic Algorithm with repair & fitness operators
├── app.py                        # Streamlit web application & Plotly telemetry dashboard
├── requirements.txt              # Production and testing Python package dependencies
├── .gitignore                    # Version control ignore rules (caches, environments, temp files)
├── README.md                     # Deployment, setup, and developer operations guide
├── ACADEMIC_DOCUMENTATION.md     # Full academic project report with mathematical proofs & flowcharts
└── tests/
    ├── __init__.py               # Test package initialization
    ├── test_optimizer.py         # Automated unit & integration tests for GA operators
    └── test_database.py          # Automated unit tests for database transactions & integrity
```

---

## 🚀 Key Modules & System Features

### 1. 📊 Executive Dashboard
- **Real-time KPI Metrics**: Available campus capacity, total active academic activities, gross demand units, demand satisfaction rate, resource utilization percentage, and latest run fitness score.
- **Resource Pressure Visualizer**: Interactive Plotly comparative charts contrasting physical capacities against active demands.
- **Priority Tier Breakdown**: Distribution of critical, high, medium, and low priority requests.
- **Recent Runs Ledger**: Quick-glance audit trail of recent optimization executions.

### 2. 📚 Activity Management
- Add, view, edit, toggle, and delete academic sessions (e.g. lectures, practical labs, workshops).
- Attributes: Activity Name, Required Resource Type, Demand Quantity ($D_i > 0$), Priority Rating (1: Low to 5: Critical), Unit Cost ($/unit), and Active Status.
- Real-time constraint validation and duplicate name prevention.

### 3. 🏛️ Resource Management
- Configure campus facilities: Classrooms (Seats), Computer Labs (Workstations), and Specialized Equipment (Sets).
- Adjust facility capacities dynamically.
- Relational integrity enforcement: Prevents deletion of resources currently linked to academic activities.

### 4. 🧬 Genetic Algorithm Optimizer
- **Chromosome Representation**: Integer vector where each gene corresponds to the allocated units for an academic activity ($0 \le x_i \le D_i$).
- **Tournament Selection**: Configurable tournament size ($k$) selecting superior parents.
- **Single-Point Crossover**: Recombines gene tails with probability $P_c$.
- **Gene-Level Mutation**: Small step adjustments or uniform resampling with probability $P_m$.
- **Elitism**: Retains top $k$ candidates unchanged into subsequent generations to prevent regression.
- **Strict Feasibility Repair**: Deterministically enforces capacity limits and monetary budget constraints by trimming allocations from lowest-priority/highest-cost activities first.
- **Deterministic Reproducibility**: User-configurable random seed.

### 5. 📈 Results & Visual Analytics
- **Fitness Convergence Trajectory**: Plotly interactive graph of Best, Population Mean, and Min fitness across generations.
- **Demand vs. Allocation Comparison**: Grouped bar charts showing requested vs delivered quantities.
- **Resource Utilization Analysis**: Stacked visual breakdown of physical campus occupancy vs unused capacity.
- **Financial Spending & Sunbursts**: Budget utilization per activity and resource type.
- **CSV Data Export**: One-click download of the complete allocation manifest and run summary metadata.

### 6. 📜 Optimization History & Audit Ledger
- Permanent persistence of every optimization run in SQLite.
- Complete audit parameters: population size, generations, mutation rate, best fitness, runtime, and seed.
- Historical run inspector: Reload and visualize previous allocations and convergence curves at any time.

---

## 🛠️ Local Installation & Setup Instructions

### Prerequisites
- Python 3.10, 3.11, 3.12, 3.13, or 3.14
- Git (optional, for version control)

### Step 1: Clone or Navigate to the Repository
```bash
git clone https://github.com/your-username/smart-campus-resource-optimizer.git
cd smart-campus-resource-optimizer
```

### Step 2: Create and Activate a Virtual Environment
- **On Windows (PowerShell):**
  ```powershell
  python -m venv venv
  .\venv\Scripts\Activate.ps1
  ```
- **On macOS / Linux:**
  ```bash
  python3 -m venv venv
  source venv/bin/activate
  ```

### Step 3: Install Required Dependencies
```bash
pip install -r requirements.txt
```

### Step 4: Run Automated Tests
Verify algorithm correctness, constraint adherence, and database persistence:
```bash
python -m pytest tests -v
```
*(Alternative using Python standard library: `python -m unittest discover tests`)*

### Step 5: Launch the Streamlit Web Application
```bash
python -m streamlit run app.py
```
Open your browser and navigate to: **`http://localhost:8501`**

---

## ☁️ Streamlit Community Cloud Deployment Guide

Deploy your application online for free in under 5 minutes:

1. **Push Code to GitHub**:
   ```bash
   git init
   git add .
   git commit -m "feat: complete Smart Campus Resource Optimizer for Team EvoNex"
   git branch -M main
   git remote add origin https://github.com/<your-github-username>/smart-campus-resource-optimizer.git
   git push -u origin main
   ```

2. **Access Streamlit Community Cloud**:
   - Visit [share.streamlit.io](https://share.streamlit.io/) and log in with your GitHub account.

3. **Deploy New App**:
   - Click **"New app"**.
   - Select your repository: `<your-github-username>/smart-campus-resource-optimizer`.
   - Set Branch: `main`.
   - Set Main file path: `app.py`.
   - Click **"Deploy!"**.

### ⚠️ Note on SQLite Persistence on Free Cloud Hosting
> [!IMPORTANT]
> Streamlit Community Cloud operates on ephemeral container instances. While SQLite works locally with permanent persistence, free cloud containers reset their local disk upon redeployment, server sleep, or container migration. 
> 
> The application is engineered to automatically self-seed realistic campus data (`campus_optimizer.db`) whenever a fresh container launches. For permanent enterprise persistence across cloud restarts, the database layer in `database.py` can be pointed to PostgreSQL, Supabase, or AWS RDS by swapping the connection string.

---

## 🧪 Automated Test Suite Validation

The automated test suite (`tests/test_optimizer.py` and `tests/test_database.py`) covers:
1. **Fitness Proportionality**: Verifies higher priority activities yield higher fitness gains.
2. **Demand Boundary Enforcement**: Ensures allocations never exceed requested demand ($0 \le x_i \le D_i$).
3. **Resource Capacity Limits**: Validates that multi-activity allocations never exceed physical classroom, lab, or equipment capacities.
4. **Budget Constraint Compliance**: Confirms total spending strictly respects maximum budgetary ceilings.
5. **Genetic Operator Variation**: Verifies crossover recombinations and valid gene mutations.
6. **Deterministic Seed Reproducibility**: Ensures identical random seeds yield identical solutions.
7. **Database Transaction Integrity**: Tests relational foreign keys, cascade constraints, duplicate name prevention, and historical record retrieval.

---

## 👥 Team EvoNex & Project Information

- **Project**: Smart Campus Resource Optimizer
- **Team**: EvoNex
- **Motto**: *“Evolving Intelligence, Optimizing Tomorrow.”*
- **Course**: Evolutionary Computing (EC) / Metaheuristic Optimization
- **License**: MIT Open Source License
