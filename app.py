"""
Smart Campus Resource Optimizer
College Evolutionary Computing (EC) Project
Developed by Team EvoNex
Tagline: "Evolving Intelligence, Optimizing Tomorrow."
Main Streamlit Application Module
"""

import time
import json
from datetime import datetime
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import streamlit as st

import database as db
from optimizer import GeneticAlgorithmOptimizer, PRIORITY_WEIGHTS


# -----------------------------------------------------------------------------
# Streamlit App Configuration & Styling
# -----------------------------------------------------------------------------

st.set_page_config(
    page_title="Smart Campus Resource Optimizer | EvoNex",
    page_icon="🧬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom High-Aesthetic Styling
CUSTOM_CSS = """
<style>
    /* Global styles */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;600&display=swap');

    html, body, [class*="css"] {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }

    code, pre {
        font-family: 'JetBrains Mono', monospace !important;
    }

    /* Gradient header banner */
    .evonex-banner {
        background: linear-gradient(135deg, rgba(30, 58, 138, 0.7) 0%, rgba(15, 23, 42, 0.9) 100%);
        border: 1px solid rgba(59, 130, 246, 0.3);
        border-radius: 14px;
        padding: 24px 28px;
        margin-bottom: 24px;
        box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.4);
    }
    .evonex-title {
        font-size: 2.2rem;
        font-weight: 800;
        letter-spacing: -0.02em;
        background: linear-gradient(90deg, #60A5FA 0%, #A78BFA 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 4px;
    }
    .evonex-tagline {
        color: #94A3B8;
        font-size: 1.05rem;
        font-weight: 500;
        letter-spacing: 0.02em;
    }
    .evonex-badge {
        display: inline-block;
        background: rgba(59, 130, 246, 0.2);
        color: #60A5FA;
        border: 1px solid rgba(59, 130, 246, 0.4);
        padding: 4px 10px;
        border-radius: 9999px;
        font-size: 0.8rem;
        font-weight: 600;
        margin-top: 6px;
    }

    /* KPI Cards */
    .kpi-container {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
        gap: 16px;
        margin-bottom: 24px;
    }
    .kpi-card {
        background: rgba(30, 41, 59, 0.8);
        border: 1px solid rgba(51, 65, 85, 0.8);
        border-radius: 12px;
        padding: 18px 20px;
        transition: all 0.2s ease-in-out;
    }
    .kpi-card:hover {
        border-color: rgba(59, 130, 246, 0.5);
        transform: translateY(-2px);
        box-shadow: 0 8px 20px -4px rgba(59, 130, 246, 0.15);
    }
    .kpi-label {
        font-size: 0.82rem;
        font-weight: 600;
        color: #94A3B8;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        margin-bottom: 6px;
    }
    .kpi-value {
        font-size: 1.85rem;
        font-weight: 700;
        color: #F8FAFC;
        line-height: 1.1;
    }
    .kpi-sub {
        font-size: 0.8rem;
        color: #64748B;
        margin-top: 4px;
    }

    /* Pill Badges */
    .prio-pill-5 { background: #E11D48; color: white; padding: 2px 8px; border-radius: 6px; font-weight: 700; font-size: 0.75rem; }
    .prio-pill-4 { background: #EA580C; color: white; padding: 2px 8px; border-radius: 6px; font-weight: 700; font-size: 0.75rem; }
    .prio-pill-3 { background: #2563EB; color: white; padding: 2px 8px; border-radius: 6px; font-weight: 700; font-size: 0.75rem; }
    .prio-pill-2 { background: #0D9488; color: white; padding: 2px 8px; border-radius: 6px; font-weight: 700; font-size: 0.75rem; }
    .prio-pill-1 { background: #475569; color: white; padding: 2px 8px; border-radius: 6px; font-weight: 700; font-size: 0.75rem; }

    /* Custom buttons */
    div.stButton > button:first-child {
        border-radius: 8px;
        font-weight: 600;
        transition: all 0.2s ease;
    }
    div.stButton > button[kind="primary"] {
        background: linear-gradient(135deg, #2563EB 0%, #4F46E5 100%);
        border: none;
        color: #FFFFFF;
        box-shadow: 0 4px 14px rgba(37, 99, 235, 0.35);
    }
    div.stButton > button[kind="primary"]:hover {
        background: linear-gradient(135deg, #1D4ED8 0%, #4338CA 100%);
        box-shadow: 0 6px 20px rgba(37, 99, 235, 0.5);
        transform: translateY(-1px);
    }
</style>
"""
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)


# -----------------------------------------------------------------------------
# Initialize SQLite Database & Session State
# -----------------------------------------------------------------------------

db.init_db()

if "latest_result" not in st.session_state:
    st.session_state.latest_result = None

if "history_inspection_id" not in st.session_state:
    st.session_state.history_inspection_id = None


# -----------------------------------------------------------------------------
# Helper Functions & Plotly Dark Theme Styling
# -----------------------------------------------------------------------------

def apply_plotly_theme(fig: go.Figure) -> go.Figure:
    """Applies a cohesive modern dark aesthetic to Plotly figures."""
    fig.update_layout(
        paper_bgcolor="rgba(15, 23, 42, 0.6)",
        plot_bgcolor="rgba(30, 41, 59, 0.4)",
        font=dict(family="Inter, sans-serif", color="#E2E8F0"),
        margin=dict(l=40, r=40, t=50, b=40),
        legend=dict(
            bgcolor="rgba(15, 23, 42, 0.8)",
            bordercolor="rgba(51, 65, 85, 0.5)",
            borderwidth=1,
            font=dict(size=11)
        ),
        xaxis=dict(
            gridcolor="rgba(51, 65, 85, 0.4)",
            zerolinecolor="rgba(51, 65, 85, 0.6)",
            tickfont=dict(color="#94A3B8")
        ),
        yaxis=dict(
            gridcolor="rgba(51, 65, 85, 0.4)",
            zerolinecolor="rgba(51, 65, 85, 0.6)",
            tickfont=dict(color="#94A3B8")
        )
    )
    return fig


def render_banner():
    """Renders the top branding header."""
    st.markdown("""
    <div class="evonex-banner">
        <div style="display: flex; justify-content: space-between; align-items: flex-start; flex-wrap: wrap;">
            <div>
                <div class="evonex-title">Smart Campus Resource Optimizer</div>
                <div class="evonex-tagline">“Evolving Intelligence, Optimizing Tomorrow.”</div>
                <div class="evonex-badge">Team EvoNex &bull; Evolutionary Computing Lab</div>
            </div>
            <div style="text-align: right; margin-top: 8px;">
                <span style="font-size: 0.85rem; color: #94A3B8;">Algorithm: </span>
                <span style="font-size: 0.85rem; font-weight: 700; color: #60A5FA;">Genetic Algorithm (From Scratch)</span>
                <br>
                <span style="font-size: 0.85rem; color: #94A3B8;">Architecture: </span>
                <span style="font-size: 0.85rem; font-weight: 600; color: #A78BFA;">Streamlit &bull; SQLite &bull; Plotly</span>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)


# -----------------------------------------------------------------------------
# Sidebar Navigation and Global Parameters
# -----------------------------------------------------------------------------

with st.sidebar:
    st.markdown("### 🧬 **EvoNex Control Center**")
    st.caption("College Evolutionary Computing Project")
    st.markdown("---")

    selected_module = st.radio(
        "**Navigation Modules**",
        [
            "📊 Dashboard",
            "🧬 GA Optimizer",
            "📈 Results & Analytics",
            "📚 Activity Management",
            "🏛️ Resource Management",
            "📜 Optimization History",
            "📖 Academic Project Docs"
        ],
        index=0
    )

    st.markdown("---")
    st.markdown("#### ⚙️ Quick GA Defaults")

    # Fetch resources & activities for sidebar counts
    resources_list = db.get_resources()
    activities_list = db.get_activities()
    active_count = sum(1 for a in activities_list if a["is_active"] == 1)
    total_cap = sum(r["capacity"] for r in resources_list)

    st.metric("Total Resource Capacity", f"{total_cap} units")
    st.metric("Active Activities", f"{active_count} of {len(activities_list)}")

    st.markdown("---")
    with st.expander("🛠️ Database Tools", expanded=False):
        if st.button("🔄 Reset Sample Dataset", use_container_width=True):
            db.seed_default_data(overwrite=True)
            st.session_state.latest_result = None
            st.toast("Database reset to original campus sample dataset!", icon="✅")
            st.rerun()

        if st.button("🗑️ Clear Optimization History", use_container_width=True):
            db.clear_history()
            st.session_state.latest_result = None
            st.toast("Optimization history cleared.", icon="ℹ️")
            st.rerun()

    st.markdown(
        "<div style='text-align: center; color: #64748B; font-size: 0.78rem; margin-top: 20px;'>"
        "EvoNex v2.4 &bull; Open Source EC Platform<br>"
        "&copy; 2026 Academic Innovation Project"
        "</div>",
        unsafe_allow_html=True
    )


# Render Global Header
render_banner()


# =============================================================================
# MODULE 1: DASHBOARD
# =============================================================================
if selected_module == "📊 Dashboard":
    st.subheader("Campus Resource Optimization Dashboard")
    st.markdown("Real-time telemetry and overview of academic activities, resource allocation status, and historical optimization efficiency.")

    # Live data extraction
    resources = db.get_resources()
    activities = db.get_activities()
    active_activities = [a for a in activities if a["is_active"] == 1]
    runs = db.get_optimization_runs(limit=10)

    total_capacity = sum(r["capacity"] for r in resources)
    total_demand = sum(a["demand"] for a in active_activities)
    active_count = len(active_activities)

    latest_run = runs[0] if runs else None

    # Top KPI Metrics Cards
    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-label">Total Capacity</div>
            <div class="kpi-value">{total_capacity:,}</div>
            <div class="kpi-sub">Across {len(resources)} resource types</div>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-label">Active Activities</div>
            <div class="kpi-value">{active_count}</div>
            <div class="kpi-sub">{len(activities) - active_count} disabled</div>
        </div>
        """, unsafe_allow_html=True)
    with col3:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-label">Gross Demand</div>
            <div class="kpi-value">{total_demand:,}</div>
            <div class="kpi-sub">Requested resource units</div>
        </div>
        """, unsafe_allow_html=True)
    with col4:
        demand_sat = f"{latest_run['demand_satisfaction_pct']}%" if latest_run else "—"
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-label">Demand Satisfied</div>
            <div class="kpi-value" style="color: #34D399;">{demand_sat}</div>
            <div class="kpi-sub">{"Latest Run Result" if latest_run else "No runs recorded"}</div>
        </div>
        """, unsafe_allow_html=True)
    with col5:
        res_util = f"{latest_run['resource_utilization_pct']}%" if latest_run else "—"
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-label">Resource Util.</div>
            <div class="kpi-value" style="color: #60A5FA;">{res_util}</div>
            <div class="kpi-sub">Physical campus occupancy</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Main Visual Analytics Columns
    v_col1, v_col2 = st.columns([3, 2])

    with v_col1:
        st.markdown("##### 🏛️ Resource Capacity vs. Active Academic Demand")
        res_summary = []
        for r in resources:
            r_name = r["name"]
            r_cap = r["capacity"]
            r_dem = sum(a["demand"] for a in active_activities if a["resource_type"] == r_name)
            res_summary.append({
                "Resource": r_name,
                "Available Capacity": r_cap,
                "Total Demand Requested": r_dem,
                "Deficit / Surplus": r_cap - r_dem
            })

        df_res = pd.DataFrame(res_summary)
        fig_bar = px.bar(
            df_res,
            x="Resource",
            y=["Available Capacity", "Total Demand Requested"],
            barmode="group",
            color_discrete_map={
                "Available Capacity": "#3B82F6",
                "Total Demand Requested": "#EC4899"
            },
            title="Capacity vs. Demand Breakdown by Resource"
        )
        fig_bar.update_layout(height=340)
        st.plotly_chart(apply_plotly_theme(fig_bar), use_container_width=True)

    with v_col2:
        st.markdown("##### 🎯 Academic Activities by Priority Tier")
        prio_counts = {p: 0 for p in range(1, 6)}
        prio_names = {1: "1 - Low", 2: "2 - Med-Low", 3: "3 - Medium", 4: "4 - High", 5: "5 - Critical"}
        for a in active_activities:
            prio_counts[a["priority"]] = prio_counts.get(a["priority"], 0) + 1

        df_prio = pd.DataFrame([
            {"Priority Tier": prio_names[k], "Count": v, "Priority": k}
            for k, v in prio_counts.items() if v > 0
        ])

        if not df_prio.empty:
            fig_pie = px.pie(
                df_prio,
                names="Priority Tier",
                values="Count",
                hole=0.55,
                color="Priority Tier",
                color_discrete_map={
                    "5 - Critical": "#E11D48",
                    "4 - High": "#EA580C",
                    "3 - Medium": "#2563EB",
                    "2 - Med-Low": "#0D9488",
                    "1 - Low": "#64748B"
                },
                title="Priority Distribution (Active Activities)"
            )
            fig_pie.update_layout(height=340)
            st.plotly_chart(apply_plotly_theme(fig_pie), use_container_width=True)
        else:
            st.info("No active activities found.")

    # Recent Optimization Runs Table
    st.markdown("---")
    st.markdown("##### 📜 Recent Optimization Runs")
    if runs:
        display_runs = []
        for r in runs:
            display_runs.append({
                "Run ID": f"#{r['id']}",
                "Timestamp": r["timestamp"],
                "Population": r["population_size"],
                "Generations": r["generations"],
                "Best Fitness": r["best_fitness"],
                "Allocated / Demand": f"{r['total_allocated']} / {r['total_demand']}",
                "Demand Satisfaction": f"{r['demand_satisfaction_pct']}%",
                "Resource Util.": f"{r['resource_utilization_pct']}%",
                "Budget Spent": f"${r['budget_spent']:,.2f} ({r['budget_utilization_pct']}%)",
                "Runtime": f"{r['execution_time_sec']:.3f}s"
            })
        st.dataframe(pd.DataFrame(display_runs), use_container_width=True, hide_index=True)
    else:
        st.info("No optimization runs recorded yet. Navigate to **🧬 GA Optimizer** to execute your first evolutionary run!")


# =============================================================================
# MODULE 2: ACTIVITY MANAGEMENT
# =============================================================================
elif selected_module == "📚 Activity Management":
    st.subheader("Academic Activity Management")
    st.markdown("Configure academic sessions, workshops, laboratory practicals, and lectures competing for campus resources.")

    resources = db.get_resources()
    resource_names = [r["name"] for r in resources]

    if not resource_names:
        st.error("No resources configured. Please add resources in 'Resource Management' first.")
        st.stop()

    tab_view, tab_add, tab_edit, tab_delete = st.tabs([
        "📋 Registered Activities",
        "➕ Add New Activity",
        "✏️ Edit Activity",
        "🗑️ Delete / Toggle"
    ])

    with tab_view:
        activities = db.get_activities()
        if activities:
            table_data = []
            for act in activities:
                table_data.append({
                    "ID": act["id"],
                    "Activity Name": act["name"],
                    "Resource Type": act["resource_type"],
                    "Demand": act["demand"],
                    "Priority": act["priority"],
                    "Unit Cost ($)": f"${act['cost_per_unit']:.2f}",
                    "Max Total Cost ($)": f"${act['demand'] * act['cost_per_unit']:.2f}",
                    "Status": "🟢 Enabled" if act["is_active"] == 1 else "🔴 Disabled"
                })
            df_table = pd.DataFrame(table_data)
            st.dataframe(df_table, use_container_width=True, hide_index=True)

            # Quick summary stats
            col_a, col_b, col_c = st.columns(3)
            col_a.metric("Total Activities", len(activities))
            col_b.metric("Active Activities", sum(1 for a in activities if a["is_active"] == 1))
            total_active_cost = sum(a["demand"] * a["cost_per_unit"] for a in activities if a["is_active"] == 1)
            col_c.metric("Active Demand Potential Cost", f"${total_active_cost:,.2f}")
        else:
            st.warning("No activities found. Add an activity in the next tab or reset to sample data.")

    with tab_add:
        st.markdown("##### Register a New Academic Activity")
        with st.form("add_activity_form", clear_on_submit=True):
            col1, col2 = st.columns(2)
            with col1:
                name_in = st.text_input("Activity Name *", placeholder="e.g. Distributed Systems Lab")
                res_type_in = st.selectbox("Required Resource Type *", resource_names)
                demand_in = st.number_input("Required Resource Quantity (Demand) *", min_value=1, max_value=500, value=30, step=1)
            with col2:
                priority_in = st.select_slider(
                    "Priority Level (1: Low to 5: Critical) *",
                    options=[1, 2, 3, 4, 5],
                    value=3,
                    format_func=lambda p: {
                        1: "1 - Low (Elective / Optional)",
                        2: "2 - Medium-Low (Guest Seminar)",
                        3: "3 - Medium (Regular Class/Tutorial)",
                        4: "4 - High (Core Lab / Assessment)",
                        5: "5 - Critical (Accredited / Capstone)"
                    }[p]
                )
                cost_in = st.number_input("Cost per Resource Unit ($) *", min_value=0.0, max_value=5000.0, value=20.0, step=1.0)
                active_in = st.checkbox("Enable Activity Immediately", value=True)

            submit_add = st.form_submit_button("➕ Register Activity", use_container_width=True, type="primary")

            if submit_add:
                ok, msg = db.add_activity(
                    db_path=db.DEFAULT_DB_PATH,
                    name=name_in,
                    resource_type=res_type_in,
                    demand=demand_in,
                    priority=priority_in,
                    cost_per_unit=cost_in,
                    is_active=active_in
                )
                if ok:
                    st.success(msg)
                    time.sleep(0.5)
                    st.rerun()
                else:
                    st.error(msg)

    with tab_edit:
        st.markdown("##### Modify Existing Academic Activity")
        activities = db.get_activities()
        if activities:
            act_names = {f"#{a['id']} - {a['name']} ({a['resource_type']})": a for a in activities}
            selected_key = st.selectbox("Select Activity to Edit", list(act_names.keys()))
            target_act = act_names[selected_key]

            with st.form("edit_activity_form"):
                col_e1, col_e2 = st.columns(2)
                with col_e1:
                    new_name = st.text_input("Activity Name", value=target_act["name"])
                    current_res_idx = resource_names.index(target_act["resource_type"]) if target_act["resource_type"] in resource_names else 0
                    new_res = st.selectbox("Resource Type", resource_names, index=current_res_idx)
                    new_demand = st.number_input("Resource Demand", min_value=1, max_value=500, value=int(target_act["demand"]))
                with col_e2:
                    new_prio = st.select_slider(
                        "Priority Level",
                        options=[1, 2, 3, 4, 5],
                        value=int(target_act["priority"])
                    )
                    new_cost = st.number_input("Cost per Unit ($)", min_value=0.0, max_value=5000.0, value=float(target_act["cost_per_unit"]))
                    new_status = st.checkbox("Is Enabled", value=(target_act["is_active"] == 1))

                submit_edit = st.form_submit_button("💾 Save Changes", use_container_width=True, type="primary")

                if submit_edit:
                    ok, msg = db.update_activity(
                        db_path=db.DEFAULT_DB_PATH,
                        activity_id=target_act["id"],
                        name=new_name,
                        resource_type=new_res,
                        demand=new_demand,
                        priority=new_prio,
                        cost_per_unit=new_cost,
                        is_active=new_status
                    )
                    if ok:
                        st.success(msg)
                        time.sleep(0.5)
                        st.rerun()
                    else:
                        st.error(msg)
        else:
            st.info("No activities available to edit.")

    with tab_delete:
        st.markdown("##### Delete or Toggle Activity State")
        activities = db.get_activities()
        if activities:
            col_d1, col_d2 = st.columns(2)
            with col_d1:
                st.markdown("###### Quick Toggle Status")
                act_to_toggle = st.selectbox("Select Activity to Toggle", [f"#{a['id']}: {a['name']} ({'Enabled' if a['is_active']==1 else 'Disabled'})" for a in activities], key="toggle_sel")
                act_id_toggle = int(act_to_toggle.split(":")[0].replace("#", ""))
                if st.button("🔄 Toggle Active / Inactive", use_container_width=True):
                    ok, msg = db.toggle_activity_status(db.DEFAULT_DB_PATH, act_id_toggle)
                    if ok:
                        st.success(msg)
                        st.rerun()
                    else:
                        st.error(msg)

            with col_d2:
                st.markdown("###### Permanently Remove Activity")
                act_to_del = st.selectbox("Select Activity to Delete", [f"#{a['id']}: {a['name']}" for a in activities], key="del_sel")
                act_id_del = int(act_to_del.split(":")[0].replace("#", ""))
                if st.button("🗑️ Permanently Delete", use_container_width=True, type="secondary"):
                    ok, msg = db.delete_activity(db.DEFAULT_DB_PATH, act_id_del)
                    if ok:
                        st.warning(msg)
                        time.sleep(0.5)
                        st.rerun()
                    else:
                        st.error(msg)


# =============================================================================
# MODULE 3: RESOURCE MANAGEMENT
# =============================================================================
elif selected_module == "🏛️ Resource Management":
    st.subheader("Campus Resource Inventory")
    st.markdown("Manage scarce institutional facilities, specialized labs, tiered classrooms, and experimental equipment.")

    tab_r_view, tab_r_add, tab_r_edit, tab_r_del = st.tabs([
        "🏛️ Current Resources",
        "➕ Add Resource",
        "✏️ Edit Capacity",
        "🗑️ Delete Resource"
    ])

    with tab_r_view:
        resources = db.get_resources()
        activities = db.get_activities(only_active=True)

        res_table = []
        for r in resources:
            r_name = r["name"]
            linked_dem = sum(a["demand"] for a in activities if a["resource_type"] == r_name)
            linked_count = sum(1 for a in activities if a["resource_type"] == r_name)
            util_potential = round((linked_dem / r["capacity"] * 100.0) if r["capacity"] > 0 else 0.0, 1)

            res_table.append({
                "Resource Name": r_name,
                "Total Capacity": f"{r['capacity']} {r['unit']}",
                "Active Demand": f"{linked_dem} {r['unit']}",
                "Demand Pressure": f"{util_potential}%",
                "Linked Activities": linked_count,
                "Description": r["description"]
            })
        st.dataframe(pd.DataFrame(res_table), use_container_width=True, hide_index=True)

    with tab_r_add:
        st.markdown("##### Add New Campus Resource Type")
        with st.form("add_resource_form", clear_on_submit=True):
            r_name_in = st.text_input("Resource Name *", placeholder="e.g. Auditorium / VR Lab")
            col_rc1, col_rc2 = st.columns(2)
            with col_rc1:
                r_cap_in = st.number_input("Available Total Capacity *", min_value=1, max_value=5000, value=50, step=1)
            with col_rc2:
                r_unit_in = st.text_input("Unit of Measure *", value="Seats", placeholder="e.g. Seats, Workstations, Kits")
            r_desc_in = st.text_area("Location and Facility Description", placeholder="e.g. Building C, Room 402 with projector setup")

            submit_r_add = st.form_submit_button("➕ Register Resource", use_container_width=True, type="primary")
            if submit_r_add:
                ok, msg = db.add_resource(
                    db.DEFAULT_DB_PATH,
                    name=r_name_in,
                    capacity=r_cap_in,
                    unit=r_unit_in,
                    description=r_desc_in
                )
                if ok:
                    st.success(msg)
                    st.rerun()
                else:
                    st.error(msg)

    with tab_r_edit:
        st.markdown("##### Adjust Facility Capacity")
        resources = db.get_resources()
        if resources:
            r_map = {r["name"]: r for r in resources}
            sel_res_name = st.selectbox("Select Resource to Modify", list(r_map.keys()))
            cur_r = r_map[sel_res_name]

            with st.form("edit_resource_form"):
                new_r_name = st.text_input("Resource Name", value=cur_r["name"])
                new_r_cap = st.number_input("Adjusted Capacity", min_value=0, max_value=5000, value=int(cur_r["capacity"]))
                new_r_unit = st.text_input("Unit", value=cur_r["unit"])
                new_r_desc = st.text_area("Description", value=cur_r["description"] or "")

                submit_r_edit = st.form_submit_button("💾 Save Resource Changes", use_container_width=True, type="primary")
                if submit_r_edit:
                    ok, msg = db.update_resource(
                        db.DEFAULT_DB_PATH,
                        old_name=sel_res_name,
                        new_name=new_r_name,
                        capacity=new_r_cap,
                        unit=new_r_unit,
                        description=new_r_desc
                    )
                    if ok:
                        st.success(msg)
                        st.rerun()
                    else:
                        st.error(msg)
        else:
            st.info("No resources found.")

    with tab_r_del:
        st.markdown("##### Remove Resource Type")
        resources = db.get_resources()
        if resources:
            r_del_name = st.selectbox("Select Resource to Remove", [r["name"] for r in resources], key="del_res_sel")
            st.caption("Note: You cannot delete a resource if any active or disabled academic activity depends on it.")
            if st.button("🗑️ Delete Resource", use_container_width=True, type="secondary"):
                ok, msg = db.delete_resource(db.DEFAULT_DB_PATH, r_del_name)
                if ok:
                    st.success(msg)
                    st.rerun()
                else:
                    st.error(msg)


# =============================================================================
# MODULE 4: GENETIC ALGORITHM OPTIMIZATION
# =============================================================================
elif selected_module == "🧬 GA Optimizer":
    st.subheader("Genetic Algorithm Optimization Engine")
    st.markdown("Configure Evolutionary parameters and execute the Genetic Algorithm to synthesize an optimal allocation plan.")

    resources = db.get_resources()
    activities = db.get_activities(only_active=True)

    if not activities:
        st.warning("⚠️ There are no active academic activities enabled. Please enable or add activities in 'Activity Management'.")
        st.stop()

    if not resources:
        st.warning("⚠️ No campus resources found. Please add resources in 'Resource Management'.")
        st.stop()

    # Layout: Controls in Left Column, Preview/Stats in Right Column
    col_ctrl, col_prev = st.columns([1, 1], gap="large")

    with col_ctrl:
        st.markdown("#### ⚙️ Algorithm Hyperparameters")

        with st.container():
            col_p1, col_p2 = st.columns(2)
            with col_p1:
                pop_size = st.slider("Population Size (N)", min_value=20, max_value=300, value=60, step=10,
                                     help="Number of candidate allocation plans maintained per generation.")
                generations = st.slider("Generations (G)", min_value=10, max_value=200, value=50, step=5,
                                        help="Total evolution iterations before termination.")
                crossover_rate = st.slider("Crossover Probability (Pc)", min_value=0.10, max_value=1.00, value=0.85, step=0.05,
                                           help="Probability of gene recombination between two tournament winners.")
            with col_p2:
                mutation_rate = st.slider("Mutation Probability (Pm)", min_value=0.01, max_value=0.50, value=0.10, step=0.01,
                                          help="Probability of gene-level variation to discover new search regions.")
                tournament_size = st.slider("Tournament Size (k)", min_value=2, max_value=7, value=3, step=1,
                                            help="Number of candidates sampled for tournament selection.")
                elitism_count = st.slider("Elitism Count", min_value=1, max_value=5, value=2, step=1,
                                          help="Number of strictly best chromosomes preserved unchanged into the next generation.")

        st.markdown("#### 💰 Campus Financial Constraint")
        # Estimate recommended default budget
        total_potential_cost = sum(a["demand"] * a["cost_per_unit"] for a in activities)
        default_budget = round(total_potential_cost * 0.75, 2)
        budget_limit = st.number_input(
            "Total Maximum Operating Budget ($)",
            min_value=100.0,
            max_value=100000.0,
            value=float(default_budget),
            step=250.0,
            help="Enforces that sum(allocated * unit_cost) <= budget."
        )

        st.markdown("#### 🎲 Reproducibility")
        use_seed = st.checkbox("Set Fixed Random Seed (Deterministic Reproducibility)", value=True)
        if use_seed:
            random_seed = st.number_input("Random Seed Value", min_value=0, max_value=999999, value=42, step=1)
        else:
            random_seed = None

        st.markdown("<br>", unsafe_allow_html=True)
        run_btn = st.button("🚀 Execute Genetic Algorithm Optimization", type="primary", use_container_width=True)

    with col_prev:
        st.markdown("#### 📋 Problem Space Under Optimization")
        st.info(f"**{len(activities)} Active Activities** competing across **{len(resources)} Resource Types**.")

        # Demands by resource
        res_caps = {r["name"]: r["capacity"] for r in resources}
        summary_rows = []
        for r_name, cap in res_caps.items():
            req_demand = sum(a["demand"] for a in activities if a["resource_type"] == r_name)
            summary_rows.append({
                "Resource": r_name,
                "Capacity": cap,
                "Total Requested": req_demand,
                "Status": "Exceeded (Competition)" if req_demand > cap else "Sufficient"
            })
        st.dataframe(pd.DataFrame(summary_rows), use_container_width=True, hide_index=True)

        st.markdown("##### Activities Queue:")
        act_summary = [
            {"Activity": a["name"], "Resource": a["resource_type"], "Demand": a["demand"], "Priority": a["priority"], "Unit Cost": f"${a['cost_per_unit']:.2f}"}
            for a in activities
        ]
        st.dataframe(pd.DataFrame(act_summary), use_container_width=True, hide_index=True)

    # Execution Action
    if run_btn:
        progress_bar = st.progress(0, text="Initializing Evolutionary Population...")
        status_box = st.empty()

        # Step 1: Initialize optimizer
        optimizer = GeneticAlgorithmOptimizer(
            activities=activities,
            resource_capacities=res_caps,
            budget_limit=budget_limit,
            population_size=pop_size,
            generations=generations,
            crossover_rate=crossover_rate,
            mutation_rate=mutation_rate,
            tournament_size=tournament_size,
            elitism_count=elitism_count,
            random_seed=random_seed
        )

        time.sleep(0.2)
        progress_bar.progress(35, text="Executing Genetic Algorithm: Selection, Crossover, Mutation & Elitism...")

        # Step 2: Run optimization
        result = optimizer.optimize()

        progress_bar.progress(85, text="Enforcing multi-resource constraints & persisting results to SQLite...")

        # Step 3: Save to SQLite
        metadata = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "population_size": pop_size,
            "generations": generations,
            "mutation_rate": mutation_rate,
            "crossover_rate": crossover_rate,
            "budget_limit": budget_limit,
            "random_seed": random_seed,
            "best_fitness": result["best_fitness"],
            "total_demand": result["total_demand"],
            "total_allocated": result["total_allocated"],
            "demand_satisfaction_pct": result["demand_satisfaction_pct"],
            "budget_spent": result["budget_spent"],
            "budget_utilization_pct": result["budget_utilization_pct"],
            "resource_utilization_pct": result["overall_resource_utilization_pct"],
            "execution_time_sec": result["execution_time_sec"]
        }

        run_id = db.save_optimization_run(
            db_path=db.DEFAULT_DB_PATH,
            metadata=metadata,
            allocations=result["allocations"],
            convergence_history=result["convergence_history"]
        )
        result["run_id"] = run_id

        # Save to session state
        st.session_state.latest_result = result

        progress_bar.progress(100, text="Optimization Complete!")
        time.sleep(0.3)
        progress_bar.empty()

        st.toast(f"Optimization run #{run_id} completed successfully in {result['execution_time_sec']:.3f}s!", icon="🎉")
        st.success(f"✅ Optimization run completed! Best Fitness Score: **{result['best_fitness']}** | Demand Satisfied: **{result['demand_satisfaction_pct']}%**")

        st.info("👉 Switch to **📈 Results & Analytics** in the sidebar to inspect interactive charts and download CSV reports!")


# =============================================================================
# MODULE 5: RESULTS AND ANALYTICS
# =============================================================================
elif selected_module == "📈 Results & Analytics":
    st.subheader("Optimization Results & Evolutionary Analytics")
    st.markdown("Detailed breakdown of chromosome allocations, constraint adherence, convergence dynamics, and financial utilization.")

    res = st.session_state.latest_result

    # If no run in session state, look up latest from DB
    if res is None:
        runs = db.get_optimization_runs(limit=1)
        if runs:
            latest_id = runs[0]["id"]
            db_run = db.get_run_details(db.DEFAULT_DB_PATH, latest_id)
            if db_run:
                # Reconstruct result structure
                res = {
                    "run_id": db_run["id"],
                    "best_fitness": db_run["best_fitness"],
                    "total_demand": db_run["total_demand"],
                    "total_allocated": db_run["total_allocated"],
                    "total_unmet": db_run["total_demand"] - db_run["total_allocated"],
                    "demand_satisfaction_pct": db_run["demand_satisfaction_pct"],
                    "budget_limit": db_run["budget_limit"],
                    "budget_spent": db_run["budget_spent"],
                    "remaining_budget": round(db_run["budget_limit"] - db_run["budget_spent"], 2),
                    "budget_utilization_pct": db_run["budget_utilization_pct"],
                    "overall_resource_utilization_pct": db_run["resource_utilization_pct"],
                    "allocations": [
                        {
                            "name": a["activity_name"],
                            "resource_type": a["resource_type"],
                            "priority": a["priority"],
                            "demand": a["demand"],
                            "allocated": a["allocated"],
                            "unmet": a["unmet"],
                            "satisfaction_pct": a["satisfaction_pct"],
                            "cost_per_unit": a["cost_per_unit"],
                            "total_cost": a["total_cost"],
                            "status": "Full" if a["unmet"] == 0 else ("Partial" if a["allocated"] > 0 else "Unmet")
                        }
                        for a in db_run["allocations"]
                    ],
                    "convergence_history": db_run["convergence_history"],
                    "execution_time_sec": db_run["execution_time_sec"],
                    "algorithm_parameters": {
                        "population_size": db_run["population_size"],
                        "generations": db_run["generations"],
                        "mutation_rate": db_run["mutation_rate"],
                        "crossover_rate": db_run["crossover_rate"],
                        "random_seed": db_run["random_seed"]
                    }
                }

    if res is None:
        st.warning("No optimization results available yet. Please execute an optimization run from **🧬 GA Optimizer**.")
        st.stop()

    run_title = f"Run #{res.get('run_id', 'Active')}"
    st.markdown(f"#### 🏆 Optimal Solution Summary ({run_title})")

    # KPI Summary Cards
    m1, m2, m3, m4, m5, m6 = st.columns(6)
    m1.metric("Best Fitness", f"{res['best_fitness']}")
    m2.metric("Demand Satisfied", f"{res['demand_satisfaction_pct']}%", f"{res['total_allocated']} / {res['total_demand']} units")
    m3.metric("Unmet Demand", f"{res['total_unmet']} units", delta=f"-{res['total_unmet']}", delta_color="inverse")
    m4.metric("Resource Util.", f"{res['overall_resource_utilization_pct']}%", "Physical capacity")
    m5.metric("Budget Spent", f"${res['budget_spent']:,.2f}", f"of ${res['budget_limit']:,.2f} ({res['budget_utilization_pct']}%)")
    m6.metric("Execution Time", f"{res['execution_time_sec']:.3f}s", f"{len(res['convergence_history'])} generations")

    st.markdown("---")

    # Interactive Plots Section
    tab_chart1, tab_chart2, tab_chart3, tab_chart4 = st.tabs([
        "📈 Fitness Convergence",
        "📊 Demand vs Allocation",
        "🏛️ Resource Utilization",
        "💰 Budget & Priority Analysis"
    ])

    with tab_chart1:
        st.markdown("##### Evolutionary Fitness Convergence Trajectory")
        conv = res.get("convergence_history", [])
        if conv:
            df_conv = pd.DataFrame(conv)
            fig_conv = go.Figure()

            # Best fitness line
            fig_conv.add_trace(go.Scatter(
                x=df_conv["generation"],
                y=df_conv["best_fitness"],
                mode="lines+markers",
                name="Best Fitness",
                line=dict(color="#3B82F6", width=3),
                marker=dict(size=6, color="#60A5FA")
            ))

            # Average fitness line
            if "avg_fitness" in df_conv.columns:
                fig_conv.add_trace(go.Scatter(
                    x=df_conv["generation"],
                    y=df_conv["avg_fitness"],
                    mode="lines",
                    name="Population Mean Fitness",
                    line=dict(color="#A78BFA", width=2, dash="dash")
                ))

            # Min fitness
            if "min_fitness" in df_conv.columns:
                fig_conv.add_trace(go.Scatter(
                    x=df_conv["generation"],
                    y=df_conv["min_fitness"],
                    mode="lines",
                    name="Population Min Fitness",
                    line=dict(color="#64748B", width=1.5, dash="dot")
                ))

            fig_conv.update_layout(
                title="Evolutionary Convergence Curve across Generations",
                xaxis_title="Generation (Iteration)",
                yaxis_title="Fitness Score",
                hovermode="x unified",
                height=380
            )
            st.plotly_chart(apply_plotly_theme(fig_conv), use_container_width=True)
            st.caption("Notice how fitness ascends rapidly in early generations via tournament selection and elitism, stabilizing at the optimal feasible plateau.")
        else:
            st.info("No convergence history logged for this run.")

    with tab_chart2:
        st.markdown("##### Requested Demand vs. Optimized Allocation by Activity")
        alloc_data = res["allocations"]
        df_alloc = pd.DataFrame(alloc_data)

        if not df_alloc.empty:
            fig_alloc = go.Figure()
            fig_alloc.add_trace(go.Bar(
                x=df_alloc["name"],
                y=df_alloc["demand"],
                name="Requested Demand",
                marker_color="rgba(148, 163, 184, 0.4)",
                bordercolor="rgba(148, 163, 184, 0.8)"
            ))
            fig_alloc.add_trace(go.Bar(
                x=df_alloc["name"],
                y=df_alloc["allocated"],
                name="Optimized Allocation",
                marker_color="#3B82F6"
            ))
            fig_alloc.update_layout(
                barmode="group",
                title="Activity Demand Fulfillment Comparison",
                xaxis_title="Academic Activity",
                yaxis_title="Resource Units",
                height=380
            )
            st.plotly_chart(apply_plotly_theme(fig_alloc), use_container_width=True)
        else:
            st.info("No allocation data.")

    with tab_chart3:
        st.markdown("##### Resource Capacity and Physical Campus Utilization")
        resources = db.get_resources()
        res_caps = {r["name"]: r["capacity"] for r in resources}
        res_usage = {}
        for a in res["allocations"]:
            rt = a["resource_type"]
            res_usage[rt] = res_usage.get(rt, 0) + a["allocated"]

        res_plot_rows = []
        for r_name, cap in res_caps.items():
            used = res_usage.get(r_name, 0)
            res_plot_rows.append({
                "Resource": r_name,
                "Allocated (Used)": used,
                "Unused Capacity": max(0, cap - used),
                "Total Capacity": cap,
                "Utilization %": round((used / cap * 100.0) if cap > 0 else 0.0, 1)
            })
        df_res_plot = pd.DataFrame(res_plot_rows)

        col_g1, col_g2 = st.columns([3, 2])
        with col_g1:
            fig_res = px.bar(
                df_res_plot,
                x="Resource",
                y=["Allocated (Used)", "Unused Capacity"],
                barmode="stack",
                color_discrete_map={
                    "Allocated (Used)": "#10B981",
                    "Unused Capacity": "#334155"
                },
                title="Physical Resource Allocation Breakdown"
            )
            fig_res.update_layout(height=360)
            st.plotly_chart(apply_plotly_theme(fig_res), use_container_width=True)

        with col_g2:
            st.markdown("###### Utilization Summary:")
            for row in res_plot_rows:
                pct = row["Utilization %"]
                st.write(f"**{row['Resource']}**: {row['Allocated (Used)']}/{row['Total Capacity']} ({pct}%)")
                st.progress(min(1.0, pct / 100.0))

    with tab_chart4:
        st.markdown("##### Financial Spending & Priority Alignment")
        col_b1, col_b2 = st.columns(2)

        with col_b1:
            # Budget breakdown by activity
            df_cost = pd.DataFrame(res["allocations"])
            df_cost_nonzero = df_cost[df_cost["total_cost"] > 0]
            if not df_cost_nonzero.empty:
                fig_donut = px.pie(
                    df_cost_nonzero,
                    names="name",
                    values="total_cost",
                    hole=0.55,
                    title=f"Cost Distribution (Total: ${res['budget_spent']:,.2f})"
                )
                fig_donut.update_layout(height=340)
                st.plotly_chart(apply_plotly_theme(fig_donut), use_container_width=True)
            else:
                st.info("No cost incurred.")

        with col_b2:
            # Priority Satisfaction breakdown
            prio_summary = []
            for prio in range(1, 6):
                p_acts = [a for a in res["allocations"] if a["priority"] == prio]
                if p_acts:
                    p_dem = sum(a["demand"] for a in p_acts)
                    p_alloc = sum(a["allocated"] for a in p_acts)
                    p_pct = round((p_alloc / p_dem * 100.0) if p_dem > 0 else 0.0, 1)
                    prio_summary.append({
                        "Priority Level": f"Priority {prio}",
                        "Fulfillment %": p_pct
                    })
            if prio_summary:
                df_p_sat = pd.DataFrame(prio_summary)
                fig_p_sat = px.bar(
                    df_p_sat,
                    x="Priority Level",
                    y="Fulfillment %",
                    color="Fulfillment %",
                    color_continuous_scale="Viridis",
                    title="Demand Satisfaction Rate by Priority Level"
                )
                fig_p_sat.update_layout(height=340, yaxis_range=[0, 105])
                st.plotly_chart(apply_plotly_theme(fig_p_sat), use_container_width=True)

    # Detailed Table & CSV Download
    st.markdown("---")
    st.markdown("##### 📋 Complete Activity Allocation Manifest")
    df_manifest = pd.DataFrame(res["allocations"])
    st.dataframe(df_manifest, use_container_width=True, hide_index=True)

    # Downloadable CSVs
    c_d1, c_d2 = st.columns(2)
    with c_d1:
        csv_alloc = df_manifest.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Download Allocation Plan (CSV)",
            data=csv_alloc,
            file_name=f"evonex_campus_allocation_run_{res.get('run_id', 'latest')}.csv",
            mime="text/csv",
            use_container_width=True
        )
    with c_d2:
        meta_summary = {
            "Run ID": res.get("run_id"),
            "Fitness Score": res["best_fitness"],
            "Total Demand": res["total_demand"],
            "Total Allocated": res["total_allocated"],
            "Demand Satisfaction %": res["demand_satisfaction_pct"],
            "Budget Limit": res["budget_limit"],
            "Budget Spent": res["budget_spent"],
            "Resource Utilization %": res["overall_resource_utilization_pct"],
            "Execution Time (s)": res["execution_time_sec"]
        }
        df_meta = pd.DataFrame([meta_summary])
        csv_meta = df_meta.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Download Optimization Summary (CSV)",
            data=csv_meta,
            file_name=f"evonex_optimization_summary_{res.get('run_id', 'latest')}.csv",
            mime="text/csv",
            use_container_width=True
        )


# =============================================================================
# MODULE 6: OPTIMIZATION HISTORY
# =============================================================================
elif selected_module == "📜 Optimization History":
    st.subheader("Historical Optimization Ledger")
    st.markdown("Review audit trails of previous genetic algorithm iterations, compare convergence rates, and load historical runs.")

    runs = db.get_optimization_runs(limit=100)

    if not runs:
        st.info("No historical optimization records found. Run an optimization from 'GA Optimizer' to build your audit log.")
    else:
        df_runs = pd.DataFrame(runs)

        # Overview Table
        display_cols = [
            "id", "timestamp", "population_size", "generations", "mutation_rate",
            "crossover_rate", "best_fitness", "total_demand", "total_allocated",
            "demand_satisfaction_pct", "budget_spent", "resource_utilization_pct",
            "execution_time_sec"
        ]
        df_display = df_runs[display_cols].rename(columns={
            "id": "Run ID",
            "timestamp": "Timestamp",
            "population_size": "Pop Size",
            "generations": "Gens",
            "mutation_rate": "Pm",
            "crossover_rate": "Pc",
            "best_fitness": "Best Fitness",
            "total_demand": "Demand",
            "total_allocated": "Allocated",
            "demand_satisfaction_pct": "Demand Sat %",
            "budget_spent": "Budget ($)",
            "resource_utilization_pct": "Res Util %",
            "execution_time_sec": "Time (s)"
        })
        st.dataframe(df_display, use_container_width=True, hide_index=True)

        # Download History CSV
        csv_history = df_display.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Export Complete Run History to CSV",
            data=csv_history,
            file_name="evonex_optimization_history.csv",
            mime="text/csv"
        )

        st.markdown("---")
        st.markdown("#### 🔍 Inspect Historical Run Detail")

        run_options = {f"Run #{r['id']} - {r['timestamp']} (Fitness: {r['best_fitness']})": r["id"] for r in runs}
        selected_run_label = st.selectbox("Select Run to Inspect:", list(run_options.keys()))
        inspected_id = run_options[selected_run_label]

        run_detail = db.get_run_details(db.DEFAULT_DB_PATH, inspected_id)
        if run_detail:
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Run ID", f"#{run_detail['id']}")
            c2.metric("Fitness Score", f"{run_detail['best_fitness']}")
            c3.metric("Demand Fulfillment", f"{run_detail['demand_satisfaction_pct']}%")
            c4.metric("Resource Util.", f"{run_detail['resource_utilization_pct']}%")

            # Allocations table for this run
            allocs = run_detail.get("allocations", [])
            if allocs:
                st.markdown("##### Detailed Allocations for this Run:")
                st.dataframe(pd.DataFrame(allocs), use_container_width=True, hide_index=True)

            # Convergence plot if available
            conv = run_detail.get("convergence_history", [])
            if conv:
                df_c = pd.DataFrame(conv)
                fig_h = px.line(df_c, x="generation", y="best_fitness", title=f"Convergence Trajectory for Run #{inspected_id}")
                st.plotly_chart(apply_plotly_theme(fig_h), use_container_width=True)


# =============================================================================
# MODULE 7: ACADEMIC PROJECT DOCUMENTATION
# =============================================================================
elif selected_module == "📖 Academic Project Docs":
    st.subheader("Academic Project Documentation")
    st.markdown("Comprehensive technical specification for the Evolutionary Computing (EC) coursework project.")

    st.markdown(r"""
    ### 1. Abstract
    The **Smart Campus Resource Optimizer** applies Evolutionary Computing principles to address the Non-deterministic Polynomial-time hard (NP-hard) multi-resource allocation problem faced by modern universities. With physical teaching laboratories, tiered classrooms, and specialized hardware equipment constrained by strict capacity and monetary budgets, naive manual or greedy heuristic scheduling frequently fails to satisfy critical academic needs. 

    By employing a custom-engineered Genetic Algorithm (GA) featuring priority-weighted fitness scaling, tournament selection, single-point crossover, gene-level mutation, and strict repair operators, the system converges toward global Pareto-efficient resource assignments. Developed by **Team EvoNex**, the application provides administrators with real-time visual telemetry, historical audit ledgers, and mathematically rigorous allocations.

    ---

    ### 2. Mathematical Formulation

    #### 2.1 Optimization Objective
    Let $N$ denote the set of active academic activities $\{A_1, A_2, \dots, A_N\}$, and let $M$ denote the campus resource types $\{R_1, R_2, \dots, R_M\}$.
    Each activity $A_i$ is characterized by:
    - Requested demand: $D_i \in \mathbb{Z}^+$
    - Priority tier: $P_i \in \{1, 2, 3, 4, 5\}$
    - Associated resource type: $T_i \in \{R_1, \dots, R_M\}$
    - Cost per unit allocated: $C_i \ge 0$

    A candidate chromosome is represented as an integer vector:
    $$\mathbf{X} = [x_1, x_2, \dots, x_N], \quad \text{where } x_i \in \{0, 1, \dots, D_i\}$$

    #### 2.2 Objective Fitness Function
    The objective function maximizes priority-weighted demand fulfillment while incentivizing efficient capacity utilization:

    $$\text{Maximize } \mathcal{F}(\mathbf{X}) = \left( \frac{\sum_{i=1}^{N} w(P_i) \cdot \frac{x_i}{D_i}}{\sum_{i=1}^{N} w(P_i)} \times 100 \right) + 5 \cdot \left( \frac{\sum_{i=1}^{N} x_i}{\sum_{j=1}^{M} \text{Cap}(R_j)} \right)$$

    Where priority weights $w(P_i)$ are exponentially scaled:
    $$w(1) = 1.0, \quad w(2) = 2.0, \quad w(3) = 4.0, \quad w(4) = 7.0, \quad w(5) = 11.0$$

    #### 2.3 Strict Feasibility Constraints
    1. **Demand Bounds**:
       $$0 \le x_i \le D_i, \quad \forall i \in \{1, \dots, N\}$$
    2. **Resource Capacity Constraints**:
       $$\sum_{i : T_i = R_j} x_i \le \text{Capacity}(R_j), \quad \forall j \in \{1, \dots, M\}$$
    3. **Total Budget Constraint**:
       $$\sum_{i=1}^{N} x_i \cdot C_i \le \text{Budget}_{\text{max}}$$

    ---

    ### 3. Evolutionary Computing Flowchart & Pseudocode

    ```mermaid
    graph TD
        A([Start: Initialize Database & Problem Space]) --> B[Create Initial Population: Diverse & Heuristic Seeds]
        B --> C[Evaluate Fitness of Population]
        C --> D{Termination Met? Max Generations?}
        D -- Yes --> E[Extract Best Chromosome & Return Optimal Plan]
        D -- No --> F[Elitism: Retain Top k Chromosomes]
        F --> G[Tournament Selection: Sample k candidates]
        G --> H[Single-Point Crossover: Prob Pc]
        H --> I[Gene Mutation: Prob Pm]
        I --> J[Deterministic Feasibility Repair: Capacity & Budget]
        J --> K[Form Next Generation Population]
        K --> C
        E --> L([End: Display Plots & Persist to SQLite])
    ```

    #### Pseudocode
    ```python
    Algorithm: Genetic_Algorithm_Resource_Optimizer
    Input: Activities A, Capacities Cap, Budget B, PopSize, Generations, Pc, Pm
    Output: Best Feasible Allocation Vector X*

    1. Initialize Population P with heuristic candidates (Greedy, Proportional, Random)
    2. For each individual in P:
         individual = Repair_Chromosome(individual, Cap, B)
         fitness = Calculate_Fitness(individual)
    3. For g = 1 to Generations do:
         P_next = []
         P_next.append(Top_Elites(P, count=ElitismCount))
         While length(P_next) < PopSize do:
             Parent1 = Tournament_Select(P, k=3)
             Parent2 = Tournament_Select(P, k=3)
             Child1, Child2 = Single_Point_Crossover(Parent1, Parent2, Pc)
             Child1 = Mutate(Child1, Pm)
             Child2 = Mutate(Child2, Pm)
             Child1 = Repair_Chromosome(Child1, Cap, B)
             Child2 = Repair_Chromosome(Child2, Cap, B)
             P_next.append(Child1, Child2)
         P = P_next
    4. Return argmax(Calculate_Fitness(ind) for ind in P)
    ```

    ---

    ### 4. System Architecture
    - **Frontend Layer**: Streamlit reactive web framework with dynamic Plotly visualizations.
    - **Optimization Engine**: Pure Python & NumPy Genetic Algorithm implemented from scratch (no closed-source or black-box solvers).
    - **Persistence Layer**: ACID-compliant SQLite relational database with foreign key constraints, migration handling, and indexed audit logs.
    - **Deployment Target**: Streamlit Community Cloud & Local Cross-Platform execution.

    ---

    ### 5. Team EvoNex Credits & Citation
    - **Project**: Smart Campus Resource Optimizer
    - **Team**: EvoNex
    - **Tagline**: *“Evolving Intelligence, Optimizing Tomorrow.”*
    - **References**:
      1. Goldberg, D. E. (1989). *Genetic Algorithms in Search, Optimization, and Machine Learning*. Addison-Wesley.
      2. Deb, K. (2001). *Multi-Objective Optimization using Evolutionary Algorithms*. John Wiley & Sons.
      3. Eiben, A. E., & Smith, J. E. (2015). *Introduction to Evolutionary Computing*. Springer.
    """)
