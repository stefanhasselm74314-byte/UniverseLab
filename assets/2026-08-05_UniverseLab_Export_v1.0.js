/* UniverseLab export module v1.0
 * Browser-only, dependency-free, no network requests and no telemetry.
 * Exports: print/PDF, Markdown, TXT, standalone HTML and clipboard text.
 */
(() => {
  'use strict';

  if (window.__UNIVERSELAB_EXPORT_V1__) return;
  window.__UNIVERSELAB_EXPORT_V1__ = true;

  const VERSION = '1.0';
  const NON_EXPORT_SELECTORS = [
    '.ul-export-widget',
    '[data-no-export]',
    'script',
    'style',
    'noscript',
    'template',
    'nav',
    '.nav',
    '.shell',
    '.ul-shell',
    '.top',
    '.tools',
    '.toolbar',
    '.actions',
    '.branch-controls',
    '.clean-note'
  ];

  const $ = (selector, root = document) => root.querySelector(selector);
  const $$ = (selector, root = document) => [...root.querySelectorAll(selector)];

  const config = Object.assign({
    rootSelector: document.body.dataset.ulExportRoot || 'main',
    title: document.body.dataset.ulExportTitle || document.title || 'UniverseLab',
    fileName: document.body.dataset.ulExportFilename || '',
    pageBreakSections: document.body.dataset.ulExportPageBreaks !== 'off'
  }, window.UniverseLabExportConfig || {});

  const exportRoot = $(config.rootSelector) || $('main') || document.body;
  if (!exportRoot || document.body.dataset.ulExport === 'off') return;

  const normaliseSpace = value => String(value || '')
    .replace(/\u00a0/g, ' ')
    .replace(/[ \t]+\n/g, '\n')
    .replace(/\n[ \t]+/g, '\n')
    .replace(/\n{3,}/g, '\n\n')
    .trim();

  const escapeHtml = value => String(value || '')
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#039;');

  const fileStem = value => normaliseSpace(value)
    .normalize('NFKD')
    .replace(/[\u0300-\u036f]/g, '')
    .replace(/[^a-zA-Z0-9äöüÄÖÜß_-]+/g, '-')
    .replace(/^-+|-+$/g, '')
    .replace(/-{2,}/g, '-')
    .slice(0, 90) || 'UniverseLab-Export';

  const isoDate = () => new Date().toISOString().slice(0, 10);
  const localeDate = () => new Intl.DateTimeFormat('de-DE', {
    dateStyle: 'long',
    timeStyle: 'short'
  }).format(new Date());

  function sourceTitle() {
    return normaliseSpace(config.title || document.title || 'UniverseLab');
  }

  function baseFileName(scopeLabel = '') {
    const configured = config.fileName ? fileStem(config.fileName) : fileStem(sourceTitle());
    const scope = scopeLabel && scopeLabel !== 'Gesamte Seite' ? `-${fileStem(scopeLabel)}` : '';
    return `${configured}${scope}-${isoDate()}`;
  }

  function chapterEntries() {
    const details = $$('.chapter, details[data-export-section], details.chapter', exportRoot)
      .filter(node => node.matches('details'));
    if (details.length) {
      return details.map((node, index) => ({
        node,
        index,
        label: normaliseSpace($(':scope > summary', node)?.textContent || `Kapitel ${index + 1}`),
        kind: 'detail'
      }));
    }

    const explicit = $$('[data-export-section]', exportRoot).filter(node => !node.matches('details'));
    return explicit.map((node, index) => ({
      node,
      index,
      label: normaliseSpace(node.dataset.exportTitle || $('h1,h2,h3', node)?.textContent || `Abschnitt ${index + 1}`),
      kind: 'section'
    }));
  }

  const chapters = chapterEntries();

  function replaceFormControl(control) {
    const replacement = document.createElement('span');
    replacement.className = 'ul-export-control-value';
    if (control instanceof HTMLSelectElement) {
      replacement.textContent = control.selectedOptions[0]?.textContent || control.value || '';
    } else if (control instanceof HTMLInputElement && control.type === 'checkbox') {
      replacement.textContent = control.checked ? '☑' : '☐';
    } else if (control instanceof HTMLInputElement && control.type === 'radio') {
      replacement.textContent = control.checked ? '◉' : '○';
    } else {
      replacement.textContent = control.value || control.getAttribute('value') || '';
    }
    control.replaceWith(replacement);
  }

  function convertDetails(details, headingLevel = 2) {
    const section = document.createElement('section');
    section.className = `${details.className || ''} ul-export-section`.trim();
    const summary = $(':scope > summary', details);
    if (summary) {
      const heading = document.createElement(`h${Math.max(2, Math.min(4, headingLevel))}`);
      heading.textContent = normaliseSpace(summary.textContent);
      section.appendChild(heading);
    }
    [...details.childNodes].forEach(child => {
      if (child !== summary) section.appendChild(child.cloneNode(true));
    });
    details.replaceWith(section);
  }

  function cleanClone(container) {
    NON_EXPORT_SELECTORS.forEach(selector => {
      $$(selector, container).forEach(node => node.remove());
    });

    $$('input, select, textarea', container).forEach(replaceFormControl);
    $$('button', container).forEach(node => node.remove());

    $$('canvas', container).forEach(canvas => {
      const note = document.createElement('p');
      note.className = 'ul-export-canvas-note';
      note.textContent = '[Interaktives Diagramm – Werte und Beschreibung siehe Begleittext]';
      canvas.replaceWith(note);
    });

    $$('details', container).forEach((details, index) => convertDetails(details, index === 0 ? 2 : 2));

    $$('[hidden]', container).forEach(node => node.removeAttribute('hidden'));
    $$('[aria-hidden="true"]', container).forEach(node => node.removeAttribute('aria-hidden'));
    $$('[style]', container).forEach(node => {
      const style = node.getAttribute('style') || '';
      const cleaned = style
        .replace(/display\s*:\s*none\s*;?/gi, '')
        .replace(/visibility\s*:\s*hidden\s*;?/gi, '')
        .replace(/opacity\s*:\s*0\s*;?/gi, '');
      if (cleaned.trim()) node.setAttribute('style', cleaned);
      else node.removeAttribute('style');
    });

    $$('a[href]', container).forEach(link => {
      const raw = link.getAttribute('href') || '';
      if (!raw || raw.startsWith('javascript:')) link.removeAttribute('href');
      else {
        try {
          link.href = new URL(raw, document.baseURI).href;
        } catch {
          link.removeAttribute('href');
        }
      }
    });

    return container;
  }

  function selectedNodes(scopeValue) {
    if (scopeValue === 'open' && chapters.length) {
      const open = chapters.filter(entry => entry.node.open || entry.node.matches('[open]'));
      return (open.length ? open : chapters).map(entry => entry.node);
    }
    if (scopeValue.startsWith('chapter:')) {
      const index = Number(scopeValue.split(':')[1]);
      const entry = chapters[index];
      return entry ? [entry.node] : [exportRoot];
    }
    return [exportRoot];
  }

  function scopeLabel(scopeValue) {
    if (scopeValue === 'open') return 'Geöffnete Kapitel';
    if (scopeValue.startsWith('chapter:')) {
      const index = Number(scopeValue.split(':')[1]);
      return chapters[index]?.label || 'Kapitel';
    }
    return 'Gesamte Seite';
  }

  function cloneScope(scopeValue) {
    const wrapper = document.createElement('div');
    wrapper.className = 'ul-export-content';
    selectedNodes(scopeValue).forEach((node, index) => {
      const clone = node.cloneNode(true);
      if (index > 0 && config.pageBreakSections) clone.classList.add('ul-export-page-break');
      wrapper.appendChild(clone);
    });
    return cleanClone(wrapper);
  }

  function documentHeader(scopeValue) {
    const header = document.createElement('header');
    header.className = 'ul-export-document-head';
    const h1 = document.createElement('h1');
    h1.textContent = sourceTitle();
    const scope = document.createElement('p');
    scope.textContent = `Exportbereich: ${scopeLabel(scopeValue)}`;
    const meta = document.createElement('p');
    meta.textContent = `Erstellt am ${localeDate()} · Quelle: ${location.href}`;
    header.append(h1, scope, meta);
    return header;
  }

  function cloneWithHeader(scopeValue) {
    const documentNode = document.createElement('article');
    documentNode.className = 'ul-export-document';
    documentNode.append(documentHeader(scopeValue), cloneScope(scopeValue));
    return documentNode;
  }

  function textOf(node) {
    const host = document.createElement('div');
    host.style.cssText = 'position:fixed;left:-100000px;top:0;width:900px;opacity:0;pointer-events:none;';
    host.appendChild(node.cloneNode(true));
    document.body.appendChild(host);
    const text = host.innerText || host.textContent || '';
    host.remove();
    return normaliseSpace(text);
  }

  function inlineMarkdown(node) {
    if (node.nodeType === Node.TEXT_NODE) return node.nodeValue || '';
    if (node.nodeType !== Node.ELEMENT_NODE) return '';
    const tag = node.tagName.toLowerCase();
    const content = [...node.childNodes].map(inlineMarkdown).join('');
    if (tag === 'br') return '  \n';
    if (tag === 'strong' || tag === 'b') return `**${content.trim()}**`;
    if (tag === 'em' || tag === 'i') return `*${content.trim()}*`;
    if (tag === 'code') return `\`${content.replace(/`/g, '\\`').trim()}\``;
    if (tag === 'a' && node.getAttribute('href')) {
      const label = content.trim() || node.getAttribute('href');
      return `[${label}](${node.getAttribute('href')})`;
    }
    if (tag === 'img') {
      return `![${node.getAttribute('alt') || ''}](${node.getAttribute('src') || ''})`;
    }
    return content;
  }

  function tableMarkdown(table) {
    const rows = $$('tr', table).map(row => $$('th,td', row).map(cell => normaliseSpace(cell.textContent).replace(/\|/g, '\\|')));
    if (!rows.length) return '';
    const width = Math.max(...rows.map(row => row.length));
    const padded = rows.map(row => [...row, ...Array(Math.max(0, width - row.length)).fill('')]);
    const header = padded[0];
    const separator = header.map(() => '---');
    return `| ${header.join(' | ')} |\n| ${separator.join(' | ')} |\n${padded.slice(1).map(row => `| ${row.join(' | ')} |`).join('\n')}\n\n`;
  }

  function listMarkdown(list, depth = 0) {
    const ordered = list.tagName.toLowerCase() === 'ol';
    return [...list.children].filter(item => item.tagName?.toLowerCase() === 'li').map((item, index) => {
      const clone = item.cloneNode(true);
      $$(':scope > ul, :scope > ol', clone).forEach(nested => nested.remove());
      const prefix = ordered ? `${index + 1}. ` : '- ';
      const line = `${'  '.repeat(depth)}${prefix}${normaliseSpace(inlineMarkdown(clone))}`;
      const nested = [...item.children]
        .filter(child => ['ul', 'ol'].includes(child.tagName.toLowerCase()))
        .map(child => listMarkdown(child, depth + 1))
        .join('');
      return `${line}\n${nested}`;
    }).join('') + (depth === 0 ? '\n' : '');
  }

  function blockMarkdown(node) {
    if (node.nodeType === Node.TEXT_NODE) return node.nodeValue || '';
    if (node.nodeType !== Node.ELEMENT_NODE) return '';
    const tag = node.tagName.toLowerCase();

    if (/^h[1-6]$/.test(tag)) {
      const level = Number(tag.slice(1));
      return `${'#'.repeat(level)} ${normaliseSpace(inlineMarkdown(node))}\n\n`;
    }
    if (tag === 'p') return `${normaliseSpace(inlineMarkdown(node))}\n\n`;
    if (tag === 'pre') return `\`\`\`text\n${node.textContent.trim()}\n\`\`\`\n\n`;
    if (tag === 'blockquote') {
      return `${normaliseSpace(textOf(node)).split('\n').map(line => `> ${line}`).join('\n')}\n\n`;
    }
    if (tag === 'ul' || tag === 'ol') return listMarkdown(node);
    if (tag === 'table') return tableMarkdown(node);
    if (tag === 'hr') return '---\n\n';
    if (tag === 'img') return `${inlineMarkdown(node)}\n\n`;
    if (tag === 'br') return '\n';
    if (['strong', 'b', 'em', 'i', 'code', 'a', 'span', 'small'].includes(tag)) return inlineMarkdown(node);

    return [...node.childNodes].map(blockMarkdown).join('');
  }

  function markdownOf(scopeValue) {
    const node = cloneWithHeader(scopeValue);
    const markdown = blockMarkdown(node)
      .replace(/[ \t]+\n/g, '\n')
      .replace(/\n{3,}/g, '\n\n')
      .trim();
    return `${markdown}\n`;
  }

  function plainTextOf(scopeValue) {
    return `${textOf(cloneWithHeader(scopeValue))}\n`;
  }

  function standaloneHtml(scopeValue) {
    const node = cloneWithHeader(scopeValue);
    const title = `${sourceTitle()} – ${scopeLabel(scopeValue)}`;
    return `<!doctype html>
<html lang="de">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>${escapeHtml(title)}</title>
<style>
:root{color-scheme:light}*{box-sizing:border-box}body{max-width:980px;margin:0 auto;padding:32px 24px 72px;color:#171717;background:#fff;font:16px/1.58 system-ui,-apple-system,"Segoe UI",sans-serif}h1,h2,h3,h4{line-height:1.18;break-after:avoid-page}h1{font-size:2.3rem}h2{margin-top:2.1rem;padding-bottom:.35rem;border-bottom:1px solid #bbb}a{color:#174d9c}table{width:100%;border-collapse:collapse;margin:1rem 0}th,td{padding:.5rem;border:1px solid #aaa;text-align:left;vertical-align:top}pre,.equation,.eq,.formula-box{overflow:auto;padding:.8rem;border:1px solid #bbb;background:#f5f5f5;white-space:pre-wrap;font-family:ui-monospace,SFMono-Regular,Consolas,monospace}.card,.callout,.term,.audit{margin:.8rem 0;padding:.8rem;border:1px solid #bbb;border-radius:.35rem}.ul-export-document-head{margin-bottom:2rem;padding-bottom:1rem;border-bottom:2px solid #555}.ul-export-document-head p{color:#555}@media print{@page{size:A4;margin:16mm}body{max-width:none;padding:0;font-size:10.5pt}.ul-export-page-break{break-before:page}}
</style>
</head>
<body>
${node.outerHTML}
</body>
</html>`;
  }

  function download(content, mime, extension, scopeValue) {
    const blob = new Blob([content], { type: `${mime};charset=utf-8` });
    const url = URL.createObjectURL(blob);
    const anchor = document.createElement('a');
    anchor.href = url;
    anchor.download = `${baseFileName(scopeLabel(scopeValue))}.${extension}`;
    document.body.appendChild(anchor);
    anchor.click();
    anchor.remove();
    setTimeout(() => URL.revokeObjectURL(url), 1000);
  }

  function copyText(text) {
    if (navigator.clipboard?.writeText) return navigator.clipboard.writeText(text);
    return new Promise((resolve, reject) => {
      const area = document.createElement('textarea');
      area.value = text;
      area.style.cssText = 'position:fixed;left:-10000px;top:0;';
      document.body.appendChild(area);
      area.select();
      try {
        if (!document.execCommand('copy')) throw new Error('copy command rejected');
        resolve();
      } catch (error) {
        reject(error);
      } finally {
        area.remove();
      }
    });
  }

  function printScope(scopeValue) {
    $('#ul-export-print-root')?.remove();
    const printRoot = document.createElement('div');
    printRoot.id = 'ul-export-print-root';
    printRoot.appendChild(cloneWithHeader(scopeValue));
    document.body.appendChild(printRoot);
    document.body.classList.add('ul-export-printing');

    let cleaned = false;
    const cleanup = () => {
      if (cleaned) return;
      cleaned = true;
      document.body.classList.remove('ul-export-printing');
      printRoot.remove();
      window.removeEventListener('afterprint', cleanup);
    };
    window.addEventListener('afterprint', cleanup, { once: true });
    requestAnimationFrame(() => requestAnimationFrame(() => {
      window.print();
      setTimeout(cleanup, 15000);
    }));
  }

  function buildWidget() {
    const widget = document.createElement('aside');
    widget.className = 'ul-export-widget';
    widget.dataset.noExport = 'true';
    widget.setAttribute('aria-label', 'Export und Druck');

    const toggle = document.createElement('button');
    toggle.type = 'button';
    toggle.className = 'ul-export-toggle';
    toggle.textContent = 'Exportieren';
    toggle.setAttribute('aria-expanded', 'false');

    const panel = document.createElement('section');
    panel.className = 'ul-export-panel';
    panel.hidden = true;

    const head = document.createElement('div');
    head.className = 'ul-export-head';
    const heading = document.createElement('strong');
    heading.textContent = 'Text & Dokument exportieren';
    const close = document.createElement('button');
    close.type = 'button';
    close.className = 'ul-export-close';
    close.textContent = '×';
    close.setAttribute('aria-label', 'Exportfenster schließen');
    head.append(heading, close);

    const label = document.createElement('label');
    label.textContent = 'Exportbereich';
    const scope = document.createElement('select');
    scope.className = 'ul-export-scope';
    scope.innerHTML = '<option value="all">Gesamte Seite</option>';
    if (chapters.length) {
      scope.insertAdjacentHTML('beforeend', '<option value="open">Nur geöffnete Kapitel</option>');
      chapters.forEach((entry, index) => {
        const option = document.createElement('option');
        option.value = `chapter:${index}`;
        option.textContent = entry.label;
        scope.appendChild(option);
      });
    }
    label.appendChild(scope);

    const actions = document.createElement('div');
    actions.className = 'ul-export-actions';
    const buttons = [
      ['print', 'Drucken / PDF', 'primary'],
      ['markdown', 'Markdown', ''],
      ['text', 'Textdatei', ''],
      ['html', 'HTML-Dokument', ''],
      ['copy', 'Text kopieren', '']
    ];
    buttons.forEach(([action, text, className]) => {
      const button = document.createElement('button');
      button.type = 'button';
      button.dataset.exportAction = action;
      button.textContent = text;
      if (className) button.classList.add(className);
      actions.appendChild(button);
    });

    const note = document.createElement('p');
    note.className = 'ul-export-note';
    note.textContent = 'PDF: Im Druckdialog „Als PDF speichern“ wählen. Interaktive Bedienelemente werden automatisch entfernt.';
    const status = document.createElement('p');
    status.className = 'ul-export-status';
    status.setAttribute('aria-live', 'polite');

    panel.append(head, label, actions, note, status);
    widget.append(toggle, panel);
    document.body.appendChild(widget);

    const setOpen = open => {
      panel.hidden = !open;
      toggle.setAttribute('aria-expanded', String(open));
      if (open) scope.focus();
    };

    toggle.addEventListener('click', () => setOpen(panel.hidden));
    close.addEventListener('click', () => setOpen(false));
    document.addEventListener('keydown', event => {
      if (event.key === 'Escape' && !panel.hidden) setOpen(false);
    });

    actions.addEventListener('click', async event => {
      const button = event.target.closest('[data-export-action]');
      if (!button) return;
      const action = button.dataset.exportAction;
      const value = scope.value;
      status.textContent = '';
      button.disabled = true;
      try {
        if (action === 'print') {
          printScope(value);
          status.textContent = 'Druckansicht vorbereitet.';
        } else if (action === 'markdown') {
          download(markdownOf(value), 'text/markdown', 'md', value);
          status.textContent = 'Markdown wurde erstellt.';
        } else if (action === 'text') {
          download(plainTextOf(value), 'text/plain', 'txt', value);
          status.textContent = 'Textdatei wurde erstellt.';
        } else if (action === 'html') {
          download(standaloneHtml(value), 'text/html', 'html', value);
          status.textContent = 'Eigenständiges HTML-Dokument wurde erstellt.';
        } else if (action === 'copy') {
          await copyText(plainTextOf(value));
          status.textContent = 'Text wurde in die Zwischenablage kopiert.';
        }
      } catch (error) {
        console.error('[UniverseLab Export]', error);
        status.textContent = 'Export fehlgeschlagen. Bitte erneut versuchen.';
      } finally {
        button.disabled = false;
      }
    });
  }

  function init() {
    buildWidget();
    document.documentElement.dataset.ulExportVersion = VERSION;
  }

  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init, { once: true });
  else init();
})();
