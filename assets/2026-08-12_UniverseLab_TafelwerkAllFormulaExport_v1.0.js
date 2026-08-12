/* UniverseLab Tafelwerk all-formula export v1.0
 * Browser-only, dependency-free, no network requests and no telemetry.
 * Adds full-catalog exports without changing formula data or scientific status.
 */
(() => {
  'use strict';

  if (window.__UNIVERSELAB_TAFELWERK_ALL_EXPORT_V1__) return;
  window.__UNIVERSELAB_TAFELWERK_ALL_EXPORT_V1__ = true;

  const VERSION = '1.0';
  const STATUS_KEYS = ['established', 'derived', 'model', 'diagnostic', 'open', 'blocked', 'historical'];
  const $ = id => document.getElementById(id);
  const text = id => ($(id)?.textContent || '').trim();
  const escapeHtml = value => String(value ?? '')
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#039;');
  const isoDate = () => new Date().toISOString().slice(0, 10);
  const fileStem = () => `UniverseLab-Tafelwerk-Alle-Formeln-${isoDate()}`;

  function isTafelwerk() {
    return Boolean($('formulaList') && $('formulaName') && $('formulaEq') && $('totalCount'));
  }

  function saveUiState() {
    const values = {};
    document.querySelectorAll('#formulaInputs input[data-key]').forEach(input => {
      values[input.dataset.key] = input.value;
    });
    return {
      search: $('search')?.value || '',
      category: $('category')?.value || '',
      status: $('statusFilter')?.value || '',
      calcOnly: Boolean($('calcOnly')?.checked),
      selected: $('formulaList')?.value || '',
      listScrollTop: $('formulaList')?.scrollTop || 0,
      inputValues: values,
      activeId: document.activeElement?.id || ''
    };
  }

  function applyAllFilter() {
    const search = $('search');
    const category = $('category');
    const status = $('statusFilter');
    const calcOnly = $('calcOnly');
    if (!search || !category || !status || !calcOnly) throw new Error('Tafelwerk-Filter nicht gefunden.');
    search.value = '';
    category.value = '';
    status.value = '';
    calcOnly.checked = false;
    search.dispatchEvent(new Event('input', { bubbles: true }));
  }

  function restoreUiState(state) {
    const search = $('search');
    const category = $('category');
    const status = $('statusFilter');
    const calcOnly = $('calcOnly');
    const list = $('formulaList');
    if (!search || !category || !status || !calcOnly || !list) return;

    search.value = state.search;
    category.value = state.category;
    status.value = state.status;
    calcOnly.checked = state.calcOnly;
    search.dispatchEvent(new Event('input', { bubbles: true }));

    if (state.selected && [...list.querySelectorAll('option')].some(option => option.value === state.selected)) {
      list.value = state.selected;
      list.dispatchEvent(new Event('change', { bubbles: true }));
      document.querySelectorAll('#formulaInputs input[data-key]').forEach(input => {
        if (Object.prototype.hasOwnProperty.call(state.inputValues, input.dataset.key)) {
          input.value = state.inputValues[input.dataset.key];
          input.dispatchEvent(new Event('input', { bubbles: true }));
        }
      });
    }
    list.scrollTop = state.listScrollTop;
    if (state.activeId) document.getElementById(state.activeId)?.focus({ preventScroll: true });
  }

  function currentFormulaRecord(id) {
    const statusNode = $('formulaStatus');
    const statusKey = STATUS_KEYS.find(key => statusNode?.classList.contains(key)) || '';
    const result = text('formulaResult');
    const resultUnit = text('formulaResultUnit');
    const inputs = [...document.querySelectorAll('#formulaInputs .input-card')].map(card => {
      const input = card.querySelector('input[data-key]');
      return {
        key: input?.dataset.key || '',
        label: (card.querySelector('span')?.textContent || '').trim(),
        unit: (card.querySelector('small')?.textContent || '').trim(),
        default_value: input?.value ?? '',
        min: input?.getAttribute('min') ?? '',
        max: input?.getAttribute('max') ?? '',
        step: input?.getAttribute('step') ?? ''
      };
    });

    return {
      id,
      category: text('formulaCategory'),
      name: text('formulaName'),
      equation: text('formulaEq'),
      status: statusKey,
      status_label: text('formulaStatus'),
      description: text('formulaDesc'),
      unit_dimension: text('formulaUnit'),
      validity: text('formulaValidity'),
      limit_note: text('formulaLimit'),
      hint: text('formulaHint'),
      numerically_calculable: result !== 'symbolische Referenz',
      default_result: result,
      default_result_unit: resultUnit,
      inputs
    };
  }

  function collectAllFormulaRecords() {
    if (!isTafelwerk()) throw new Error('Tafelwerk ist nicht initialisiert.');
    const state = saveUiState();
    const list = $('formulaList');
    const root = document.documentElement;
    root.dataset.ulTafelwerkExportBusy = 'true';
    try {
      applyAllFilter();
      const options = [...list.querySelectorAll('option')].filter(option => option.value);
      const records = [];
      for (const option of options) {
        list.value = option.value;
        list.dispatchEvent(new Event('change', { bubbles: true }));
        records.push(currentFormulaRecord(option.value));
      }
      const expected = Number(text('totalCount'));
      if (Number.isFinite(expected) && expected > 0 && records.length !== expected) {
        throw new Error(`Vollständigkeitsprüfung fehlgeschlagen: ${records.length}/${expected} Formeln erfasst.`);
      }
      return records;
    } finally {
      restoreUiState(state);
      delete root.dataset.ulTafelwerkExportBusy;
    }
  }

  function payload(records) {
    return {
      schema: 'universelab.tafelwerk.all-formulas-export.v1',
      version: VERSION,
      title: 'UniverseLab Mathematisches Tafelwerk 2.0 — alle Formeln',
      generated_at: new Date().toISOString(),
      source: location.href,
      formula_count: records.length,
      formulas: records
    };
  }

  function download(content, mime, extension) {
    const blob = new Blob([content], { type: `${mime};charset=utf-8` });
    const url = URL.createObjectURL(blob);
    const anchor = document.createElement('a');
    anchor.href = url;
    anchor.download = `${fileStem()}.${extension}`;
    document.body.appendChild(anchor);
    anchor.click();
    anchor.remove();
    setTimeout(() => URL.revokeObjectURL(url), 1000);
  }

  function csvCell(value) {
    return `"${String(value ?? '').replace(/"/g, '""')}"`;
  }

  function csvOf(records) {
    const header = [
      'id', 'category', 'name', 'equation', 'status', 'status_label', 'description',
      'unit_dimension', 'validity', 'limit_note', 'hint', 'numerically_calculable',
      'default_result', 'default_result_unit', 'inputs_json'
    ];
    const rows = records.map(record => [
      record.id, record.category, record.name, record.equation, record.status,
      record.status_label, record.description, record.unit_dimension, record.validity,
      record.limit_note, record.hint, record.numerically_calculable,
      record.default_result, record.default_result_unit, JSON.stringify(record.inputs)
    ]);
    return `\uFEFF${[header, ...rows].map(row => row.map(csvCell).join(';')).join('\r\n')}\r\n`;
  }

  function markdownOf(records) {
    const groups = new Map();
    for (const record of records) {
      if (!groups.has(record.category)) groups.set(record.category, []);
      groups.get(record.category).push(record);
    }
    const out = [
      '# UniverseLab Mathematisches Tafelwerk 2.0 — alle Formeln',
      '',
      `Exportiert: ${new Date().toLocaleString('de-DE')}`,
      `Formeln: ${records.length}`,
      `Quelle: ${location.href}`,
      ''
    ];
    for (const [category, formulas] of groups) {
      out.push(`## ${category}`, '');
      for (const f of formulas) {
        out.push(`### ${f.name}`, '', `**Status:** ${f.status_label}`, '', '```text', f.equation, '```', '');
        if (f.description) out.push(f.description, '');
        out.push(`- Einheit / Dimension: ${f.unit_dimension || '–'}`);
        out.push(`- Gültigkeit: ${f.validity || '–'}`);
        out.push(`- Grenzfall / Hinweis: ${f.limit_note || '–'}`);
        out.push(`- Numerisch berechenbar: ${f.numerically_calculable ? 'ja' : 'nein'}`);
        if (f.inputs.length) {
          out.push('- Eingaben:');
          f.inputs.forEach(input => out.push(`  - ${input.label}: ${input.default_value}${input.unit ? ` ${input.unit}` : ''}`));
        }
        if (f.hint) out.push(`- Verwendungshinweis: ${f.hint}`);
        out.push('');
      }
    }
    return `${out.join('\n')}\n`;
  }

  function formulaHtml(record) {
    const inputRows = record.inputs.length
      ? `<table><thead><tr><th>Parameter</th><th>Standardwert</th><th>Einheit</th><th>Bereich / Schritt</th></tr></thead><tbody>${record.inputs.map(input => `<tr><td>${escapeHtml(input.label)}</td><td>${escapeHtml(input.default_value)}</td><td>${escapeHtml(input.unit || '–')}</td><td>${escapeHtml([input.min && `min ${input.min}`, input.max && `max ${input.max}`, input.step && `Schritt ${input.step}`].filter(Boolean).join(' · ') || '–')}</td></tr>`).join('')}</tbody></table>`
      : '<p class="muted">Keine numerischen Eingabeparameter.</p>';
    return `<article class="formula-card">
      <div class="formula-head"><h3>${escapeHtml(record.name)}</h3><span class="badge">${escapeHtml(record.status_label)}</span></div>
      <pre>${escapeHtml(record.equation)}</pre>
      <p>${escapeHtml(record.description)}</p>
      <dl><div><dt>Einheit / Dimension</dt><dd>${escapeHtml(record.unit_dimension || '–')}</dd></div><div><dt>Gültigkeit</dt><dd>${escapeHtml(record.validity || '–')}</dd></div><div><dt>Grenzfall / Hinweis</dt><dd>${escapeHtml(record.limit_note || '–')}</dd></div></dl>
      ${inputRows}
      <p><strong>Standardergebnis:</strong> ${escapeHtml(record.default_result || '–')} ${escapeHtml(record.default_result_unit || '')}</p>
      <p class="hint"><strong>Hinweis:</strong> ${escapeHtml(record.hint || '–')}</p>
    </article>`;
  }

  function htmlOf(records, autoPrint = false) {
    const groups = new Map();
    for (const record of records) {
      if (!groups.has(record.category)) groups.set(record.category, []);
      groups.get(record.category).push(record);
    }
    const categories = [...groups.entries()].map(([category, formulas]) => `<section class="category"><h2>${escapeHtml(category)} <small>${formulas.length} Formeln</small></h2>${formulas.map(formulaHtml).join('')}</section>`).join('');
    const printScript = autoPrint ? '<script>addEventListener("load",()=>setTimeout(()=>print(),120));<\/script>' : '';
    return `<!doctype html>
<html lang="de"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>UniverseLab Tafelwerk — alle Formeln</title>
<style>
*{box-sizing:border-box}body{max-width:1120px;margin:0 auto;padding:34px 28px 80px;color:#161616;background:#fff;font:15px/1.5 system-ui,-apple-system,"Segoe UI",sans-serif}header{padding-bottom:18px;border-bottom:3px solid #222}h1{margin:.2rem 0;font-size:2.1rem}h2{margin:2.3rem 0 1rem;padding-bottom:.45rem;border-bottom:2px solid #555}h2 small{font-size:.55em;color:#666}h3{margin:0}.formula-card{margin:0 0 1rem;padding:1rem;border:1px solid #aaa;border-radius:8px;break-inside:avoid-page}.formula-head{display:flex;justify-content:space-between;gap:1rem;align-items:start}.badge{padding:.2rem .5rem;border:1px solid #888;border-radius:999px;font-size:.78rem;font-weight:700;white-space:nowrap}pre{padding:.75rem;border:1px solid #bbb;background:#f5f5f5;white-space:pre-wrap;overflow-wrap:anywhere;font:14px/1.5 ui-monospace,SFMono-Regular,Consolas,monospace}dl{display:grid;grid-template-columns:repeat(3,1fr);gap:.6rem}dl div{padding:.55rem;border:1px solid #ccc}dt{font-weight:700;font-size:.8rem}dd{margin:.15rem 0 0}table{width:100%;border-collapse:collapse;margin:.7rem 0}th,td{padding:.4rem;border:1px solid #bbb;text-align:left;vertical-align:top}.hint,.muted{color:#555}.meta{color:#555}@media(max-width:700px){body{padding:20px 14px}dl{grid-template-columns:1fr}.formula-head{display:block}.badge{display:inline-block;margin-top:.4rem}}@media print{@page{size:A4;margin:14mm}body{max-width:none;padding:0;font-size:9.5pt}header{break-after:avoid-page}.category{break-before:page}.category:first-of-type{break-before:auto}.formula-card{border-color:#777;box-shadow:none}a{color:#000;text-decoration:none}}
</style></head><body><header><div>UniverseLab · mathematische Referenz und Funktionsbibliothek</div><h1>Mathematisches Tafelwerk 2.0 — alle Formeln</h1><p class="meta">${records.length} Formeln · Exportiert ${escapeHtml(new Date().toLocaleString('de-DE'))} · Quelle ${escapeHtml(location.href)}</p></header>${categories}${printScript}</body></html>`;
  }

  function printAll(records) {
    const target = window.open('', '_blank');
    if (!target) throw new Error('Druckfenster wurde vom Browser blockiert.');
    target.opener = null;
    target.document.open();
    target.document.write(htmlOf(records, true));
    target.document.close();
  }

  function addAllFormulaControls() {
    if (!isTafelwerk()) return false;
    const panel = document.querySelector('.ul-export-widget .ul-export-panel');
    if (!panel || panel.querySelector('[data-ul-tafelwerk-all-export]')) return Boolean(panel);

    const section = document.createElement('section');
    section.dataset.ulTafelwerkAllExport = 'true';
    section.dataset.noExport = 'true';
    section.style.cssText = 'margin-top:12px;padding-top:12px;border-top:1px solid rgba(255,255,255,.18)';

    const heading = document.createElement('strong');
    heading.textContent = `Tafelwerk komplett — alle ${text('totalCount') || '–'} Formeln`;

    const note = document.createElement('p');
    note.className = 'ul-export-note';
    note.textContent = 'Exportiert immer den vollständigen Formelkatalog — unabhängig von Suche, Kategorie, Status oder „nur berechenbar“. Die aktuelle Auswahl wird danach wiederhergestellt.';

    const actions = document.createElement('div');
    actions.className = 'ul-export-actions';
    const definitions = [
      ['print', 'Alle Formeln · PDF/Drucken'],
      ['html', 'Alle Formeln · HTML'],
      ['markdown', 'Alle Formeln · Markdown'],
      ['json', 'Alle Formeln · JSON'],
      ['csv', 'Alle Formeln · CSV']
    ];
    definitions.forEach(([action, label], index) => {
      const button = document.createElement('button');
      button.type = 'button';
      button.dataset.tafelwerkExportAction = action;
      button.textContent = label;
      if (index === 0) button.classList.add('primary');
      actions.appendChild(button);
    });

    const status = document.createElement('p');
    status.className = 'ul-export-status';
    status.setAttribute('aria-live', 'polite');

    actions.addEventListener('click', event => {
      const button = event.target.closest('[data-tafelwerk-export-action]');
      if (!button) return;
      const action = button.dataset.tafelwerkExportAction;
      status.textContent = 'Alle Formeln werden zusammengestellt …';
      [...actions.querySelectorAll('button')].forEach(item => { item.disabled = true; });
      try {
        const records = collectAllFormulaRecords();
        if (action === 'print') printAll(records);
        else if (action === 'html') download(htmlOf(records), 'text/html', 'html');
        else if (action === 'markdown') download(markdownOf(records), 'text/markdown', 'md');
        else if (action === 'json') download(`${JSON.stringify(payload(records), null, 2)}\n`, 'application/json', 'json');
        else if (action === 'csv') download(csvOf(records), 'text/csv', 'csv');
        status.textContent = `${records.length} Formeln vollständig für ${action === 'print' ? 'Druck/PDF' : action.toUpperCase()} vorbereitet.`;
      } catch (error) {
        console.error('[UniverseLab Tafelwerk All Export]', error);
        status.textContent = `Export fehlgeschlagen: ${error.message || error}`;
      } finally {
        [...actions.querySelectorAll('button')].forEach(item => { item.disabled = false; });
      }
    });

    section.append(heading, note, actions, status);
    panel.appendChild(section);
    document.documentElement.dataset.ulTafelwerkAllExportVersion = VERSION;
    return true;
  }

  function init(attempt = 0) {
    if (addAllFormulaControls()) return;
    if (attempt < 40) setTimeout(() => init(attempt + 1), 50);
  }

  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', () => init(), { once: true });
  else init();
})();
