const LiveCaptureViewer = (() => {
  const terminalStates = new Set(["idle", "complete", "warn", "fail"]);
  const stopEnabledStates = new Set(["starting", "running"]);
  const transcriptionEnabledStates = new Set(["recorded"]);
  const previewKeys = ["transcript_txt", "transcript_srt"];
  const outputKeys = [
    ["recording_file", "capture-recording-link", "open recording"],
    ["transcript_txt", "capture-transcript-link", "open transcript txt"],
    ["transcript_srt", "capture-transcript-srt-link", "open transcript srt"],
    ["run_summary_json", "capture-summary-link", "open run summary"],
    ["log_file", "capture-log-link", "open log file"],
    ["zip_bundle", "capture-zip-link", "open zip bundle"]
  ];
  const state = {
    config: null,
    client: null,
    pollHandle: null,
    tickHandle: null,
    currentRun: normalizeRun(),
    recentRuns: [],
    transportOnline: false
  };

  function $(id) {
    return document.getElementById(id);
  }

  function escapeHtml(value) {
    return String(value ?? "").replace(/[&<>"']/g, (character) => ({
      "&": "&amp;",
      "<": "&lt;",
      ">": "&gt;",
      "\"": "&quot;",
      "'": "&#39;"
    }[character]));
  }

  function formatElapsed(seconds) {
    const safe = Math.max(0, Math.floor(Number(seconds || 0)));
    const hours = Math.floor(safe / 3600);
    const minutes = Math.floor((safe % 3600) / 60);
    const remainder = safe % 60;
    if (hours > 0) {
      return `${String(hours).padStart(2, "0")}:${String(minutes).padStart(2, "0")}:${String(remainder).padStart(2, "0")}`;
    }
    return `${String(minutes).padStart(2, "0")}:${String(remainder).padStart(2, "0")}`;
  }

  function formatDateTime(value, fallback = "—") {
    if (!value) {
      return fallback;
    }
    const parsed = new Date(value);
    if (Number.isNaN(parsed.getTime())) {
      return value;
    }
    return parsed.toLocaleString();
  }

  function normalizeWarnings(value) {
    if (!value) {
      return [];
    }
    if (Array.isArray(value)) {
      return value.map((item) => typeof item === "string" ? item : JSON.stringify(item));
    }
    if (typeof value === "string") {
      return [value];
    }
    return [JSON.stringify(value)];
  }

  function normalizeRun(input = {}) {
    const outputs = input.outputs && typeof input.outputs === "object" ? input.outputs : {};
    return {
      raw: input,
      run_id: input.run_id || "",
      status: input.status || "idle",
      started_at: input.started_at || "",
      updated_at: input.updated_at || "",
      input_file: input.input_file || "",
      duration_seconds: Number(input.duration_seconds || 0),
      warnings: normalizeWarnings(input.warnings),
      outputs: {
        recording_file: outputs.recording_file || "",
        transcript_txt: outputs.transcript_txt || "",
        transcript_srt: outputs.transcript_srt || "",
        run_summary_json: outputs.run_summary_json || "",
        log_file: outputs.log_file || "",
        zip_bundle: outputs.zip_bundle || ""
      }
    };
  }

  function resolveTemplate(template, values) {
    return String(template || "").replace(/\{([^}]+)\}/g, (_, key) => encodeURIComponent(values[key] || ""));
  }

  function buildClient(config) {
    const baseUrl = String(config.bridgeBaseUrl || "http://127.0.0.1:8765").replace(/\/$/, "");
    const endpoints = config.endpoints || {};
    return {
      baseUrl,
      async request(path, options = {}) {
        const response = await fetch(`${baseUrl}${path}`, {
          method: options.method || "GET",
          headers: {
            "Content-Type": "application/json",
            ...(options.headers || {})
          },
          cache: "no-store",
          body: options.body ? JSON.stringify(options.body) : undefined
        });
        let payload = {};
        try {
          payload = await response.json();
        } catch (error) {
          payload = {};
        }
        if (!response.ok) {
          throw new Error(payload.error || payload.message || `${response.status} ${response.statusText}`);
        }
        return payload;
      },
      getStatus() {
        return this.request(endpoints.captureStatus || "/api/capture/status");
      },
      listRuns() {
        return this.request(endpoints.runs || "/api/runs");
      },
      getRun(runId) {
        return this.request(resolveTemplate(endpoints.runDetailsTemplate || "/api/runs/{run_id}", { run_id: runId }));
      },
      startCapture(body) {
        return this.request(endpoints.captureStart || "/api/capture/start", { method: "POST", body });
      },
      stopCapture(body) {
        return this.request(endpoints.captureStop || "/api/capture/stop", { method: "POST", body });
      },
      startTranscription(body) {
        return this.request(endpoints.transcriptionStart || "/api/transcription/start", { method: "POST", body });
      }
    };
  }

  function isBrowserSafeUrl(value) {
    return /^https?:\/\//i.test(value || "");
  }

  function isBridgeRelativePath(value) {
    return /^\/(?!\/)/.test(value || "") || /^api\//i.test(value || "");
  }

  function isWindowsPath(value) {
    return /^[a-zA-Z]:\\/.test(value || "");
  }

  function artifactHref(run, key) {
    if (!run?.run_id) {
      return "#";
    }
    const outputValue = run.outputs?.[key];
    if (isBrowserSafeUrl(outputValue)) {
      return outputValue;
    }
    if (isBridgeRelativePath(outputValue)) {
      const relative = outputValue.startsWith("/") ? outputValue : `/${outputValue}`;
      return `${state.client.baseUrl}${relative}`;
    }
    const route = state.config.artifactRouteTemplate || "/api/runs/{run_id}/artifact/{artifact_key}";
    return `${state.client.baseUrl}${resolveTemplate(route, { run_id: run.run_id, artifact_key: key })}`;
  }

  function setLink(linkId, href, readyText, isReady) {
    const link = $(linkId);
    if (!link) {
      return;
    }
    link.href = isReady ? href : "#";
    link.textContent = isReady ? readyText : "not ready";
    link.setAttribute("aria-disabled", isReady ? "false" : "true");
  }

  function setBadge(status) {
    const safeStatus = status || "idle";
    const badge = $("capture-status-badge");
    if (badge) {
      badge.textContent = safeStatus;
      badge.className = `capture-badge ${safeStatus}`;
    }
    const serviceState = $("capture-service-state");
    if (serviceState) {
      serviceState.textContent = state.transportOnline ? "online" : "offline";
    }
    const startButton = $("capture-start");
    const stopButton = $("capture-stop");
    const transcriptionButton = $("capture-start-transcription");
    const runActive = !terminalStates.has(safeStatus);
    if (startButton) {
      startButton.disabled = !state.transportOnline || runActive;
    }
    if (stopButton) {
      stopButton.disabled = !state.transportOnline || !stopEnabledStates.has(safeStatus);
    }
    if (transcriptionButton) {
      transcriptionButton.disabled = !state.transportOnline || !transcriptionEnabledStates.has(safeStatus) || !state.currentRun.run_id;
    }
  }

  function renderTransport(message, online) {
    const panel = $("capture-transport-panel");
    if (!panel) {
      return;
    }
    panel.className = `capture-transport-panel ${online ? "is-online" : "is-offline"}`;
    panel.textContent = message;
  }

  function renderWarnings(runWarnings, runStatus, transportError) {
    const panel = $("capture-warning-panel");
    if (!panel) {
      return;
    }
    if (transportError) {
      panel.className = "capture-warning-panel is-error";
      panel.textContent = transportError;
      return;
    }
    if (runWarnings.length === 0 && !["warn", "fail"].includes(runStatus)) {
      panel.className = "capture-warning-panel";
      panel.textContent = "No current warnings.";
      return;
    }
    panel.className = `capture-warning-panel ${runStatus === "fail" ? "is-error" : "is-warn"}`;
    panel.innerHTML = runWarnings.length
      ? runWarnings.map((item) => `<div>${escapeHtml(item)}</div>`).join("")
      : `<div>${escapeHtml(`Run status is ${runStatus}. Inspect available outputs for details.`)}</div>`;
  }

  function renderRun(run) {
    state.currentRun = normalizeRun(run);
    setBadge(state.currentRun.status);
    $("capture-run-id").textContent = state.currentRun.run_id || "none";
    $("capture-started").textContent = formatDateTime(state.currentRun.started_at, "not started");
    $("capture-elapsed").textContent = formatElapsed(state.currentRun.duration_seconds);
    $("capture-updated").textContent = formatDateTime(state.currentRun.updated_at);
    $("capture-input-file").textContent = state.currentRun.input_file || "not provided";
    outputKeys.forEach(([key, linkId, label]) => {
      const outputValue = state.currentRun.outputs[key];
      const ready = Boolean(state.currentRun.run_id) && Boolean(outputValue) && state.currentRun.status !== "idle";
      setLink(linkId, artifactHref(state.currentRun, key), label, ready);
    });
    renderWarnings(state.currentRun.warnings, state.currentRun.status, "");
    renderTranscriptPreview(state.currentRun).catch((error) => {
      console.warn(error);
    });
  }

  function renderHistory(runs) {
    const list = $("capture-history-list");
    if (!list) {
      return;
    }
    list.innerHTML = "";
    const limited = runs.slice(0, Number(state.config.historyLimit || 10));
    if (!limited.length) {
      const item = document.createElement("li");
      item.textContent = "No runs yet.";
      list.appendChild(item);
      return;
    }
    limited.forEach((run) => {
      const safeRun = normalizeRun(run);
      const item = document.createElement("li");
      item.className = "capture-history-item";
      item.innerHTML = `
        <div class="capture-history-meta">
          <strong>${escapeHtml(safeRun.run_id || "unknown")}</strong>
          <span>${escapeHtml(formatDateTime(safeRun.started_at, "not started"))}</span>
        </div>
        <span class="capture-inline-status ${escapeHtml(safeRun.status || "idle")}">${escapeHtml(safeRun.status || "idle")}</span>
        <button type="button" data-run-load="${escapeHtml(safeRun.run_id)}">Load</button>
        <a href="${escapeHtml(artifactHref(safeRun, "transcript_txt"))}" target="_blank" rel="noreferrer">transcript</a>
        <a href="${escapeHtml(artifactHref(safeRun, "zip_bundle"))}" target="_blank" rel="noreferrer">zip</a>
        <span>${escapeHtml(formatElapsed(safeRun.duration_seconds))}</span>
      `;
      list.appendChild(item);
    });
    list.querySelectorAll("[data-run-load]").forEach((button) => {
      button.addEventListener("click", async () => {
        const runId = button.getAttribute("data-run-load");
        if (!runId) {
          return;
        }
        try {
          const run = await state.client.getRun(runId);
          renderRun(run);
        } catch (error) {
          console.warn(error);
          renderWarnings([], state.currentRun.status, `Could not load run ${runId}: ${error.message}`);
        }
      });
    });
  }

  function startElapsedTicker() {
    if (state.tickHandle) {
      window.clearInterval(state.tickHandle);
      state.tickHandle = null;
    }
    if (!state.currentRun.run_id || terminalStates.has(state.currentRun.status)) {
      return;
    }
    state.tickHandle = window.setInterval(() => {
      const started = state.currentRun.started_at ? new Date(state.currentRun.started_at).getTime() : 0;
      if (!started || Number.isNaN(started)) {
        $("capture-elapsed").textContent = formatElapsed(state.currentRun.duration_seconds);
        return;
      }
      const elapsedSeconds = Math.max(
        state.currentRun.duration_seconds,
        Math.floor((Date.now() - started) / 1000)
      );
      $("capture-elapsed").textContent = formatElapsed(elapsedSeconds);
    }, 1000);
  }

  async function renderTranscriptPreview(run) {
    const preview = $("capture-transcript-preview");
    if (!preview) {
      return;
    }
    if (!run?.run_id) {
      preview.textContent = "No transcript loaded.";
      return;
    }
    const previewKey = previewKeys.find((key) => run.outputs[key]);
    if (!previewKey) {
      preview.textContent = "Transcript file not ready yet.";
      return;
    }
    try {
      const response = await fetch(artifactHref(run, previewKey), { cache: "no-store" });
      if (!response.ok) {
        preview.textContent = "Transcript preview unavailable from the bridge right now.";
        return;
      }
      const text = await response.text();
      preview.textContent = text.slice(0, 6000) || "Transcript file is empty.";
    } catch (error) {
      preview.textContent = `Transcript preview unavailable: ${error.message}`;
    }
  }

  function nextPollDelay(status, online) {
    const intervals = state.config.pollIntervalsMs || {};
    if (!online) {
      return Number(intervals.offline || 5000);
    }
    if (!terminalStates.has(status)) {
      return Number(intervals.active || 3000);
    }
    return Number(intervals.idle || 15000);
  }

  function scheduleRefresh() {
    if (state.pollHandle) {
      window.clearTimeout(state.pollHandle);
    }
    state.pollHandle = window.setTimeout(() => {
      refresh().catch((error) => {
        console.warn(error);
      });
    }, nextPollDelay(state.currentRun.status, state.transportOnline));
  }

  async function refresh() {
    try {
      const [statusPayload, runsPayload] = await Promise.all([
        state.client.getStatus(),
        state.client.listRuns()
      ]);
      state.transportOnline = true;
      renderTransport(`${state.config.serviceLabel || "Local capture bridge"} online at ${state.client.baseUrl}.`, true);
      const statusCandidate = statusPayload.run || statusPayload.current_run || statusPayload;
      let run = normalizeRun(statusCandidate);
      if (run.run_id) {
        try {
          run = normalizeRun(await state.client.getRun(run.run_id));
        } catch (error) {
          console.warn(error);
        }
      }
      renderRun(run);
      startElapsedTicker();
      const runs = Array.isArray(runsPayload) ? runsPayload : Array.isArray(runsPayload.runs) ? runsPayload.runs : [];
      state.recentRuns = runs.map((item) => normalizeRun(item));
      renderHistory(state.recentRuns);
    } catch (error) {
      state.transportOnline = false;
      setBadge("offline");
      renderTransport(`Local capture service offline: ${error.message}`, false);
      renderWarnings([], state.currentRun.status, `Local capture service offline: ${error.message}`);
      const preview = $("capture-transcript-preview");
      if (preview && !state.currentRun.run_id) {
        preview.textContent = "Transcript preview unavailable while the bridge is offline.";
      }
    } finally {
      scheduleRefresh();
    }
  }

  function buildRunContext() {
    return {
      ...(state.config.startRequestTemplate || {}),
      ...(state.config.roleContext || {}),
      run_label: $("capture-run-label").value.trim() || state.config.runLabelDefault || "live_capture_run"
    };
  }

  async function startCapture() {
    renderWarnings([], state.currentRun.status, "");
    await state.client.startCapture(buildRunContext());
    await refresh();
  }

  async function stopCapture() {
    if (!state.currentRun.run_id) {
      return;
    }
    renderWarnings([], state.currentRun.status, "");
    await state.client.stopCapture({
      run_id: state.currentRun.run_id,
      source: "my_git_documents_viewer"
    });
    await refresh();
  }

  async function startTranscription() {
    if (!state.currentRun.run_id) {
      return;
    }
    renderWarnings([], state.currentRun.status, "");
    await state.client.startTranscription({
      ...(state.config.transcriptionRequestTemplate || {}),
      run_id: state.currentRun.run_id
    });
    await refresh();
  }

  async function loadJson(path) {
    const response = await fetch(path, { cache: "no-store" });
    if (!response.ok) {
      throw new Error(`Failed to load ${path}: ${response.status}`);
    }
    return response.json();
  }

  function renderSourceList(dataSources) {
    const list = $("capture-source-list");
    if (!list) {
      return;
    }
    list.innerHTML = "";
    dataSources.forEach((item) => {
      const li = document.createElement("li");
      li.innerHTML = `<strong>${escapeHtml(item.label)}</strong><a href="${escapeHtml(item.path)}" target="_blank" rel="noreferrer">${escapeHtml(item.path)}</a>`;
      list.appendChild(li);
    });
  }

  function renderContextCards(payloads) {
    const panel = $("capture-context-panel");
    if (!panel) {
      return;
    }
    const cards = [];
    if (payloads.live_interview_config) {
      cards.push(`
        <div class="capture-context-card">
          <h3>Opening positioning</h3>
          <div>${escapeHtml(payloads.live_interview_config.opening_positioning || "Not provided.")}</div>
          <ul>${(payloads.live_interview_config.question_prompts_to_ask_them || []).slice(0, 4).map((item) => `<li>${escapeHtml(item)}</li>`).join("")}</ul>
        </div>
      `);
    }
    if (payloads.opportunity_profile) {
      cards.push(`
        <div class="capture-context-card">
          <h3>Role focus</h3>
          <div>${escapeHtml(payloads.opportunity_profile.role_summary || "Not provided.")}</div>
          <ul>${(payloads.opportunity_profile.must_haves || []).slice(0, 4).map((item) => `<li>${escapeHtml(item)}</li>`).join("")}</ul>
        </div>
      `);
    }
    if (payloads.opportunity_interview_response_bank) {
      cards.push(`
        <div class="capture-context-card">
          <h3>Likely interview questions</h3>
          <ul>${(payloads.opportunity_interview_response_bank.likely_question_bank || []).slice(0, 5).map((item) => `<li>${escapeHtml(item.question || "")}</li>`).join("")}</ul>
        </div>
      `);
    }
    if (payloads.company_people_research) {
      const companies = payloads.company_people_research.companies || [];
      cards.push(`
        <div class="capture-context-card">
          <h3>Company context</h3>
          <div>${escapeHtml(payloads.company_people_research.canonical_group?.summary || payloads.company_people_research.canonical_group?.name || "Not provided.")}</div>
          <ul>${companies.slice(0, 3).map((item) => `<li>${escapeHtml(item.display_name || item.entity_id || "")}</li>`).join("")}</ul>
        </div>
      `);
    }
    if (payloads.career_master || payloads.story_master) {
      cards.push(`
        <div class="capture-context-card">
          <h3>Career evidence package</h3>
          <div>${escapeHtml(payloads.career_master?.profile?.summary || "Career summary not provided.")}</div>
          <ul>
            <li>${escapeHtml(`Story count: ${payloads.story_master?.stories?.length || 0}`)}</li>
            <li>${escapeHtml(`Employer count: ${payloads.career_master?.employers?.length || 0}`)}</li>
          </ul>
        </div>
      `);
    }
    panel.innerHTML = cards.join("") || "Configured interview context loaded, but no summary fields were available.";
  }

  async function loadInterviewContext() {
    const dataSources = state.config.dataSources || [];
    renderSourceList(dataSources);
    if (!dataSources.length) {
      $("capture-context-panel").textContent = "No interview context sources configured.";
      return;
    }
    const results = await Promise.allSettled(dataSources.map((item) => loadJson(item.path)));
    const payloads = {};
    results.forEach((result, index) => {
      const source = dataSources[index];
      if (result.status === "fulfilled") {
        payloads[source.id] = result.value;
      } else {
        console.warn(result.reason);
      }
    });
    renderContextCards(payloads);
  }

  function bind() {
    $("capture-start")?.addEventListener("click", () => startCapture().catch((error) => {
      console.warn(error);
      renderWarnings([], state.currentRun.status, `Start failed: ${error.message}`);
    }));
    $("capture-stop")?.addEventListener("click", () => stopCapture().catch((error) => {
      console.warn(error);
      renderWarnings([], state.currentRun.status, `Stop failed: ${error.message}`);
    }));
    $("capture-start-transcription")?.addEventListener("click", () => startTranscription().catch((error) => {
      console.warn(error);
      renderWarnings([], state.currentRun.status, `Transcription failed: ${error.message}`);
    }));
    $("capture-refresh")?.addEventListener("click", () => refresh().catch((error) => {
      console.warn(error);
    }));
  }

  function applyConfig(config) {
    state.config = config.liveCapture || {};
    state.client = buildClient(state.config);
    const panel = $("live-capture-panel");
    panel.hidden = false;
    $("capture-run-label").value = state.config.runLabelDefault || "live_capture_run";
    $("capture-service-summary").textContent = `${state.config.serviceLabel || "Local capture bridge"} at ${state.client.baseUrl}. Toolkit dependency: ${state.config.toolkitRoot || "external local toolkit"}.`;
    $("capture-helper-copy").textContent = `The browser controls run lifecycle through the localhost bridge only. Execution remains in ${state.config.toolkitRoot || "the external local toolkit"}.`;
    $("capture-contract-link").href = state.config.docs?.integrationContract || "#";
    $("capture-state-model-link").href = state.config.docs?.uiStateModel || "#";
    $("capture-runbook-link").href = state.config.docs?.runbook || "#";
  }

  async function init() {
    const panel = $("live-capture-panel");
    if (!panel) {
      return;
    }
    const bootPromise = window.MyGitDocumentsViewerBootPromise || Promise.resolve(window.MyGitDocumentsViewerConfig || null);
    let config = null;
    try {
      config = await bootPromise;
    } catch (error) {
      console.warn(error);
      return;
    }
    if (!config?.liveCapture?.enabled) {
      panel.hidden = true;
      return;
    }
    applyConfig(config);
    bind();
    await Promise.allSettled([loadInterviewContext(), refresh()]);
  }

  return { init };
})();

window.addEventListener("DOMContentLoaded", () => {
  LiveCaptureViewer.init().catch((error) => {
    console.warn(error);
  });
});
