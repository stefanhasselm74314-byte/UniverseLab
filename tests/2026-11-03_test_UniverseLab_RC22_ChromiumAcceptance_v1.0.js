#!/usr/bin/env node
/*
 * UniverseLab RC22: real headless Chromium, temporary isolated HTTP staging.
 * Neither the source tree, GitHub Pages, nor the published RC19 manifest changes.
 * Mobile Chromium emulation is NOT an actual Android/Opera/Samsung device test.
 * Installation is an in-memory HTTP response overlay ONLY.
 */
'use strict';

const assert = require('node:assert/strict');
const crypto = require('node:crypto');
const fs = require('node:fs');
const http = require('node:http');
const path = require('node:path');
const { chromium } = require('playwright');

const REPO = path.resolve(__dirname, '..');
if (!process.argv[2]) throw Error('RC22_EXPLICIT_STAGING_PATH_REQUIRED');
const STAGE = path.resolve(process.argv[2]);
if (STAGE === REPO || STAGE.startsWith(REPO + path.sep)) throw Error('RC22_STAGING_MUST_BE_OUTSIDE_REPOSITORY');
const EVIDENCE_DIR = process.argv[3] ? path.resolve(process.argv[3]) : null;
const MANIFEST = JSON.parse(fs.readFileSync(path.join(REPO, 'governance/2026-11-03_UniverseLab_RC19_PublicFiles_v1.0_DRAFT.json'), 'utf8'));
const REGISTRY = JSON.parse(fs.readFileSync(path.join(REPO, 'registry/2026-08-07_ULSH_SolverDevelopmentProgram_v1.0.json'), 'utf8'));
const CANDIDATE = fs.readFileSync(path.join(REPO, 'drafts/2026-11-03_UniverseLab_RC21_SafeDocumentRouter_v1.0_DRAFT.js'));
const ROUTER = 'assets/2026-08-27_UniverseLab_DocumentLinkRouter_v1.0.js';
const DOC = MANIFEST.files.map(f => f.path).find(p => p.endsWith('.md'));
const SOURCE = ROUTER;
const GITHUB = 'https://github.com/stefanhasselm74314-byte/UniverseLab/blob/main/';
const PREFIX = '/UniverseLab/';
const ALLOWED = new Set(MANIFEST.files.map(f => f.path));
const counters = { assertions: 0, browser_sessions: 0, baseline_rc20_404: 0, desktop_overlay: 0, mobile_chromium_emulated: 0, service_worker_registered: 0, service_worker_controlled: 0, dynamic_roadmaps: 0, offline_failure_expected: 0, offline_recovery: 0, visual_overflow_warnings: [] };

async function screenshot(page, name) {
  if (EVIDENCE_DIR) await page.screenshot({ path: path.join(EVIDENCE_DIR, name), fullPage: true, animations: 'disabled' });
}

function eq(actual, wanted, label) { assert.equal(actual, wanted, label); counters.assertions++; }
function ok(actual, label) { assert.ok(actual, label); counters.assertions++; }

function responseType(p) {
  const ext = path.extname(p).toLowerCase();
  return ({ '.html':'text/html; charset=utf-8', '.js':'text/javascript; charset=utf-8',
    '.json':'application/json; charset=utf-8', '.css':'text/css; charset=utf-8',
    '.md':'text/markdown; charset=utf-8', '.txt':'text/plain; charset=utf-8',
    '.svg':'image/svg+xml', '.xml':'application/xml; charset=utf-8',
    '.webmanifest':'application/manifest+json', '.png':'image/png',
    '.jpg':'image/jpeg', '.jpeg':'image/jpeg', '.ico':'image/x-icon' })[ext] || 'application/octet-stream';
}

async function servePublic({ overlay }) {
  const counts = { total: 0, router: 0, blocked: 0 };
  const server = http.createServer((req, res) => {
    counts.total++;
    if (req.method !== 'GET' && req.method !== 'HEAD') {
      res.writeHead(405); res.end(); return;
    }
    let rel;
    try {
      const raw = new URL(req.url, 'http://127.0.0.1');
      if (!raw.pathname.startsWith(PREFIX)) throw Error('WRONG_PREFIX');
      rel = decodeURIComponent(raw.pathname.slice(PREFIX.length)) || 'index.html';
      if (!ALLOWED.has(rel)) throw Error('PATH_NOT_ALLOWED');
    } catch (_error) {
      counts.blocked++;
      res.writeHead(404, { 'Content-Type': 'text/plain' }); res.end('RC22_NOT_IN_PUBLIC_MANIFEST'); return;
    }
    const asset = overlay && rel === ROUTER ? CANDIDATE : fs.readFileSync(path.join(STAGE, rel));
    if (rel === ROUTER) counts.router++;
    res.writeHead(200, { 'Content-Type': responseType(rel), 'Content-Length': asset.length, 'Cache-Control': 'no-store' });
    res.end(req.method === 'HEAD' ? undefined : asset);
  });
  await new Promise((resolve, reject) => { server.once('error', reject); server.listen(0, '127.0.0.1', resolve); });
  return { server, base: `http://127.0.0.1:${server.address().port}`, counts };
}

async function goto(page, site, route) {
  const response = await page.goto(site.base + PREFIX + route, { waitUntil: 'domcontentloaded', timeout: 15000 });
  eq(response.status(), 200, 'HTML route ' + route);
  return response;
}

async function waitRouter(page, site) {
  // An inserted whitelisted anchor is also a timing canary for the real router.
  await page.evaluate(({ doc, github }) => {
    const old = document.getElementById('rc22-router-canary');
    if (old) old.remove();
    const a = document.createElement('a');
    a.id = 'rc22-router-canary';
    a.textContent = 'RC22 positive canary';
    a.href = github + doc;
    document.body.append(a);
  }, { doc: DOC, github: GITHUB });
  await page.waitForFunction(() => document.getElementById('rc22-router-canary')?.dataset.ulSafeDocumentRouter === '1', null, { timeout: 12000 });
  const href = await page.locator('#rc22-router-canary').getAttribute('href');
  const url = new URL(href, site.base);
  eq(url.pathname, PREFIX + '2026-08-27_UniverseLab_DocumentViewer_v1.0.html', 'whitelisted doc viewer');
  eq(url.searchParams.get('src'), PREFIX + DOC, 'whitelisted exact src');
  return href;
}

async function checkExclusions(page, selectors) {
  for (const [label, selector, resource] of selectors) {
    await page.locator(selector).first().waitFor({ timeout: 10000 });
    const href = await page.locator(selector).first().getAttribute('href');
    eq(href, GITHUB + resource, label + ': unchanged GitHub URL');
  }
}

async function checkViewer(page, site, kind, resource, href) {
  const response = await page.goto(new URL(href, site.base).href, { waitUntil: 'domcontentloaded', timeout: 15000 });
  eq(response.status(), 200, kind + ' viewer HTML HTTP 200');
  await page.waitForFunction(() => {
    const f = document.getElementById('fileName');
    const size = document.getElementById('size');
    const e = document.getElementById('error');
    return f?.textContent !== '–' && size?.textContent !== '–' &&
      (e?.classList.contains('hidden') || !e);
  }, null, { timeout: 12000 });
  eq(await page.locator('#fileName').textContent(), resource.split('/').pop(), kind + ' displayed filename');
  const error = page.locator('#error');
  ok(await error.count() === 0 || await error.evaluate(e => e.classList.contains('hidden')), kind + ' no fetch error');
  const text = await page.locator('#sourceLabel').textContent();
  eq(text, PREFIX + resource, kind + ' exact source label');
  const rawUrl = await page.locator('#rawOpen').getAttribute('href');
  eq(new URL(rawUrl, site.base).pathname, PREFIX + resource, kind + ' raw source local HTTP path');
  const fetched = await page.request.get(site.base + PREFIX + resource);
  eq(fetched.status(), 200, kind + ' source HTTP 200');
  ok((await fetched.body()).length > 0, kind + ' nonempty source');
  const viewport = await page.evaluate(() => ({ width: window.innerWidth, scrollWidth: document.documentElement.scrollWidth }));
  if (viewport.scrollWidth > viewport.width + 2) counters.visual_overflow_warnings.push({ kind, ...viewport });
}

async function checkBaseline(browser, site) {
  const context = await browser.newContext({ serviceWorkers: 'block' });
  counters.browser_sessions++;
  const page = await context.newPage();
  try {
    await goto(page, site, 'solver-hub.html');
    await page.waitForFunction(() => [...document.querySelectorAll('a')].some(a => a.textContent.trim() === 'ULSH-01 Roadmap' && a.dataset.ulDocumentSource?.includes('science/solver-hub/')), null, { timeout: 12000 });
    const href = await page.getByRole('link', { name: 'ULSH-01 Roadmap' }).getAttribute('href');
    const viewer = new URL(href, site.base);
    eq(viewer.pathname, PREFIX + '2026-08-27_UniverseLab_DocumentViewer_v1.0.html', 'existing router improperly redirects excluded roadmap');
    eq(viewer.searchParams.get('src'), PREFIX + REGISTRY.solvers[0].roadmap_path, 'existing router targets excluded roadmap');
    const response = await page.goto(viewer.href, { waitUntil: 'domcontentloaded' });
    eq(response.status(), 200, 'existing viewer HTML responds 200');
    await page.waitForFunction(() => !document.querySelector('#error')?.classList.contains('hidden'), null, { timeout: 12000 });
    ok((await page.locator('#error').textContent()).includes('404'), 'existing viewer source fetch returns 404');
    counters.baseline_rc20_404++;
  } finally { await context.close(); }
}

async function checkDesktop(browser, site) {
  const context = await browser.newContext({ serviceWorkers: 'block', viewport: { width: 1340, height: 900 } });
  counters.browser_sessions++;
  const page = await context.newPage();
  try {
    await goto(page, site, 'solver-hub.html');
    await waitRouter(page, site);
    await checkExclusions(page, [
      ['Python-Kern', 'a:has-text("Python-Kern")', 'md2s_bvp_solver_v1_0.py'],
      ['ULSH-01 Roadmap', 'a:has-text("ULSH-01 Roadmap")', REGISTRY.solvers[0].roadmap_path],
    ]);
    await goto(page, site, 'source.html');
    await waitRouter(page, site);
    await checkExclusions(page, [['Privacy-Validator', 'a:has-text("Privacy-Validator im Repository")', 'tools/2026-08-03_validate_public_repository_privacy_v1.0.py']]);
    await goto(page, site, 'solver-hub-en.html');
    // On the first unregistered local HTTP visit there is no GlobalShell and no SW-injected router.
    await checkExclusions(page, [['English Python core', 'a:has-text("Python core")', 'md2s_bvp_solver_v1_0.py']]);
    await goto(page, site, 'solver-hub.html');
    const docHref = await waitRouter(page, site);
    await screenshot(page, 'rc22-desktop-solver-hub-overlay.png');
    await checkViewer(page, site, 'document', DOC, docHref);
    counters.desktop_overlay++;
  } finally { await context.close(); }
}

async function checkMobile(browser, site) {
  const context = await browser.newContext({
    serviceWorkers: 'allow', viewport: { width: 412, height: 915 }, deviceScaleFactor: 3,
    isMobile: true, hasTouch: true,
    userAgent: 'Mozilla/5.0 (Linux; Android 17; SM-S928B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Mobile Safari/537.36',
  });
  counters.browser_sessions++;
  const page = await context.newPage();
  try {
    await goto(page, site, 'solver-hub.html');
    await waitRouter(page, site);
    await checkExclusions(page, [['mobile roadmap', 'a:has-text("ULSH-01 Roadmap")', REGISTRY.solvers[0].roadmap_path]]);
    const ua = await page.evaluate(() => navigator.userAgent);
    ok(ua.includes('SM-S928B'), 'emulated mobile user-agent');
    const sourceLink = await page.evaluate(({ source, github }) => {
      const a = document.createElement('a'); a.id = 'rc22-mobile-source'; a.href = github + source;
      a.textContent = 'RC22 source'; document.body.append(a); return a.href;
    }, { source: SOURCE, github: GITHUB });
    ok(sourceLink.includes('github.com'), 'new async source has original URL until observed');
    await page.waitForFunction(() => document.querySelector('#rc22-mobile-source')?.dataset.ulSafeDocumentRouter === '1', null, { timeout: 12000 });
    const rewritten = await page.locator('#rc22-mobile-source').getAttribute('href');
    eq(new URL(rewritten, site.base).pathname, PREFIX + '2026-08-27_UniverseLab_SourceTextViewer_v1.0.html', 'mobile source viewer route');
    await page.locator('#rc22-mobile-source').tap();
    await page.waitForURL('**/2026-08-27_UniverseLab_SourceTextViewer_v1.0.html?src=*', { timeout: 12000 });
    await checkViewer(page, site, 'source', SOURCE, page.url());
    await screenshot(page, 'rc22-mobile-source-viewer-emulated.png');
    counters.mobile_chromium_emulated++;

    // Explicit local registration: the site's HTTPS-only auto-register condition
    // is NOT tested by HTTP localhost. Verify the real SW fetch/injection path.
    const reg = await page.evaluate(async () => {
      const sw = '/UniverseLab/2026-08-19_UniverseLab_SitePrintExportServiceWorker_v1.0.js';
      const r = await navigator.serviceWorker.register(sw, { scope: '/UniverseLab/' });
      await navigator.serviceWorker.ready;
      return r.active?.scriptURL || '';
    });
    ok(reg.includes('SitePrintExportServiceWorker'), 'service worker script registered on localhost');
    counters.service_worker_registered++;
    await goto(page, site, '2026-08-07_ULSH_SolverDevelopmentProgram_v1.0.html');
    const controlled = await page.evaluate(() => Boolean(navigator.serviceWorker.controller));
    ok(controlled, 'SW controls second navigation');
    counters.service_worker_controlled++;
    await page.waitForFunction(() => document.querySelectorAll('#solverGrid a').length === 14, null, { timeout: 12000 });
    const links = await page.locator('#solverGrid a').evaluateAll(items => items.map(a => a.getAttribute('href')));
    eq(links.length, 14, '14 actual asynchronously rendered registry roadmap links');
    const expected = new Set(REGISTRY.solvers.map(s => GITHUB + s.roadmap_path));
    for (const href of links) ok(expected.has(href), 'SW/observer retains excluded dynamic GitHub roadmap');
    counters.dynamic_roadmaps = 14;
    await waitRouter(page, site);
    await screenshot(page, 'rc22-mobile-program-sw-emulated.png');

    await context.setOffline(true);
    let blockedOffline = false;
    try { await page.goto(site.base + PREFIX + 'solver-hub.html', { waitUntil: 'domcontentloaded', timeout: 8000 }); }
    catch (_err) { blockedOffline = true; }
    ok(blockedOffline, 'no unsupported offline cache claim: navigation fails without network');
    counters.offline_failure_expected++;
    await context.setOffline(false);
    await goto(page, site, 'solver-hub.html');
    await waitRouter(page, site);
    counters.offline_recovery++;
    await page.evaluate(async () => {
      for (const registration of await navigator.serviceWorker.getRegistrations()) await registration.unregister();
      for (const name of await caches.keys()) await caches.delete(name);
    });
  } finally { await context.close(); }
}

async function main() {
  if (EVIDENCE_DIR) fs.mkdirSync(EVIDENCE_DIR, { recursive: true });
  ok(fs.existsSync(STAGE), 'RC19 staging tree exists');
  eq(MANIFEST.files.length, 446, 'pinned RC19 manifest count');
  ok(ALLOWED.has(DOC) && ALLOWED.has(SOURCE), 'tested positive resources manifest-bound');
  ok(ALLOWED.has(ROUTER), 'original active router exists in static stage');
  for (const x of REGISTRY.solvers) ok(!ALLOWED.has(x.roadmap_path), 'dynamic target excluded from static stage');
  ok(!ALLOWED.has('md2s_bvp_solver_v1_0.py'), 'static negative target excluded');
  for (const f of MANIFEST.files) ok(fs.existsSync(path.join(STAGE, f.path)), 'staged manifest entry present');
  const baseline = await servePublic({ overlay: false });
  const overlay = await servePublic({ overlay: true });
  let browser;
  try {
    browser = await chromium.launch({ headless: true });
    await checkBaseline(browser, baseline);
    await checkDesktop(browser, overlay);
    await checkMobile(browser, overlay);
    ok(overlay.counts.router > 0, 'candidate served by in-memory overlay at original router URL');
    ok(baseline.counts.router > 0, 'original router served in unmodified baseline');
    ok(overlay.counts.blocked >= 0, 'public allowlist HTTP handler active');
    const report = { status: 'RC22_CHROMIUM_REAL_BROWSER_QA_PASS_NOT_RELEASE', ...counters,
      original_rc19_stage_files: ALLOWED.size, browser_engine: 'chromium', browser_version: browser.version(),
      rc19_manifest_sha256: crypto.createHash('sha256').update(fs.readFileSync(path.join(REPO, 'governance/2026-11-03_UniverseLab_RC19_PublicFiles_v1.0_DRAFT.json'))).digest('hex'),
      rc21_candidate_sha256: crypto.createHash('sha256').update(CANDIDATE).digest('hex'),
      emulated_android_is_real_device: false, opera_tested: false, actual_github_pages_tested: false,
      candidate_overlay_writes_to_published_files: false, release_gate: 'HOLD' };
    if (EVIDENCE_DIR) fs.writeFileSync(path.join(EVIDENCE_DIR, 'rc22-browser-evidence.json'), JSON.stringify(report, null, 2) + '\n');
    console.log(JSON.stringify(report));
  } finally {
    if (browser) await browser.close();
    await Promise.all([new Promise(resolve => baseline.server.close(resolve)), new Promise(resolve => overlay.server.close(resolve))]);
  }
}

main().catch(err => { console.error('RC22_CHROMIUM_QA_HOLD', err.stack || String(err)); process.exitCode = 2; });
