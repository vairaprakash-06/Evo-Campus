# 📄 Smart Campus Resource Optimizer: Comprehensive Academic Project Report

**Project Title:** Smart Campus Resource Allocation and Capacity Optimization using Genetic Algorithms  
**Course:** Evolutionary Computing (EC) / Bio-Inspired Artificial Intelligence  
**Team Name:** EvoNex  
**Team Tagline:** *“Evolving Intelligence, Optimizing Tomorrow.”*  
**Date:** Academic Year 2026  

---

## 1. Abstract
Institutional resource management in modern universities involves distributing finite physical assets—such as general-purpose classrooms, high-performance computer laboratories, specialized experimental apparatus, and operational budgets—among competing academic departments, student cohorts, and research labs. This operational problem maps directly to the multi-dimensional, multi-choice knapsack problem (MMKP), proven to be NP-hard. 

Traditional heuristic or manual spreadsheet allocations frequently produce sub-optimal schedules characterized by severe resource bottlenecks, under-utilized physical facilities, and neglect of high-priority academic milestones (e.g., capstone defenses and accredited laboratory practicals). 

This project presents the **Smart Campus Resource Optimizer**, a full-stack decision-support system driven by a Genetic Algorithm (GA) implemented from scratch in Python. The algorithm employs an integer chromosome encoding, priority-weighted fitness modeling, tournament selection, single-point crossover, gene mutation, elitism, and a deterministic feasibility repair operator. Built on Streamlit, Plotly, and SQLite, the system provides real-time telemetry, visual Pareto convergence diagnostics, and verifiable constraint satisfaction. Empirical evaluation demonstrates that the proposed algorithm consistently satisfies critical academic demands while optimizing resource occupancy and operating within financial constraints.

---

## 2. Problem Statement
Campus administrators routinely encounter conflicting operational trade-offs:
1. **Severe Resource Scarcity**: Departmental demand for specialized computer laboratories and sensor kits regularly exceeds available inventory.
2. **Conflicting Priorities**: Accredited curriculum sessions and final examinations require near-100% resource fulfillment, whereas informal elective workshops can tolerate proportional compromises.
3. **Multi-Dimensional Constraint Coupling**: An allocation plan must simultaneously satisfy capacity bounds across disparate physical asset classes and adhere to strict department-level financial budgets.
4. **Intractability of Exhaustive Search**: For $N$ activities with integer allocations bounded by demand $D_i$, the discrete combinatorial search space expands to $\prod_{i=1}^N (D_i + 1)$. For a typical scenario of 10 activities with average demand of 40 units, the candidate state space exceeds $40^{10} \approx 10^{16}$ configurations, making brute-force enumeration computationally infeasible.

---

## 3. Objectives
The key objectives of this project are:
1. **Model the University Resource Allocation Problem (URAP)** as a multi-constrained combinatorial optimization model.
2. **Engineer a Pure Python Genetic Algorithm** from first principles, avoiding black-box closed solvers.
3. **Formulate a Priority-Weighted Objective Function** that balances demand fulfillment, prioritizes critical academic events, and rewards campus capacity utilization.
4. **Guarantee 100% Feasibility** across capacity and budgetary boundaries via an intelligent constraint repair operator.
5. **Develop an Interactive Telemetry Dashboard** featuring live Plotly convergence curves, comparative demand-versus-allocation charts, and SQLite audit logging.
6. **Validate the Solution** through automated unit tests verifying constraint adherence, genetic operators, and deterministic seed reproducibility.

---

## 4. Existing System vs. Proposed System

| Dimension | Existing System (Manual / Rule-Based) | Proposed System (**EvoNex Smart Campus Optimizer**) |
| :--- | :--- | :--- |
| **Methodology** | Ad-hoc spreadsheets, first-come-first-served (FCFS), or greedy heuristics. | Genetic Algorithm (GA) utilizing stochastic global search with elitism. |
| **Priority Handling** | Arbitrary or political; often neglects lower-tier requests or over-allocates early applicants. | Normalized exponential weighting ($w(p) \in [1, 11]$); mathematically optimizes global priority satisfaction. |
| **Constraint Adherence** | Prone to human error, double-booking, and post-allocation budgetary overruns. | Programmatically enforced via deterministic repair operators; mathematically impossible to violate bounds. |
| **Adaptability** | Labor-intensive rescheduling whenever capacities or departmental budgets shift. | Real-time re-optimization in under 500 milliseconds upon updating parameter sliders. |
| **Auditability & Visuals** | Static tabular sheets lacking convergence insights. | Interactive Plotly visual telemetry, convergence curves, and persistent SQLite historical ledger. |

---

## 5. Mathematical Formulation

### 5.1 System Entities and Sets
- Let $\mathcal{R} = \{R_1, R_2, \dots, R_M\}$ be the set of $M$ distinct campus resource categories (e.g., Classroom, Computer Lab, Equipment).
- Let each resource $R_j$ have an upper capacity limit:
  $$\text{Cap}(R_j) \in \mathbb{Z}^+, \quad \forall j \in \{1, \dots, M\}$$
- Let $\mathcal{A} = \{A_1, A_2, \dots, A_N\}$ represent $N$ active academic activities.
- Each activity $A_i$ is defined by the tuple:
  $$A_i = \langle \text{Name}_i, T_i, D_i, P_i, C_i \rangle$$
  where:
  - $T_i \in \mathcal{R}$: Assigned resource type
  - $D_i \in \mathbb{Z}^+$: Requested demand units
  - $P_i \in \{1, 2, 3, 4, 5\}$: Priority tier (1 = Low, 5 = Critical)
  - $C_i \in \mathbb{R}^+$: Operating cost per allocated unit
- Let $B \in \mathbb{R}^+$ represent the maximum institutional budget ceiling.

### 5.2 Decision Variable & Chromosome Encoding
The chromosome is encoded as an integer vector $\mathbf{X}$ of length $N$:
$$\mathbf{X} = [x_1, x_2, \dots, x_N]^\top \in \mathbb{Z}^N$$
where each gene $x_i$ denotes the integer number of resource units allocated to activity $A_i$.

### 5.3 Objective Function (Fitness Function)
The optimization goal is to maximize the composite fitness function $\mathcal{F}(\mathbf{X})$:

$$\max_{\mathbf{X}} \mathcal{F}(\mathbf{X}) = \mathcal{S}_{\text{priority}}(\mathbf{X}) + \beta \cdot \mathcal{U}_{\text{capacity}}(\mathbf{X}) - \mathcal{P}_{\text{violation}}(\mathbf{X})$$

Where:
1. **Priority-Weighted Satisfaction Score** ($\mathcal{S}_{\text{priority}} \in [0, 100]$):
   $$\mathcal{S}_{\text{priority}}(\mathbf{X}) = \frac{\sum_{i=1}^{N} w(P_i) \cdot \left( \frac{x_i}{D_i} \right)}{\sum_{i=1}^{N} w(P_i)} \times 100$$
   The weight mapping $w(P_i)$ penalizes neglect of critical academic requirements:
   $$w(1) = 1.0, \quad w(2) = 2.0, \quad w(3) = 4.0, \quad w(4) = 7.0, \quad w(5) = 11.0$$

2. **Capacity Utilization Bonus** ($\mathcal{U}_{\text{capacity}} \in [0, 5]$):
   $$\mathcal{U}_{\text{capacity}}(\mathbf{X}) = 5.0 \times \left( \frac{\sum_{i=1}^{N} x_i}{\sum_{j=1}^{M} \text{Cap}(R_j)} \right)$$

3. **Penalty Function** ($\mathcal{P}_{\text{violation}}$):
   Acts as a safeguard for un-repaired candidate chromosomes:
   $$\mathcal{P}_{\text{violation}}(\mathbf{X}) = 200 \sum_{j=1}^M \max\left(0, \sum_{i: T_i = R_j} x_i - \text{Cap}(R_j)\right) + 150 \max\left(0, \frac{\sum_{i=1}^N x_i C_i - B}{B}\right)$$

### 5.4 Hard Constraints
A candidate vector $\mathbf{X}$ is strictly feasible if and only if:
1. **Demand Boundedness**:
   $$0 \le x_i \le D_i, \quad \forall i \in \{1, \dots, N\}$$
2. **Physical Facility Capacity Limits**:
   $$\sum_{i : T_i = R_j} x_i \le \text{Cap}(R_j), \quad \forall R_j \in \mathcal{R}$$
3. **Monetary Budget Boundary**:
   $$\sum_{i=1}^{N} x_i \cdot C_i \le B$$

---

## 6. Genetic Algorithm Design & Operators

### 6.1 Feasibility Repair Operator
Rather than discarding infeasible individuals (death penalty), the EvoNex optimizer implements a deterministic repair operator $\mathcal{R}(\mathbf{X})$:
1. **Step 1: Bounds Clamping**: Clamps every gene $x_i \leftarrow \min(D_i, \max(0, x_i))$.
2. **Step 2: Capacity Repair**: For any resource $R_j$ where $\sum x_i > \text{Cap}(R_j)$, activities assigned to $R_j$ are sorted by ascending priority and descending cost. Allocations are iteratively trimmed from the lowest-priority activity until the capacity ceiling is respected.
3. **Step 3: Budget Repair**: If total cost exceeds $B$, non-zero activities are sorted by lowest priority and trimmed until $\sum x_i C_i \le B$.

### 6.2 Initial Population Seeding
The population of size $N_{\text{pop}}$ is initialized with a combination of domain-specific heuristics and stochastic exploration:
- **Individual 1 (Greedy Prioritized)**: Fills demand starting from Priority 5 down to Priority 1, repaired to budget/capacity.
- **Individual 2 (Proportional Scaled)**: Allocates $\lfloor 0.50 \cdot D_i \rfloor$ across all activities.
- **Individual 3 (High-Occupancy)**: Allocates $\lfloor 0.75 \cdot D_i \rfloor$.
- **Individual 4 (Conservative Base)**: Zero allocation baseline.
- **Individuals $5 \dots N_{\text{pop}}$ (Uniform Random)**: Each gene randomized $x_i \sim \mathcal{U}\{0, D_i\}$ and repaired.

### 6.3 Genetic Operators
1. **Selection (Tournament Selection)**: Samples $k=3$ random chromosomes from the population and selects the individual with highest fitness.
2. **Crossover (Single-Point Crossover)**: Given parents $\mathbf{P}_1, \mathbf{P}_2$ and crossover probability $P_c \approx 0.85$, a crossover point $c \in \{1, \dots, N-1\}$ is chosen uniformly at random:
   $$\mathbf{C}_1 = [p_{1,1}, \dots, p_{1,c}, p_{2,c+1}, \dots, p_{2,N}], \quad \mathbf{C}_2 = [p_{2,1}, \dots, p_{2,c}, p_{1,c+1}, \dots, p_{1,N}]$$
3. **Mutation (Gene-Wise Stochastic Mutation)**: Each gene is mutated with probability $P_m \approx 0.10$. Mutated genes undergo either a bounded random walk step ($\pm 1, \pm 2, \pm 5$) or uniform resampling within $[0, D_i]$.
4. **Elitism**: The top $e=2$ fittest chromosomes from generation $g$ bypass crossover and mutation, copied directly into generation $g+1$.

---

## 7. Algorithm Pseudocode

```text
Algorithm: EvoNex Genetic Algorithm for Campus Resource Allocation
Input:
  Activities A = {A_1, ..., A_N}
  Resource Capacities Cap = {R_1: C_1, ..., R_M: C_M}
  Budget B
  Parameters: PopSize (N_pop), Generations (G), Pc, Pm, TournamentSize (k), Elites (e)
Output:
  Optimal Allocation Vector X* and Convergence Metrics

1.  Initialize Population P <- []
2.  Seed Heuristic Individuals (Greedy, Proportional, Conservative) into P
3.  While |P| < N_pop do:
4.      Generate random vector X where X_i ~ Uniform(0, D_i)
5.      P.append(Repair_Chromosome(X, Cap, B))
6.  End While
7.  BestChrom <- null, BestFitness <- -infinity, History <- []
8.  For gen = 1 to G do:
9.      For each chromosome X in P:
10.         Fitness[X] <- Calculate_Fitness(X, Cap, B)
11.     End For
12.     CurrBest <- argmax(Fitness)
13.     If Fitness[CurrBest] > BestFitness then:
14.         BestFitness <- Fitness[CurrBest]
15.         BestChrom <- Copy(CurrBest)
16.     End If
17.     History.append({gen, BestFitness, Mean(Fitness), Min(Fitness)})
18.     P_next <- []
19.     // Elitism
20.     SortedP <- Sort P by Fitness descending
21.     P_next.append(SortedP[1 ... e])
22.     // Reproduction Loop
23.     While |P_next| < N_pop do:
24.         Parent1 <- Tournament_Select(P, Fitness, k)
25.         Parent2 <- Tournament_Select(P, Fitness, k)
26.         If Random(0, 1) < Pc then:
27.             Child1, Child2 <- Single_Point_Crossover(Parent1, Parent2)
28.         Else:
29.             Child1, Child2 <- Copy(Parent1), Copy(Parent2)
30.         End If
31.         Child1 <- Mutate(Child1, Pm)
32.         Child2 <- Mutate(Child2, Pm)
33.         P_next.append(Repair_Chromosome(Child1, Cap, B))
34.         If |P_next| < N_pop then:
35.             P_next.append(Repair_Chromosome(Child2, Cap, B))
36.         End If
37.     End While
38.     P <- P_next
39. End For
40. FinalChrom <- Repair_Chromosome(BestChrom, Cap, B)
41. Return Generate_Results_Manifest(FinalChrom, History)
```

---

## 8. System Architecture

```mermaid
graph TB
    subgraph UI_Layer ["Presentation & Telemetry Layer (Streamlit & Plotly)"]
        UI_Dash["Module 1: Dashboard KPI Cards"]
        UI_Act["Module 2: Activity Management"]
        UI_Res["Module 3: Resource Management"]
        UI_Opt["Module 4: GA Control Center"]
        UI_Resul["Module 5: Results & Analytics Charts"]
        UI_Hist["Module 6: Optimization History Ledger"]
    end

    subgraph Core_Optimizer ["Evolutionary Engine (optimizer.py)"]
        GA_Init["Initial Population Generator"]
        GA_Fit["Fitness Evaluator"]
        GA_Tourn["Tournament Selector"]
        GA_Cross["Single-Point Recombinator"]
        GA_Mut["Gene Mutation Operator"]
        GA_Elite["Elitism Preserver"]
        GA_Repair["Feasibility Repair Engine"]
    end

    subgraph Data_Storage ["Persistence Layer (SQLite & database.py)"]
        DB_Res[("resources table")]
        DB_Act[("activities table")]
        DB_Runs[("optimization_runs table")]
        DB_Alloc[("run_allocations table")]
    end

    UI_Act -->|CRUD Operations| DB_Act
    UI_Res -->|Capacity Updates| DB_Res
    UI_Opt -->|Trigger GA Run| Core_Optimizer
    Core_Optimizer -->|Fetch Active Problem Space| DB_Act
    Core_Optimizer -->|Fetch Available Capacities| DB_Res
    Core_Optimizer -->|Enforce Boundaries| GA_Repair
    Core_Optimizer -->|Persist Run & Convergence| DB_Runs
    Core_Optimizer -->|Persist Detailed Allocations| DB_Alloc
    DB_Runs -->|Audit Visualization| UI_Hist
    DB_Alloc -->|Manifest Export| UI_Resul
```

---

## 9. Requirements Specifications

### 9.1 Functional Requirements
- **FR-1**: System shall maintain persistent storage for resources and academic activities in an ACID-compliant SQLite database.
- **FR-2**: System shall prevent duplicate activity or resource names.
- **FR-3**: System shall prevent deletion of any resource linked to existing academic activities.
- **FR-4**: System shall allow administrators to enable or disable activities without permanently deleting them.
- **FR-5**: GA engine shall enforce that no allocation exceeds requested demand ($0 \le x_i \le D_i$).
- **FR-6**: GA engine shall enforce that the sum of allocated units for any resource type does not exceed total facility capacity.
- **FR-7**: GA engine shall enforce that total financial spending does not exceed the user-defined budget.
- **FR-8**: GA engine shall support fixed random seeds for deterministic repeatability.
- **FR-9**: System shall render interactive Plotly convergence plots and export results as RFC-4180 CSV files.

### 9.2 Non-Functional Requirements
- **NFR-1 (Performance)**: GA convergence for up to 50 activities and 200 generations must complete within 2.0 seconds on standard consumer CPUs.
- **NFR-2 (Reliability)**: The system must handle zero active activities or unfeasible budgets gracefully without throwing uncaught exceptions.
- **NFR-3 (Usability)**: Responsive navigation layout with dark navy theme and modern typography.
- **NFR-4 (Portability)**: Cross-platform compatibility across Windows, macOS, and Linux without requiring proprietary binaries.

---

## 10. Automated Testing & Verification Suite

The repository contains an automated test suite executed via `pytest` and Python standard `unittest`:

| Test ID | Target Component | Verification Scenario | Expected Outcome | Actual Result |
| :--- | :--- | :--- | :--- | :--- |
| **TC-01** | `optimizer.py` | Priority Fitness Scaling | Priority 5 allocation yields strictly higher fitness than Priority 3. | **PASS** |
| **TC-02** | `optimizer.py` | Demand Limit Clamping | Extreme negative or excessive inputs are clamped within $[0, D_i]$. | **PASS** |
| **TC-03** | `optimizer.py` | Tight Capacity Enforcement | Allocations with artificially constrained capacity ($Cap \ll \sum D$) strictly do not exceed $Cap$. | **PASS** |
| **TC-04** | `optimizer.py` | Budget Constraint Trimming | Allocations with tight budget limit ($B = \$500$) strictly satisfy $\sum x_i C_i \le B$. | **PASS** |
| **TC-05** | `optimizer.py` | Crossover & Mutation | Recombination produces valid child vectors; mutation modifies gene within bounds. | **PASS** |
| **TC-06** | `optimizer.py` | Seed Reproducibility | Two optimization runs with identical seed (`seed=777`) return identical chromosomes and fitness. | **PASS** |
| **TC-07** | `optimizer.py` | Inactive Activity Isolation | Disabled activities are excluded from allocation with 0 demand assigned. | **PASS** |
| **TC-08** | `database.py` | Schema Auto-Seeding | Fresh database initializes `Classroom`, `Computer Lab`, `Equipment`, and sample sessions. | **PASS** |
| **TC-09** | `database.py` | Duplicate Name Rejection | Inserting existing activity name raises handled `IntegrityError`. | **PASS** |
| **TC-10** | `database.py` | Status Toggling | Toggling active status successfully updates SQLite record ($1 \to 0 \to 1$). | **PASS** |
| **TC-11** | `database.py` | Foreign Key Integrity | Deletion of `Classroom` while activities depend on it is rejected. | **PASS** |
| **TC-12** | `database.py` | Run Ledger Persistence | Optimization run metadata and per-activity records are stored and queryable by Run ID. | **PASS** |

---

## 11. Advantages and Limitations

### Advantages
1. **Global Search Capability**: Overcomes the myopic traps of traditional greedy FCFS heuristics by exploring combinations across the multi-resource landscape.
2. **Deterministic Feasibility**: Guaranteeing 100% feasibility via intelligent repair prevents unexecutable allocation plans.
3. **Priority Sensitivity**: High-priority degree requirements and exams receive protected allocation even under severe resource contraction.
4. **Complete Transparency**: Unlike black-box neural networks, every step of the genetic algorithm (fitness formula, weights, mutation rates) is transparent and auditable.

### Limitations
1. **Discrete Integer Granularity**: Current model optimizes discrete quantities per session rather than dynamic continuous-time interval scheduling (e.g. 9:00 AM - 11:00 AM slotting).
2. **Static Capacity Bounds**: Assumes fixed capacity limits throughout the run without time-varying availability or maintenance schedules.

---

## 12. Future Enhancements
1. **Multi-Objective Pareto Optimization (NSGA-II)**: Transition to Non-dominated Sorting Genetic Algorithm II to simultaneously optimize three distinct objectives: fitness, budget minimization, and carbon footprint.
2. **Spatio-Temporal Time-Slot Scheduling**: Extend chromosome encoding to matrix form $\mathbf{X} \in \mathbb{Z}^{N \times T}$ to schedule both room allocation and time-slot timetabling.
3. **Cloud Database Integration**: Provide direct connectors to PostgreSQL/Supabase for persistent multi-tenant deployments on Streamlit Community Cloud.

---

## 13. Conclusion
The **Smart Campus Resource Optimizer** successfully demonstrates how Evolutionary Computing and Genetic Algorithms solve complex, constrained institutional resource scheduling problems. By synthesizing priority-weighted fitness evaluation, tournament selection, single-point crossover, gene mutation, elitism, and strict feasibility repair, the system reliably converges on optimal allocations in sub-second execution times. 

Developed by **Team EvoNex**, the platform fulfills all technical and academic requirements of the college Evolutionary Computing project, providing a modular, fully tested, and professionally documented open-source solution.

---

## 14. References
1. **Goldberg, D. E.** (1989). *Genetic Algorithms in Search, Optimization, and Machine Learning*. Addison-Wesley.
2. **Deb, K., Pratap, A., Agarwal, S., & Meyarivan, T.** (2002). A fast and elitist multiobjective genetic algorithm: NSGA-II. *IEEE Transactions on Evolutionary Computation*, 6(2), 182-197.
3. **Eiben, A. E., & Smith, J. E.** (2015). *Introduction to Evolutionary Computing* (2nd ed.). Natural Computing Series, Springer.
4. **Michalewicz, Z.** (1996). *Genetic Algorithms + Data Structures = Evolution Programs*. Springer Science & Business Media.
5. **Burke, E. K., Kingston, J. H., & de Werra, D.** (2004). Applications to school timetabling. In *Handbook of Graph Theory* (pp. 445-474). CRC Press.
6. **Holland, J. H.** (1992). *Adaptation in Natural and Artificial Systems: An Introductory Analysis with Applications to Biology, Control, and Artificial Intelligence*. MIT Press.
