"""
Genetic Algorithm Optimizer for Smart Campus Resource Allocation.
Developed by Team EvoCampus.
Tagline: "Evolving Intelligence, Optimizing Tomorrow."

A genuine, pure-Python Evolutionary Algorithm that solves the multi-constrained
campus resource scheduling problem (classrooms, labs, seminar halls, equipment, and time slots).
"""

import time
import random
from typing import List, Dict, Any, Tuple, Optional
import numpy as np

# Priority weighting map: exponential scaling for critical academic events
PRIORITY_WEIGHTS = {
    1: 1.0,   # Low priority (e.g. elective club meet)
    2: 2.0,   # Medium-Low (e.g. review session)
    3: 4.0,   # Medium (e.g. general tutorial)
    4: 7.0,   # High (e.g. core laboratory / major lecture)
    5: 11.0   # Critical (e.g. capstone defense / final examination)
}

# Standard university academic time slot pool
DEFAULT_TIME_SLOTS = [
    "Monday 09:00 - 11:00",
    "Monday 11:00 - 13:00",
    "Monday 14:00 - 16:00",
    "Tuesday 09:00 - 11:00",
    "Tuesday 11:00 - 13:00",
    "Tuesday 14:00 - 16:00",
    "Wednesday 09:00 - 11:00",
    "Wednesday 11:00 - 13:00",
    "Wednesday 14:00 - 16:00",
    "Thursday 09:00 - 11:00",
    "Thursday 11:00 - 13:00",
    "Thursday 14:00 - 16:00",
    "Friday 09:00 - 11:00",
    "Friday 11:00 - 13:00",
    "Friday 15:00 - 17:00"
]


class GeneticAlgorithmOptimizer:
    """
    Genuine Genetic Algorithm for university multi-resource and time-slot scheduling.
    Solves constraints across capacity, facility type matching, time collisions, and budgets.
    """

    def __init__(
        self,
        activities: List[Dict[str, Any]],
        resources: List[Dict[str, Any]],
        population_size: int = 50,
        generations: int = 40,
        mutation_rate: float = 0.15,
        crossover_rate: float = 0.85,
        elitism_count: int = 2,
        tournament_size: int = 3,
        random_seed: Optional[int] = None,
        time_slots: Optional[List[str]] = None
    ):
        # Filter for active activities
        self.activities = [act for act in activities if act.get("is_active", 1) == 1]
        self.num_activities = len(self.activities)
        self.resources = list(resources)
        self.num_resources = len(self.resources)
        self.time_slots = time_slots if time_slots else DEFAULT_TIME_SLOTS

        # Hyperparameters
        self.population_size = max(10, int(population_size))
        self.generations = max(5, int(generations))
        self.mutation_rate = min(1.0, max(0.0, float(mutation_rate)))
        self.crossover_rate = min(1.0, max(0.0, float(crossover_rate)))
        self.elitism_count = max(1, min(self.population_size // 2, int(elitism_count)))
        self.tournament_size = max(2, min(self.population_size, int(tournament_size)))
        self.random_seed = random_seed

        if self.random_seed is not None:
            random.seed(self.random_seed)
            np.random.seed(self.random_seed)

        # Lookup maps for rapid gene evaluation
        self.resource_by_id = {r["id"]: r for r in self.resources}
        self.compatible_resources_by_type = {}
        for r in self.resources:
            rtype = r.get("resource_type", "")
            if rtype not in self.compatible_resources_by_type:
                self.compatible_resources_by_type[rtype] = []
            self.compatible_resources_by_type[rtype].append(r["id"])

    def _get_preferred_slot(self, activity: Dict[str, Any]) -> str:
        """Constructs preferred day + slot string or falls back to first standard slot."""
        day = activity.get("preferred_day", "Monday")
        slot = activity.get("preferred_time_slot", "09:00 - 11:00")
        combined = f"{day} {slot}"
        for s in self.time_slots:
            if day.lower() in s.lower() and slot.split("-")[0].strip() in s:
                return s
        return combined if combined in self.time_slots else self.time_slots[0]

    def _create_heuristic_individual(self) -> List[Tuple[int, str]]:
        """
        Creates a heuristic seed individual by sorting activities by priority
        and greedily assigning best-fit compatible resources without time collisions.
        """
        chromosome = [(0, self.time_slots[0])] * self.num_activities
        sorted_indices = sorted(
            range(self.num_activities),
            key=lambda i: (self.activities[i].get("priority", 1), self.activities[i].get("num_students", 0)),
            reverse=True
        )

        occupied_schedule = set()  # set of (resource_id, time_slot)

        for idx in sorted_indices:
            act = self.activities[idx]
            req_type = act.get("required_resource_type", "")
            students = act.get("num_students", 0)
            preferred_slot = self._get_preferred_slot(act)

            # Find matching resources with sufficient capacity
            compatible_ids = self.compatible_resources_by_type.get(req_type, [])
            valid_candidates = [
                self.resource_by_id[rid] for rid in compatible_ids
                if self.resource_by_id[rid].get("capacity", 0) >= students
                and self.resource_by_id[rid].get("availability", "Available") == "Available"
            ]

            # Sort by tightest capacity fit (minimizing wasted seats)
            valid_candidates.sort(key=lambda r: r.get("capacity", 0) - students)

            assigned = False
            # Try preferred slot first
            for res in valid_candidates:
                key = (res["id"], preferred_slot)
                if key not in occupied_schedule:
                    chromosome[idx] = (res["id"], preferred_slot)
                    occupied_schedule.add(key)
                    assigned = True
                    break

            # Try other slots if preferred slot was taken
            if not assigned:
                for slot in self.time_slots:
                    for res in valid_candidates:
                        key = (res["id"], slot)
                        if key not in occupied_schedule:
                            chromosome[idx] = (res["id"], slot)
                            occupied_schedule.add(key)
                            assigned = True
                            break
                    if assigned:
                        break

            # Fallback if overconstrained
            if not assigned and self.resources:
                fallback_res = valid_candidates[0] if valid_candidates else random.choice(self.resources)
                chromosome[idx] = (fallback_res["id"], preferred_slot)

        return chromosome

    def _create_random_individual(self) -> List[Tuple[int, str]]:
        """Generates a stochastic chromosome with semi-biased matching to valid types."""
        chromosome = []
        for act in self.activities:
            req_type = act.get("required_resource_type", "")
            compatible_ids = self.compatible_resources_by_type.get(req_type, [])

            # 75% chance to pick compatible resource type, 25% random exploration
            if compatible_ids and random.random() < 0.75:
                rid = random.choice(compatible_ids)
            elif self.resources:
                rid = random.choice(self.resources)["id"]
            else:
                rid = 0

            # 50% chance to pick preferred time slot, 50% random slot
            if random.random() < 0.50:
                slot = self._get_preferred_slot(act)
            else:
                slot = random.choice(self.time_slots)

            chromosome.append((rid, slot))
        return chromosome

    def _initialize_population(self) -> List[List[Tuple[int, str]]]:
        """Initializes population using heuristic seeds and stochastic exploration."""
        population = []
        if self.num_activities == 0 or self.num_resources == 0:
            return population

        # Seed 1 & 2: Heuristic greedy individuals
        population.append(self._create_heuristic_individual())
        if self.population_size > 1:
            population.append(self._create_heuristic_individual())

        # Seed remaining individuals stochastically
        while len(population) < self.population_size:
            population.append(self._create_random_individual())

        return population

    def evaluate_chromosome(self, chromosome: List[Tuple[int, str]]) -> Tuple[float, Dict[str, Any]]:
        """
        Calculates fitness and constraint statistics for a candidate chromosome.
        Hard constraints strictly penalize violations.
        Soft constraints reward priority satisfaction, utilization, and budget control.
        """
        if not chromosome or self.num_activities == 0:
            return 0.0, {
                "hard_violations": 0,
                "soft_violations": 0,
                "allocated_count": 0,
                "total_cost": 0.0,
                "utilization_pct": 0.0,
                "violation_details": []
            }

        hard_penalty = 0.0
        soft_score = 0.0
        hard_violations = 0
        soft_violations = 0
        allocated_count = 0
        total_cost = 0.0
        utilized_capacity = 0
        total_assigned_capacity = 0
        violation_details = []

        # Schedule occupancy map: (resource_id, time_slot) -> list of activity indices
        occupied_schedule: Dict[Tuple[int, str], List[int]] = {}

        for i, (rid, slot) in enumerate(chromosome):
            act = self.activities[i]
            res = self.resource_by_id.get(rid)

            if not res:
                hard_penalty += 800.0
                hard_violations += 1
                violation_details.append(f"Activity '{act['name']}': assigned to non-existent resource ID {rid}.")
                continue

            # Hard Constraint 1: Resource Type Compatibility
            req_type = act.get("required_resource_type", "")
            actual_type = res.get("resource_type", "")
            if actual_type != req_type:
                hard_penalty += 500.0
                hard_violations += 1
                violation_details.append(f"Type Mismatch: '{act['name']}' requires '{req_type}' but assigned to '{actual_type}' ({res['name']}).")

            # Hard Constraint 2: Resource Availability
            avail = res.get("availability", "Available")
            if avail != "Available":
                hard_penalty += 400.0
                hard_violations += 1
                violation_details.append(f"Availability Issue: '{res['name']}' is '{avail}' (not Available).")

            # Hard Constraint 3: Capacity Sufficiency
            cap = res.get("capacity", 0)
            students = act.get("num_students", 0)
            if cap < students:
                deficit = students - cap
                hard_penalty += 350.0 + (deficit * 10.0)
                hard_violations += 1
                violation_details.append(f"Capacity Exceeded: '{act['name']}' has {students} students but '{res['name']}' capacity is {cap}.")
            else:
                utilized_capacity += students
                total_assigned_capacity += cap

            # Track time collisions
            schedule_key = (rid, slot)
            if schedule_key not in occupied_schedule:
                occupied_schedule[schedule_key] = []
            occupied_schedule[schedule_key].append(i)

            # Soft Objective 1: Priority-Weighted Satisfaction
            priority = act.get("priority", 1)
            weight = PRIORITY_WEIGHTS.get(priority, 1.0)
            soft_score += weight * 40.0

            # Soft Objective 2: Capacity Utilization Efficiency (Reward snug fit, penalize huge empty space)
            if cap >= students and cap > 0:
                fit_ratio = students / cap
                soft_score += fit_ratio * 25.0

            # Soft Objective 3: Preferred Time Slot Bonus
            preferred_slot = self._get_preferred_slot(act)
            if slot == preferred_slot:
                soft_score += 15.0

            # Operating cost calculation
            duration = act.get("duration_hours", 1.0)
            unit_cost = res.get("operating_cost", 0.0)
            act_cost = duration * unit_cost
            total_cost += act_cost

            # Soft Objective 4: Activity Budget Compliance
            budget = act.get("budget", 0.0)
            if budget > 0:
                if act_cost <= budget:
                    soft_score += 10.0
                else:
                    overage = act_cost - budget
                    soft_score -= (overage * 0.5)
                    soft_violations += 1
                    violation_details.append(f"Budget Exceeded: '{act['name']}' cost ${act_cost:.2f} exceeds budget ${budget:.2f}.")

        # Hard Constraint 4: Collision / Double-Booking Enforcement
        for (rid, slot), acts in occupied_schedule.items():
            if len(acts) > 1:
                res_name = self.resource_by_id.get(rid, {}).get("name", f"Resource #{rid}")
                collision_count = len(acts) - 1
                hard_penalty += 450.0 * collision_count
                hard_violations += collision_count
                colliding_names = [self.activities[idx]["name"] for idx in acts]
                violation_details.append(f"Scheduling Collision: {len(acts)} activities ({', '.join(colliding_names)}) double-booked in '{res_name}' at '{slot}'.")

        # Total overall fitness
        # Base constant of 1000 so positive numbers are maintained when feasible
        fitness = 1000.0 + soft_score - hard_penalty

        # Utilization calculation
        utilization_pct = 0.0
        if total_assigned_capacity > 0:
            utilization_pct = min(100.0, round((utilized_capacity / total_assigned_capacity) * 100.0, 1))

        # Successfully allocated count (activities without hard constraint violations)
        allocated_count = max(0, self.num_activities - hard_violations)

        stats = {
            "hard_violations": hard_violations,
            "soft_violations": soft_violations,
            "allocated_count": allocated_count,
            "total_cost": round(total_cost, 2),
            "utilization_pct": utilization_pct,
            "violation_details": violation_details
        }
        return fitness, stats

    def _repair_chromosome(self, chromosome: List[Tuple[int, str]]) -> List[Tuple[int, str]]:
        """
        Feasibility repair operator:
        Detects collisions and invalid capacities, attempting to shift activities
        to unoccupied, compatible resources and alternative time slots.
        """
        repaired = list(chromosome)
        occupied = set()

        # Sort activities by priority descending to protect high priority assignments
        sorted_indices = sorted(
            range(self.num_activities),
            key=lambda i: self.activities[i].get("priority", 1),
            reverse=True
        )

        for idx in sorted_indices:
            rid, slot = repaired[idx]
            act = self.activities[idx]
            res = self.resource_by_id.get(rid)
            req_type = act.get("required_resource_type", "")
            students = act.get("num_students", 0)

            is_valid = (
                res is not None
                and res.get("resource_type") == req_type
                and res.get("capacity", 0) >= students
                and res.get("availability") == "Available"
                and (rid, slot) not in occupied
            )

            if is_valid:
                occupied.add((rid, slot))
                continue

            # Need repair: Search for an unoccupied compatible alternative
            compatible_ids = self.compatible_resources_by_type.get(req_type, [])
            valid_resources = [
                self.resource_by_id[r_id] for r_id in compatible_ids
                if self.resource_by_id[r_id].get("capacity", 0) >= students
                and self.resource_by_id[r_id].get("availability", "Available") == "Available"
            ]
            valid_resources.sort(key=lambda r: r.get("capacity", 0) - students)

            found = False
            # Check preferred slot first
            preferred_slot = self._get_preferred_slot(act)
            for cand in valid_resources:
                if (cand["id"], preferred_slot) not in occupied:
                    repaired[idx] = (cand["id"], preferred_slot)
                    occupied.add((cand["id"], preferred_slot))
                    found = True
                    break

            if not found:
                # Check all other slots
                for test_slot in self.time_slots:
                    for cand in valid_resources:
                        if (cand["id"], test_slot) not in occupied:
                            repaired[idx] = (cand["id"], test_slot)
                            occupied.add((cand["id"], test_slot))
                            found = True
                            break
                    if found:
                        break

            if not found:
                # Keep original and let fitness penalize
                occupied.add((rid, slot))

        return repaired

    def _tournament_selection(self, population: List[List[Tuple[int, str]]], fitnesses: List[float]) -> List[Tuple[int, str]]:
        """Samples k random candidates and selects the fittest individual."""
        selected_indices = random.sample(range(len(population)), self.tournament_size)
        best_idx = max(selected_indices, key=lambda idx: fitnesses[idx])
        return list(population[best_idx])

    def _crossover(
        self,
        parent1: List[Tuple[int, str]],
        parent2: List[Tuple[int, str]]
    ) -> Tuple[List[Tuple[int, str]], List[Tuple[int, str]]]:
        """Single-point crossover combining chromosome sub-vectors."""
        if random.random() > self.crossover_rate or self.num_activities < 2:
            return list(parent1), list(parent2)

        point = random.randint(1, self.num_activities - 1)
        child1 = parent1[:point] + parent2[point:]
        child2 = parent2[:point] + parent1[point:]
        return child1, child2

    def _mutate(self, chromosome: List[Tuple[int, str]]) -> List[Tuple[int, str]]:
        """Gene mutation: randomly reassigns resource or time slot with mutation probability."""
        mutated = list(chromosome)
        for i in range(self.num_activities):
            if random.random() < self.mutation_rate:
                act = self.activities[i]
                req_type = act.get("required_resource_type", "")
                compatible_ids = self.compatible_resources_by_type.get(req_type, [])

                # Mutate resource
                if compatible_ids and random.random() < 0.70:
                    new_rid = random.choice(compatible_ids)
                elif self.resources:
                    new_rid = random.choice(self.resources)["id"]
                else:
                    new_rid = mutated[i][0]

                # Mutate time slot
                new_slot = random.choice(self.time_slots)
                mutated[i] = (new_rid, new_slot)
        return mutated

    def run(self) -> Dict[str, Any]:
        """
        Executes the Genetic Algorithm across all generations.
        Returns the optimal chromosome, convergence telemetry, and full allocation manifest.
        """
        start_time = time.time()

        if self.num_activities == 0 or self.num_resources == 0:
            return {
                "best_fitness": 0.0,
                "allocations": [],
                "total_activities": 0,
                "allocated_activities": 0,
                "unallocated_activities": 0,
                "resource_utilization_pct": 0.0,
                "total_cost": 0.0,
                "hard_violations": 0,
                "soft_violations": 0,
                "execution_time_sec": round(time.time() - start_time, 3),
                "convergence_history": [],
                "status": "No Active Activities",
                "notes": "No active activities or resources available for scheduling."
            }

        # Step 1: Initialize Population
        population = self._initialize_population()
        for i in range(len(population)):
            population[i] = self._repair_chromosome(population[i])

        best_chromosome = None
        best_fitness = -float("inf")
        best_stats = {}
        convergence_history = []

        # Step 2: Generation Loop
        for gen in range(1, self.generations + 1):
            # Evaluate all individuals
            eval_results = [self.evaluate_chromosome(ind) for ind in population]
            fitnesses = [res[0] for res in eval_results]

            # Track generation best
            current_max_idx = int(np.argmax(fitnesses))
            current_best_fit = fitnesses[current_max_idx]

            if current_best_fit > best_fitness:
                best_fitness = current_best_fit
                best_chromosome = list(population[current_max_idx])
                best_stats = eval_results[current_max_idx][1]

            mean_fit = float(np.mean(fitnesses))
            min_fit = float(np.min(fitnesses))

            convergence_history.append({
                "generation": gen,
                "best_fitness": round(best_fitness, 2),
                "avg_fitness": round(mean_fit, 2),
                "min_fitness": round(min_fit, 2),
                "hard_violations": best_stats.get("hard_violations", 0)
            })

            # Check early termination if perfect optimal fitness reached
            if best_stats.get("hard_violations", 0) == 0 and best_stats.get("soft_violations", 0) == 0:
                # Continue small elitism step or finish
                pass

            # Step 3: Elitism - retain top k individuals
            sorted_indices = np.argsort(fitnesses)[::-1]
            next_population = [list(population[idx]) for idx in sorted_indices[:self.elitism_count]]

            # Step 4: Reproduction (Selection, Crossover, Mutation, Repair)
            while len(next_population) < self.population_size:
                parent1 = self._tournament_selection(population, fitnesses)
                parent2 = self._tournament_selection(population, fitnesses)
                child1, child2 = self._crossover(parent1, parent2)

                child1 = self._repair_chromosome(self._mutate(child1))
                next_population.append(child1)

                if len(next_population) < self.population_size:
                    child2 = self._repair_chromosome(self._mutate(child2))
                    next_population.append(child2)

            population = next_population

        # Final repair pass on best solution to guarantee maximum feasibility
        if best_chromosome:
            repaired_best = self._repair_chromosome(best_chromosome)
            repaired_fit, repaired_stats = self.evaluate_chromosome(repaired_best)
            if repaired_fit >= best_fitness:
                best_chromosome = repaired_best
                best_fitness = repaired_fit
                best_stats = repaired_stats

        # Step 5: Format Final Allocation Manifest
        allocations_manifest = []
        for i, (rid, slot) in enumerate(best_chromosome):
            act = self.activities[i]
            res = self.resource_by_id.get(rid)

            act_id = act.get("id", i + 1)
            act_name = act.get("name", f"Activity #{i+1}")
            dept = act.get("department", "General")
            students = act.get("num_students", 0)
            priority = act.get("priority", 1)
            duration = act.get("duration_hours", 1.0)

            # Check individual activity violations
            act_violations = []
            status = "Allocated"

            if not res:
                status = "Unallocated"
                act_violations.append("No resource assigned")
                cost = 0.0
                rname, rtype, rcap = "None", "None", 0
            else:
                rname = res.get("name", "")
                rtype = res.get("resource_type", "")
                rcap = res.get("capacity", 0)
                unit_cost = res.get("operating_cost", 0.0)
                cost = duration * unit_cost

                if rtype != act.get("required_resource_type"):
                    status = "Conflict"
                    act_violations.append(f"Type mismatch (requires {act.get('required_resource_type')})")
                if rcap < students:
                    status = "Conflict"
                    act_violations.append(f"Capacity deficit (-{students - rcap})")
                if res.get("availability") != "Available":
                    status = "Conflict"
                    act_violations.append(f"Resource {res.get('availability')}")

            # Extract day and time slot components
            day = slot.split()[0] if " " in slot else "Monday"
            time_part = " ".join(slot.split()[1:]) if " " in slot else slot

            allocations_manifest.append({
                "activity_id": act_id,
                "activity_name": act_name,
                "department": dept,
                "num_students": students,
                "priority": priority,
                "resource_id": rid if res else None,
                "resource_name": rname,
                "resource_type": rtype,
                "resource_capacity": rcap,
                "day": day,
                "time_slot": time_part,
                "cost": round(cost, 2),
                "status": status,
                "violations": "; ".join(act_violations) if act_violations else "None"
            })

        execution_time = round(time.time() - start_time, 3)
        hard_v = best_stats.get("hard_violations", 0)
        soft_v = best_stats.get("soft_violations", 0)

        if hard_v == 0:
            status_text = "Optimal Solution Found" if soft_v == 0 else "Feasible Allocation (No Hard Conflicts)"
        else:
            status_text = f"Unresolved Conflicts ({hard_v} Hard Violations)"

        notes = (
            f"Optimized {self.num_activities} activities across {self.num_resources} resources in "
            f"{execution_time}s across {self.generations} generations (Population: {self.population_size})."
        )

        return {
            "best_fitness": round(best_fitness, 2),
            "allocations": allocations_manifest,
            "total_activities": self.num_activities,
            "allocated_activities": best_stats.get("allocated_count", self.num_activities - hard_v),
            "unallocated_activities": hard_v,
            "resource_utilization_pct": best_stats.get("utilization_pct", 0.0),
            "total_cost": best_stats.get("total_cost", 0.0),
            "hard_violations": hard_v,
            "soft_violations": soft_v,
            "execution_time_sec": execution_time,
            "convergence_history": convergence_history,
            "status": status_text,
            "notes": notes,
            "violation_details": best_stats.get("violation_details", [])
        }
