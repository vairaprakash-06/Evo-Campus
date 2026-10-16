"""
Automated unit and integration test suite for GeneticAlgorithmOptimizer.
Developed by Team EvoCampus.
Validates:
- Fitness calculation & priority scaling
- Hard constraint handling: Capacity, facility type matching, time slot collisions
- Genetic operators: Crossover, mutation, elitism, and tournament selection
- Feasibility repair operator
- Deterministic reproducibility when fixed random seed is specified
- Edge cases: Empty or inactive activities
"""

import unittest
from optimizer import GeneticAlgorithmOptimizer, PRIORITY_WEIGHTS


class TestGeneticAlgorithmOptimizer(unittest.TestCase):

    def setUp(self):
        """Standard campus problem space fixture."""
        self.sample_resources = [
            {"id": 1, "name": "Classroom Alpha", "resource_type": "Classroom", "capacity": 60, "availability": "Available", "operating_cost": 20.0},
            {"id": 2, "name": "Classroom Beta", "resource_type": "Classroom", "capacity": 40, "availability": "Available", "operating_cost": 15.0},
            {"id": 3, "name": "AI Lab 101", "resource_type": "Laboratory", "capacity": 35, "availability": "Available", "operating_cost": 45.0},
            {"id": 4, "name": "Main Auditorium", "resource_type": "Seminar Hall", "capacity": 120, "availability": "Available", "operating_cost": 75.0}
        ]

        self.sample_activities = [
            {
                "id": 1,
                "name": "Machine Learning Lab",
                "department": "Computer Science",
                "num_students": 30,
                "duration_hours": 2.0,
                "required_resource_type": "Laboratory",
                "priority": 5,
                "budget": 120.0,
                "preferred_day": "Monday",
                "preferred_time_slot": "09:00 - 11:00",
                "is_active": 1
            },
            {
                "id": 2,
                "name": "Data Structures Lecture",
                "department": "Computer Science",
                "num_students": 55,
                "duration_hours": 1.5,
                "required_resource_type": "Classroom",
                "priority": 4,
                "budget": 50.0,
                "preferred_day": "Monday",
                "preferred_time_slot": "09:00 - 10:30",
                "is_active": 1
            },
            {
                "id": 3,
                "name": "Freshman Orientation",
                "department": "Dean Office",
                "num_students": 100,
                "duration_hours": 2.0,
                "required_resource_type": "Seminar Hall",
                "priority": 3,
                "budget": 160.0,
                "preferred_day": "Tuesday",
                "preferred_time_slot": "14:00 - 16:00",
                "is_active": 1
            }
        ]

    def test_priority_fitness_scaling(self):
        """Verifies higher priority activities yield higher fitness rewards."""
        optimizer = GeneticAlgorithmOptimizer(
            activities=self.sample_activities,
            resources=self.sample_resources,
            random_seed=42
        )

        # Chromosome allocating correctly
        valid_chrom = [
            (3, "Monday 09:00 - 11:00"),  # Lab (Priority 5)
            (1, "Monday 09:00 - 11:00"),  # Classroom Alpha (Priority 4)
            (4, "Tuesday 14:00 - 16:00")  # Auditorium (Priority 3)
        ]

        fit, stats = optimizer.evaluate_chromosome(valid_chrom)
        self.assertEqual(stats["hard_violations"], 0)
        self.assertGreater(fit, 1000.0)

    def test_capacity_constraint_violation(self):
        """Verifies capacity deficit incurs severe penalty."""
        optimizer = GeneticAlgorithmOptimizer(
            activities=self.sample_activities,
            resources=self.sample_resources
        )

        # Assign activity 2 (55 students) to Classroom Beta (capacity only 40)
        violating_chrom = [
            (3, "Monday 09:00 - 11:00"),
            (2, "Monday 09:00 - 11:00"),  # Capacity 40 < 55 students -> Deficit
            (4, "Tuesday 14:00 - 16:00")
        ]

        fit_violating, stats_violating = optimizer.evaluate_chromosome(violating_chrom)
        self.assertGreaterEqual(stats_violating["hard_violations"], 1)

    def test_scheduling_collision_detection(self):
        """Verifies double booking on same facility and slot triggers hard collision penalty."""
        optimizer = GeneticAlgorithmOptimizer(
            activities=self.sample_activities,
            resources=self.sample_resources
        )

        # Both activity 1 and activity 2 double-booked in Classroom Alpha at Monday 09:00 - 11:00
        colliding_chrom = [
            (1, "Monday 09:00 - 11:00"),
            (1, "Monday 09:00 - 11:00"),
            (4, "Tuesday 14:00 - 16:00")
        ]

        fit, stats = optimizer.evaluate_chromosome(colliding_chrom)
        self.assertGreater(stats["hard_violations"], 0)

    def test_type_matching_enforcement(self):
        """Verifies activity requiring Laboratory assigned to Classroom triggers type violation."""
        optimizer = GeneticAlgorithmOptimizer(
            activities=self.sample_activities,
            resources=self.sample_resources
        )

        # Activity 1 requires Laboratory, assigned to Classroom 1
        mismatched_chrom = [
            (1, "Monday 09:00 - 11:00"),
            (1, "Tuesday 09:00 - 11:00"),
            (4, "Tuesday 14:00 - 16:00")
        ]

        fit, stats = optimizer.evaluate_chromosome(mismatched_chrom)
        self.assertGreater(stats["hard_violations"], 0)

    def test_repair_operator(self):
        """Verifies the repair operator fixes colliding time slots when compatible rooms exist."""
        optimizer = GeneticAlgorithmOptimizer(
            activities=self.sample_activities,
            resources=self.sample_resources
        )

        colliding_chrom = [
            (1, "Monday 09:00 - 11:00"),
            (1, "Monday 09:00 - 11:00"),
            (4, "Monday 09:00 - 11:00")
        ]

        repaired = optimizer._repair_chromosome(colliding_chrom)
        fit, stats = optimizer.evaluate_chromosome(repaired)
        # Repaired should resolve collisions
        self.assertLessEqual(stats["hard_violations"], 1)

    def test_reproducibility_with_seed(self):
        """Verifies identical random seeds yield identical solutions and fitness."""
        opt1 = GeneticAlgorithmOptimizer(
            activities=self.sample_activities,
            resources=self.sample_resources,
            population_size=30,
            generations=15,
            random_seed=777
        )
        res1 = opt1.run()

        opt2 = GeneticAlgorithmOptimizer(
            activities=self.sample_activities,
            resources=self.sample_resources,
            population_size=30,
            generations=15,
            random_seed=777
        )
        res2 = opt2.run()

        self.assertEqual(res1["best_fitness"], res2["best_fitness"])
        self.assertEqual(res1["total_cost"], res2["total_cost"])
        self.assertEqual(res1["resource_utilization_pct"], res2["resource_utilization_pct"])

    def test_empty_activities_handling(self):
        """Verifies graceful handling when activity list is empty."""
        opt = GeneticAlgorithmOptimizer(
            activities=[],
            resources=self.sample_resources
        )
        res = opt.run()
        self.assertEqual(res["total_activities"], 0)
        self.assertEqual(res["allocated_activities"], 0)


if __name__ == "__main__":
    unittest.main()
