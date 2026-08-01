/* UniverseLab Runtime Loader v0.1
 *
 * Declarative bindings:
 *   data-ul-gate="K1-D"
 *   data-ul-page="hyperlab"
 *   data-ul-issue-count="CRITICAL"
 *   data-ul-release
 *
 * This file performs no physical calculation. It prevents status drift.
 */
(() => {
  "use strict";

  const DEFAULTS = {
    manifest: "./project-manifest.json",
    conventions: "./convention-registry.json",
    audit: "./universelab-audit-2026-07-31.json"
  };

  const allowedGateValues = new Set([
    "PASS", "CONDITIONAL", "NOT_RELEASED", "NOT_ADMISSIBLE",
    "OPEN", "BLOCKED", "REJECTED", "QUARANTINED"
  ]);

  async function loadJson(url) {
    const response = await fetch(url, { cache: "no-cache" });
    if (!response.ok) {
      throw new Error(`UniverseLab runtime load failed: ${url} (${response.status})`);
    }
    return response.json();
  }

  function assertCoreSchemas(manifest, conventions, audit) {
    if (manifest.schema !== "universelab.project-manifest.v1") {
      throw new Error("Unknown project manifest schema");
    }
    if (conventions.schema !== "universelab.conventions.v1") {
      throw new Error("Unknown convention registry schema");
    }
    if (audit.schema !== "universelab.audit.v1") {
      throw new Error("Unknown audit schema");
    }
    for (const [gate, value] of Object.entries(manifest.gates || {})) {
      if (gate.startsWith("K1") && !allowedGateValues.has(value)) {
        throw new Error(`Unknown gate value ${gate}=${value}`);
      }
    }
  }

  function renderGates(manifest) {
    document.querySelectorAll("[data-ul-gate]").forEach(node => {
      const key = node.dataset.ulGate;
      const value = manifest.gates?.[key];
      if (value === undefined) return;
      node.textContent = value.replaceAll("_", " ");
      node.dataset.ulStatus = value;
    });
  }

  function renderPages(manifest) {
    const pages = new Map(
      (manifest.canonical_pages || []).map(page => [page.id, page])
    );
    document.querySelectorAll("[data-ul-page]").forEach(node => {
      const page = pages.get(node.dataset.ulPage);
      if (!page) return;
      node.setAttribute("href", page.live || `./${page.path}`);
      if (!node.textContent.trim()) node.textContent = page.id;
      node.dataset.ulPageStatus = page.status;
    });
  }

  function renderAuditCounts(audit) {
    const counts = (audit.issues || []).reduce((acc, issue) => {
      acc[issue.severity] = (acc[issue.severity] || 0) + 1;
      acc.ALL = (acc.ALL || 0) + 1;
      return acc;
    }, {});
    document.querySelectorAll("[data-ul-issue-count]").forEach(node => {
      node.textContent = String(counts[node.dataset.ulIssueCount] || 0);
    });
  }

  function renderRelease(manifest) {
    document.querySelectorAll("[data-ul-release]").forEach(node => {
      node.textContent = manifest.release;
    });
    document.documentElement.dataset.ulRelease = manifest.release;
  }

  async function boot(config = {}) {
    const urls = { ...DEFAULTS, ...config };
    const [manifest, conventions, audit] = await Promise.all([
      loadJson(urls.manifest),
      loadJson(urls.conventions),
      loadJson(urls.audit)
    ]);

    assertCoreSchemas(manifest, conventions, audit);
    renderGates(manifest);
    renderPages(manifest);
    renderAuditCounts(audit);
    renderRelease(manifest);

    window.UniverseLabState = Object.freeze({
      manifest, conventions, audit
    });

    document.dispatchEvent(new CustomEvent("universelab:ready", {
      detail: window.UniverseLabState
    }));

    return window.UniverseLabState;
  }

  window.UniverseLabRuntime = { boot };
})();
