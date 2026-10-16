"""
Smart Campus Resource Optimizer
Campus Resource Allocation & Optimization System
Developed by Team EvoCampus
Tagline: "Evolving Intelligence, Optimizing Tomorrow."

Main Flask Application Module.
Serves responsive HTML5/CSS3/JavaScript frontend and REST endpoints.
No Streamlit used.
"""

import os
import io
import csv
import json
from datetime import datetime
from flask import (
    Flask, render_template, request, redirect,
    url_for, flash, jsonify, Response, send_file
)

import database as db
from optimizer import GeneticAlgorithmOptimizer, DEFAULT_TIME_SLOTS

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
app = Flask(
    __name__,
    template_folder=os.path.join(BASE_DIR, "templates"),
    static_folder=os.path.join(BASE_DIR, "static"),
    static_url_path="/static"
)
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "evocampus_smart_campus_optimizer_secret_2026")

# Ensure SQLite database is created and initialized at application launch
try:
    with app.app_context():
        db.init_db()
except Exception as e:
    app.logger.warning(f"Initial DB setup notice: {e}")

import urllib.parse

class VercelPathFixMiddleware:
    """WSGI middleware to restore original PATH_INFO in Vercel serverless environment."""
    def __init__(self, wsgi_app):
        self.wsgi_app = wsgi_app

    def __call__(self, environ, start_response):
        qs = environ.get("QUERY_STRING", "")
        if "__path__=" in qs:
            params = urllib.parse.parse_qs(qs)
            injected_path = params.get("__path__", [""])[0]
            if injected_path:
                clean_path = "/" + injected_path.lstrip("/")
                environ["PATH_INFO"] = clean_path
                filtered = [p for p in qs.split("&") if not p.startswith("__path__=")]
                environ["QUERY_STRING"] = "&".join(filtered)
        elif environ.get("PATH_INFO") in ("/api/index", "/api/index.py"):
            environ["PATH_INFO"] = "/"
        return self.wsgi_app(environ, start_response)

app.wsgi_app = VercelPathFixMiddleware(app.wsgi_app)




# ---------------------------------------------------------------------------
# Template Context Processors & Filters
# ---------------------------------------------------------------------------

@app.context_processor
def inject_global_data():
    """Injects project metadata and sidebar counters into all templates."""
    stats = db.get_dashboard_stats()
    return {
        "team_name": "EvoCampus",
        "team_tagline": "Evolving Intelligence, Optimizing Tomorrow.",
        "year": "2026",
        "global_stats": stats,
        "current_time": datetime.now().strftime("%Y-%m-%d %H:%M")
    }


# ---------------------------------------------------------------------------
# Page Navigation Routes
# ---------------------------------------------------------------------------

@app.route("/api/debug")
def debug_environ():
    safe_env = {k: str(v) for k, v in request.environ.items() if isinstance(v, (str, int, float, bool))}
    return jsonify(safe_env)

@app.route("/")
@app.route("/dashboard")
@app.route("/api/index")
def dashboard():
    """Home Dashboard displaying KPI metrics, utilization stats, and Chart.js data."""
    stats = db.get_dashboard_stats()
    resources = db.get_resources()
    activities = db.get_activities()
    return render_template(
        "index.html",
        stats=stats,
        resources=resources,
        activities=activities,
        active_page="dashboard"
    )


@app.route("/activities")
def activities_page():
    """Activity Management: Search, filter, add, edit, and toggle academic activities."""
    activities = db.get_activities()
    resources = db.get_resources()
    departments = sorted(list(set(a["department"] for a in activities)))
    resource_types = sorted(list(set(r["resource_type"] for r in resources)))
    return render_template(
        "activities.html",
        activities=activities,
        departments=departments,
        resource_types=resource_types,
        time_slots=DEFAULT_TIME_SLOTS,
        active_page="activities"
    )


@app.route("/resources")
def resources_page():
    """Resource Management: View, add, edit, and delete campus facilities and equipment."""
    resources = db.get_resources()
    resource_types = sorted(list(set(r["resource_type"] for r in resources)))
    return render_template(
        "resources.html",
        resources=resources,
        resource_types=resource_types,
        active_page="resources"
    )


@app.route("/optimize")
def optimize_page():
    """Genetic Algorithm Control Center: Hyperparameter configuration and run launcher."""
    activities = db.get_activities(only_active=True)
    all_activities = db.get_activities()
    resources = db.get_resources()
    return render_template(
        "optimize.html",
        active_activities=activities,
        total_activities_count=len(all_activities),
        resources=resources,
        time_slots=DEFAULT_TIME_SLOTS,
        active_page="optimize"
    )


@app.route("/results")
@app.route("/results/<int:run_id>")
def results_page(run_id=None):
    """Displays detailed allocation manifest, Chart.js telemetry, and conflict reporting."""
    if run_id is None:
        runs = db.get_optimization_runs(limit=1)
        if not runs:
            flash("No optimization runs found. Please run the Genetic Algorithm first.", "info")
            return redirect(url_for("optimize_page"))
        run_id = runs[0]["id"]

    run = db.get_run_by_id(run_id)
    if not run:
        flash(f"Optimization run #{run_id} not found.", "warning")
        return redirect(url_for("history_page"))

    allocations = db.get_run_allocations(run_id)
    return render_template(
        "results.html",
        run=run,
        allocations=allocations,
        active_page="results"
    )


@app.route("/history")
def history_page():
    """Optimization Run History: Permanent SQLite audit trail and run comparisons."""
    runs = db.get_optimization_runs(limit=50)
    return render_template(
        "history.html",
        runs=runs,
        active_page="history"
    )


@app.route("/reports")
@app.route("/reports/<int:run_id>")
def reports_page(run_id=None):
    """Formal Printable Academic Report page with printable CSS formatting."""
    if run_id is None:
        runs = db.get_optimization_runs(limit=1)
        if not runs:
            flash("No optimization runs found to generate a report.", "info")
            return redirect(url_for("optimize_page"))
        run_id = runs[0]["id"]

    run = db.get_run_by_id(run_id)
    if not run:
        flash(f"Run #{run_id} not found.", "warning")
        return redirect(url_for("history_page"))

    allocations = db.get_run_allocations(run_id)
    resources = db.get_resources()
    activities = db.get_activities()

    return render_template(
        "reports.html",
        run=run,
        allocations=allocations,
        resources=resources,
        activities=activities,
        active_page="reports"
    )


@app.route("/about")
def about_page():
    """Project Information: Mathematical formulation, GA workflow, and team details."""
    return render_template("about.html", active_page="about")


# ---------------------------------------------------------------------------
# Optimization Execution Endpoints
# ---------------------------------------------------------------------------

@app.route("/optimize/run", methods=["POST"])
def run_optimization():
    """
    Executes the Genetic Algorithm with user-configured parameters.
    Saves the run into SQLite and returns JSON for seamless AJAX handling.
    """
    data = request.get_json(silent=True) or request.form

    pop_size = int(data.get("population_size", 50))
    generations = int(data.get("generations", 40))
    mutation_rate = float(data.get("mutation_rate", 0.15))
    crossover_rate = float(data.get("crossover_rate", 0.85))
    elitism_count = int(data.get("elitism_count", 2))
    tournament_size = int(data.get("tournament_size", 3))

    seed_raw = data.get("random_seed")
    random_seed = int(seed_raw) if seed_raw and str(seed_raw).strip() != "" else None

    # Retrieve current active problem space from SQLite
    activities = db.get_activities(only_active=True)
    resources = db.get_resources()

    if not activities:
        if request.is_json:
            return jsonify({"success": False, "error": "No active activities to optimize. Please enable or add activities."}), 400
        flash("No active activities to optimize. Please add or enable activities.", "warning")
        return redirect(url_for("activities_page"))

    if not resources:
        if request.is_json:
            return jsonify({"success": False, "error": "No campus resources available in database."}), 400
        flash("No campus resources found in database.", "warning")
        return redirect(url_for("resources_page"))

    # Instantiate and execute genuine GA
    optimizer = GeneticAlgorithmOptimizer(
        activities=activities,
        resources=resources,
        population_size=pop_size,
        generations=generations,
        mutation_rate=mutation_rate,
        crossover_rate=crossover_rate,
        elitism_count=elitism_count,
        tournament_size=tournament_size,
        random_seed=random_seed
    )

    result = optimizer.run()

    # Save to SQLite
    run_meta = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "population_size": pop_size,
        "generations": generations,
        "mutation_rate": mutation_rate,
        "crossover_rate": crossover_rate,
        "elitism_count": elitism_count,
        "tournament_size": tournament_size,
        "random_seed": random_seed,
        "best_fitness": result["best_fitness"],
        "total_activities": result["total_activities"],
        "allocated_activities": result["allocated_activities"],
        "unallocated_activities": result["unallocated_activities"],
        "resource_utilization_pct": result["resource_utilization_pct"],
        "total_cost": result["total_cost"],
        "hard_violations": result["hard_violations"],
        "soft_violations": result["soft_violations"],
        "execution_time_sec": result["execution_time_sec"],
        "status": result["status"],
        "convergence_history": result["convergence_history"],
        "notes": result["notes"]
    }

    run_id = db.save_optimization_run(run_meta, result["allocations"])

    if request.is_json or request.headers.get("X-Requested-With") == "XMLHttpRequest":
        return jsonify({
            "success": True,
            "run_id": run_id,
            "redirect_url": url_for("results_page", run_id=run_id),
            "result": result
        })

    flash(f"Genetic Algorithm optimization completed in {result['execution_time_sec']}s! (Run #{run_id})", "success")
    return redirect(url_for("results_page", run_id=run_id))


# ---------------------------------------------------------------------------
# CSV Export
# ---------------------------------------------------------------------------

@app.route("/results/export-csv/<int:run_id>")
def export_csv(run_id):
    """Streams an RFC-4180 CSV export of the complete run allocation manifest."""
    run = db.get_run_by_id(run_id)
    if not run:
        flash(f"Run #{run_id} not found for export.", "warning")
        return redirect(url_for("history_page"))

    allocations = db.get_run_allocations(run_id)

    output = io.StringIO()
    writer = csv.writer(output)

    # Write Metadata Header
    writer.writerow(["# Smart Campus Resource Optimizer - Allocation Manifest"])
    writer.writerow(["# Developed by Team EvoCampus"])
    writer.writerow(["# Run ID", run["id"]])
    writer.writerow(["# Timestamp", run["timestamp"]])
    writer.writerow(["# Best Fitness", run["best_fitness"]])
    writer.writerow(["# Resource Utilization", f"{run['resource_utilization_pct']}%"])
    writer.writerow(["# Total Cost", f"${run['total_cost']}"])
    writer.writerow(["# Execution Time", f"{run['execution_time_sec']}s"])
    writer.writerow([])

    # Table Column Headers
    writer.writerow([
        "Activity ID",
        "Activity Name",
        "Department",
        "Students",
        "Priority Tier",
        "Assigned Resource",
        "Resource Type",
        "Capacity",
        "Day",
        "Time Slot",
        "Cost ($)",
        "Allocation Status",
        "Constraint Violations"
    ])

    for a in allocations:
        writer.writerow([
            a.get("activity_id", ""),
            a.get("activity_name", ""),
            a.get("department", ""),
            a.get("num_students", ""),
            a.get("priority", ""),
            a.get("resource_name", "None"),
            a.get("resource_type", "None"),
            a.get("resource_capacity", 0),
            a.get("day", ""),
            a.get("time_slot", ""),
            f"{a.get('cost', 0.0):.2f}",
            a.get("status", ""),
            a.get("violations", "")
        ])

    output.seek(0)
    filename = f"evocampus_campus_allocation_run_{run_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    return Response(
        output.getvalue(),
        mimetype="text/csv",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )


# ---------------------------------------------------------------------------
# Activity CRUD Action Routes
# ---------------------------------------------------------------------------

@app.route("/activities/add", methods=["POST"])
def add_activity_action():
    """Creates a new academic activity."""
    name = request.form.get("name", "")
    department = request.form.get("department", "")
    num_students = int(request.form.get("num_students", 30))
    duration_hours = float(request.form.get("duration_hours", 1.5))
    required_resource_type = request.form.get("required_resource_type", "Classroom")
    priority = int(request.form.get("priority", 3))
    budget = float(request.form.get("budget", 50.0))
    preferred_day = request.form.get("preferred_day", "Monday")
    preferred_time_slot = request.form.get("preferred_time_slot", "09:00 - 11:00")
    is_active = 1 if request.form.get("is_active") else 0

    success, message = db.add_activity(
        name=name,
        department=department,
        num_students=num_students,
        duration_hours=duration_hours,
        required_resource_type=required_resource_type,
        priority=priority,
        budget=budget,
        preferred_day=preferred_day,
        preferred_time_slot=preferred_time_slot,
        is_active=is_active
    )
    flash(message, "success" if success else "danger")
    return redirect(url_for("activities_page"))


@app.route("/activities/edit/<int:activity_id>", methods=["POST"])
def edit_activity_action(activity_id):
    """Updates an existing academic activity."""
    name = request.form.get("name", "")
    department = request.form.get("department", "")
    num_students = int(request.form.get("num_students", 30))
    duration_hours = float(request.form.get("duration_hours", 1.5))
    required_resource_type = request.form.get("required_resource_type", "Classroom")
    priority = int(request.form.get("priority", 3))
    budget = float(request.form.get("budget", 50.0))
    preferred_day = request.form.get("preferred_day", "Monday")
    preferred_time_slot = request.form.get("preferred_time_slot", "09:00 - 11:00")
    is_active = 1 if request.form.get("is_active") else 0

    success, message = db.update_activity(
        activity_id=activity_id,
        name=name,
        department=department,
        num_students=num_students,
        duration_hours=duration_hours,
        required_resource_type=required_resource_type,
        priority=priority,
        budget=budget,
        preferred_day=preferred_day,
        preferred_time_slot=preferred_time_slot,
        is_active=is_active
    )
    flash(message, "success" if success else "danger")
    return redirect(url_for("activities_page"))


@app.route("/activities/delete/<int:activity_id>", methods=["POST"])
def delete_activity_action(activity_id):
    """Deletes an academic activity."""
    success, message = db.delete_activity(activity_id)
    flash(message, "success" if success else "danger")
    return redirect(url_for("activities_page"))


@app.route("/activities/toggle/<int:activity_id>", methods=["POST"])
def toggle_activity_action(activity_id):
    """Toggles activity between active and inactive."""
    success, message = db.toggle_activity_status(activity_id)
    flash(message, "info" if success else "danger")
    return redirect(url_for("activities_page"))


# ---------------------------------------------------------------------------
# Resource CRUD Action Routes
# ---------------------------------------------------------------------------

@app.route("/resources/add", methods=["POST"])
def add_resource_action():
    """Creates a new campus resource."""
    name = request.form.get("name", "")
    resource_type = request.form.get("resource_type", "Classroom")
    capacity = int(request.form.get("capacity", 40))
    location = request.form.get("location", "")
    availability = request.form.get("availability", "Available")
    operating_cost = float(request.form.get("operating_cost", 20.0))

    success, message = db.add_resource(
        name=name,
        resource_type=resource_type,
        capacity=capacity,
        location=location,
        availability=availability,
        operating_cost=operating_cost
    )
    flash(message, "success" if success else "danger")
    return redirect(url_for("resources_page"))


@app.route("/resources/edit/<int:resource_id>", methods=["POST"])
def edit_resource_action(resource_id):
    """Updates an existing campus resource."""
    name = request.form.get("name", "")
    resource_type = request.form.get("resource_type", "Classroom")
    capacity = int(request.form.get("capacity", 40))
    location = request.form.get("location", "")
    availability = request.form.get("availability", "Available")
    operating_cost = float(request.form.get("operating_cost", 20.0))

    success, message = db.update_resource(
        resource_id=resource_id,
        name=name,
        resource_type=resource_type,
        capacity=capacity,
        location=location,
        availability=availability,
        operating_cost=operating_cost
    )
    flash(message, "success" if success else "danger")
    return redirect(url_for("resources_page"))


@app.route("/resources/delete/<int:resource_id>", methods=["POST"])
def delete_resource_action(resource_id):
    """Deletes a campus resource."""
    success, message = db.delete_resource(resource_id)
    flash(message, "success" if success else "danger")
    return redirect(url_for("resources_page"))


# ---------------------------------------------------------------------------
# Run History Management
# ---------------------------------------------------------------------------

@app.route("/history/delete/<int:run_id>", methods=["POST"])
def delete_history_action(run_id):
    """Deletes an optimization run and cascading allocations."""
    success, message = db.delete_optimization_run(run_id)
    flash(message, "info" if success else "danger")
    return redirect(url_for("history_page"))


# ---------------------------------------------------------------------------
# Utility API Routes
# ---------------------------------------------------------------------------

@app.route("/api/reset-sample-data", methods=["POST"])
def reset_sample_data_action():
    """Resets the SQLite database to factory campus dataset."""
    db.seed_default_data(overwrite=True)
    flash("Database successfully restored to original campus dataset!", "success")
    return redirect(request.referrer or url_for("dashboard"))


@app.route("/api/stats")
def api_stats():
    """Returns current dashboard statistics in JSON format."""
    stats = db.get_dashboard_stats()
    return jsonify(stats)


@app.route("/api/run-details/<int:run_id>")
def api_run_details(run_id):
    """Returns run metadata and allocations in JSON format."""
    run = db.get_run_by_id(run_id)
    if not run:
        return jsonify({"error": "Run not found"}), 404
    allocations = db.get_run_allocations(run_id)
    return jsonify({"run": run, "allocations": allocations})


# ---------------------------------------------------------------------------
# Server Launcher
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    print("\n==================================================================")
    print("  Smart Campus Resource Optimizer -- Team EvoCampus")
    print("  'Evolving Intelligence, Optimizing Tomorrow.'")
    print(f"  Running locally on: http://127.0.0.1:{port}")
    print("==================================================================\n")
    app.run(host="0.0.0.0", port=port, debug=False)
