
const viewerState = {
  layout: "auto",
  panelSize: "medium",
  activeDocId: null,
  sidebarHidden: false,
};

function workspaceParams() { return new URLSearchParams(window.location.search); }
function viewerParam(name) { return workspaceParams().get(name); }

async function readDataConfig() {
  const path = viewerParam("workspaceJson") || document.body?.dataset.workspaceJson;
  if (!path) return null;
  const response = await fetch(path, { cache: "no-store" });
  if (!response.ok) throw new Error(`Workspace config failed: ${response.status}`);
  return response.json();
}

function buildConfigFromQuery() {
  const params = workspaceParams();
  const docs = (params.get("docs") || "").split(",").map((item) => item.trim()).filter(Boolean);
  return {
    siteTitle: params.get("title") || "Viewer",
    siteSummary: "",
    noteStorageKey: params.get("notesKey") || "mgd:notes:default",
    showNotes: true,
    tree: [{
      id: "query-documents",
      type: "folder",
      label: "Documents",
      open: true,
      children: docs.map((doc, index) => ({
        id: `doc-${index + 1}`,
        type: "file",
        label: decodeURIComponent(doc.split("/").pop()),
        href: doc,
        selected: true
      }))
    }]
  };
}
async function workspaceConfig() { return await readDataConfig() || buildConfigFromQuery(); }

function flattenFiles(nodes) {
  return nodes.flatMap((node) => node.type === "folder" ? flattenFiles(node.children || []) : [node]);
}
function selectedItems(config) { return flattenFiles(config.tree || []).filter((item) => item.selected && item.href && !item.disabled); }
function selectedCount(config) { return selectedItems(config).length; }
function countEnabledFiles(nodes) { return flattenFiles(nodes).filter((item) => item.href && !item.disabled).length; }
function findNode(nodes, id) {
  for (const node of nodes) {
    if (node.id === id) return node;
    if (node.type === "folder") {
      const child = findNode(node.children || [], id);
      if (child) return child;
    }
  }
  return null;
}
function normalizeLayout(layout, count) {
  if (layout === "rows") return "rows";
  if (layout === "auto") return "auto";
  const numeric = Number(layout);
  if (numeric >= 1 && numeric <= 5) return String(Math.min(numeric, Math.max(1, count)));
  return "auto";
}
function buildGridClass(count) {
  const layout = viewerState.layout === "auto"
    ? String(Math.min(5, Math.max(1, count)))
    : normalizeLayout(viewerState.layout, count);
  return layout;
}
function renderNode(node, depth = 0) {
  if (node.type === "folder") {
    const isOpen = node.open !== false;
    const children = (node.children || []).map((child) => renderNode(child, depth + 1)).join("");
    return `<li class="tree-node tree-folder-node">
      <button class="tree-folder-row" type="button" data-folder-id="${node.id}" aria-expanded="${isOpen ? "true" : "false"}" style="padding-left:${depth * 14}px">
        <span class="tree-folder-arrow">${isOpen ? "▾" : "▸"}</span>
        <span class="tree-folder-icon">□</span>
        <span class="tree-folder-name">${node.label}</span>
      </button>
      <ul class="tree-children" ${isOpen ? "" : "hidden"}>${children}</ul>
    </li>`;
  }
  return `<li class="tree-node tree-file-node">
    <label class="tree-file-row ${node.disabled ? "is-disabled" : ""}" style="padding-left:${depth * 14}px">
      <input type="checkbox" data-doc-id="${node.id}" ${node.selected ? "checked" : ""} ${node.disabled ? "disabled" : ""}>
      <span class="tree-file-icon">—</span>
      <span class="tree-file-text"><strong>${node.label}</strong>${node.description ? `<span class="tree-item-meta">${node.description}</span>` : ""}</span>
    </label>
  </li>`;
}
function renderSidebar(config) {
  const root = document.getElementById("workspace-tree");
  root.innerHTML = `<ul class="tree-root">${(config.tree || []).map((node) => renderNode(node)).join("")}</ul>`;
  document.querySelectorAll("[data-folder-id]").forEach((button) => {
    button.addEventListener("click", () => {
      const folder = findNode(config.tree || [], button.dataset.folderId);
      if (!folder) return;
      folder.open = folder.open === false;
      renderSidebar(config);
      bindFileToggles(config);
    });
  });
}
function updateToolbar(config) {
  const count = selectedCount(config);
  const totalEnabled = countEnabledFiles(config.tree || []);
  document.querySelectorAll("[data-layout-button]").forEach((button) => {
    const value = button.dataset.layoutButton;
    button.classList.toggle("is-active", value === viewerState.layout);
    if (value !== "auto" && value !== "rows") {
      button.hidden = totalEnabled < Number(value);
    } else if (value === "rows") {
      button.hidden = totalEnabled < 2;
    }
  });
  document.getElementById("size-small").classList.toggle("is-active", viewerState.panelSize === "small");
  document.getElementById("size-medium").classList.toggle("is-active", viewerState.panelSize === "medium");
  document.getElementById("size-large").classList.toggle("is-active", viewerState.panelSize === "large");
  const status = document.getElementById("toolbar-status");
  status.textContent = `${count} selected`;
}
function renderTabs(config, items) {
  const host = document.getElementById("viewer-tabs");
  host.innerHTML = items.map((item) => `
    <button class="viewer-tab ${item.id === viewerState.activeDocId ? "is-active" : ""}" type="button" data-doc-tab="${item.id}">
      ${item.label}
    </button>
  `).join("");
  host.querySelectorAll("[data-doc-tab]").forEach((button) => {
    button.addEventListener("click", () => {
      viewerState.activeDocId = button.dataset.docTab;
      const panel = document.querySelector(`.viewer-panel[data-doc-id="${viewerState.activeDocId}"]`);
      if (panel) {
        panel.scrollIntoView({ behavior: "smooth", block: "nearest", inline: "center" });
        setActivePanel(viewerState.activeDocId);
      }
    });
  });
}
function noteStorageKey(config) { return config.noteStorageKey || "mgd:notes:default"; }
function saveViewerNotes(config) {
  const key = noteStorageKey(config);
  const value = document.getElementById("notes-text").value;
  localStorage.setItem(key, value);
  document.getElementById("save-status").textContent = `Saved locally ${new Date().toLocaleString()}`;
}
function panelHeightPx() {
  if (viewerState.panelSize === "small") return 340;
  if (viewerState.panelSize === "large") return 740;
  return 520;
}
function setActivePanel(docId) {
  viewerState.activeDocId = docId;
  document.querySelectorAll(".viewer-panel").forEach((panel) => {
    panel.classList.toggle("is-active", panel.dataset.docId === docId);
  });
  document.querySelectorAll(".viewer-tab").forEach((tab) => {
    tab.classList.toggle("is-active", tab.dataset.docTab === docId);
  });
}
function renderDocuments(config) {
  const items = selectedItems(config);
  if (!items.length) return;
  if (!viewerState.activeDocId || !items.some((item) => item.id === viewerState.activeDocId)) viewerState.activeDocId = items[0].id;
  updateToolbar(config);
  renderTabs(config, items);
  const grid = document.getElementById("viewer-grid");
  grid.dataset.layout = buildGridClass(items.length);
  grid.dataset.size = viewerState.panelSize;
  grid.innerHTML = items.map((item) => `
    <section class="viewer-panel ${item.id === viewerState.activeDocId ? "is-active" : ""}" data-doc-id="${item.id}">
      <div class="viewer-head">
        <strong>${item.label}</strong>
        <a class="button-link" href="${item.href}" target="_blank" rel="noreferrer">Open direct</a>
      </div>
      <div class="doc-frame" style="height:${panelHeightPx()}px">
        <iframe src="${item.href}" title="${item.label}"></iframe>
      </div>
    </section>
  `).join("");
  document.querySelectorAll(".viewer-panel").forEach((panel) => {
    panel.addEventListener("click", () => setActivePanel(panel.dataset.docId));
  });
}
function bindFileToggles(config) {
  document.querySelectorAll("[data-doc-id]").forEach((checkbox) => {
    checkbox.addEventListener("change", () => {
      const node = findNode(config.tree || [], checkbox.dataset.docId);
      if (!node) return;
      node.selected = checkbox.checked;
      if (selectedCount(config) === 0) {
        node.selected = true;
        checkbox.checked = true;
      }
      renderDocuments(config);
      renderGroups(config);
    });
  });
}
function groupStorageKey(config) { return `${noteStorageKey(config)}:groups`; }
function readGroups(config) {
  try { return JSON.parse(localStorage.getItem(groupStorageKey(config)) || "[]"); } catch { return []; }
}
function writeGroups(config, groups) { localStorage.setItem(groupStorageKey(config), JSON.stringify(groups)); }
function applyGroup(config, ids) {
  flattenFiles(config.tree || []).forEach((item) => { item.selected = ids.includes(item.id); });
  if (selectedCount(config) === 0) {
    const first = flattenFiles(config.tree || []).find((item) => item.href && !item.disabled);
    if (first) first.selected = true;
  }
  renderSidebar(config);
  bindFileToggles(config);
  renderDocuments(config);
  renderGroups(config);
}
function renderGroups(config) {
  const host = document.getElementById("viewer-groups");
  const groups = readGroups(config);
  host.innerHTML = groups.map((group, index) => `
    <button class="viewer-group-chip" type="button" data-group-index="${index}">${group.name}</button>
  `).join("");
  host.querySelectorAll("[data-group-index]").forEach((button) => {
    button.addEventListener("click", () => {
      const group = groups[Number(button.dataset.groupIndex)];
      if (group) applyGroup(config, group.ids || []);
    });
  });
}
function setLayout(value, config) {
  viewerState.layout = value;
  localStorage.setItem("mgd:last_layout", value);
  renderDocuments(config);
}
function bindToolbar(config) {
  document.querySelectorAll("[data-layout-button]").forEach((button) => {
    button.addEventListener("click", () => setLayout(button.dataset.layoutButton, config));
  });
  document.getElementById("size-small").addEventListener("click", () => { viewerState.panelSize = "small"; renderDocuments(config); });
  document.getElementById("size-medium").addEventListener("click", () => { viewerState.panelSize = "medium"; renderDocuments(config); });
  document.getElementById("size-large").addEventListener("click", () => { viewerState.panelSize = "large"; renderDocuments(config); });
  document.getElementById("viewer-find-button").addEventListener("click", () => {
    const query = document.getElementById("viewer-find").value;
    const frame = document.querySelector(`.viewer-panel[data-doc-id="${viewerState.activeDocId}"] iframe`);
    try { if (frame && query) frame.contentWindow.find(query); } catch (error) { console.warn(error); }
  });
  document.getElementById("print-view").addEventListener("click", () => window.print());
  document.getElementById("save-group").addEventListener("click", () => {
    const name = window.prompt("Group name");
    if (!name) return;
    const groups = readGroups(config);
    groups.push({ name, ids: selectedItems(config).map((item) => item.id) });
    writeGroups(config, groups);
    renderGroups(config);
  });
}
function applySidebarState() {
  const shell = document.querySelector(".workspace-shell");
  shell.classList.toggle("is-sidebar-hidden", viewerState.sidebarHidden);
}
async function bootViewer() {
  const config = await workspaceConfig();
  const title = document.getElementById("workspace-title");
  const subtitle = document.getElementById("workspace-subtitle");
  if (title && config.siteTitle) { title.textContent = config.siteTitle; document.title = config.siteTitle; }
  if (subtitle) subtitle.textContent = config.siteSummary || "";
  renderSidebar(config);
  viewerState.sidebarHidden = localStorage.getItem("mgd:sidebar:hidden") === "true";
  viewerState.layout = localStorage.getItem("mgd:last_layout") || "auto";
  applySidebarState();
  bindFileToggles(config);
  bindToolbar(config);
  renderDocuments(config);
  renderGroups(config);

  document.getElementById("toggle-sidebar").addEventListener("click", () => {
    viewerState.sidebarHidden = !viewerState.sidebarHidden;
    localStorage.setItem("mgd:sidebar:hidden", viewerState.sidebarHidden ? "true" : "false");
    applySidebarState();
  });

  const notes = document.getElementById("notes-text");
  const notesPanel = document.getElementById("notes-panel");
  if (config.showNotes === false) {
    notesPanel.hidden = true;
  } else {
    notes.value = localStorage.getItem(noteStorageKey(config)) || "";
    notes.addEventListener("input", () => saveViewerNotes(config));
    document.getElementById("insert-timestamp").addEventListener("click", () => {
      notes.setRangeText(`[${new Date().toLocaleTimeString()}] `, notes.selectionStart, notes.selectionEnd, "end");
      saveViewerNotes(config);
    });
    document.getElementById("copy-notes").addEventListener("click", async () => { await navigator.clipboard.writeText(notes.value); });
  }
}
window.addEventListener("DOMContentLoaded", () => { bootViewer().catch((error) => { console.error(error); }); });
