#!/usr/bin/env python3
"""RC23 deterministic, non-distributed local-only Android preview ZIP.

Uses exactly the 446 RC19 manifest files, with ONE verified RC21 router
replacement; two root-level contract documents are NOT served in /UniverseLab/.
This tool NEVER publishes, uploads, deploys, installs, or starts a server.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import sys
from zipfile import ZIP_STORED, ZipFile, ZipInfo, BadZipFile


PUBLIC_PREFIX = "UniverseLab/"
ROUTER = "assets/2026-08-27_UniverseLab_DocumentLinkRouter_v1.0.js"
README_NAME = "RC23_LOCAL_PREVIEW_README.txt"
META_NAME = "RC23_PREVIEW_META.json"
FIXED_ZIP_TIME = (2026, 11, 3, 0, 0, 0)
MAX_ARCHIVE_BYTES = 8_000_000
MAX_ENTRY_BYTES = 5_000_000


class PreviewHold(RuntimeError):
    """Fail-closed preview QA, never a release decision."""


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _import(root: Path, rel: str, name: str):
    spec = importlib.util.spec_from_file_location(name, root / rel)
    if spec is None or spec.loader is None:
        raise PreviewHold("DEPENDENCY_UNAVAILABLE:" + rel)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def _source_contract(root: Path, manifest_path: Path, candidate_path: Path,
                     provenance_path: Path, template_path: Path):
    rc19 = _import(root, "tools/2026-11-03_UniverseLab_RC19_PublicOnlyBuild_v1.0.py", "rc23_rc19")
    rc21 = _import(root, "tools/2026-11-03_UniverseLab_RC21_RenderSafeRouter_v1.0.py", "rc23_rc21")
    allowed = rc19.load_manifest(manifest_path)
    if len(allowed) != 446 or ROUTER not in allowed:
        raise PreviewHold("RC19_INVENTORY_OR_ROUTER_MISMATCH")
    generated, expected_provenance = rc21.render(root, manifest_path, template_path)
    candidate = candidate_path.read_bytes()
    if candidate != generated.encode("utf-8"):
        raise PreviewHold("RC21_ROUTER_CANDIDATE_NOT_REPRODUCIBLE")
    try:
        recorded = json.loads(provenance_path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        raise PreviewHold("RC21_PROVENANCE_NOT_READABLE") from exc
    if recorded != expected_provenance or recorded["status"] != "CANDIDATE_NOT_INSTALLED":
        raise PreviewHold("RC21_PROVENANCE_MISMATCH")
    if sha256(candidate) != recorded["generated_router_sha256"]:
        raise PreviewHold("RC21_CANDIDATE_DIGEST_MISMATCH")

    public_files: dict[str, bytes] = {}
    for rel, expected_digest in allowed.items():
        source = rc19._source_file(root, rel)
        data = source.read_bytes()
        if sha256(data) != expected_digest:
            raise PreviewHold("RC19_PUBLIC_DIGEST_CHANGED:" + rel)
        public_files[rel] = data
    public_files[ROUTER] = candidate
    return allowed, public_files, expected_provenance


def _readme(meta: dict) -> bytes:
    text = f"""UniverseLab RC23 — LOKALE ANDROID-TESTVORSCHAU — NICHT VERÖFFENTLICHEN

STATUS: PREVIEW_CANDIDATE / OWNER_DISTRIBUTION_APPROVAL_NOT_GRANTED / RELEASE_HOLD
Prüfbasis main: {meta['basis_main_commit']}
RC19 Manifest SHA-256: {meta['rc19_manifest_sha256']}
RC21 Router SHA-256: {meta['rc21_router_sha256']}
Einziger ersetzter Pages-Dateipfad: {ROUTER}
Dateien unter UniverseLab/: {meta['public_file_count']} (445 unverändert, ein Router-Overlay)

HINWEIS: Diese Datei ist eine VORBEREITETE, NICHT FREIGEGEBENE VORSCHAU.
Sie wurde nicht auf GitHub Pages installiert. Das ZIP darf vor gesonderter
Betreiberfreigabe weder verteilt noch als offizieller UniverseLab-Build
bezeichnet werden. Die HTTP-Auslieferung erfolgt nur auf dem eigenen Gerät.

WENN UND NUR WENN EINE VERTEILUNG SPÄTER EXPLIZIT FREIGEGEBEN WURDE:
1. ZIP-Hash gegen die separat übermittelte SHA-256-Prüfsumme vergleichen.
2. ZIP mit Termux entpacken. Bei Bedarf: pkg install python unzip
3. In das Verzeichnis wechseln, das diesen README und UniverseLab/ enthält.
4. Ausschließlich lokalen HTTP-Server starten:

   python -m http.server 8765 --bind 127.0.0.1

5. In Opera Android öffnen: http://127.0.0.1:8765/UniverseLab/
6. Nach dem Test den lokalen Server mit Strg+C beenden.

NICHT die Option --bind 0.0.0.0 verwenden. Nicht über Portfreigabe,
Tunneldienst oder öffentliche Domain ins Internet stellen.
Die eingebauten GitHub-Quelllinks können das Gerät weiterhin nach außen
auf github.com führen; diese sind nicht Teil des lokalen Seitenarchivs.

Das SitePrintExport-Service-Worker-Autoregistrierungsskript erfordert HTTPS.
Diese localhost-HTTP-Vorschau testet daher NICHT die produktive automatische
Service-Worker-Registrierung oder die echte GitHub-Pages-Konfiguration.
Für S24-/Opera-Befunde gilt weiterhin RC22_RealAndroidManualGate.
Physikalische Evidenz/kanonische Promotion: KEINE. Release: HOLD.
"""
    return text.encode("utf-8")


def _metadata(allowed: dict[str, str], public_files: dict[str, bytes],
              provenance: dict) -> dict:
    return {
        "schema": "universelab.rc23.local-preview-candidate.v1",
        "status": "NONCANONICAL_NOT_DISTRIBUTED",
        "owner_distribution_approval": "NOT_GRANTED",
        "release_gate": "HOLD",
        "basis_main_commit": provenance["basis_main_commit"],
        "rc19_manifest_sha256": provenance["manifest_sha256"],
        "rc21_router_sha256": provenance["generated_router_sha256"],
        "overlay_path": ROUTER,
        "original_router_sha256": allowed[ROUTER],
        "public_file_count": len(public_files),
        "unchanged_files": len(public_files) - 1,
        "in_place_public_path_additions": 0,
        "published_pages_changed": False,
        "physical_gate_effect": "NONE",
        "physical_evidence_effect": "NONE",
        "files": [{"path": rel, "sha256": sha256(data), "bytes": len(data)}
                  for rel, data in sorted(public_files.items())],
    }


def _entry(name: str, data: bytes) -> tuple[ZipInfo, bytes]:
    if len(data) > MAX_ENTRY_BYTES:
        raise PreviewHold("ZIP_ENTRY_TOO_LARGE:" + name)
    info = ZipInfo(name, date_time=FIXED_ZIP_TIME)
    info.compress_type = ZIP_STORED
    info.create_system = 3
    info.external_attr = 0o100644 << 16
    info.flag_bits = 0x800
    return info, data


def _payload(root: Path, manifest: Path, candidate: Path,
             provenance: Path, template: Path) -> tuple[list[tuple[ZipInfo, bytes]], dict]:
    allowed, public_files, expected_provenance = _source_contract(
        root, manifest, candidate, provenance, template)
    meta = _metadata(allowed, public_files, expected_provenance)
    meta_data = (json.dumps(meta, ensure_ascii=False, sort_keys=True, indent=2) + "\n").encode("utf-8")
    archive = [_entry(README_NAME, _readme(meta)), _entry(META_NAME, meta_data)]
    archive += [_entry(PUBLIC_PREFIX + rel, data) for rel, data in sorted(public_files.items())]
    if len(archive) != 448 or sum(len(data) for _, data in archive) > MAX_ARCHIVE_BYTES:
        raise PreviewHold("PREVIEW_TOTAL_INVENTORY_OR_SIZE_MISMATCH")
    return archive, meta


def build(root: Path, manifest: Path, candidate: Path, provenance: Path,
          template: Path, out: Path) -> dict:
    root = root.resolve(strict=True)
    out = out.resolve(strict=False)
    if out == root or root in out.parents:
        raise PreviewHold("ZIP_OUTSIDE_REPOSITORY_REQUIRED")
    if out.exists() or not out.parent.is_dir():
        raise PreviewHold("ZIP_OUTPUT_MUST_BE_ABSENT_WITH_EXISTING_PARENT")
    entries, meta = _payload(root, manifest, candidate, provenance, template)
    created = False
    try:
        with ZipFile(out, "x", compression=ZIP_STORED, allowZip64=False) as target:
            created = True
            for entry, data in entries:
                target.writestr(entry, data)
    except Exception:
        if created and out.is_file():
            out.unlink()
        raise
    return {"status": "RC23_CANDIDATE_BUILT_NOT_DISTRIBUTED", "zip_sha256": sha256(out.read_bytes()),
            "zip_bytes": out.stat().st_size, "zip_entries": len(entries),
            "public_file_count": meta["public_file_count"], "overlay_count": 1,
            "release_gate": "HOLD", "published_pages_changed": False}


def verify(root: Path, manifest: Path, candidate: Path, provenance: Path,
           template: Path, archive_path: Path) -> dict:
    root = root.resolve(strict=True)
    entries, meta = _payload(root, manifest, candidate, provenance, template)
    expected = {info.filename: (info, data) for info, data in entries}
    try:
        with ZipFile(archive_path, "r") as archive:
            actual = archive.infolist()
            names = [item.filename for item in actual]
            if len(names) != len(set(names)) or set(names) != set(expected):
                raise PreviewHold("ZIP_PATH_INVENTORY_MISMATCH")
            total = 0
            for item in actual:
                original, data = expected[item.filename]
                if (item.date_time != FIXED_ZIP_TIME or item.compress_type != ZIP_STORED or
                        (item.external_attr >> 16) != 0o100644):
                    raise PreviewHold("ZIP_NONCANONICAL_ENTRY_METADATA:" + item.filename)
                if item.file_size != len(data) or item.file_size > MAX_ENTRY_BYTES:
                    raise PreviewHold("ZIP_ENTRY_LENGTH_MISMATCH:" + item.filename)
                total += item.file_size
                if total > MAX_ARCHIVE_BYTES or archive.read(item) != data:
                    raise PreviewHold("ZIP_BYTES_OR_TOTAL_SIZE_MISMATCH:" + item.filename)
    except BadZipFile as exc:
        raise PreviewHold("ZIP_CORRUPTED") from exc
    return {"status": "RC23_ARCHIVE_VERIFIED_NOT_AUTHORIZED", "zip_sha256": sha256(archive_path.read_bytes()),
            "zip_entries": len(expected), "public_file_count": meta["public_file_count"],
            "one_overlay_only": True, "published_pages_changed": False, "release_gate": "HOLD"}


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--root", type=Path, default=Path("."))
    p.add_argument("--manifest", type=Path, required=True)
    p.add_argument("--candidate", type=Path, required=True)
    p.add_argument("--provenance", type=Path, required=True)
    p.add_argument("--template", type=Path, required=True)
    p.add_argument("--out", type=Path, required=True)
    p.add_argument("--verify-only", action="store_true")
    args = p.parse_args()
    try:
        if args.verify_only:
            result = verify(args.root, args.manifest, args.candidate, args.provenance,
                            args.template, args.out)
        else:
            result = build(args.root, args.manifest, args.candidate, args.provenance,
                           args.template, args.out)
    except (PreviewHold, OSError, ValueError, KeyError) as exc:
        print(json.dumps({"status": "RC23_HOLD", "reason": str(exc)}, ensure_ascii=False))
        return 2
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
