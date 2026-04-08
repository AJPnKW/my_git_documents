function viewerParams() {
  return new URLSearchParams(window.location.search);
}

function viewerDocs() {
  return (viewerParams().get("docs") || "").split(",").map((item) => item.trim()).filter(Boolean);
}

function setViewerMode(mode) {
  const grid = document.getElementById("viewer-grid");
  grid.dataset.mode = mode;
  localStorage.setItem("mgd:last_view_mode", mode);
  document.querySelectorAll("[data-mode-button]").forEach((button) => {
    button.classList.toggle("is-active", button.dataset.modeButton === mode);
  });
}

function noteStorageKey() {
  return viewerParams().get("notesKey") || "mgd:notes:default";
}

function saveViewerNotes() {
  const key = noteStorageKey();
  const value = document.getElementById("notes-text").value;
  localStorage.setItem(key, value);
  document.getElementById("save-status").textContent = `Saved locally ${new Date().toLocaleString()}`;
}

function bootViewer() {
  const params = viewerParams();
  const docs = viewerDocs();
  const labels = params.getAll("labels");
  const grid = document.getElementById("viewer-grid");

  grid.innerHTML = docs.map((doc, index) => `
    <section class="viewer-panel">
      <div class="viewer-head">
        <strong>${labels[index] || decodeURIComponent(doc.split("/").pop())}</strong>
        <a class="button-link" href="${doc}" target="_blank" rel="noreferrer">Open direct</a>
      </div>
      <div class="doc-frame">
        <iframe src="${doc}" title="Document ${index + 1}"></iframe>
      </div>
    </section>
  `).join("");

  const initialMode = params.get("mode") || localStorage.getItem("mgd:last_view_mode") || (docs.length >= 3 ? "tri" : docs.length === 2 ? "dual" : "single");
  setViewerMode(initialMode);
  document.querySelectorAll("[data-mode-button]").forEach((button) => {
    button.addEventListener("click", () => setViewerMode(button.dataset.modeButton));
  });

  const key = noteStorageKey();
  document.getElementById("notes-text").value = localStorage.getItem(key) || "";
  document.getElementById("notes-text").addEventListener("input", saveViewerNotes);
  document.getElementById("insert-timestamp").addEventListener("click", () => {
    const box = document.getElementById("notes-text");
    box.setRangeText(`[${new Date().toLocaleTimeString()}] `, box.selectionStart, box.selectionEnd, "end");
    saveViewerNotes();
  });
  document.getElementById("copy-notes").addEventListener("click", async () => {
    await navigator.clipboard.writeText(document.getElementById("notes-text").value);
  });
}

window.addEventListener("DOMContentLoaded", bootViewer);
