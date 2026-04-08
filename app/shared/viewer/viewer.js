function workspaceParams() {
  return new URLSearchParams(window.location.search);
}

function readEmbeddedConfig() {
  const tag = document.getElementById("workspace-config");
  if (!tag) {
    return null;
  }
  return JSON.parse(tag.textContent);
}

function buildConfigFromQuery() {
  const params = workspaceParams();
  const docs = (params.get("docs") || "").split(",").map((item) => item.trim()).filter(Boolean);
  const labels = params.getAll("labels");
  return {
    siteTitle: params.get("title") || "Viewer",
    noteStorageKey: params.get("notesKey") || "mgd:notes:default",
    notePlaceholder: "Capture notes here.",
    groups: [
      {
        label: "Documents",
        heading: params.get("title") || "Documents",
        items: docs.map((doc, index) => ({
          id: `doc-${index + 1}`,
          label: labels[index] || decodeURIComponent(doc.split("/").pop()),
          description: "",
          href: doc,
          selected: index < 3
        }))
      }
    ]
  };
}

function workspaceConfig() {
  return readEmbeddedConfig() || buildConfigFromQuery();
}

function selectedItems(config) {
  return config.groups.flatMap((group) => group.items).filter((item) => item.selected);
}

function setViewerMode(mode) {
  const grid = document.getElementById("viewer-grid");
  grid.dataset.mode = mode;
  localStorage.setItem("mgd:last_view_mode", mode);
  document.querySelectorAll("[data-mode-button]").forEach((button) => {
    button.classList.toggle("is-active", button.dataset.modeButton === mode);
  });
}

function renderSidebar(config) {
  const root = document.getElementById("workspace-tree");
  root.innerHTML = config.groups.map((group) => `
    <section class="tree-group">
      <span class="tree-label">${group.label}</span>
      <div class="tree-heading">${group.heading}</div>
      <ul class="tree-items">
        ${group.items.map((item) => `
          <li class="tree-item">
            <input type="checkbox" id="${item.id}" data-doc-id="${item.id}" ${item.selected ? "checked" : ""}>
            <label for="${item.id}">
              <strong>${item.label}</strong>
              ${item.description ? `<span class="tree-item-meta">${item.description}</span>` : ""}
            </label>
          </li>
        `).join("")}
      </ul>
    </section>
  `).join("");
}

function renderDocuments(config) {
  const grid = document.getElementById("viewer-grid");
  const mode = grid.dataset.mode || "single";
  const limit = mode === "single" ? 1 : mode === "dual" ? 2 : 3;
  const items = selectedItems(config);
  const visible = items.slice(0, limit);

  document.getElementById("toolbar-status").textContent =
    items.length > limit
      ? `${items.length} documents selected. Showing the first ${limit}.`
      : `${items.length || 0} documents selected.`;

  grid.innerHTML = visible.map((item, index) => `
    <section class="viewer-panel">
      <div class="viewer-head">
        <strong>${item.label}</strong>
        <a class="button-link" href="${item.href}" target="_blank" rel="noreferrer">Open direct</a>
      </div>
      <div class="doc-frame">
        <iframe src="${item.href}" title="Document ${index + 1}" data-zoom="1"></iframe>
      </div>
    </section>
  `).join("");
}

function noteStorageKey(config) {
  return config.noteStorageKey || "mgd:notes:default";
}

function saveViewerNotes(config) {
  const key = noteStorageKey(config);
  const value = document.getElementById("notes-text").value;
  localStorage.setItem(key, value);
  document.getElementById("save-status").textContent = `Saved locally ${new Date().toLocaleString()}`;
}

function setZoom(delta) {
  document.querySelectorAll(".viewer-panel iframe").forEach((frame) => {
    const current = Number(frame.dataset.zoom || "1");
    const next = Math.max(0.6, Math.min(1.8, current + delta));
    frame.dataset.zoom = String(next);
    frame.style.transform = `scale(${next})`;
    frame.style.height = `${Math.round(66 / next)}vh`;
  });
}

function fitWidth() {
  document.querySelectorAll(".viewer-panel iframe").forEach((frame) => {
    frame.style.width = "100%";
    frame.style.height = "66vh";
  });
}

function fitPage() {
  document.querySelectorAll(".viewer-panel iframe").forEach((frame) => {
    frame.style.width = "100%";
    frame.style.height = "82vh";
  });
}

function findInCurrent() {
  const frame = document.querySelector(".viewer-panel iframe");
  const query = document.getElementById("viewer-find").value;
  try {
    if (frame && query) {
      frame.contentWindow.find(query);
    }
  } catch (error) {
    console.warn(error);
  }
}

function bootViewer() {
  const config = workspaceConfig();
  const title = document.getElementById("workspace-title");
  const subtitle = document.getElementById("workspace-subtitle");
  const notes = document.getElementById("notes-text");

  if (title && config.siteTitle) {
    title.textContent = config.siteTitle;
  }
  if (subtitle) {
    subtitle.textContent = config.siteSummary || "";
  }
  if (notes && config.notePlaceholder) {
    notes.placeholder = config.notePlaceholder;
  }

  renderSidebar(config);
  const initialMode = localStorage.getItem("mgd:last_view_mode") || "single";
  setViewerMode(initialMode);
  renderDocuments(config);

  document.querySelectorAll("[data-mode-button]").forEach((button) => {
    button.addEventListener("click", () => {
      setViewerMode(button.dataset.modeButton);
      renderDocuments(config);
    });
  });

  document.querySelectorAll("[data-doc-id]").forEach((checkbox) => {
    checkbox.addEventListener("change", () => {
      const docId = checkbox.dataset.docId;
      config.groups.forEach((group) => {
        group.items.forEach((item) => {
          if (item.id === docId) {
            item.selected = checkbox.checked;
          }
        });
      });
      renderDocuments(config);
    });
  });

  const key = noteStorageKey(config);
  notes.value = localStorage.getItem(key) || "";
  notes.addEventListener("input", () => saveViewerNotes(config));
  document.getElementById("insert-timestamp").addEventListener("click", () => {
    notes.setRangeText(`[${new Date().toLocaleTimeString()}] `, notes.selectionStart, notes.selectionEnd, "end");
    saveViewerNotes(config);
  });
  document.getElementById("copy-notes").addEventListener("click", async () => {
    await navigator.clipboard.writeText(notes.value);
  });
  document.getElementById("zoom-in").addEventListener("click", () => setZoom(0.1));
  document.getElementById("zoom-out").addEventListener("click", () => setZoom(-0.1));
  document.getElementById("zoom-reset").addEventListener("click", () => {
    document.querySelectorAll(".viewer-panel iframe").forEach((frame) => {
      frame.dataset.zoom = "1";
      frame.style.transform = "scale(1)";
      frame.style.height = "66vh";
    });
  });
  document.getElementById("fit-width").addEventListener("click", fitWidth);
  document.getElementById("fit-page").addEventListener("click", fitPage);
  document.getElementById("viewer-find-button").addEventListener("click", findInCurrent);
  document.getElementById("print-view").addEventListener("click", () => window.print());
}

window.addEventListener("DOMContentLoaded", bootViewer);
