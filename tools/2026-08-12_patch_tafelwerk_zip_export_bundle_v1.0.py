#!/usr/bin/env python3
from pathlib import Path

path = Path('assets/2026-08-12_UniverseLab_TafelwerkAllFormulaExport_v1.0.js')
text = path.read_text(encoding='utf-8')

replacements = []

old = "  const VERSION = '1.0';"
new = "  const VERSION = '1.1';"
if old in text:
    text = text.replace(old, new, 1)
elif new not in text:
    raise SystemExit('VERSION marker missing')

marker = "  function csvCell(value) {\n"
zip_helpers = r'''  function downloadBlob(blob, extension) {
    const url = URL.createObjectURL(blob);
    const anchor = document.createElement('a');
    anchor.href = url;
    anchor.download = `${fileStem()}.${extension}`;
    document.body.appendChild(anchor);
    anchor.click();
    anchor.remove();
    setTimeout(() => URL.revokeObjectURL(url), 1000);
  }

  const CRC32_TABLE = (() => {
    const table = new Uint32Array(256);
    for (let n = 0; n < 256; n += 1) {
      let c = n;
      for (let k = 0; k < 8; k += 1) c = (c & 1) ? (0xEDB88320 ^ (c >>> 1)) : (c >>> 1);
      table[n] = c >>> 0;
    }
    return table;
  })();

  function crc32(bytes) {
    let crc = 0xFFFFFFFF;
    for (const byte of bytes) crc = CRC32_TABLE[(crc ^ byte) & 0xFF] ^ (crc >>> 8);
    return (crc ^ 0xFFFFFFFF) >>> 0;
  }

  function le16(value) {
    const out = new Uint8Array(2);
    new DataView(out.buffer).setUint16(0, value & 0xFFFF, true);
    return out;
  }

  function le32(value) {
    const out = new Uint8Array(4);
    new DataView(out.buffer).setUint32(0, value >>> 0, true);
    return out;
  }

  function joinBytes(parts) {
    const total = parts.reduce((sum, part) => sum + part.length, 0);
    const out = new Uint8Array(total);
    let offset = 0;
    for (const part of parts) {
      out.set(part, offset);
      offset += part.length;
    }
    return out;
  }

  function dosDateTime(date = new Date()) {
    const year = Math.max(1980, Math.min(2107, date.getFullYear()));
    const time = ((date.getHours() & 0x1F) << 11) | ((date.getMinutes() & 0x3F) << 5) | ((Math.floor(date.getSeconds() / 2)) & 0x1F);
    const day = ((year - 1980) << 9) | (((date.getMonth() + 1) & 0x0F) << 5) | (date.getDate() & 0x1F);
    return { time, day };
  }

  function zipBlob(entries) {
    const encoder = new TextEncoder();
    const utf8Flag = 0x0800;
    const version = 20;
    const now = dosDateTime();
    const localParts = [];
    const centralParts = [];
    let localOffset = 0;

    for (const entry of entries) {
      const nameBytes = encoder.encode(entry.name);
      const dataBytes = typeof entry.content === 'string' ? encoder.encode(entry.content) : entry.content;
      if (!(dataBytes instanceof Uint8Array)) throw new TypeError(`ZIP entry ${entry.name} is not text or Uint8Array.`);
      const crc = crc32(dataBytes);
      const size = dataBytes.length;
      const localHeader = joinBytes([
        le32(0x04034b50), le16(version), le16(utf8Flag), le16(0), le16(now.time), le16(now.day),
        le32(crc), le32(size), le32(size), le16(nameBytes.length), le16(0), nameBytes
      ]);
      localParts.push(localHeader, dataBytes);

      const centralHeader = joinBytes([
        le32(0x02014b50), le16(version), le16(version), le16(utf8Flag), le16(0), le16(now.time), le16(now.day),
        le32(crc), le32(size), le32(size), le16(nameBytes.length), le16(0), le16(0), le16(0), le16(0),
        le32(0), le32(localOffset), nameBytes
      ]);
      centralParts.push(centralHeader);
      localOffset += localHeader.length + size;
    }

    if (entries.length > 0xFFFF) throw new Error('ZIP-Dateigrenze überschritten.');
    const centralDirectory = joinBytes(centralParts);
    const end = joinBytes([
      le32(0x06054b50), le16(0), le16(0), le16(entries.length), le16(entries.length),
      le32(centralDirectory.length), le32(localOffset), le16(0)
    ]);
    return new Blob([...localParts, centralDirectory, end], { type: 'application/zip' });
  }

  function zipBundle(records) {
    const stem = fileStem();
    const json = `${JSON.stringify(payload(records), null, 2)}\n`;
    const readme = [
      'UniverseLab Mathematisches Tafelwerk 2.0 — Komplettpaket',
      `Erzeugt: ${new Date().toLocaleString('de-DE')}`,
      `Formeln: ${records.length}`,
      '',
      'Enthalten:',
      `- ${stem}.html — eigenständige, druckbare Vollfassung`,
      `- ${stem}.md — Markdown-Vollfassung`,
      `- ${stem}.json — strukturierter Maschinenexport`,
      `- ${stem}.csv — tabellarischer Export`,
      '',
      'Für PDF: die HTML-Datei im Browser öffnen und Drucken → Als PDF speichern wählen.',
      'Der ZIP-Container verwendet gespeicherte ZIP-Einträge (ohne Kompression), CRC32 und UTF-8-Dateinamen.',
      ''
    ].join('\n');
    const entries = [
      { name: `${stem}.html`, content: htmlOf(records) },
      { name: `${stem}.md`, content: markdownOf(records) },
      { name: `${stem}.json`, content: json },
      { name: `${stem}.csv`, content: csvOf(records) },
      { name: 'README.txt', content: readme }
    ];
    downloadBlob(zipBlob(entries), 'zip');
  }

'''
if 'function zipBlob(entries)' not in text:
    if marker not in text:
        raise SystemExit('csvCell insertion marker missing')
    text = text.replace(marker, zip_helpers + marker, 1)

old_note = "    note.textContent = 'Exportiert immer den vollständigen Formelkatalog — unabhängig von Suche, Kategorie, Status oder „nur berechenbar“. Die aktuelle Auswahl wird danach wiederhergestellt.';"
new_note = "    note.textContent = 'Exportiert immer den vollständigen Formelkatalog — unabhängig von Suche, Kategorie, Status oder „nur berechenbar“. ZIP bündelt HTML, Markdown, JSON und CSV in einer Datei. Die aktuelle Auswahl wird danach wiederhergestellt.';"
if old_note in text:
    text = text.replace(old_note, new_note, 1)
elif new_note not in text:
    raise SystemExit('export note marker missing')

old_defs = "    const definitions = [\n      ['print', 'Alle Formeln · PDF/Drucken'],"
new_defs = "    const definitions = [\n      ['zip', 'Alle Formeln · ZIP (Komplettpaket)'],\n      ['print', 'Alle Formeln · PDF/Drucken'],"
if old_defs in text:
    text = text.replace(old_defs, new_defs, 1)
elif "['zip', 'Alle Formeln · ZIP (Komplettpaket)']" not in text:
    raise SystemExit('button definitions marker missing')

old_action = "        if (action === 'print') printAll(records);\n        else if (action === 'html') download(htmlOf(records), 'text/html', 'html');"
new_action = "        if (action === 'zip') zipBundle(records);\n        else if (action === 'print') printAll(records);\n        else if (action === 'html') download(htmlOf(records), 'text/html', 'html');"
if old_action in text:
    text = text.replace(old_action, new_action, 1)
elif "if (action === 'zip') zipBundle(records);" not in text:
    raise SystemExit('action dispatch marker missing')

path.write_text(text, encoding='utf-8')
print('PASS_TAFELWERK_ZIP_EXPORT_BUNDLE_PATCH')
