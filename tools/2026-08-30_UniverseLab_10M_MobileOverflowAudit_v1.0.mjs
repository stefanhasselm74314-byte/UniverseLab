import { chromium } from 'playwright';
import fs from 'node:fs';

const BASE = process.env.UNIVERSELAB_BASE_URL || 'https://stefanhasselm74314-byte.github.io/UniverseLab/';
const PATH = '2026-08-29_UniverseLab_Hyperzeit_10M_ResearchProgram_v1.0.html';
const viewports = [
  { name: 'narrow-360', width: 360, height: 800 },
  { name: 'galaxy-class-412', width: 412, height: 915 }
];
const report = { schema_version: '1.0', base_url: BASE, page: PATH, status: 'PASS', checks: [] };
const push = (name, ok, detail = {}) => {
  report.checks.push({ name, ok, ...detail });
  if (!ok) report.status = 'FAIL';
};

const browser = await chromium.launch({ headless: true });
try {
  for (const vp of viewports) {
    const context = await browser.newContext({ viewport: { width: vp.width, height: vp.height }, deviceScaleFactor: 1, locale: 'de-DE' });
    const page = await context.newPage();
    const browserErrors = [];
    const httpFailures = [];
    page.on('pageerror', e => browserErrors.push(String(e)));
    page.on('console', m => { if (m.type() === 'error') browserErrors.push(`console: ${m.text()}`); });
    page.on('response', r => { if (r.status() >= 400) httpFailures.push({ status: r.status(), url: r.url() }); });

    const url = new URL(PATH, BASE);
    url.searchParams.set('ul_mobile_overflow_audit', Date.now());
    const response = await page.goto(url.href, { waitUntil: 'networkidle', timeout: 45000 });
    if (!response?.ok()) throw new Error(`HTTP ${response?.status()} ${url.href}`);
    await page.waitForTimeout(350);

    const metrics = await page.evaluate(() => {
      const rect = selector => {
        const el = document.querySelector(selector);
        if (!el) return null;
        const r = el.getBoundingClientRect();
        return { left: r.left, right: r.right, width: r.width };
      };
      const root = document.documentElement;
      const body = document.body;
      return {
        innerWidth: window.innerWidth,
        rootClientWidth: root.clientWidth,
        rootScrollWidth: root.scrollWidth,
        bodyClientWidth: body.clientWidth,
        bodyScrollWidth: body.scrollWidth,
        shell: rect('.ul-shell'),
        shellRow: rect('.ul-shell__row'),
        localNav: rect('body > nav, .ul-localnav'),
        main: rect('main'),
        hero: rect('.hero'),
        hold: rect('.notice.hold'),
        tablewrap: rect('.tablewrap')
      };
    });

    const within = r => !r || (r.left >= -1 && r.right <= metrics.innerWidth + 1 && r.width <= metrics.innerWidth + 2);
    const rootOverflow = metrics.rootScrollWidth - metrics.rootClientWidth;
    const bodyOverflow = metrics.bodyScrollWidth - metrics.bodyClientWidth;

    push(`${vp.name}_document_no_horizontal_overflow`, rootOverflow <= 1 && bodyOverflow <= 1, { rootOverflow, bodyOverflow, metrics });
    push(`${vp.name}_primary_blocks_contained`, [metrics.shell, metrics.shellRow, metrics.localNav, metrics.main, metrics.hero, metrics.hold, metrics.tablewrap].every(within), { metrics });
    push(`${vp.name}_runtime_health`, browserErrors.length === 0 && httpFailures.length === 0, { browserErrors, httpFailures });

    await context.close();
  }
} catch (e) {
  report.status = 'FAIL';
  report.checks.push({ name: 'audit_exception', ok: false, error: String(e?.stack || e) });
} finally {
  await browser.close();
}

fs.writeFileSync('10m-mobile-overflow-report.json', JSON.stringify(report, null, 2));
console.log(JSON.stringify(report, null, 2));
if (report.status !== 'PASS') process.exit(1);
