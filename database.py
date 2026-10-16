"""
Database management module for Smart Campus Resource Optimizer.
Developed by Team EvoCampus.
Tagline: "Evolving Intelligence, Optimizing Tomorrow."

Provides SQLite database operations, schema creation, sample data seeding,
and transactional CRUD functions for resources, activities, and optimization runs.
"""

import os
import sys
import tempfile
import sqlite3
import json
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
from contextlib import contextmanager

def get_default_db_path() -> str:
    """
    Returns the appropriate path for the SQLite database.
    In serverless environments (e.g. Vercel, AWS Lambda), the deployment directory
    is read-only, so the writable /tmp directory is used.
    """
    if os.environ.get("VERCEL") or os.environ.get("AWS_LAMBDA_FUNCTION_NAME"):
        return os.path.join(tempfile.gettempdir(), "campus_optimizer.db")

    if "DB_PATH" in os.environ:
        return os.environ["DB_PATH"]

    # Test if current working directory is writable
    try:
        test_file = os.path.abspath(".perm_test.tmp")
        with open(test_file, "w") as f:
            f.write("1")
        os.remove(test_file)
        return "campus_optimizer.db"
    except (OSError, IOError, PermissionError):
        return os.path.join(tempfile.gettempdir(), "campus_optimizer.db")

DEFAULT_DB_PATH = get_default_db_path()


@contextmanager
def get_connection(db_path: Optional[str] = None):
    """Context manager for SQLite database connection with row factory and foreign keys enabled."""
    target_path = db_path if db_path is not None else get_default_db_path()
    db_dir = os.path.dirname(os.path.abspath(target_path))
    if db_dir and not os.path.exists(db_dir):
        os.makedirs(db_dir, exist_ok=True)
    conn = sqlite3.connect(target_path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    try:
        yield conn
    finally:
        conn.close()


def init_db(db_path: Optional[str] = None) -> None:
    """Initializes all necessary SQLite tables if they do not exist."""
    target_path = db_path if db_path is not None else get_default_db_path()
    with get_connection(target_path) as conn:
        cursor = conn.cursor()

        # Table 1: Campus Resources
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS resources (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                resource_type TEXT NOT NULL,
                capacity INTEGER NOT NULL CHECK(capacity >= 0),
                location TEXT DEFAULT '',
                availability TEXT NOT NULL DEFAULT 'Available',
                operating_cost REAL NOT NULL DEFAULT 0.0 CHECK(operating_cost >= 0),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)

        # Table 2: Academic Activities
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS activities (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                department TEXT NOT NULL DEFAULT 'Computer Science',
                num_students INTEGER NOT NULL CHECK(num_students > 0),
                duration_hours REAL NOT NULL DEFAULT 1.0 CHECK(duration_hours > 0),
                required_resource_type TEXT NOT NULL,
                priority INTEGER NOT NULL CHECK(priority BETWEEN 1 AND 5),
                budget REAL NOT NULL DEFAULT 0.0 CHECK(budget >= 0),
                preferred_day TEXT DEFAULT 'Monday',
                preferred_time_slot TEXT DEFAULT '09:00 - 11:00',
                is_active INTEGER NOT NULL DEFAULT 1 CHECK(is_active IN (0, 1)),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)

        # Table 3: Optimization Runs Ledger
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS optimization_runs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                population_size INTEGER NOT NULL,
                generations INTEGER NOT NULL,
                mutation_rate REAL NOT NULL,
                crossover_rate REAL NOT NULL,
                elitism_count INTEGER NOT NULL,
                tournament_size INTEGER NOT NULL DEFAULT 3,
                random_seed INTEGER,
                best_fitness REAL NOT NULL,
                total_activities INTEGER NOT NULL,
                allocated_activities INTEGER NOT NULL,
                unallocated_activities INTEGER NOT NULL,
                resource_utilization_pct REAL NOT NULL,
                total_cost REAL NOT NULL,
                hard_violations INTEGER NOT NULL,
                soft_violations INTEGER NOT NULL,
                execution_time_sec REAL NOT NULL,
                status TEXT NOT NULL DEFAULT 'Completed',
                convergence_json TEXT,
                notes TEXT
            );
        """)

        # Table 4: Optimization Allocations Detail
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS allocations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                run_id INTEGER NOT NULL,
                activity_id INTEGER NOT NULL,
                activity_name TEXT NOT NULL,
                department TEXT NOT NULL,
                num_students INTEGER NOT NULL,
                priority INTEGER NOT NULL,
                resource_id INTEGER,
                resource_name TEXT,
                resource_type TEXT,
                resource_capacity INTEGER,
                day TEXT,
                time_slot TEXT,
                cost REAL NOT NULL DEFAULT 0.0,
                status TEXT NOT NULL,
                violations TEXT,
                FOREIGN KEY (run_id) REFERENCES optimization_runs(id) ON DELETE CASCADE
            );
        """)

        conn.commit()

    # Automatically seed sample data if tables are brand new and empty
    seed_default_data(db_path=db_path, overwrite=False)


def seed_default_data(db_path: str = DEFAULT_DB_PATH, overwrite: bool = False) -> None:
    """Populates initial campus resources and academic activities if tables are empty or overwrite requested."""
    with get_connection(db_path) as conn:
        cursor = conn.cursor()

        if overwrite:
            cursor.execute("DELETE FROM allocations;")
            cursor.execute("DELETE FROM optimization_runs;")
            cursor.execute("DELETE FROM activities;")
            cursor.execute("DELETE FROM resources;")
            conn.commit()

        cursor.execute("SELECT COUNT(*) FROM resources;")
        res_count = cursor.fetchone()[0]

        if res_count == 0:
            sample_resources = [
                ("Lecture Hall Alpha", "Classroom", 65, "Block A - Floor 1", "Available", 25.0),
                ("Classroom Beta", "Classroom", 45, "Block A - Floor 2", "Available", 15.0),
                ("Classroom Gamma", "Classroom", 35, "Block B - Floor 1", "Available", 12.0),
                ("Advanced AI & Robotics Lab", "Laboratory", 35, "Tech Park - Lab 101", "Available", 50.0),
                ("Cybersecurity & Cloud Lab", "Laboratory", 30, "Tech Park - Lab 102", "Available", 45.0),
                ("Electronics & IoT Lab", "Laboratory", 25, "Block C - Lab 201", "Available", 40.0),
                ("Main University Auditorium", "Seminar Hall", 150, "Central Wing", "Available", 80.0),
                ("Faculty Board Room", "Seminar Hall", 40, "Admin Block", "Available", 30.0),
                ("4K Interactive Projector Suite", "Equipment", 100, "Media Center", "Available", 10.0),
                ("VR / AR Dev Stations", "Equipment", 20, "Innovation Hub", "Available", 35.0)
            ]
            cursor.executemany("""
                INSERT INTO resources (name, resource_type, capacity, location, availability, operating_cost)
                VALUES (?, ?, ?, ?, ?, ?);
            """, sample_resources)

        cursor.execute("SELECT COUNT(*) FROM activities;")
        act_count = cursor.fetchone()[0]

        if act_count == 0:
            sample_activities = [
                ("Deep Learning & Neural Nets Lab", "Computer Science", 32, 2.0, "Laboratory", 5, 150.0, "Monday", "09:00 - 11:00", 1),
                ("Data Structures & Algorithms Lecture", "Computer Science", 60, 1.5, "Classroom", 5, 60.0, "Monday", "09:00 - 10:30", 1),
                ("Computer Networks & Security Lab", "Cybersecurity", 28, 2.0, "Laboratory", 4, 120.0, "Monday", "11:00 - 13:00", 1),
                ("Software Engineering Capstone Seminar", "Information Tech", 120, 2.0, "Seminar Hall", 5, 200.0, "Tuesday", "14:00 - 16:00", 1),
                ("Microprocessor Embedded Systems Lab", "Electronics", 24, 2.0, "Laboratory", 4, 100.0, "Wednesday", "10:00 - 12:00", 1),
                ("Discrete Mathematics & Logic Tutorial", "Mathematics", 40, 1.0, "Classroom", 3, 30.0, "Tuesday", "11:00 - 12:00", 1),
                ("Annual Capstone Project Defense", "Academic Dean", 35, 3.0, "Seminar Hall", 5, 150.0, "Thursday", "09:00 - 12:00", 1),
                ("Database Systems & Cloud SQL Lecture", "Computer Science", 42, 1.5, "Classroom", 4, 40.0, "Wednesday", "14:00 - 15:30", 1),
                ("Virtual Reality Dev Workshop", "Multimedia & Game", 18, 2.0, "Equipment", 3, 90.0, "Friday", "10:00 - 12:00", 1),
                ("Competitive Coding Club Meet", "Student Affairs", 30, 1.5, "Classroom", 2, 25.0, "Friday", "15:00 - 16:30", 1),
                ("Open Source Hackathon Briefing", "Tech Council", 55, 1.0, "Classroom", 3, 40.0, "Thursday", "14:00 - 15:00", 1),
                ("Faculty Academic Senate Assembly", "University Board", 30, 2.0, "Seminar Hall", 4, 80.0, "Monday", "14:00 - 16:00", 1)
            ]
            cursor.executemany("""
                INSERT INTO activities (name, department, num_students, duration_hours, required_resource_type, priority, budget, preferred_day, preferred_time_slot, is_active)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
            """, sample_activities)

        conn.commit()


# ---------------------------------------------------------------------------
# Resources CRUD
# ---------------------------------------------------------------------------

def get_resources(db_path: str = DEFAULT_DB_PATH) -> List[Dict[str, Any]]:
    """Retrieves all campus resources from the database ordered by name."""
    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM resources ORDER BY resource_type, name ASC;")
        rows = cursor.fetchall()
        return [dict(row) for row in rows]


def get_resource_by_id(resource_id: int, db_path: str = DEFAULT_DB_PATH) -> Optional[Dict[str, Any]]:
    """Retrieves a single campus resource by its primary key ID."""
    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM resources WHERE id = ?;", (resource_id,))
        row = cursor.fetchone()
        return dict(row) if row else None


def add_resource(
    name: str,
    resource_type: str,
    capacity: int,
    location: str = "",
    availability: str = "Available",
    operating_cost: float = 0.0,
    db_path: str = DEFAULT_DB_PATH
) -> Tuple[bool, str]:
    """Inserts a new campus resource with validation."""
    clean_name = name.strip()
    if not clean_name:
        return False, "Resource name cannot be blank."
    if capacity <= 0:
        return False, "Resource capacity must be a positive integer."
    if operating_cost < 0:
        return False, "Operating cost cannot be negative."

    try:
        with get_connection(db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO resources (name, resource_type, capacity, location, availability, operating_cost)
                VALUES (?, ?, ?, ?, ?, ?);
            """, (clean_name, resource_type.strip(), capacity, location.strip(), availability.strip(), float(operating_cost)))
            conn.commit()
            return True, f"Resource '{clean_name}' created successfully."
    except sqlite3.IntegrityError:
        return False, f"A resource named '{clean_name}' already exists."
    except Exception as e:
        return False, f"Database error: {str(e)}"


def update_resource(
    resource_id: int,
    name: str,
    resource_type: str,
    capacity: int,
    location: str = "",
    availability: str = "Available",
    operating_cost: float = 0.0,
    db_path: str = DEFAULT_DB_PATH
) -> Tuple[bool, str]:
    """Updates an existing campus resource."""
    clean_name = name.strip()
    if not clean_name:
        return False, "Resource name cannot be blank."
    if capacity <= 0:
        return False, "Resource capacity must be a positive integer."
    if operating_cost < 0:
        return False, "Operating cost cannot be negative."

    try:
        with get_connection(db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE resources
                SET name = ?, resource_type = ?, capacity = ?, location = ?, availability = ?, operating_cost = ?
                WHERE id = ?;
            """, (clean_name, resource_type.strip(), capacity, location.strip(), availability.strip(), float(operating_cost), resource_id))
            if cursor.rowcount == 0:
                return False, "Resource not found."
            conn.commit()
            return True, f"Resource '{clean_name}' updated successfully."
    except sqlite3.IntegrityError:
        return False, f"Another resource with name '{clean_name}' already exists."
    except Exception as e:
        return False, f"Database error: {str(e)}"


def delete_resource(resource_id: int, db_path: str = DEFAULT_DB_PATH) -> Tuple[bool, str]:
    """Deletes a campus resource by ID."""
    try:
        with get_connection(db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM resources WHERE id = ?;", (resource_id,))
            row = cursor.fetchone()
            if not row:
                return False, "Resource not found."
            name = row["name"]

            cursor.execute("DELETE FROM resources WHERE id = ?;", (resource_id,))
            conn.commit()
            return True, f"Resource '{name}' deleted successfully."
    except Exception as e:
        return False, f"Could not delete resource: {str(e)}"


# ---------------------------------------------------------------------------
# Activities CRUD
# ---------------------------------------------------------------------------

def get_activities(db_path: str = DEFAULT_DB_PATH, only_active: bool = False) -> List[Dict[str, Any]]:
    """Retrieves all academic activities, optionally filtering for only active ones."""
    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        if only_active:
            cursor.execute("SELECT * FROM activities WHERE is_active = 1 ORDER BY priority DESC, name ASC;")
        else:
            cursor.execute("SELECT * FROM activities ORDER BY priority DESC, name ASC;")
        rows = cursor.fetchall()
        return [dict(row) for row in rows]


def get_activity_by_id(activity_id: int, db_path: str = DEFAULT_DB_PATH) -> Optional[Dict[str, Any]]:
    """Retrieves an academic activity by primary key ID."""
    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM activities WHERE id = ?;", (activity_id,))
        row = cursor.fetchone()
        return dict(row) if row else None


def add_activity(
    name: str,
    department: str,
    num_students: int,
    duration_hours: float,
    required_resource_type: str,
    priority: int,
    budget: float,
    preferred_day: str = "Monday",
    preferred_time_slot: str = "09:00 - 11:00",
    is_active: int = 1,
    db_path: str = DEFAULT_DB_PATH
) -> Tuple[bool, str]:
    """Inserts a new academic activity with complete validation."""
    clean_name = name.strip()
    if not clean_name:
        return False, "Activity name cannot be blank."
    if num_students <= 0:
        return False, "Number of students must be greater than zero."
    if duration_hours <= 0:
        return False, "Duration must be greater than zero."
    if priority < 1 or priority > 5:
        return False, "Priority must be between 1 (Low) and 5 (Critical)."
    if budget < 0:
        return False, "Budget cannot be negative."

    try:
        with get_connection(db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO activities (
                    name, department, num_students, duration_hours,
                    required_resource_type, priority, budget,
                    preferred_day, preferred_time_slot, is_active
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
            """, (
                clean_name, department.strip(), int(num_students), float(duration_hours),
                required_resource_type.strip(), int(priority), float(budget),
                preferred_day.strip(), preferred_time_slot.strip(), 1 if is_active else 0
            ))
            conn.commit()
            return True, f"Activity '{clean_name}' created successfully."
    except sqlite3.IntegrityError:
        return False, f"An activity named '{clean_name}' already exists."
    except Exception as e:
        return False, f"Database error: {str(e)}"


def update_activity(
    activity_id: int,
    name: str,
    department: str,
    num_students: int,
    duration_hours: float,
    required_resource_type: str,
    priority: int,
    budget: float,
    preferred_day: str = "Monday",
    preferred_time_slot: str = "09:00 - 11:00",
    is_active: int = 1,
    db_path: str = DEFAULT_DB_PATH
) -> Tuple[bool, str]:
    """Updates an existing academic activity with validation."""
    clean_name = name.strip()
    if not clean_name:
        return False, "Activity name cannot be blank."
    if num_students <= 0:
        return False, "Number of students must be greater than zero."
    if duration_hours <= 0:
        return False, "Duration must be greater than zero."
    if priority < 1 or priority > 5:
        return False, "Priority must be between 1 (Low) and 5 (Critical)."
    if budget < 0:
        return False, "Budget cannot be negative."

    try:
        with get_connection(db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE activities
                SET name = ?, department = ?, num_students = ?, duration_hours = ?,
                    required_resource_type = ?, priority = ?, budget = ?,
                    preferred_day = ?, preferred_time_slot = ?, is_active = ?
                WHERE id = ?;
            """, (
                clean_name, department.strip(), int(num_students), float(duration_hours),
                required_resource_type.strip(), int(priority), float(budget),
                preferred_day.strip(), preferred_time_slot.strip(), 1 if is_active else 0,
                activity_id
            ))
            if cursor.rowcount == 0:
                return False, "Activity not found."
            conn.commit()
            return True, f"Activity '{clean_name}' updated successfully."
    except sqlite3.IntegrityError:
        return False, f"Another activity with name '{clean_name}' already exists."
    except Exception as e:
        return False, f"Database error: {str(e)}"


def delete_activity(activity_id: int, db_path: str = DEFAULT_DB_PATH) -> Tuple[bool, str]:
    """Deletes an academic activity by ID."""
    try:
        with get_connection(db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM activities WHERE id = ?;", (activity_id,))
            row = cursor.fetchone()
            if not row:
                return False, "Activity not found."
            name = row["name"]

            cursor.execute("DELETE FROM activities WHERE id = ?;", (activity_id,))
            conn.commit()
            return True, f"Activity '{name}' deleted successfully."
    except Exception as e:
        return False, f"Could not delete activity: {str(e)}"


def toggle_activity_status(activity_id: int, db_path: str = DEFAULT_DB_PATH) -> Tuple[bool, str]:
    """Toggles an activity between active (1) and inactive (0)."""
    try:
        with get_connection(db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT name, is_active FROM activities WHERE id = ?;", (activity_id,))
            row = cursor.fetchone()
            if not row:
                return False, "Activity not found."
            new_status = 0 if row["is_active"] == 1 else 1
            status_str = "Active" if new_status == 1 else "Inactive"
            cursor.execute("UPDATE activities SET is_active = ? WHERE id = ?;", (new_status, activity_id))
            conn.commit()
            return True, f"Activity '{row['name']}' set to {status_str}."
    except Exception as e:
        return False, f"Could not toggle status: {str(e)}"


# ---------------------------------------------------------------------------
# Optimization Runs & Allocations Persistence
# ---------------------------------------------------------------------------

def save_optimization_run(
    run_meta: Dict[str, Any],
    allocations_list: List[Dict[str, Any]],
    db_path: str = DEFAULT_DB_PATH
) -> int:
    """
    Persists a complete Genetic Algorithm optimization run and all individual allocations
    within an ACID-compliant transaction. Returns the newly created run_id.
    """
    timestamp = run_meta.get("timestamp", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    convergence_json = json.dumps(run_meta.get("convergence_history", []))

    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO optimization_runs (
                timestamp, population_size, generations, mutation_rate, crossover_rate,
                elitism_count, tournament_size, random_seed, best_fitness, total_activities,
                allocated_activities, unallocated_activities, resource_utilization_pct,
                total_cost, hard_violations, soft_violations, execution_time_sec, status,
                convergence_json, notes
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
        """, (
            timestamp,
            int(run_meta.get("population_size", 50)),
            int(run_meta.get("generations", 40)),
            float(run_meta.get("mutation_rate", 0.15)),
            float(run_meta.get("crossover_rate", 0.85)),
            int(run_meta.get("elitism_count", 2)),
            int(run_meta.get("tournament_size", 3)),
            run_meta.get("random_seed"),
            float(run_meta.get("best_fitness", 0.0)),
            int(run_meta.get("total_activities", len(allocations_list))),
            int(run_meta.get("allocated_activities", 0)),
            int(run_meta.get("unallocated_activities", 0)),
            float(run_meta.get("resource_utilization_pct", 0.0)),
            float(run_meta.get("total_cost", 0.0)),
            int(run_meta.get("hard_violations", 0)),
            int(run_meta.get("soft_violations", 0)),
            float(run_meta.get("execution_time_sec", 0.0)),
            str(run_meta.get("status", "Completed")),
            convergence_json,
            str(run_meta.get("notes", ""))
        ))
        run_id = cursor.lastrowid

        # Insert detailed allocations
        alloc_records = []
        for alloc in allocations_list:
            alloc_records.append((
                run_id,
                int(alloc.get("activity_id", 0)),
                str(alloc.get("activity_name", "")),
                str(alloc.get("department", "")),
                int(alloc.get("num_students", 0)),
                int(alloc.get("priority", 1)),
                alloc.get("resource_id"),
                alloc.get("resource_name"),
                alloc.get("resource_type"),
                alloc.get("resource_capacity"),
                alloc.get("day"),
                alloc.get("time_slot"),
                float(alloc.get("cost", 0.0)),
                str(alloc.get("status", "Unallocated")),
                str(alloc.get("violations", ""))
            ))

        cursor.executemany("""
            INSERT INTO allocations (
                run_id, activity_id, activity_name, department, num_students, priority,
                resource_id, resource_name, resource_type, resource_capacity,
                day, time_slot, cost, status, violations
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
        """, alloc_records)

        conn.commit()
        return run_id


def get_optimization_runs(db_path: str = DEFAULT_DB_PATH, limit: int = 25) -> List[Dict[str, Any]]:
    """Retrieves historical optimization runs ordered by latest first."""
    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM optimization_runs ORDER BY id DESC LIMIT ?;", (limit,))
        rows = cursor.fetchall()
        result = []
        for row in rows:
            d = dict(row)
            if d.get("convergence_json"):
                try:
                    d["convergence_history"] = json.loads(d["convergence_json"])
                except Exception:
                    d["convergence_history"] = []
            else:
                d["convergence_history"] = []
            result.append(d)
        return result


def get_run_by_id(run_id: int, db_path: str = DEFAULT_DB_PATH) -> Optional[Dict[str, Any]]:
    """Retrieves a single optimization run by ID with parsed convergence history."""
    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM optimization_runs WHERE id = ?;", (run_id,))
        row = cursor.fetchone()
        if not row:
            return None
        d = dict(row)
        if d.get("convergence_json"):
            try:
                d["convergence_history"] = json.loads(d["convergence_json"])
            except Exception:
                d["convergence_history"] = []
        else:
            d["convergence_history"] = []
        return d


def get_run_allocations(run_id: int, db_path: str = DEFAULT_DB_PATH) -> List[Dict[str, Any]]:
    """Retrieves all allocations belonging to a specific run ID."""
    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM allocations WHERE run_id = ? ORDER BY priority DESC, activity_name ASC;", (run_id,))
        rows = cursor.fetchall()
        return [dict(row) for row in rows]


def delete_optimization_run(run_id: int, db_path: str = DEFAULT_DB_PATH) -> Tuple[bool, str]:
    """Deletes an optimization run and cascading allocations."""
    try:
        with get_connection(db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM optimization_runs WHERE id = ?;", (run_id,))
            conn.commit()
            return True, f"Optimization run #{run_id} deleted."
    except Exception as e:
        return False, f"Could not delete run: {str(e)}"


def _fetch_dashboard_stats(db_path: str = DEFAULT_DB_PATH) -> Dict[str, Any]:
    with get_connection(db_path) as conn:
        cursor = conn.cursor()

        cursor.execute("SELECT COUNT(*) FROM activities;")
        total_activities = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM activities WHERE is_active = 1;")
        active_activities = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM resources;")
        total_resources = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM resources WHERE resource_type = 'Classroom' AND availability = 'Available';")
        avail_classrooms = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM resources WHERE resource_type = 'Laboratory' AND availability = 'Available';")
        avail_labs = cursor.fetchone()[0]

        cursor.execute("SELECT COALESCE(SUM(capacity), 0) FROM resources WHERE availability = 'Available';")
        total_capacity = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM optimization_runs;")
        total_runs = cursor.fetchone()[0]

        cursor.execute("SELECT * FROM optimization_runs ORDER BY id DESC LIMIT 1;")
        latest_run_row = cursor.fetchone()
        latest_run = dict(latest_run_row) if latest_run_row else None

        cursor.execute("SELECT * FROM optimization_runs ORDER BY id DESC LIMIT 5;")
        recent_runs = [dict(r) for r in cursor.fetchall()]

        # Resource distribution by type
        cursor.execute("SELECT resource_type, COUNT(*) as count, SUM(capacity) as total_cap FROM resources GROUP BY resource_type;")
        resource_breakdown = [dict(r) for r in cursor.fetchall()]

        # Activity priority distribution
        cursor.execute("SELECT priority, COUNT(*) as count FROM activities GROUP BY priority ORDER BY priority DESC;")
        priority_breakdown = [dict(r) for r in cursor.fetchall()]

        return {
            "total_activities": total_activities,
            "active_activities": active_activities,
            "total_resources": total_resources,
            "available_classrooms": avail_classrooms,
            "available_labs": avail_labs,
            "total_capacity": total_capacity,
            "total_runs": total_runs,
            "latest_run": latest_run,
            "recent_runs": recent_runs,
            "resource_breakdown": resource_breakdown,
            "priority_breakdown": priority_breakdown
        }


def get_dashboard_stats(db_path: str = DEFAULT_DB_PATH) -> Dict[str, Any]:
    """Calculates summary KPIs and statistics across resources, activities, and runs."""
    try:
        return _fetch_dashboard_stats(db_path)
    except sqlite3.OperationalError as e:
        if "no such table" in str(e).lower():
            init_db(db_path)
            return _fetch_dashboard_stats(db_path)
        raise

