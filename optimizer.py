"""
Genetic Algorithm Optimizer for Smart Campus Resource Allocation.
Developed by Team EvoNex.
Provides a pure Python/NumPy implementation of an Evolutionary Algorithm designed
to optimize multi-resource campus capacity and budget allocation with priority weighting.
"""

import time
import random
from typing import List, Dict, Any, Tuple, Optional
import numpy as np


# Priority weights: exponential reward for critical academic activities
PRIORITY_WEIGHTS = {
    1: 1.0,   # Low priority (e.g. general elective club session)
    2: 2.0,   # Medium-Low (e.g. guest seminar)
    3: 4.0,   # Medium (e.g. regular tutorial/review)
    4: 7.0,   # High (e.g. core laboratory session)
    5: 11.0   # Critical (e.g. final examination, accredited lab, capstone)
}


class GeneticAlgorithmOptimizer:
    """
    Scratch-implemented Genetic Algorithm for campus resource scheduling & allocation.
    Solves a multi-dimensional knapsack-like constrained optimization problem.
    """

    def __init__(
        self,
        activities: List[Dict[str, Any]],
        resource_capacities: Dict[str, int],
        budget_limit: float,
        population_size: int = 60,
        generations: int = 50,
        crossover_rate: float = 0.85,
        mutation_rate: float = 0.10,
        tournament_size: int = 3,
        elitism_count: int = 2,
        random_seed: Optional[int] = None
    ):
        """
        Initializes the Genetic Algorithm parameters and problem space.
        """
        self.activities = [act for act in activities if act.get("is_active", 1) == 1]
        self.num_activities = len(self.activities)
        self.resource_capacities = dict(resource_capacities)
        self.budget_limit = float(budget_limit)

        self.population_size = max(10, int(population_size))
        self.generations = max(5, int(generations))
        self.crossover_rate = min(1.0, max(0.0, float(crossover_rate)))
        self.mutation_rate = min(1.0, max(0.0, float(mutation_rate)))
        self.tournament_size = max(2, min(self.population_size, int(tournament_size)))
        self.elitism_count = max(1, min(self.population_size // 2, int(elitism_count)))
        self.random_seed = random_seed

        if self.random_seed is not None:
            random.seed(self.random_seed)
            np.random.seed(self.random_seed)

        # Pre-extract vector bounds and attributes for high performance
        self.demands = [int(act["demand"]) for act in self.activities]
        self.priorities = [int(act["priority"]) for act in self.activities]
        self.costs = [float(act["cost_per_unit"]) for act in self.activities]
        self.resource_types = [str(act["resource_type"]) for act in self.activities]
        self.names = [str(act["name"]) for act in self.activities]

        # Total maximum possible priority sum for normalization
        self.total_priority_weight = sum(
            PRIORITY_WEIGHTS.get(p, 1.0) for p in self.priorities
        ) if self.num_activities > 0 else 1.0

    # -------------------------------------------------------------------------
    # Constraint Enforcement and Solution Repair
    # -------------------------------------------------------------------------

    def repair_chromosome(self, chromosome: List[int]) -> List[int]:
        """
        Enforces physical campus constraints on a candidate solution:
        1. Clamps allocation to [0, demand_i] for each activity.
        2. Enforces resource capacity limits per resource type (trims lowest priority first).
        3. Enforces total monetary budget limit (trims lowest priority / highest cost first).
        Guarantees that returned solutions are 100% feasible.
        """
        if self.num_activities == 0:
            return []

        # Step 1: Demand Bounds Clamping
        repaired = [
            max(0, min(self.demands[i], int(chromosome[i])))
            for i in range(self.num_activities)
        ]

        # Step 2: Resource Capacity Enforcement
        # Group activity indices by resource type
        res_to_indices: Dict[str, List[int]] = {}
        for idx, res_name in enumerate(self.resource_types):
            res_to_indices.setdefault(res_name, []).append(idx)

        for res_name, indices in res_to_indices.items():
            cap = self.resource_capacities.get(res_name, 0)
            current_total = sum(repaired[i] for i in indices)

            if current_total > cap:
                excess = current_total - cap
                # Sort indices by ascending priority, then descending cost (trim least critical first)
                sorted_indices = sorted(
                    indices,
                    key=lambda idx: (self.priorities[idx], -self.costs[idx])
                )
                for idx in sorted_indices:
                    if excess <= 0:
                        break
                    reduce_by = min(repaired[idx], excess)
                    repaired[idx] -= reduce_by
                    excess -= reduce_by

        # Step 3: Budget Constraint Enforcement
        current_cost = sum(repaired[i] * self.costs[i] for i in range(self.num_activities))
        if current_cost > self.budget_limit:
            # Sort non-zero allocations by ascending priority, then descending unit cost
            active_indices = [i for i in range(self.num_activities) if repaired[i] > 0]
            sorted_indices = sorted(
                active_indices,
                key=lambda idx: (self.priorities[idx], -self.costs[idx])
            )

            for idx in sorted_indices:
                if current_cost <= self.budget_limit:
                    break
                unit_cost = self.costs[idx]
                if unit_cost <= 0:
                    continue
                needed_reduction = current_cost - self.budget_limit
                units_to_cut = int(np.ceil(needed_reduction / unit_cost))
                actual_cut = min(repaired[idx], units_to_cut)
                repaired[idx] -= actual_cut
                current_cost -= actual_cut * unit_cost

        return repaired

    # -------------------------------------------------------------------------
    # Fitness Function
    # -------------------------------------------------------------------------

    def calculate_fitness(self, chromosome: List[int]) -> float:
        """
        Computes the fitness score of a candidate allocation.
        Objective:
        - Maximize priority-weighted demand fulfillment (0 - 100 points).
        - Secondary incentive: efficient resource capacity utilization (up to 10 points).
        - Penalty for any constraint violation (safety check, 0 with repair).
        """
        if self.num_activities == 0:
            return 0.0

        # Check raw constraints for penalties if un-repaired
        penalty = 0.0

        # Check resource capacities
        res_usage: Dict[str, int] = {}
        total_cost = 0.0
        for i in range(self.num_activities):
            alloc = chromosome[i]
            if alloc < 0 or alloc > self.demands[i]:
                penalty += 100.0 * abs(alloc - max(0, min(alloc, self.demands[i])))
            res_usage[self.resource_types[i]] = res_usage.get(self.resource_types[i], 0) + alloc
            total_cost += alloc * self.costs[i]

        for res, usage in res_usage.items():
            cap = self.resource_capacities.get(res, 0)
            if usage > cap:
                penalty += 200.0 * (usage - cap)

        if total_cost > self.budget_limit:
            penalty += 150.0 * ((total_cost - self.budget_limit) / max(1.0, self.budget_limit))

        # Priority-weighted satisfaction score (0 to 100)
        weighted_fulfillment_sum = 0.0
        for i in range(self.num_activities):
            demand = self.demands[i]
            alloc = chromosome[i]
            ratio = (alloc / demand) if demand > 0 else 0.0
            ratio = max(0.0, min(1.0, ratio))
            weight = PRIORITY_WEIGHTS.get(self.priorities[i], 1.0)
            weighted_fulfillment_sum += weight * ratio

        priority_score = (weighted_fulfillment_sum / self.total_priority_weight) * 100.0

        # Resource utilization bonus: Encourages active scheduling without exceeding caps
        total_capacity = sum(self.resource_capacities.values())
        total_allocated = sum(chromosome)
        utilization_ratio = (total_allocated / total_capacity) if total_capacity > 0 else 0.0
        utilization_bonus = min(1.0, max(0.0, utilization_ratio)) * 5.0

        fitness = priority_score + utilization_bonus - penalty
        return max(0.0, round(fitness, 4))

    # -------------------------------------------------------------------------
    # Initial Population
    # -------------------------------------------------------------------------

    def create_initial_population(self) -> List[List[int]]:
        """
        Creates a diverse initial population combining:
        1. Greedy priority heuristic (fill highest priority activities first).
        2. Proportional heuristic (scale demand to average resource capacity).
        3. Random candidates spanning sparse to dense allocations.
        All candidates are repaired to strictly guarantee feasibility.
        """
        population: List[List[int]] = []

        if self.num_activities == 0:
            return population

        # Heuristic 1: Greedy Priority Allocation
        greedy_cand = [0] * self.num_activities
        sorted_by_priority = sorted(
            range(self.num_activities),
            key=lambda i: (-self.priorities[i], self.costs[i])
        )
        for idx in sorted_by_priority:
            greedy_cand[idx] = self.demands[idx]
        population.append(self.repair_chromosome(greedy_cand))

        # Heuristic 2: Proportional Allocation (50% demand)
        prop_cand = [self.demands[i] // 2 for i in range(self.num_activities)]
        population.append(self.repair_chromosome(prop_cand))

        # Heuristic 3: 75% Allocation
        high_cand = [int(self.demands[i] * 0.75) for i in range(self.num_activities)]
        population.append(self.repair_chromosome(high_cand))

        # Heuristic 4: Zero Allocation (Safe fallback)
        zero_cand = [0] * self.num_activities
        population.append(self.repair_chromosome(zero_cand))

        # Fill remaining with randomized chromosomes
        while len(population) < self.population_size:
            random_cand = [
                random.randint(0, self.demands[i])
                for i in range(self.num_activities)
            ]
            population.append(self.repair_chromosome(random_cand))

        return population

    # -------------------------------------------------------------------------
    # Selection, Crossover, and Mutation Operators
    # -------------------------------------------------------------------------

    def tournament_selection(self, population: List[List[int]], fitnesses: List[float]) -> List[int]:
        """
        Tournament selection: Selects k random individuals and returns the best.
        """
        indices = random.sample(range(len(population)), self.tournament_size)
        best_idx = max(indices, key=lambda idx: fitnesses[idx])
        return list(population[best_idx])

    def crossover(self, parent1: List[int], parent2: List[int]) -> Tuple[List[int], List[int]]:
        """
        Single-point crossover with probability crossover_rate.
        """
        if self.num_activities < 2 or random.random() > self.crossover_rate:
            return list(parent1), list(parent2)

        point = random.randint(1, self.num_activities - 1)
        child1 = parent1[:point] + parent2[point:]
        child2 = parent2[:point] + parent1[point:]
        return child1, child2

    def mutate(self, chromosome: List[int]) -> List[int]:
        """
        Gene-wise mutation: with probability mutation_rate, adjust allocation
        either by random step delta or random uniform resampling.
        """
        mutated = list(chromosome)
        for i in range(self.num_activities):
            if random.random() < self.mutation_rate:
                demand = self.demands[i]
                if demand <= 0:
                    mutated[i] = 0
                    continue

                mode = random.choice(["delta", "resample"])
                if mode == "delta":
                    step = random.choice([-2, -1, 1, 2, 5, -5])
                    mutated[i] = max(0, min(demand, mutated[i] + step))
                else:
                    mutated[i] = random.randint(0, demand)

        return mutated

    # -------------------------------------------------------------------------
    # Optimization Execution Loop
    # -------------------------------------------------------------------------

    def optimize(self) -> Dict[str, Any]:
        """
        Executes the Genetic Algorithm loop:
        1. Initialize population.
        2. Evaluate fitness.
        3. For each generation:
           a. Preserve elites.
           b. Select parents via tournament selection.
           c. Apply crossover.
           d. Apply mutation.
           e. Repair offspring for constraint satisfaction.
           f. Track statistics (best, average, min fitness).
        4. Return comprehensive results and metrics.
        """
        start_time = time.time()

        if self.num_activities == 0:
            return self._build_empty_result(start_time)

        population = self.create_initial_population()
        convergence_history: List[Dict[str, Any]] = []

        best_solution: Optional[List[int]] = None
        best_fitness = -1.0

        for gen in range(self.generations):
            # Calculate fitness for all individuals
            fitnesses = [self.calculate_fitness(ind) for ind in population]

            current_best_idx = int(np.argmax(fitnesses))
            current_best_fit = float(fitnesses[current_best_idx])
            avg_fit = float(np.mean(fitnesses))
            min_fit = float(np.min(fitnesses))

            if current_best_fit > best_fitness:
                best_fitness = current_best_fit
                best_solution = list(population[current_best_idx])

            convergence_history.append({
                "generation": gen + 1,
                "best_fitness": round(current_best_fit, 3),
                "avg_fitness": round(avg_fit, 3),
                "min_fitness": round(min_fit, 3)
            })

            # Create next generation
            next_generation: List[List[int]] = []

            # Elitism: retain top k solutions directly
            sorted_indices = np.argsort(fitnesses)[::-1]
            for i in range(self.elitism_count):
                next_generation.append(list(population[sorted_indices[i]]))

            # Breed remaining individuals
            while len(next_generation) < self.population_size:
                p1 = self.tournament_selection(population, fitnesses)
                p2 = self.tournament_selection(population, fitnesses)

                c1, c2 = self.crossover(p1, p2)
                c1 = self.repair_chromosome(self.mutate(c1))
                c2 = self.repair_chromosome(self.mutate(c2))

                next_generation.append(c1)
                if len(next_generation) < self.population_size:
                    next_generation.append(c2)

            population = next_generation

        # Final evaluation on best solution found
        best_solution = self.repair_chromosome(best_solution or [0] * self.num_activities)
        final_best_fitness = self.calculate_fitness(best_solution)

        execution_time = time.time() - start_time
        return self._format_results(best_solution, final_best_fitness, convergence_history, execution_time)

    # -------------------------------------------------------------------------
    # Results Formatting & Aggregation
    # -------------------------------------------------------------------------

    def _format_results(
        self,
        chromosome: List[int],
        best_fitness: float,
        convergence_history: List[Dict[str, Any]],
        execution_time: float
    ) -> Dict[str, Any]:
        """Packages detailed metrics, table items, and KPI summaries."""
        allocations: List[Dict[str, Any]] = []
        total_demand = sum(self.demands)
        total_allocated = sum(chromosome)
        total_cost = 0.0

        # Per-resource utilization tracking
        resource_summary: Dict[str, Dict[str, Any]] = {}
        for res_name, cap in self.resource_capacities.items():
            resource_summary[res_name] = {
                "capacity": cap,
                "allocated": 0,
                "demand": 0,
                "utilization_pct": 0.0
            }

        for i in range(self.num_activities):
            alloc = chromosome[i]
            dem = self.demands[i]
            unmet = dem - alloc
            sat_pct = round((alloc / dem * 100.0) if dem > 0 else 0.0, 1)
            cost = alloc * self.costs[i]
            total_cost += cost

            res_type = self.resource_types[i]
            if res_type in resource_summary:
                resource_summary[res_type]["allocated"] += alloc
                resource_summary[res_type]["demand"] += dem

            allocations.append({
                "activity_id": self.activities[i].get("id"),
                "name": self.names[i],
                "resource_type": res_type,
                "priority": self.priorities[i],
                "demand": dem,
                "allocated": alloc,
                "unmet": unmet,
                "satisfaction_pct": sat_pct,
                "cost_per_unit": self.costs[i],
                "total_cost": round(cost, 2),
                "status": "Full" if unmet == 0 else ("Partial" if alloc > 0 else "Unmet")
            })

        for res_name, data in resource_summary.items():
            cap = data["capacity"]
            data["utilization_pct"] = round((data["allocated"] / cap * 100.0) if cap > 0 else 0.0, 1)

        total_cap_sum = sum(self.resource_capacities.values())
        overall_res_util_pct = round((total_allocated / total_cap_sum * 100.0) if total_cap_sum > 0 else 0.0, 1)
        demand_sat_pct = round((total_allocated / total_demand * 100.0) if total_demand > 0 else 0.0, 1)
        budget_util_pct = round((total_cost / self.budget_limit * 100.0) if self.budget_limit > 0 else 0.0, 1)

        return {
            "success": True,
            "best_chromosome": chromosome,
            "best_fitness": round(best_fitness, 3),
            "total_demand": total_demand,
            "total_allocated": total_allocated,
            "total_unmet": total_demand - total_allocated,
            "demand_satisfaction_pct": demand_sat_pct,
            "budget_limit": self.budget_limit,
            "budget_spent": round(total_cost, 2),
            "remaining_budget": round(max(0.0, self.budget_limit - total_cost), 2),
            "budget_utilization_pct": budget_util_pct,
            "overall_resource_utilization_pct": overall_res_util_pct,
            "resource_summary": resource_summary,
            "allocations": allocations,
            "convergence_history": convergence_history,
            "execution_time_sec": round(execution_time, 4),
            "algorithm_parameters": {
                "population_size": self.population_size,
                "generations": self.generations,
                "crossover_rate": self.crossover_rate,
                "mutation_rate": self.mutation_rate,
                "tournament_size": self.tournament_size,
                "elitism_count": self.elitism_count,
                "random_seed": self.random_seed
            }
        }

    def _build_empty_result(self, start_time: float) -> Dict[str, Any]:
        """Fallback result when no active activities exist."""
        return {
            "success": False,
            "message": "No active activities found for optimization.",
            "best_chromosome": [],
            "best_fitness": 0.0,
            "total_demand": 0,
            "total_allocated": 0,
            "total_unmet": 0,
            "demand_satisfaction_pct": 0.0,
            "budget_limit": self.budget_limit,
            "budget_spent": 0.0,
            "remaining_budget": self.budget_limit,
            "budget_utilization_pct": 0.0,
            "overall_resource_utilization_pct": 0.0,
            "resource_summary": {},
            "allocations": [],
            "convergence_history": [],
            "execution_time_sec": round(time.time() - start_time, 4),
            "algorithm_parameters": {}
        }
