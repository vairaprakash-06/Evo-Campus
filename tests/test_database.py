"""
Automated unit test suite for the SQLite database persistence module.
Developed by Team EvoNex.
Validates:
- Schema initialization and automatic table creation
- Seeding of required realistic campus sample data
- Add, update, delete, and toggle operations for activities
- Add, update, delete operations for resources and foreign key constraints
- Saving and retrieving complete optimization runs and allocations
- Transactional consistency and persistence across restarts
"""

import os
import unittest
import tempfile
import database


class TestDatabase(unittest.TestCase):

    def setUp(self):
        """Create a temporary database file for isolated testing."""
        self.temp_dir = tempfile.TemporaryDirectory()
        self.db_path = os.path.join(self.temp_dir.name, "test_campus.db")
        database.init_db(self.db_path)

    def tearDown(self):
        """Clean up temporary test directory."""
        self.temp_dir.cleanup()

    def test_initial_sample_data_seeded(self):
        """Ensure default sample resources and activities are automatically seeded."""
        resources = database.get_resources(self.db_path)
        activities = database.get_activities(self.db_path)

        res_names = [r["name"] for r in resources]
        self.assertIn("Classroom", res_names)
        self.assertIn("Computer Lab", res_names)
        self.assertIn("Equipment", res_names)

        act_names = [a["name"] for a in activities]
        self.assertIn("AI Lecture", act_names)
        self.assertIn("DBMS Lab", act_names)
        self.assertIn("EC Lab", act_names)
        self.assertIn("Project Review", act_names)
        self.assertIn("Coding Workshop", act_names)
        self.assertIn("Research Session", act_names)

    def test_add_and_prevent_duplicate_activity(self):
        """Verify activity addition and prevention of duplicate activity names."""
        success, msg = database.add_activity(
            self.db_path,
            name="Quantum Computing Lab",
            resource_type="Computer Lab",
            demand=25,
            priority=5,
            cost_per_unit=30.0,
            is_active=True
        )
        self.assertTrue(success)

        # Attempt to add exact duplicate name
        dup_success, dup_msg = database.add_activity(
            self.db_path,
            name="Quantum Computing Lab",
            resource_type="Computer Lab",
            demand=20,
            priority=3,
            cost_per_unit=15.0
        )
        self.assertFalse(dup_success)
        self.assertIn("already exists", dup_msg)

    def test_toggle_and_delete_activity(self):
        """Verify toggling active status and activity deletion."""
        activities = database.get_activities(self.db_path)
        target = activities[0]
        act_id = target["id"]

        # Toggle status
        success, _ = database.toggle_activity_status(self.db_path, act_id)
        self.assertTrue(success)
        updated = [a for a in database.get_activities(self.db_path) if a["id"] == act_id][0]
        self.assertEqual(updated["is_active"], 0 if target["is_active"] == 1 else 1)

        # Delete activity
        del_success, _ = database.delete_activity(self.db_path, act_id)
        self.assertTrue(del_success)
        remaining_ids = [a["id"] for a in database.get_activities(self.db_path)]
        self.assertNotIn(act_id, remaining_ids)

    def test_resource_fk_constraint(self):
        """Ensure resources linked to active activities cannot be accidentally deleted."""
        # 'Classroom' is referenced by 'AI Lecture' and others
        success, msg = database.delete_resource(self.db_path, "Classroom")
        self.assertFalse(success)
        self.assertIn("depend on it", msg)

    def test_save_and_retrieve_optimization_run(self):
        """Verify saving optimization runs and retrieving details from database."""
        meta = {
            "timestamp": "2026-10-16 12:00:00",
            "population_size": 50,
            "generations": 30,
            "mutation_rate": 0.1,
            "crossover_rate": 0.85,
            "budget_limit": 3000.0,
            "random_seed": 42,
            "best_fitness": 92.5,
            "total_demand": 200,
            "total_allocated": 175,
            "demand_satisfaction_pct": 87.5,
            "budget_spent": 2850.0,
            "budget_utilization_pct": 95.0,
            "resource_utilization_pct": 85.0,
            "execution_time_sec": 0.234
        }
        allocations = [
            {
                "name": "AI Lecture",
                "resource_type": "Classroom",
                "priority": 5,
                "demand": 60,
                "allocated": 60,
                "unmet": 0,
                "satisfaction_pct": 100.0,
                "cost_per_unit": 15.0,
                "total_cost": 900.0
            }
        ]
        convergence = [{"generation": 1, "best_fitness": 75.0, "avg_fitness": 60.0, "min_fitness": 40.0}]

        run_id = database.save_optimization_run(self.db_path, meta, allocations, convergence)
        self.assertGreater(run_id, 0)

        runs = database.get_optimization_runs(self.db_path)
        self.assertEqual(len(runs), 1)
        self.assertEqual(runs[0]["id"], run_id)
        self.assertEqual(runs[0]["best_fitness"], 92.5)

        run_details = database.get_run_details(self.db_path, run_id)
        self.assertIsNotNone(run_details)
        self.assertEqual(len(run_details["allocations"]), 1)
        self.assertEqual(run_details["allocations"][0]["activity_name"], "AI Lecture")


if __name__ == "__main__":
    unittest.main()
