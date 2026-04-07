(function () {
  function initTable(table) {
    const tableId = table.id;
    const pageSize = parseInt(table.dataset.pageSize || "10", 10);
    const tbody = table.querySelector("tbody");
    if (!tbody) return;
    const rows = Array.from(tbody.querySelectorAll("tr"));
    const searchInput = document.querySelector(`[data-table-search="${tableId}"]`);
    const pagination = document.querySelector(`[data-table-pagination="${tableId}"]`);
    let filtered = rows.slice();
    let page = 1;

    function render() {
      const start = (page - 1) * pageSize;
      const end = start + pageSize;
      rows.forEach(r => r.style.display = "none");
      filtered.slice(start, end).forEach(r => r.style.display = "");
      if (!pagination) return;
      pagination.innerHTML = "";
      const totalPages = Math.max(1, Math.ceil(filtered.length / pageSize));

      const prev = document.createElement("button");
      prev.type = "button";
      prev.textContent = "Anterior";
      prev.disabled = page <= 1;
      prev.onclick = () => { if (page > 1) { page--; render(); } };
      pagination.appendChild(prev);

      const info = document.createElement("span");
      info.textContent = `Página ${page} de ${totalPages}`;
      info.style.alignSelf = "center";
      pagination.appendChild(info);

      const next = document.createElement("button");
      next.type = "button";
      next.textContent = "Siguiente";
      next.disabled = page >= totalPages;
      next.onclick = () => { if (page < totalPages) { page++; render(); } };
      pagination.appendChild(next);
    }

    function applySearch() {
      const q = (searchInput?.value || "").toLowerCase().trim();
      filtered = rows.filter(r => r.innerText.toLowerCase().includes(q));
      page = 1;
      render();
    }

    if (searchInput) searchInput.addEventListener("input", applySearch);
    render();
  }

  function drawRolesChart() {
    const canvas = document.getElementById("rolesChart");
    if (!canvas) return;
    const ctx = canvas.getContext("2d");
    const labels = ["superadmin", "admin", "manager", "user"];
    const values = [
      parseInt(canvas.dataset.superadmin || "0", 10),
      parseInt(canvas.dataset.admin || "0", 10),
      parseInt(canvas.dataset.manager || "0", 10),
      parseInt(canvas.dataset.user || "0", 10),
    ];
    const colors = ["#111827", "#1f2937", "#334155", "#64748b"];
    const total = Math.max(...values, 1);
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    labels.forEach((label, i) => {
      const y = 25 + i * 35;
      const width = (values[i] / total) * 360;
      ctx.fillStyle = colors[i];
      ctx.fillRect(110, y, width, 18);
      ctx.fillStyle = "#0f172a";
      ctx.font = "14px Arial";
      ctx.fillText(label, 10, y + 14);
      ctx.fillText(String(values[i]), 480, y + 14);
    });
  }

  document.addEventListener("DOMContentLoaded", function () {
    document.querySelectorAll(".js-table").forEach(initTable);
    drawRolesChart();
  });
})();
