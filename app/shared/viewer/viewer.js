const viewerState = {
  requestedMode: "single",
  syncScroll: false,
  syncLock: false,
  activeTabIndex: 0,
};

function workspaceParams() {
  return new URLSearchParams(window.location.search);
}

function viewerParam(name) {
  return workspaceParams().get(name);
}

function readEmbeddedConfig() {
  const tag = document.getElementById("workspace-config");
  if (!tag) {
    return null;
  }
  return JSON.parse(tag.textContent);
}

async function readDataConfig() {
  const path = viewerParam("workspaceJson") || document.body?.dataset.workspaceJson;
  if (!path) {
    return null;
  }
  const response = await fetch(path, { cache: "no-store" });
  if (!response.ok) {
    throw new Error(`Workspace config failed: ${response.status}`);
  }
  return response.json();
}

function buildConfigFromQuery() {
  const params = workspaceParams();
  const docs = (params.get("docs") || "").split(",").map((item) => item.trim()).filter(Boolean);
  const labels = params.getAll("labels");
  return {
    siteTitle: params.get("title") || "Viewer",
    siteSummary: "",
    hideSidebarHeader: false,
    defaultMode: params.get("mode") || "single",
    noteStorageKey: params.get("notesKey") || "mgd:notes:default",
    notePlaceholder: "Capture notes here.",
    showNotes: true,
    showToolbarStatus: true,
    showPanelHeader: true,
    tree: [
      {
        "id": "query-documents",
        "type": "folder",
        "label": "Documents",
        "open": true,
        "children": docs.map((doc, index) => ({
          "id": `doc-${index + 1}`,
          "type": "file",
          "label": labels[index] || decodeURIComponent(doc.split("/").pop()),
          "description": "",
          "href": doc,
          "selected": index < 3
        }))
      }
    ]
  };
}

async function workspaceConfig() {
  return await readDataConfig() || readEmbeddedConfig() || buildConfigFromQuery();
}

function flattenFiles(nodes) {
  return nodes.flatMap((node) => {
    if (node.type === "folder") {
      return flattenFiles(node.children || []);
    }
    return [node];
  });
}

function selectedItems(config) {
  return flattenFiles(config.tree || []).filter((item) => item.selected && item.href && !item.disabled);
}

function selectedCount(config) {
  return selectedItems(config).length;
}

function findNode(nodes, id) {
  for (const node of nodes) {
    if (node.id === id) {
      return node;
    }
    if (node.type === "folder") {
      const child = findNode(node.children || [], id);
      if (child) {
        return child;
      }
    }
  }
  return null;
}

function countEnabledFiles(nodes) {
  return flattenFiles(nodes).filter((item) => item.href && !item.disabled).length;
}

function normalizeMode(mode, count) {
  if (count <= 1) {
    return "single";
  }
  if (mode === "columns" && count < 3) {
    return "split";
  }
  if (["split", "rows", "tabs", "arrange"].includes(mode) && count >= 2) {
    return mode;
  }
  if (mode === "columns" && count >= 3) {
    return mode;
  }
  return count >= 2 ? "split" : "single";
}

function modeLimit(mode, items) {
  if (mode === "single") {
    return 1;
  }
  if (mode === "split") {
    return 2;
  }
  if (mode === "columns") {
    return 3;
  }
  if (mode === "tabs") {
    return 1;
  }
  return items.length;
}

function setViewerMode(mode, config) {
  const count = selectedCount(config);
  viewerState.requestedMode = normalizeMode(mode, count);
  const grid = document.getElementById("viewer-grid");
  grid.dataset.mode = viewerState.requestedMode;
  localStorage.setItem("mgd:last_view_mode", viewerState.requestedMode);
  document.querySelectorAll("[data-mode-button]").forEach((button) => {
    button.classList.toggle("is-active", button.dataset.modeButton === viewerState.requestedMode);
  });
}

function renderNode(node, depth = 0) {
  if (node.type === "folder") {
    const isOpen = node.open !== false;
    const children = (node.children || []).map((child) => renderNode(child, depth + 1)).join("");
    return `
      <li class="tree-node tree-folder-node">
        <button class="tree-folder-row" type="button" data-folder-id="${node.id}" aria-expanded="${isOpen ? "true" : "false"}" style="padding-left:${depth * 14}px">
          <span class="tree-folder-arrow">${isOpen ? "▾" : "▸"}</span>
          <span class="tree-folder-icon">□</span>
          <span class="tree-folder-name">${node.label}</span>
        </button>
        <ul class="tree-children" ${isOpen ? "" : "hidden"}>
          ${children}
        </ul>
      </li>
    `;
  }

  return `
    <li class="tree-node tree-file-node">
      <label class="tree-file-row ${node.disabled ? "is-disabled" : ""}" style="padding-left:${depth * 14}px">
        <input type="checkbox" data-doc-id="${node.id}" ${node.selected ? "checked" : ""} ${node.disabled ? "disabled" : ""}>
        <span class="tree-file-icon">${node.placeholder ? "⋯" : "—"}</span>
        <span class="tree-file-text">
          <strong>${node.label}</strong>
          ${node.description ? `<span class="tree-item-meta">${node.description}</span>` : ""}
        </span>
      </label>
    </li>
  `;
}

function renderSidebar(config) {
  const root = document.getElementById("workspace-tree");
  root.innerHTML = `<ul class="tree-root">${(config.tree || []).map((node) => renderNode(node)).join("")}</ul>`;

  document.querySelectorAll("[data-folder-id]").forEach((button) => {
    button.addEventListener("click", () => {
      const folder = findNode(config.tree || [], button.dataset.folderId);
      if (!folder) {
        return;
      }
      folder.open = folder.open === false;
      renderSidebar(config);
      bindFileToggles(config);
    });
  });
}

function updateToolbar(config) {
  const count = selectedCount(config);
  const totalEnabled = countEnabledFiles(config.tree || []);
  document.querySelectorAll("[data-mode-button]").forEach((button) => {
    const mode = button.dataset.modeButton;
    let visible = true;
    if (mode === "single") {
      visible = totalEnabled > 1;
    } else if (mode === "split") {
      visible = totalEnabled >= 2;
    } else if (mode === "columns") {
      visible = totalEnabled >= 3;
    } else if (["rows", "tabs", "arrange"].includes(mode)) {
      visible = totalEnabled >= 2;
    }
    button.hidden = !visible;
  });

  const syncButton = document.getElementById("sync-scroll");
  if (syncButton) {
    syncButton.hidden = count < 2;
    syncButton.classList.toggle("is-active", viewerState.syncScroll);
    syncButton.setAttribute("aria-pressed", viewerState.syncScroll ? "true" : "false");
  }
}

function syncFrames(sourceFrame) {
  if (!viewerState.syncScroll || viewerState.syncLock) {
    return;
  }
  try {
    const sourceWindow = sourceFrame.contentWindow;
    const sourceDoc = sourceWindow.document.documentElement;
    const sourceMax = sourceDoc.scrollHeight - sourceWindow.innerHeight;
    const ratio = sourceMax > 0 ? sourceWindow.scrollY / sourceMax : 0;
    viewerState.syncLock = true;
    document.querySelectorAll(".viewer-panel iframe").forEach((frame) => {
      if (frame === sourceFrame) {
        return;
      }
      try {
        const targetWindow = frame.contentWindow;
        const targetDoc = targetWindow.document.documentElement;
        const targetMax = targetDoc.scrollHeight - targetWindow.innerHeight;
        targetWindow.scrollTo(0, Math.max(0, targetMax * ratio));
      } catch (error) {
        console.warn(error);
      }
    });
  } finally {
    viewerState.syncLock = false;
  }
}

function bindFrameBehaviors() {
  document.querySelectorAll(".viewer-panel iframe").forEach((frame) => {
    frame.addEventListener("load", () => {
      try {
        frame.contentWindow.addEventListener("scroll", () => syncFrames(frame));
      } catch (error) {
        console.warn(error);
      }
    });
  });
}

function renderDocuments(config) {
  updateToolbar(config);
  const items = selectedItems(config);
  const count = items.length;
  if (count <= 1 && viewerState.requestedMode !== "single") {
    viewerState.requestedMode = "single";
  } else {
    viewerState.requestedMode = normalizeMode(viewerState.requestedMode, count);
  }

  const grid = document.getElementById("viewer-grid");
  grid.dataset.mode = viewerState.requestedMode;
  const limit = modeLimit(viewerState.requestedMode, items);
  let visible = items.slice(0, limit);
  if (viewerState.requestedMode === "tabs") {
    viewerState.activeTabIndex = Math.max(0, Math.min(viewerState.activeTabIndex, items.length - 1));
    visible = items.length ? [items[viewerState.activeTabIndex]] : [];
  }
  const status = document.getElementById("toolbar-status");
  if (config.showToolbarStatus === false) {
    status.hidden = true;
  } else {
    status.hidden = false;
    status.textContent = `${count} selected`;
  }

  const tabsMarkup = viewerState.requestedMode === "tabs" && items.length > 1
    ? `
      <div class="viewer-tabs" role="tablist" aria-label="Documents">
        ${items.map((item, index) => `
          <button
            class="viewer-tab ${index === viewerState.activeTabIndex ? "is-active" : ""}"
            type="button"
            role="tab"
            aria-selected="${index === viewerState.activeTabIndex ? "true" : "false"}"
            data-tab-index="${index}">
            ${item.label}
          </button>
        `).join("")}
      </div>
    `
    : "";

  grid.innerHTML = `
    ${tabsMarkup}
    ${visible.map((item, index) => `
    <section class="viewer-panel">
      ${config.showPanelHeader === false ? "" : `
      <div class="viewer-head">
        <strong>${item.label}</strong>
        <a class="button-link" href="${item.href}" target="_blank" rel="noreferrer">Open direct</a>
      </div>`}
      <div class="doc-frame">
        <iframe src="${item.href}" title="Document ${index + 1}" data-zoom="1"></iframe>
      </div>
    </section>
  `).join("")}
  `;

  document.querySelectorAll("[data-tab-index]").forEach((button) => {
    button.addEventListener("click", () => {
      viewerState.activeTabIndex = Number(button.dataset.tabIndex || "0");
      renderDocuments(config);
    });
  });

  bindFrameBehaviors();
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
    frame.style.height = `calc((100vh - var(--topbar-height) - var(--toolbar-height) - 18px) / ${next})`;
  });
}

function fitWidth() {
  document.querySelectorAll(".viewer-panel iframe").forEach((frame) => {
    frame.style.width = "100%";
    frame.style.height = "calc(100vh - var(--topbar-height) - var(--toolbar-height) - 18px)";
  });
}

function fitPage() {
  document.querySelectorAll(".viewer-panel iframe").forEach((frame) => {
    frame.style.width = "100%";
    frame.style.height = "calc(100vh - var(--topbar-height) - 4px)";
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

function bindFileToggles(config) {
  document.querySelectorAll("[data-doc-id]").forEach((checkbox) => {
    checkbox.addEventListener("change", () => {
      const node = findNode(config.tree || [], checkbox.dataset.docId);
      if (!node) {
        return;
      }
      node.selected = checkbox.checked;
      if (selectedCount(config) === 0) {
        node.selected = true;
        checkbox.checked = true;
        return;
      }
      if (selectedCount(config) === 1) {
        viewerState.requestedMode = "single";
        viewerState.activeTabIndex = 0;
      }
      renderDocuments(config);
    });
  });
}

async function bootViewer() {
  const config = await workspaceConfig();
  const title = document.getElementById("workspace-title");
  const subtitle = document.getElementById("workspace-subtitle");
  const header = document.getElementById("workspace-header");
  const notes = document.getElementById("notes-text");
  const notesPanel = document.getElementById("notes-panel");

  if (title && config.siteTitle) {
    title.textContent = config.siteTitle;
    document.title = config.siteTitle;
  }
  if (subtitle) {
    subtitle.textContent = config.siteSummary || "";
  }
  if (header && config.hideSidebarHeader) {
    header.hidden = true;
  }
  if (notes && config.notePlaceholder) {
    notes.placeholder = config.notePlaceholder;
  }

  renderSidebar(config);
  viewerState.requestedMode = config.defaultMode || localStorage.getItem("mgd:last_view_mode") || "single";
  setViewerMode(viewerState.requestedMode, config);
  renderDocuments(config);
  bindFileToggles(config);

  document.querySelectorAll("[data-mode-button]").forEach((button) => {
    button.addEventListener("click", () => {
      setViewerMode(button.dataset.modeButton, config);
      renderDocuments(config);
    });
  });

  const syncButton = document.getElementById("sync-scroll");
  if (syncButton) {
    syncButton.addEventListener("click", () => {
      viewerState.syncScroll = !viewerState.syncScroll;
      updateToolbar(config);
    });
  }

  if (config.showNotes === false) {
    notesPanel.hidden = true;
  } else {
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
  }

  document.getElementById("zoom-in").addEventListener("click", () => setZoom(0.1));
  document.getElementById("zoom-out").addEventListener("click", () => setZoom(-0.1));
  document.getElementById("zoom-reset").addEventListener("click", () => {
    document.querySelectorAll(".viewer-panel iframe").forEach((frame) => {
      frame.dataset.zoom = "1";
      frame.style.transform = "scale(1)";
      frame.style.height = "calc(100vh - var(--topbar-height) - var(--toolbar-height) - 18px)";
    });
  });
  document.getElementById("fit-width").addEventListener("click", fitWidth);
  document.getElementById("fit-page").addEventListener("click", fitPage);
  document.getElementById("viewer-find-button").addEventListener("click", findInCurrent);
  document.getElementById("print-view").addEventListener("click", () => window.print());
}

window.addEventListener("DOMContentLoaded", () => {
  bootViewer().catch((error) => {
    console.error(error);
  });
  const siteKey = viewerParam("siteKey");
  if (siteKey && window.MyGitDocumentsAuth?.bootGate) {
    window.MyGitDocumentsAuth.bootGate(siteKey);
  }
});
