# 🧬 Smart Campus Resource Optimizer

> **“Evolving Intelligence, Optimizing Tomorrow.”**  
> **Team EvoCampus** &bull; Smart Campus Resource Allocation & Optimization

![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)
![Framework](https://img.shields.io/badge/Framework-Flask%203.0%2B-000000.svg)
![Optimization](https://img.shields.io/badge/Algorithm-Genetic%20Algorithm%20(Pure%20Python)-success.svg)
![Database](https://img.shields.io/badge/Database-SQLite3-003B57.svg)
![Charts](https://img.shields.io/badge/Visuals-Chart.js-FF6384.svg)
![Tests](https://img.shields.io/badge/Tests-13%20Passed%20(pytest)-brightgreen.svg)

---

## 📌 Executive Summary

The **Smart Campus Resource Optimizer** is a production-grade web application engineered to solve the multi-constrained resource scheduling challenges faced by higher education academic institutions. Modern universities contend with limited lecture halls, specialized laboratories, seminar auditoriums, faculty time slots, and financial operating budgets while managing competing, high-demand academic sessions.

Built with a modern full-stack architecture using **Python, Flask, HTML5, Vanilla CSS3, JavaScript, Chart.js, and SQLite**, this system implements a genuine **Genetic Algorithm (GA)** from first principles. It optimizes facility assignments and scheduling time slots, prevents resource collisions, respects seating capacity bounds, penalizes category mismatches, and rewards high-priority academic events.

---

## 📂 Project Architecture & Directory Structure

```text
smart-campus-resource-optimizer/
├── app.py                     # Main Flask web application, REST endpoints & routing
├── database.py                # SQLite persistence, schema initialization, & CRUD operations
├── optimizer.py               # Pure Python Genetic Algorithm with repair & fitness operators
├── requirements.txt           # Production & testing package dependencies
├── README.md                  # Complete deployment, usage, and project operations guide
├── ACADEMIC_DOCUMENTATION.md  # Academic project report with mathematical proofs & flowcharts
├── campus_optimizer.db        # SQLite ACID relational database file (auto-generated)
├── static/
│   ├── css/
│   │   └── style.css          # Custom Vanilla CSS design system (dark navy glassmorphism)
│   └── js/
│       └── main.js            # Client-side controllers, modals, table filters, & AJAX GA runner
├── templates/
│   ├── base.html              # Master layout template with sidebar navigation & alert system
│   ├── index.html             # Executive Dashboard with KPI cards & Chart.js graphs
│   ├── activities.html        # Academic Activity Management (Add, Edit, Filter, Delete, Toggle)
│   ├── resources.html         # Campus Resource Management (Classrooms, Labs, Halls, Equipment)
│   ├── optimize.html          # Genetic Algorithm Control Center with hyperparameter tuning
│   ├── results.html           # Optimization Telemetry, 4 Chart.js charts & Allocation Manifest
│   ├── history.html           # Historical Optimization Runs Ledger & Comparative Audit Trail
│   ├── reports.html           # Formal Printable Academic Project Report (@media print)
│   └── about.html             # Project details, mathematical formulation & team info
└── tests/
    ├── __init__.py            # Test package initialization
    ├── test_optimizer.py      # Automated unit tests for GA chromosome, fitness & operators
    └── test_database.py       # Automated unit tests for database transactions & integrity
```

---

## 🚀 Key Modules & System Features

### 1. 📊 Executive Dashboard

- **Real-time KPI Metrics**: Active academic sessions, available classrooms & laboratories, gross seating capacity, and total completed optimization runs.
- **Resource Distribution Analytics**: Interactive Chart.js doughnut charts categorizing physical capacities by facility type.
- **Academic Priority Breakdown**: Visual distribution of critical (P5), high (P4), medium (P3), medium-low (P2), and low (P1) priority sessions.
- **Recent Runs Ledger**: Quick-glance audit trail of recent GA executions with one-click result viewing.

### 2. 📚 Academic Activity Management

- Add, view, edit, toggle active/inactive status, and delete academic sessions (lectures, practical labs, capstone defenses, workshops).
- Attributes: Activity Name, Department, Student Cohort Size, Duration (hours), Required Resource Type, Priority Rating (1 to 5), Budget ($), Preferred Day, and Preferred Time Slot.
- Live client-side search and dual dropdown filtering by Department and Priority tier.
- Server-side and client-side constraint validation preventing duplicate names or invalid negative bounds.

### 3. 🏛️ Campus Resource Management

- Configure campus facilities: General Classrooms (seats), Computer & Hardware Laboratories, University Seminar Halls, and Specialized Equipment.
- Attributes: Facility Name, Category, Seating Capacity, Campus Location, Operational Availability (Available, Maintenance, Reserved), and Hourly Operating Cost.
- Real-time search and filtering by Category and Operational Availability.

### 4. 🧬 Genuine Genetic Algorithm Optimizer

- **Chromosome Representation**: Integer tuple vector $\mathbf{X} = [(R_1, T_1), (R_2, T_2), \dots, (R_N, T_N)]$ where each gene encodes the assigned facility ID and scheduled time slot.
- **Tournament Selection**: Configurable tournament size ($k$) selecting superior parents while maintaining genetic diversity.
- **Single-Point Crossover**: Recombines gene tails with probability $P_c \approx 0.85$.
- **Gene-Level Mutation**: Perturbs facility IDs and time slots with probability $P_m \approx 0.15$ to escape local optima.
- **Elitism**: Retains top $e=2$ fittest candidates unchanged across generations to guarantee non-decreasing convergence.
- **Deterministic Feasibility Repair**: Deterministically enforces capacity limits and eliminates time collisions by dynamically re-routing conflicting sessions to vacant compatible facilities.
- **Deterministic Reproducibility**: User-configurable random seed for identical result replication during academic defenses.

### 5. 📈 Results & Visual Analytics

- **Fitness Convergence Trajectory**: Chart.js interactive graph contrasting Best Solution Fitness vs. Population Mean across generations.
- **Resource Utilization Breakdown**: Comparative bar chart contrasting enrolled student cohort sizes against room capacities.
- **Allocation Status Doughnut**: Visual breakdown of Feasible Allocations, Hard Conflicts, and Unallocated sessions.
- **Before-and-After Optimization Comparison**: Bar chart showing performance improvements over unoptimized random configurations.
- **CSV Data Export**: One-click download of the complete RFC-4180 allocation manifest.

### 6. 📜 Optimization History & Audit Ledger

- Permanent persistence of every optimization run in SQLite.
- Complete audit parameters: population size, generations, mutation rate, crossover rate, best fitness, runtime, and seed.
- Historical run inspector: Reload and visualize previous allocations and convergence curves at any time.

### 7. 📋 Academic Printable Reports

- Standardized printable academic report with print stylesheet (`@media print`).
- Executive summary, hyperparameter audit, full allocation manifest, constraint checklist, and team sign-off.

---

## 🛠️ Local Installation & Setup Instructions

### Prerequisites

- Python 3.10, 3.11, 3.12, 3.13, or 3.14
- Web browser (Chrome, Edge, Firefox, or Safari)

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

*(Expected result: 13 passed tests verifying GA operators, capacity violations, collision detection, and database transactions).*

### Step 5: Launch the Application

```bash
python app.py
```

Open your browser and navigate to: **`http://127.0.0.1:5000`**

---

## 📸 Screenshots to Capture for Your Project Report

When preparing your submission report or slide deck, capture screenshots of:

1. **Dashboard Overview (`/dashboard`)**: Shows KPI cards, Resource Distribution Chart, and Priority Breakdown Bar Chart.
2. **Activity Management (`/activities`)**: Displays the live search filter and the "Add New Activity" modal.
3. **Resource Management (`/resources`)**: Highlights campus room capacities, locations, and operational availabilities.
4. **GA Control Center (`/optimize`)**: Demonstrates hyperparameter sliders (population, generations, mutation rate) and the live execution progress bar.
5. **Optimization Results (`/results/1`)**: Captures the Fitness Convergence Trajectory, Occupancy Bar Chart, and the Final Allocation Table.
6. **Printable Academic Report (`/reports/1`)**: Shows the formal submission-ready report formatted with `@media print`.

---

## 🧪 Automated Test Suite Validation

The automated test suite (`tests/test_optimizer.py` and `tests/test_database.py`) covers:

| Test Identifier | Target Module | Verification Scope | Result |
| :--- | :--- | :--- | :--- |
| **TC-01** | `optimizer.py` | Priority Fitness Scaling: High priority allocates receive strictly higher fitness | **PASS** |
| **TC-02** | `optimizer.py` | Capacity Constraint: Detects and penalizes room capacity deficits | **PASS** |
| **TC-03** | `optimizer.py` | Collision Detection: Enforces penalty on simultaneous double-booking | **PASS** |
| **TC-04** | `optimizer.py` | Facility Type Match: Penalizes laboratory requests placed in lecture halls | **PASS** |
| **TC-05** | `optimizer.py` | Feasibility Repair: Automatically re-routes collisions to unoccupied slots | **PASS** |
| **TC-06** | `optimizer.py` | Deterministic Seed: Identical random seeds produce 100% identical solutions | **PASS** |
| **TC-07** | `optimizer.py` | Empty Activity Handling: Gracefully handles empty session inputs | **PASS** |
| **TC-08** | `database.py` | Schema Initialization: Creates all 4 relational tables and seeds campus data | **PASS** |
| **TC-09** | `database.py` | Resource CRUD: Validates insertion, update, delete, and duplicate rejection | **PASS** |
| **TC-10** | `database.py` | Activity CRUD: Validates creation, status toggle (Active/Inactive), and updates | **PASS** |
| **TC-11** | `database.py` | Run Persistence: Verifies ACID transaction saving and query retrieval | **PASS** |
| **TC-12** | `database.py` | Cascading Deletes: Deleting an optimization run safely deletes its allocations | **PASS** |
| **TC-13** | `database.py` | Summary Statistics: Confirms calculations for dashboard metrics | **PASS** |

---

## 👥 Team EvoCampus & Project Information

- **Project**: Smart Campus Resource Optimizer
- **Team**: EvoCampus
- **Tagline**: *“Evolving Intelligence, Optimizing Tomorrow.”*
- **Domain**: Bio-Inspired AI / Optimization
- **License**: MIT Open Source License
