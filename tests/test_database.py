"""
Automated unit and integration test suite for database.py.
Developed by Team EvoCampus.
Validates:
- Schema initialization & tables creation
- Resource CRUD operations & validation
- Activity CRUD operations, validation & status toggling
- Optimization runs & allocations persistence with cascading deletes
- Dashboard summary statistics calculations
"""

import os
import unittest
import database as db

TEST_DB_PATH = "test_campus_optimizer.db"


class TestDatabase(unittest.TestCase):

    def setUp(self):
        """Set up clean temporary SQLite database for isolated test execution."""
        if os.path.exists(TEST_DB_PATH):
            os.remove(TEST_DB_PATH)
        db.init_db(TEST_DB_PATH)

    def tearDown(self):
        """Clean up temporary test SQLite database."""
        if os.path.exists(TEST_DB_PATH):
            os.remove(TEST_DB_PATH)

    def test_schema_initialization(self):
        """Verifies that all 4 required tables and sample data are initialized."""
        resources = db.get_resources(TEST_DB_PATH)
        activities = db.get_activities(TEST_DB_PATH)
        self.assertGreater(len(resources), 0)
        self.assertGreater(len(activities), 0)

    def test_add_and_duplicate_resource(self):
        """Verifies adding resource and rejecting duplicates."""
        success, msg = db.add_resource(
            name="Quantum Computing Lab",
            resource_type="Laboratory",
            capacity=30,
            location="Building Q",
            availability="Available",
            operating_cost=60.0,
            db_path=TEST_DB_PATH
        )
        self.assertTrue(success)

        # Duplicate name must fail
        dup_success, dup_msg = db.add_resource(
            name="Quantum Computing Lab",
            resource_type="Laboratory",
            capacity=30,
            db_path=TEST_DB_PATH
        )
        self.assertFalse(dup_success)

    def test_update_and_delete_resource(self):
        """Verifies resource update and deletion."""
        resources = db.get_resources(TEST_DB_PATH)
        first_res = resources[0]

        # Update capacity
        up_success, up_msg = db.update_resource(
            resource_id=first_res["id"],
            name=first_res["name"],
            resource_type=first_res["resource_type"],
            capacity=999,
            db_path=TEST_DB_PATH
        )
        self.assertTrue(up_success)

        updated_res = db.get_resource_by_id(first_res["id"], TEST_DB_PATH)
        self.assertEqual(updated_res["capacity"], 999)

        # Delete
        del_success, del_msg = db.delete_resource(first_res["id"], TEST_DB_PATH)
        self.assertTrue(del_success)
        self.assertIsNone(db.get_resource_by_id(first_res["id"], TEST_DB_PATH))

    def test_add_and_toggle_activity(self):
        """Verifies activity creation and active status toggling."""
        success, msg = db.add_activity(
            name="Bio-Inspired Robotics Practical",
            department="Biomedical Eng",
            num_students=28,
            duration_hours=2.0,
            required_resource_type="Laboratory",
            priority=5,
            budget=140.0,
            preferred_day="Wednesday",
            preferred_time_slot="10:00 - 12:00",
            is_active=1,
            db_path=TEST_DB_PATH
        )
        self.assertTrue(success)

        # Find created activity
        activities = db.get_activities(TEST_DB_PATH)
        created = [a for a in activities if a["name"] == "Bio-Inspired Robotics Practical"][0]
        self.assertEqual(created["is_active"], 1)

        # Toggle to inactive
        t_success, t_msg = db.toggle_activity_status(created["id"], TEST_DB_PATH)
        self.assertTrue(t_success)
        toggled = db.get_activity_by_id(created["id"], TEST_DB_PATH)
        self.assertEqual(toggled["is_active"], 0)

    def test_save_and_retrieve_optimization_run(self):
        """Verifies saving an optimization run and cascading allocations."""
        run_meta = {
            "timestamp": "2026-10-16 12:00:00",
            "population_size": 40,
            "generations": 25,
            "mutation_rate": 0.15,
            "crossover_rate": 0.85,
            "elitism_count": 2,
            "tournament_size": 3,
            "best_fitness": 1250.5,
            "total_activities": 2,
            "allocated_activities": 2,
            "unallocated_activities": 0,
            "resource_utilization_pct": 82.5,
            "total_cost": 95.0,
            "hard_violations": 0,
            "soft_violations": 0,
            "execution_time_sec": 0.45,
            "status": "Optimal Solution Found"
        }

        allocations = [
            {
                "activity_id": 1,
                "activity_name": "Test Act 1",
                "department": "CS",
                "num_students": 30,
                "priority": 5,
                "resource_id": 1,
                "resource_name": "Room A",
                "resource_type": "Classroom",
                "resource_capacity": 40,
                "day": "Monday",
                "time_slot": "09:00 - 11:00",
                "cost": 50.0,
                "status": "Allocated",
                "violations": "None"
            },
            {
                "activity_id": 2,
                "activity_name": "Test Act 2",
                "department": "CS",
                "num_students": 25,
                "priority": 4,
                "resource_id": 2,
                "resource_name": "Lab B",
                "resource_type": "Laboratory",
                "resource_capacity": 30,
                "day": "Tuesday",
                "time_slot": "11:00 - 13:00",
                "cost": 45.0,
                "status": "Allocated",
                "violations": "None"
            }
        ]

        run_id = db.save_optimization_run(run_meta, allocations, TEST_DB_PATH)
        self.assertGreater(run_id, 0)

        # Retrieve run and allocations
        saved_run = db.get_run_by_id(run_id, TEST_DB_PATH)
        self.assertIsNotNone(saved_run)
        self.assertEqual(saved_run["best_fitness"], 1250.5)

        saved_allocs = db.get_run_allocations(run_id, TEST_DB_PATH)
        self.assertEqual(len(saved_allocs), 2)

        # Delete run
        del_success, del_msg = db.delete_optimization_run(run_id, TEST_DB_PATH)
        self.assertTrue(del_success)
        self.assertIsNone(db.get_run_by_id(run_id, TEST_DB_PATH))
        self.assertEqual(len(db.get_run_allocations(run_id, TEST_DB_PATH)), 0)

    def test_dashboard_stats(self):
        """Verifies dashboard summary statistics calculation."""
        stats = db.get_dashboard_stats(TEST_DB_PATH)
        self.assertIn("total_activities", stats)
        self.assertIn("active_activities", stats)
        self.assertIn("total_resources", stats)
        self.assertIn("total_capacity", stats)
        self.assertGreater(stats["total_capacity"], 0)


if __name__ == "__main__":
    unittest.main()
