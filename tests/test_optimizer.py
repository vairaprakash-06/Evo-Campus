"""
Automated unit and integration test suite for GeneticAlgorithmOptimizer.
Developed by Team EvoNex.
Validates:
- Fitness calculation & priority scaling
- Crossover and mutation operators
- Resource capacity constraints enforcement
- Budget constraints enforcement
- Demand limits clamping
- Handling of empty, single, and boundary inputs
- Deterministic reproducibility when fixed random seed is specified
"""

import unittest
from optimizer import GeneticAlgorithmOptimizer, PRIORITY_WEIGHTS


class TestGeneticAlgorithmOptimizer(unittest.TestCase):

    def setUp(self):
        """Set up standard test activities and resources."""
        self.sample_activities = [
            {"id": 1, "name": "AI Lecture", "resource_type": "Classroom", "demand": 60, "priority": 5, "cost_per_unit": 15.0, "is_active": 1},
            {"id": 2, "name": "DBMS Lab", "resource_type": "Computer Lab", "demand": 40, "priority": 4, "cost_per_unit": 25.0, "is_active": 1},
            {"id": 3, "name": "EC Lab", "resource_type": "Equipment", "demand": 20, "priority": 5, "cost_per_unit": 40.0, "is_active": 1},
            {"id": 4, "name": "Project Review", "resource_type": "Classroom", "demand": 50, "priority": 3, "cost_per_unit": 10.0, "is_active": 1},
            {"id": 5, "name": "Coding Workshop", "resource_type": "Computer Lab", "demand": 45, "priority": 3, "cost_per_unit": 20.0, "is_active": 1},
            {"id": 6, "name": "Research Session", "resource_type": "Equipment", "demand": 15, "priority": 4, "cost_per_unit": 35.0, "is_active": 1},
        ]
        self.sample_capacities = {
            "Classroom": 100,
            "Computer Lab": 70,
            "Equipment": 30
        }
        self.budget_limit = 3500.0

    def test_fitness_calculation_proportionality(self):
        """Verify that higher priority allocations yield strictly higher fitness."""
        optimizer = GeneticAlgorithmOptimizer(
            activities=self.sample_activities,
            resource_capacities=self.sample_capacities,
            budget_limit=self.budget_limit,
            random_seed=42
        )

        # Baseline zero allocation
        zero_alloc = [0] * len(self.sample_activities)
        fit_zero = optimizer.calculate_fitness(zero_alloc)
        self.assertAlmostEqual(fit_zero, 0.0, places=2)

        # Allocating only low priority (Project Review, priority 3)
        low_prio_alloc = [0, 0, 0, 30, 0, 0]
        fit_low = optimizer.calculate_fitness(low_prio_alloc)

        # Allocating same amount to high priority (AI Lecture, priority 5)
        high_prio_alloc = [30, 0, 0, 0, 0, 0]
        fit_high = optimizer.calculate_fitness(high_prio_alloc)

        # Priority 5 has higher weight (11.0 vs 4.0), so fitness must be significantly higher
        self.assertGreater(fit_high, fit_low)

    def test_demand_limits_enforced(self):
        """Ensure allocations never exceed requested demand or become negative."""
        optimizer = GeneticAlgorithmOptimizer(
            activities=self.sample_activities,
            resource_capacities=self.sample_capacities,
            budget_limit=self.budget_limit,
            random_seed=42
        )

        excessive_chromosome = [999, -50, 1000, 200, -10, 500]
        repaired = optimizer.repair_chromosome(excessive_chromosome)

        for i, alloc in enumerate(repaired):
            self.assertGreaterEqual(alloc, 0)
            self.assertLessEqual(alloc, self.sample_activities[i]["demand"])

    def test_resource_capacity_constraints(self):
        """Ensure allocations per resource type strictly do not exceed total available capacity."""
        # Restrict capacities to tight bounds
        tight_capacities = {
            "Classroom": 50,      # Classroom demands: 60 + 50 = 110 > 50
            "Computer Lab": 40,   # Lab demands: 40 + 45 = 85 > 40
            "Equipment": 15       # Equipment demands: 20 + 15 = 35 > 15
        }

        optimizer = GeneticAlgorithmOptimizer(
            activities=self.sample_activities,
            resource_capacities=tight_capacities,
            budget_limit=10000.0,  # Generous budget to test capacity independently
            population_size=40,
            generations=30,
            random_seed=123
        )

        result = optimizer.optimize()
        self.assertTrue(result["success"])

        # Check each resource type against tight capacity
        allocations = result["allocations"]
        classroom_total = sum(a["allocated"] for a in allocations if a["resource_type"] == "Classroom")
        lab_total = sum(a["allocated"] for a in allocations if a["resource_type"] == "Computer Lab")
        equipment_total = sum(a["allocated"] for a in allocations if a["resource_type"] == "Equipment")

        self.assertLessEqual(classroom_total, tight_capacities["Classroom"])
        self.assertLessEqual(lab_total, tight_capacities["Computer Lab"])
        self.assertLessEqual(equipment_total, tight_capacities["Equipment"])

    def test_budget_constraints(self):
        """Verify that total cost of allocated resources strictly respects total budget."""
        tight_budget = 500.0  # Very tight budget

        optimizer = GeneticAlgorithmOptimizer(
            activities=self.sample_activities,
            resource_capacities=self.sample_capacities,
            budget_limit=tight_budget,
            population_size=30,
            generations=25,
            random_seed=999
        )

        result = optimizer.optimize()
        self.assertTrue(result["success"])
        self.assertLessEqual(result["budget_spent"], tight_budget)

    def test_crossover_and_mutation(self):
        """Verify crossover swaps genes and mutation creates valid variation."""
        optimizer = GeneticAlgorithmOptimizer(
            activities=self.sample_activities,
            resource_capacities=self.sample_capacities,
            budget_limit=self.budget_limit,
            crossover_rate=1.0,
            mutation_rate=1.0,
            random_seed=42
        )

        p1 = [10, 10, 10, 10, 10, 10]
        p2 = [20, 20, 20, 20, 20, 20]

        # Crossover
        c1, c2 = optimizer.crossover(p1, p2)
        self.assertEqual(len(c1), len(p1))
        self.assertEqual(len(c2), len(p2))
        # Ensure offspring combined parts of parents
        self.assertTrue(any(g == 10 for g in c1) or any(g == 20 for g in c1))

        # Mutation
        mutated = optimizer.mutate(p1)
        self.assertEqual(len(mutated), len(p1))
        # Every gene should remain valid
        repaired = optimizer.repair_chromosome(mutated)
        for i, val in enumerate(repaired):
            self.assertGreaterEqual(val, 0)
            self.assertLessEqual(val, self.sample_activities[i]["demand"])

    def test_reproducibility_with_fixed_seed(self):
        """Confirm that using an identical random seed produces identical results."""
        opt1 = GeneticAlgorithmOptimizer(
            activities=self.sample_activities,
            resource_capacities=self.sample_capacities,
            budget_limit=self.budget_limit,
            population_size=40,
            generations=25,
            random_seed=777
        )
        res1 = opt1.optimize()

        opt2 = GeneticAlgorithmOptimizer(
            activities=self.sample_activities,
            resource_capacities=self.sample_capacities,
            budget_limit=self.budget_limit,
            population_size=40,
            generations=25,
            random_seed=777
        )
        res2 = opt2.optimize()

        self.assertEqual(res1["best_chromosome"], res2["best_chromosome"])
        self.assertAlmostEqual(res1["best_fitness"], res2["best_fitness"], places=3)
        self.assertEqual(res1["total_allocated"], res2["total_allocated"])
        self.assertAlmostEqual(res1["budget_spent"], res2["budget_spent"], places=2)

    def test_empty_and_disabled_activities(self):
        """Verify graceful handling when no active activities are present."""
        disabled_activities = [
            {"id": 1, "name": "Inactive 1", "resource_type": "Classroom", "demand": 50, "priority": 3, "cost_per_unit": 10.0, "is_active": 0}
        ]
        optimizer = GeneticAlgorithmOptimizer(
            activities=disabled_activities,
            resource_capacities=self.sample_capacities,
            budget_limit=1000.0
        )
        res = optimizer.optimize()
        self.assertFalse(res["success"])
        self.assertEqual(res["total_allocated"], 0)
        self.assertEqual(res["best_chromosome"], [])


if __name__ == "__main__":
    unittest.main()
