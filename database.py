"""
Database management module for Smart Campus Resource Optimizer.
Developed by Team EvoNex.
Handles SQLite persistence, schema initialization, sample data seeding,
and transactional CRUD operations for resources, activities, and optimization history.
"""

import sqlite3
import json
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime


from contextlib import contextmanager


DEFAULT_DB_PATH = "campus_optimizer.db"


@contextmanager
def get_connection(db_path: str = DEFAULT_DB_PATH):
    """Context manager that yields an SQLite connection and ensures it is properly closed."""
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    try:
        yield conn
    finally:
        conn.close()


def init_db(db_path: str = DEFAULT_DB_PATH) -> None:
    """
    Initializes database tables and default sample data if the tables are empty.
    Preserves all existing data during normal application restarts.
    """
    with get_connection(db_path) as conn:
        cursor = conn.cursor()

        # Table 1: Resources
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS resources (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                capacity INTEGER NOT NULL CHECK(capacity >= 0),
                unit TEXT NOT NULL DEFAULT 'Units',
                description TEXT DEFAULT '',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)

        # Table 2: Activities
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS activities (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                resource_type TEXT NOT NULL,
                demand INTEGER NOT NULL CHECK(demand > 0),
                priority INTEGER NOT NULL CHECK(priority BETWEEN 1 AND 5),
                cost_per_unit REAL NOT NULL CHECK(cost_per_unit >= 0),
                is_active INTEGER NOT NULL DEFAULT 1 CHECK(is_active IN (0, 1)),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (resource_type) REFERENCES resources(name) ON UPDATE CASCADE ON DELETE RESTRICT
            );
        """)

        # Table 3: Optimization Runs
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS optimization_runs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                population_size INTEGER NOT NULL,
                generations INTEGER NOT NULL,
                mutation_rate REAL NOT NULL,
                crossover_rate REAL NOT NULL,
                budget_limit REAL NOT NULL,
                random_seed INTEGER,
                best_fitness REAL NOT NULL,
                total_demand INTEGER NOT NULL,
                total_allocated INTEGER NOT NULL,
                demand_satisfaction_pct REAL NOT NULL,
                budget_spent REAL NOT NULL,
                budget_utilization_pct REAL NOT NULL,
                resource_utilization_pct REAL NOT NULL,
                execution_time_sec REAL NOT NULL,
                convergence_history_json TEXT
            );
        """)

        # Table 4: Run Allocations Detail
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS run_allocations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                run_id INTEGER NOT NULL,
                activity_name TEXT NOT NULL,
                resource_type TEXT NOT NULL,
                priority INTEGER NOT NULL,
                demand INTEGER NOT NULL,
                allocated INTEGER NOT NULL,
                unmet INTEGER NOT NULL,
                satisfaction_pct REAL NOT NULL,
                cost_per_unit REAL NOT NULL,
                total_cost REAL NOT NULL,
                FOREIGN KEY (run_id) REFERENCES optimization_runs(id) ON DELETE CASCADE
            );
        """)

        conn.commit()

    # Seed default data if resources table is empty
    seed_default_data(db_path, overwrite=False)


def seed_default_data(db_path: str = DEFAULT_DB_PATH, overwrite: bool = False) -> None:
    """
    Seeds realistic campus resource and activity sample data.
    If overwrite is True, existing data is cleared and refreshed with defaults.
    """
    with get_connection(db_path) as conn:
        cursor = conn.cursor()

        if overwrite:
            cursor.execute("DELETE FROM run_allocations;")
            cursor.execute("DELETE FROM optimization_runs;")
            cursor.execute("DELETE FROM activities;")
            cursor.execute("DELETE FROM resources;")

        cursor.execute("SELECT COUNT(*) AS cnt FROM resources;")
        res_count = cursor.fetchone()["cnt"]

        if res_count == 0:
            default_resources = [
                ("Classroom", 180, "Seats", "Standard lecture halls and tiered seminar rooms (Block A & B)"),
                ("Computer Lab", 90, "Workstations", "High-performance computing terminals with GPU acceleration"),
                ("Equipment", 35, "Sets", "IoT prototyping kits, oscilloscopes, and specialized sensors")
            ]
            cursor.executemany(
                "INSERT INTO resources (name, capacity, unit, description) VALUES (?, ?, ?, ?);",
                default_resources
            )

        cursor.execute("SELECT COUNT(*) AS cnt FROM activities;")
        act_count = cursor.fetchone()["cnt"]

        if act_count == 0:
            # Realistic academic sample dataset as required by specifications
            default_activities = [
                ("AI Lecture", "Classroom", 60, 5, 15.0, 1),
                ("DBMS Lab", "Computer Lab", 40, 4, 25.0, 1),
                ("EC Lab", "Equipment", 20, 5, 40.0, 1),
                ("Project Review", "Classroom", 50, 3, 10.0, 1),
                ("Coding Workshop", "Computer Lab", 45, 3, 20.0, 1),
                ("Research Session", "Equipment", 15, 4, 35.0, 1),
                ("Robotics Seminar", "Classroom", 70, 2, 12.0, 1),
                ("Cybersecurity Lab", "Computer Lab", 30, 4, 28.0, 1),
            ]
            cursor.executemany(
                """INSERT INTO activities 
                   (name, resource_type, demand, priority, cost_per_unit, is_active) 
                   VALUES (?, ?, ?, ?, ?, ?);""",
                default_activities
            )

        conn.commit()


# ============================================================================
# Resource Operations
# ============================================================================

def get_resources(db_path: str = DEFAULT_DB_PATH) -> List[Dict[str, Any]]:
    """Fetches all resources from the database sorted by name."""
    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM resources ORDER BY name ASC;")
        return [dict(row) for row in cursor.fetchall()]


def get_resource_names(db_path: str = DEFAULT_DB_PATH) -> List[str]:
    """Returns a list of resource names."""
    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM resources ORDER BY name ASC;")
        return [row["name"] for row in cursor.fetchall()]


def add_resource(
    db_path: str,
    name: str,
    capacity: int,
    unit: str = "Units",
    description: str = ""
) -> Tuple[bool, str]:
    """Validates and adds a new resource."""
    name = name.strip()
    unit = unit.strip() or "Units"
    if not name:
        return False, "Resource name cannot be empty."
    if capacity < 0:
        return False, "Capacity cannot be negative."

    try:
        with get_connection(db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO resources (name, capacity, unit, description) VALUES (?, ?, ?, ?);",
                (name, capacity, unit, description.strip())
            )
            conn.commit()
            return True, f"Resource '{name}' added successfully."
    except sqlite3.IntegrityError:
        return False, f"A resource with the name '{name}' already exists."
    except Exception as e:
        return False, f"Database error: {str(e)}"


def update_resource(
    db_path: str,
    old_name: str,
    new_name: str,
    capacity: int,
    unit: str,
    description: str
) -> Tuple[bool, str]:
    """Updates an existing resource and cascades rename to activities."""
    new_name = new_name.strip()
    unit = unit.strip() or "Units"
    if not new_name:
        return False, "Resource name cannot be empty."
    if capacity < 0:
        return False, "Capacity cannot be negative."

    try:
        with get_connection(db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                """UPDATE resources 
                   SET name = ?, capacity = ?, unit = ?, description = ? 
                   WHERE name = ?;""",
                (new_name, capacity, unit, description.strip(), old_name)
            )
            if cursor.rowcount == 0:
                return False, f"Resource '{old_name}' not found."
            conn.commit()
            return True, f"Resource '{new_name}' updated successfully."
    except sqlite3.IntegrityError:
        return False, f"Resource name '{new_name}' already exists."
    except Exception as e:
        return False, f"Database error: {str(e)}"


def delete_resource(db_path: str, name: str) -> Tuple[bool, str]:
    """Deletes a resource if no activities are linked to it."""
    try:
        with get_connection(db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) AS cnt FROM activities WHERE resource_type = ?;", (name,))
            linked_count = cursor.fetchone()["cnt"]
            if linked_count > 0:
                return False, f"Cannot delete '{name}' because {linked_count} academic activity(s) depend on it. Reassign or delete those activities first."

            cursor.execute("DELETE FROM resources WHERE name = ?;", (name,))
            conn.commit()
            return True, f"Resource '{name}' deleted successfully."
    except Exception as e:
        return False, f"Database error: {str(e)}"


# ============================================================================
# Activity Operations
# ============================================================================

def get_activities(db_path: str = DEFAULT_DB_PATH, only_active: bool = False) -> List[Dict[str, Any]]:
    """Retrieves activities, optionally filtering for only enabled ones."""
    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        if only_active:
            cursor.execute("SELECT * FROM activities WHERE is_active = 1 ORDER BY priority DESC, name ASC;")
        else:
            cursor.execute("SELECT * FROM activities ORDER BY is_active DESC, priority DESC, name ASC;")
        return [dict(row) for row in cursor.fetchall()]


def add_activity(
    db_path: str,
    name: str,
    resource_type: str,
    demand: int,
    priority: int,
    cost_per_unit: float,
    is_active: bool = True
) -> Tuple[bool, str]:
    """Validates and adds an academic activity."""
    name = name.strip()
    if not name:
        return False, "Activity name cannot be empty."
    if demand <= 0:
        return False, "Resource demand must be a positive integer (> 0)."
    if not (1 <= priority <= 5):
        return False, "Priority must be an integer between 1 (Lowest) and 5 (Highest)."
    if cost_per_unit < 0:
        return False, "Cost per unit cannot be negative."

    try:
        with get_connection(db_path) as conn:
            cursor = conn.cursor()
            # Verify resource exists
            cursor.execute("SELECT id FROM resources WHERE name = ?;", (resource_type,))
            if not cursor.fetchone():
                return False, f"Resource type '{resource_type}' does not exist."

            cursor.execute(
                """INSERT INTO activities 
                   (name, resource_type, demand, priority, cost_per_unit, is_active)
                   VALUES (?, ?, ?, ?, ?, ?);""",
                (name, resource_type, int(demand), int(priority), float(cost_per_unit), 1 if is_active else 0)
            )
            conn.commit()
            return True, f"Activity '{name}' registered successfully."
    except sqlite3.IntegrityError:
        return False, f"An activity with the name '{name}' already exists."
    except Exception as e:
        return False, f"Database error: {str(e)}"


def update_activity(
    db_path: str,
    activity_id: int,
    name: str,
    resource_type: str,
    demand: int,
    priority: int,
    cost_per_unit: float,
    is_active: bool
) -> Tuple[bool, str]:
    """Updates an existing activity."""
    name = name.strip()
    if not name:
        return False, "Activity name cannot be empty."
    if demand <= 0:
        return False, "Demand must be greater than zero."
    if not (1 <= priority <= 5):
        return False, "Priority must be between 1 and 5."
    if cost_per_unit < 0:
        return False, "Cost cannot be negative."

    try:
        with get_connection(db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                """UPDATE activities
                   SET name = ?, resource_type = ?, demand = ?, priority = ?, 
                       cost_per_unit = ?, is_active = ?
                   WHERE id = ?;""",
                (name, resource_type, int(demand), int(priority), float(cost_per_unit), 1 if is_active else 0, activity_id)
            )
            if cursor.rowcount == 0:
                return False, "Activity not found."
            conn.commit()
            return True, f"Activity '{name}' updated successfully."
    except sqlite3.IntegrityError:
        return False, f"Another activity with the name '{name}' already exists."
    except Exception as e:
        return False, f"Database error: {str(e)}"


def delete_activity(db_path: str, activity_id: int) -> Tuple[bool, str]:
    """Deletes an activity by ID."""
    try:
        with get_connection(db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM activities WHERE id = ?;", (activity_id,))
            if cursor.rowcount == 0:
                return False, "Activity not found."
            conn.commit()
            return True, "Activity deleted successfully."
    except Exception as e:
        return False, f"Database error: {str(e)}"


def toggle_activity_status(db_path: str, activity_id: int) -> Tuple[bool, str]:
    """Toggles active status of an activity between 0 and 1."""
    try:
        with get_connection(db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT is_active, name FROM activities WHERE id = ?;", (activity_id,))
            row = cursor.fetchone()
            if not row:
                return False, "Activity not found."
            new_status = 0 if row["is_active"] == 1 else 1
            cursor.execute("UPDATE activities SET is_active = ? WHERE id = ?;", (new_status, activity_id))
            conn.commit()
            status_text = "enabled" if new_status == 1 else "disabled"
            return True, f"Activity '{row['name']}' is now {status_text}."
    except Exception as e:
        return False, f"Database error: {str(e)}"


# ============================================================================
# Optimization History Operations
# ============================================================================

def save_optimization_run(
    db_path: str,
    metadata: Dict[str, Any],
    allocations: List[Dict[str, Any]],
    convergence_history: List[Dict[str, Any]]
) -> int:
    """
    Saves an optimization run and its per-activity allocations inside a safe transaction.
    Returns the generated run_id.
    """
    with get_connection(db_path) as conn:
        cursor = conn.cursor()

        cursor.execute(
            """INSERT INTO optimization_runs (
                timestamp, population_size, generations, mutation_rate, crossover_rate,
                budget_limit, random_seed, best_fitness, total_demand, total_allocated,
                demand_satisfaction_pct, budget_spent, budget_utilization_pct,
                resource_utilization_pct, execution_time_sec, convergence_history_json
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);""",
            (
                metadata.get("timestamp", datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
                metadata["population_size"],
                metadata["generations"],
                metadata["mutation_rate"],
                metadata["crossover_rate"],
                metadata["budget_limit"],
                metadata.get("random_seed"),
                metadata["best_fitness"],
                metadata["total_demand"],
                metadata["total_allocated"],
                metadata["demand_satisfaction_pct"],
                metadata["budget_spent"],
                metadata["budget_utilization_pct"],
                metadata["resource_utilization_pct"],
                metadata["execution_time_sec"],
                json.dumps(convergence_history)
            )
        )
        run_id = cursor.lastrowid

        allocation_rows = [
            (
                run_id,
                item["name"],
                item["resource_type"],
                item["priority"],
                item["demand"],
                item["allocated"],
                item["unmet"],
                item["satisfaction_pct"],
                item["cost_per_unit"],
                item["total_cost"]
            )
            for item in allocations
        ]

        cursor.executemany(
            """INSERT INTO run_allocations (
                run_id, activity_name, resource_type, priority, demand,
                allocated, unmet, satisfaction_pct, cost_per_unit, total_cost
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?);""",
            allocation_rows
        )

        conn.commit()
        return run_id


def get_optimization_runs(db_path: str = DEFAULT_DB_PATH, limit: int = 50) -> List[Dict[str, Any]]:
    """Returns recent optimization runs."""
    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM optimization_runs ORDER BY id DESC LIMIT ?;",
            (limit,)
        )
        return [dict(row) for row in cursor.fetchall()]


def get_run_details(db_path: str, run_id: int) -> Optional[Dict[str, Any]]:
    """Returns complete details of a specific optimization run including allocations."""
    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM optimization_runs WHERE id = ?;", (run_id,))
        run_row = cursor.fetchone()
        if not run_row:
            return None

        run_dict = dict(run_row)
        if run_dict.get("convergence_history_json"):
            try:
                run_dict["convergence_history"] = json.loads(run_dict["convergence_history_json"])
            except Exception:
                run_dict["convergence_history"] = []
        else:
            run_dict["convergence_history"] = []

        cursor.execute(
            "SELECT * FROM run_allocations WHERE run_id = ? ORDER BY priority DESC, activity_name ASC;",
            (run_id,)
        )
        run_dict["allocations"] = [dict(row) for row in cursor.fetchall()]
        return run_dict


def clear_history(db_path: str = DEFAULT_DB_PATH) -> Tuple[bool, str]:
    """Deletes all stored optimization runs and detailed allocations."""
    try:
        with get_connection(db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM run_allocations;")
            cursor.execute("DELETE FROM optimization_runs;")
            conn.commit()
            return True, "Optimization history cleared successfully."
    except Exception as e:
        return False, f"Failed to clear history: {str(e)}"
