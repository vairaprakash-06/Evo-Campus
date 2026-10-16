/**
 * Smart Campus Resource Optimizer — Team EvoCampus
 * Client-Side JavaScript Application Logic & Chart.js Controllers
 */

document.addEventListener("DOMContentLoaded", function () {
  // -------------------------------------------------------------------------
  // Modal Utilities
  // -------------------------------------------------------------------------
  window.openModal = function (modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
      modal.classList.add("active");
      document.body.style.overflow = "hidden";
    }
  };

  window.closeModal = function (modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
      modal.classList.remove("active");
      document.body.style.overflow = "auto";
    }
  };

  // Close modals on clicking backdrop
  document.querySelectorAll(".modal-overlay").forEach((overlay) => {
    overlay.addEventListener("click", function (e) {
      if (e.target === this) {
        this.classList.remove("active");
        document.body.style.overflow = "auto";
      }
    });
  });

  // Close modals on Escape key
  document.addEventListener("keydown", function (e) {
    if (e.key === "Escape") {
      document.querySelectorAll(".modal-overlay.active").forEach((m) => {
        m.classList.remove("active");
      });
      document.body.style.overflow = "auto";
    }
  });

  // -------------------------------------------------------------------------
  // Delete Confirmation Helper
  // -------------------------------------------------------------------------
  window.confirmDelete = function (message) {
    return confirm(message || "Are you sure you want to delete this record? This action cannot be undone.");
  };

  // -------------------------------------------------------------------------
  // Table Filtering (Activities Table)
  // -------------------------------------------------------------------------
  const searchInput = document.getElementById("activitySearchInput");
  const deptFilter = document.getElementById("activityDeptFilter");
  const priorityFilter = document.getElementById("activityPriorityFilter");
  const activitiesTable = document.getElementById("activitiesTable");

  function filterActivitiesTable() {
    if (!activitiesTable) return;
    const searchVal = (searchInput ? searchInput.value : "").toLowerCase().trim();
    const deptVal = (deptFilter ? deptFilter.value : "").toLowerCase().trim();
    const priorityVal = (priorityFilter ? priorityFilter.value : "").trim();

    const rows = activitiesTable.querySelectorAll("tbody tr");
    rows.forEach((row) => {
      const name = (row.getAttribute("data-name") || "").toLowerCase();
      const dept = (row.getAttribute("data-department") || "").toLowerCase();
      const priority = (row.getAttribute("data-priority") || "").trim();

      const matchSearch = !searchVal || name.includes(searchVal) || dept.includes(searchVal);
      const matchDept = !deptVal || dept === deptVal;
      const matchPriority = !priorityVal || priority === priorityVal;

      if (matchSearch && matchDept && matchPriority) {
        row.style.display = "";
      } else {
        row.style.display = "none";
      }
    });
  }

  if (searchInput) searchInput.addEventListener("input", filterActivitiesTable);
  if (deptFilter) deptFilter.addEventListener("change", filterActivitiesTable);
  if (priorityFilter) priorityFilter.addEventListener("change", filterActivitiesTable);

  // -------------------------------------------------------------------------
  // Table Filtering (Resources Table)
  // -------------------------------------------------------------------------
  const resSearchInput = document.getElementById("resourceSearchInput");
  const resTypeFilter = document.getElementById("resourceTypeFilter");
  const resAvailFilter = document.getElementById("resourceAvailFilter");
  const resourcesTable = document.getElementById("resourcesTable");

  function filterResourcesTable() {
    if (!resourcesTable) return;
    const searchVal = (resSearchInput ? resSearchInput.value : "").toLowerCase().trim();
    const typeVal = (resTypeFilter ? resTypeFilter.value : "").toLowerCase().trim();
    const availVal = (resAvailFilter ? resAvailFilter.value : "").toLowerCase().trim();

    const rows = resourcesTable.querySelectorAll("tbody tr");
    rows.forEach((row) => {
      const name = (row.getAttribute("data-name") || "").toLowerCase();
      const type = (row.getAttribute("data-type") || "").toLowerCase();
      const avail = (row.getAttribute("data-availability") || "").toLowerCase();

      const matchSearch = !searchVal || name.includes(searchVal) || type.includes(searchVal);
      const matchType = !typeVal || type === typeVal;
      const matchAvail = !availVal || avail === availVal;

      if (matchSearch && matchType && matchAvail) {
        row.style.display = "";
      } else {
        row.style.display = "none";
      }
    });
  }

  if (resSearchInput) resSearchInput.addEventListener("input", filterResourcesTable);
  if (resTypeFilter) resTypeFilter.addEventListener("change", filterResourcesTable);
  if (resAvailFilter) resAvailFilter.addEventListener("change", filterResourcesTable);

  // -------------------------------------------------------------------------
  // Optimization Runner with Animated Telemetry UI
  // -------------------------------------------------------------------------
  const gaRunForm = document.getElementById("gaRunForm");
  const gaRunBtn = document.getElementById("gaRunBtn");
  const gaProgressContainer = document.getElementById("gaProgressContainer");
  const gaProgressBar = document.getElementById("gaProgressBar");
  const gaStatusText = document.getElementById("gaStatusText");

  if (gaRunForm) {
    gaRunForm.addEventListener("submit", function (e) {
      e.preventDefault();

      if (gaRunBtn) {
        gaRunBtn.disabled = true;
        gaRunBtn.innerHTML = `
          <span style="display:inline-block; width:16px; height:16px; border:2px solid #fff; border-top-color:transparent; border-radius:50%; animation:spin 0.7s linear infinite;"></span>
          Evolving Population...
        `;
      }

      if (gaProgressContainer) gaProgressContainer.style.display = "block";
      if (gaProgressBar) gaProgressBar.style.width = "15%";
      if (gaStatusText) gaStatusText.textContent = "Initializing heuristic seed chromosome and problem space...";

      const formData = new FormData(gaRunForm);
      const payload = {};
      formData.forEach((val, key) => { payload[key] = val; });

      // Simulate step progress for user feedback
      setTimeout(() => {
        if (gaProgressBar) gaProgressBar.style.width = "45%";
        if (gaStatusText) gaStatusText.textContent = "Running tournament selection & single-point crossover...";
      }, 300);

      setTimeout(() => {
        if (gaProgressBar) gaProgressBar.style.width = "75%";
        if (gaStatusText) gaStatusText.textContent = "Applying gene-wise mutation & deterministic feasibility repair...";
      }, 600);

      fetch("/optimize/run", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "X-Requested-With": "XMLHttpRequest"
        },
        body: JSON.stringify(payload)
      })
      .then((res) => {
        if (!res.ok) {
          return res.json().then((err) => { throw new Error(err.error || "Optimization failed."); });
        }
        return res.json();
      })
      .then((data) => {
        if (gaProgressBar) gaProgressBar.style.width = "100%";
        if (gaStatusText) gaStatusText.textContent = "Optimization complete! Redirecting to results dashboard...";
        setTimeout(() => {
          window.location.href = data.redirect_url;
        }, 400);
      })
      .catch((err) => {
        alert("Error executing Genetic Algorithm: " + err.message);
        if (gaRunBtn) {
          gaRunBtn.disabled = false;
          gaRunBtn.innerHTML = "🚀 Launch Genetic Algorithm Optimization";
        }
        if (gaProgressContainer) gaProgressContainer.style.display = "none";
      });
    });
  }

  // Inject spin keyframes if not present
  const styleEl = document.createElement("style");
  styleEl.innerHTML = `@keyframes spin { to { transform: rotate(360deg); } }`;
  document.head.appendChild(styleEl);
});
