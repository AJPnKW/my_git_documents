async function digestValue(value) {
  const bytes = new TextEncoder().encode(value);
  const hash = await crypto.subtle.digest("SHA-256", bytes);
  return Array.from(new Uint8Array(hash)).map((item) => item.toString(16).padStart(2, "0")).join("");
}

async function loadGateConfig(siteKey) {
  try {
    const response = await fetch("../../config/auth_config.local.json", { cache: "no-store" });
    if (!response.ok) {
      return null;
    }
    const config = await response.json();
    return config.sites[siteKey] || null;
  } catch {
    return null;
  }
}

async function bootGate(siteKey) {
  const gate = document.querySelector("[data-access-gate]");
  const protectedBody = document.querySelector("[data-protected-body]");

  if (!gate || !protectedBody) {
    return;
  }

  const config = await loadGateConfig(siteKey);
  if (!config) {
    gate.hidden = true;
    protectedBody.hidden = false;
    return;
  }

  const storageKey = `mgd:gate:${siteKey}`;
  if (sessionStorage.getItem(storageKey) === "open") {
    gate.hidden = true;
    protectedBody.hidden = false;
    return;
  }

  gate.hidden = false;
  protectedBody.hidden = true;
  gate.querySelector("[data-gate-title]").textContent = config.title;
  gate.querySelector("[data-gate-prompt]").textContent = config.prompt;
  gate.querySelector("button").addEventListener("click", async () => {
    const value = gate.querySelector("input").value;
    const digest = await digestValue(value);
    if (digest === config.sha256) {
      sessionStorage.setItem(storageKey, "open");
      gate.hidden = true;
      protectedBody.hidden = false;
    } else {
      gate.querySelector("[data-gate-error]").textContent = "That entry did not unlock this area.";
    }
  });
}

window.MyGitDocumentsAuth = { bootGate };
