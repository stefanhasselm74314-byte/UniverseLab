#!/usr/bin/env node
/* RC21 browser-like VM tests. This is NOT a real browser or Android test. */
'use strict';

const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');

const ROOT = path.resolve(__dirname, '..');
const SCRIPT = fs.readFileSync(path.join(ROOT, 'drafts/2026-11-03_UniverseLab_RC21_SafeDocumentRouter_v1.0_DRAFT.js'), 'utf8');
const MANIFEST = JSON.parse(fs.readFileSync(path.join(ROOT, 'governance/2026-11-03_UniverseLab_RC19_PublicFiles_v1.0_DRAFT.json'), 'utf8'));
const REGISTRY = JSON.parse(fs.readFileSync(path.join(ROOT, 'registry/2026-08-07_ULSH_SolverDevelopmentProgram_v1.0.json'), 'utf8'));
const PAGE = 'https://stefanhasselm74314-byte.github.io/UniverseLab/index.html';
const GITHUB = 'https://github.com/stefanhasselm74314-byte/UniverseLab/blob/main/';
const ROUTABLE = MANIFEST.files.map(file => file.path).filter(p => /\.(md|markdown|txt|yml|yaml|py|js|mjs|cjs|ts|tsx|jsx|css|scss|sh|bash|zsh|ps1|bat|cmd|toml|ini|cfg|conf|xml|tex|bib|sql|r|jl|java|c|h|cpp|hpp|log|properties)$/i.test(p));
const EXCLUDED = [
  'md2s_bvp_solver_v1_0.py',
  'science/solver-hub/2026-08-07_ULSH-01_MD2S-BVP_Roadmap_v1.0.md',
  'tools/2026-08-03_validate_public_repository_privacy_v1.0.py',
];

let checks = 0;
function ok(condition, detail) { assert.ok(condition, detail); checks++; }
function eq(actual, expected, detail) { assert.equal(actual, expected, detail); checks++; }

class Anchor {
  constructor(href, attrs = {}) {
    this.nodeType = 1;
    this.tagName = 'A';
    this.dataset = { ...(attrs.dataset || {}) };
    this.attrs = new Map([['href', href]]);
    for (const key of attrs.attributes || []) this.attrs.set(key, '');
  }
  hasAttribute(name) { return this.attrs.has(name); }
  getAttribute(name) { return this.attrs.get(name) ?? null; }
  setAttribute(name, value) { this.attrs.set(name, value); }
  get href() { return new URL(this.attrs.get('href'), PAGE).href; }
  set href(value) { this.attrs.set('href', value); }
  querySelectorAll() { return []; }
}

class Group {
  constructor(...children) { this.nodeType = 1; this.tagName = 'DIV'; this.children = children; }
  querySelectorAll(selector) {
    assert.equal(selector, 'a[href]');
    return this.children.flatMap(child => child.tagName === 'A' ? [child] : child.querySelectorAll(selector));
  }
}

function mount(initial = [], options = {}) {
  const state = { observer: null, boot: null };
  const document = {
    readyState: options.loading ? 'loading' : 'complete',
    documentElement: options.noDocumentElement ? null : new Group(...initial),
    querySelectorAll(selector) { assert.equal(selector, 'a[href]'); return initial; },
    addEventListener(event, cb, opts) { eq(event, 'DOMContentLoaded', 'event'); ok(opts.once, 'single init'); state.boot = cb; },
  };
  class FakeObserver {
    constructor(callback) { this.callback = callback; state.observer = this; }
    observe(target, config) {
      eq(target, document.documentElement, 'observer root');
      ok(config.subtree && config.childList && config.attributes && config.attributeFilter.includes('href'), 'observer configuration');
    }
    trigger(records) { this.callback(records); }
  }
  const location = { href: PAGE, origin: new URL(PAGE).origin };
  vm.runInNewContext(SCRIPT, { URL, document, location, MutationObserver: options.noObserver ? undefined : FakeObserver }, { timeout: 1500 });
  return state;
}

function assertRouted(anchor, rel, query = '') {
  const kind = /\.(md|markdown|txt|yml|yaml)$/i.test(rel) ? 'doc' : 'source';
  const view = new URL(anchor.href);
  const wantedViewer = kind === 'doc' ? '2026-08-27_UniverseLab_DocumentViewer_v1.0.html' : '2026-08-27_UniverseLab_SourceTextViewer_v1.0.html';
  eq(view.origin, new URL(PAGE).origin, `same-origin viewer ${rel}`);
  eq(view.pathname, '/UniverseLab/' + wantedViewer, `correct viewer ${rel}`);
  eq(view.searchParams.get('src'), '/UniverseLab/' + rel + query, `exact src ${rel}`);
  eq(anchor.dataset.ulDocumentSource, '/UniverseLab/' + rel + query, `dataset src ${rel}`);
  eq(anchor.dataset.ulDocumentKind, kind, `dataset kind ${rel}`);
}

function assertPreserved(anchor, initial, reason) {
  eq(anchor.getAttribute('href'), initial, reason + ': href retained');
  ok(!Object.hasOwn(anchor.dataset, 'ulDocumentSource'), reason + ': no stale source metadata');
  ok(!Object.hasOwn(anchor.dataset, 'ulDocumentKind'), reason + ': no stale kind metadata');
}

function main() {
  eq(ROUTABLE.length, 77, 'RC19 manifest derived routable paths');
  eq(new Set(ROUTABLE).size, 77, 'no duplicate public source paths');
  eq(REGISTRY.solvers.length, 14, '14 dynamic roadmap paths');
  const set = new Set(MANIFEST.files.map(f => f.path));
  for (const blocked of EXCLUDED) ok(!set.has(blocked), 'excluded static ' + blocked);
  for (const solver of REGISTRY.solvers) ok(!set.has(solver.roadmap_path), 'excluded roadmap ' + solver.roadmap_path);
  ok(SCRIPT.includes('CANDIDATE ONLY; NOT INSTALLED OR DEPLOYED'), 'candidate marker');

  const localAnchors = ROUTABLE.map(rel => new Anchor('/UniverseLab/' + rel));
  const githubAnchors = ROUTABLE.map(rel => new Anchor(GITHUB + rel));
  const initial = [...localAnchors, ...githubAnchors];
  const state = mount(initial);
  ok(state.observer !== null, 'MutationObserver installed');
  ROUTABLE.forEach((rel, i) => {
    assertRouted(localAnchors[i], rel);
    assertRouted(githubAnchors[i], rel);
  });
  // The router must be idempotent when its own href mutation is observed.
  const stable = initial.map(a => a.href);
  state.observer.trigger(initial.map(target => ({ type: 'attributes', target })));
  initial.forEach((a, i) => eq(a.href, stable[i], 'idempotence ' + i));

  const blockedLinks = EXCLUDED.map(rel => new Anchor(GITHUB + rel));
  const dynamicRoadmaps = REGISTRY.solvers.map(s => new Anchor(GITHUB + s.roadmap_path));
  const excludedAll = [...blockedLinks, ...dynamicRoadmaps];
  state.observer.trigger([{ type: 'childList', addedNodes: [new Group(...excludedAll)] }]);
  excludedAll.forEach(a => assertPreserved(a, a.getAttribute('href'), 'external excluded resource'));

  const laterDoc = new Anchor(GITHUB + ROUTABLE.find(rel => rel.endsWith('.md')));
  const laterSource = new Anchor('/UniverseLab/' + ROUTABLE.find(rel => rel.endsWith('.js')));
  const nest = new Group(new Group(laterDoc, laterSource));
  state.observer.trigger([{ type: 'childList', addedNodes: [nest] }]);
  assertRouted(laterDoc, ROUTABLE.find(rel => rel.endsWith('.md')));
  assertRouted(laterSource, ROUTABLE.find(rel => rel.endsWith('.js')));

  const hostile = [
    'https://github.com.evil.example/stefanhasselm74314-byte/UniverseLab/blob/main/' + ROUTABLE[0],
    'https://github.com:8443/stefanhasselm74314-byte/UniverseLab/blob/main/' + ROUTABLE[0],
    'http://github.com/stefanhasselm74314-byte/UniverseLab/blob/main/' + ROUTABLE[0],
    'https://github.com/another-owner/UniverseLab/blob/main/' + ROUTABLE[0],
    'https://github.com/stefanhasselm74314-byte/UniverseLab/blob/dev/' + ROUTABLE[0],
    'https://github.com/stefanhasselm74314-byte/UniverseLab/raw/main/' + ROUTABLE[0],
    'https://external.example/UniverseLab/' + ROUTABLE[0],
    '/UniverSeLab/' + ROUTABLE[0],
    '/UniverseLab/%2eHidden/' + ROUTABLE[0],
    '/UniverseLab/other%252fpath.md',
    '/UniverseLab/assets/not-whitelisted.md',
    '/UniverseLab/governance/internal.md',
    '/UniverseLab/' + ROUTABLE[0] + '/trailing',
    '/UniverseLab/' + ROUTABLE.find(rel => rel.includes('/')).replaceAll('/', '%2F'),
  ];
  const adversarial = hostile.map(href => new Anchor(href));
  state.observer.trigger([{ type: 'childList', addedNodes: adversarial }]);
  adversarial.forEach((a, i) => assertPreserved(a, hostile[i], 'hostile/disallowed ' + i));

  const doc = ROUTABLE.find(p => p.endsWith('.md'));
  const flags = [
    { attributes: ['download'] },
    { dataset: { ulRawLink: '1' } },
    { dataset: { ulNoDocumentViewer: '1' } },
    { dataset: { ulNoDataViewer: '1' } },
  ];
  const skipped = flags.map(f => new Anchor(GITHUB + doc, f));
  state.observer.trigger([{ type: 'childList', addedNodes: skipped }]);
  skipped.forEach(a => assertPreserved(a, GITHUB + doc, 'explicit opt-out'));

  const query = new Anchor(GITHUB + doc + '?plain=1#section');
  state.observer.trigger([{ type: 'childList', addedNodes: [query] }]);
  assertRouted(query, doc, '?plain=1');
  const noObserver = new Anchor(GITHUB + doc);
  mount([noObserver], { noObserver: true });
  assertRouted(noObserver, doc);
  const defer = new Anchor(GITHUB + doc);
  const before = defer.href;
  const delayed = mount([defer], { loading: true });
  eq(defer.href, before, 'no early DOM rewrite');
  ok(delayed.boot !== null, 'DOMContentLoaded scheduled');
  delayed.boot();
  assertRouted(defer, doc);

  const changed = new Anchor(GITHUB + EXCLUDED[0]);
  state.observer.trigger([{ type: 'childList', addedNodes: [changed] }]);
  assertPreserved(changed, GITHUB + EXCLUDED[0], 'initially excluded');
  changed.setAttribute('href', GITHUB + doc);
  state.observer.trigger([{ type: 'attributes', target: changed }]);
  assertRouted(changed, doc);
  changed.setAttribute('href', GITHUB + EXCLUDED[0]);
  state.observer.trigger([{ type: 'attributes', target: changed }]);
  assertPreserved(changed, GITHUB + EXCLUDED[0], 'reverted to excluded');

  console.log(JSON.stringify({ status: 'RC21_VM_PASS_NOT_BROWSER', assertions: checks, positive_manifest_paths: ROUTABLE.length, tested_static_excluded: EXCLUDED.length, tested_dynamic_roadmaps: REGISTRY.solvers.length, real_browser_tested: false, real_android_tested: false }));
}

main();
