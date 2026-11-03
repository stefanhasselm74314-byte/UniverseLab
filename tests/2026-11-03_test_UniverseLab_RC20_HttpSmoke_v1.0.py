#!/usr/bin/env python3
"""Local HTTP-only Pages-prefix replay; not a JS/browser/Android execution test."""

from __future__ import annotations

import argparse
from functools import partial
from hashlib import sha256
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
import json
from pathlib import Path
import shutil
import tempfile
from threading import Thread
from urllib.error import HTTPError
from urllib.parse import quote
from urllib.request import Request, urlopen


class QuietHandler(SimpleHTTPRequestHandler):
    def log_message(self, *args) -> None:
        return


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--stage", type=Path, required=True)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--runtime-report", type=Path, required=True)
    parser.add_argument("--report", type=Path)
    args = parser.parse_args()

    stage = args.stage.resolve(strict=True)
    manifest = json.loads(args.manifest.read_text(encoding="utf-8"))
    audit = json.loads(args.runtime_report.read_text(encoding="utf-8"))
    allowed = {x["path"]: x["sha256"] for x in manifest["files"]}
    if any((stage / path).is_symlink() for path in allowed):
        raise RuntimeError("STAGING_SYMLINK_FORBIDDEN")
    bad_targets = sorted({x["target"] for x in
                          audit["source_link_router"]["excluded_existing_file_links"]})
    if not bad_targets:
        raise RuntimeError("EXPECTED_HOLD_FIXTURE_NO_LONGER_PRESENT_REAUDIT_REQUIRED")

    with tempfile.TemporaryDirectory(prefix="rc20-http-prefix-") as tmp:
        root = Path(tmp)
        shutil.copytree(stage, root / "UniverseLab", symlinks=False)
        srv = ThreadingHTTPServer(("127.0.0.1", 0), partial(QuietHandler, directory=str(root)))
        thread = Thread(target=srv.serve_forever, daemon=True)
        thread.start()
        base = f"http://127.0.0.1:{srv.server_port}/UniverseLab/"
        checked_files = 0
        checked_bytes = 0
        html_mobile_checks = 0
        try:
            for path, expected_sha in sorted(allowed.items()):
                url = base + quote(path, safe="/")
                req = Request(url, headers={"User-Agent": "RC20-Desktop-HTTP-Smoke/1.0"})
                with urlopen(req, timeout=6) as response:
                    if response.status != 200:
                        raise RuntimeError(f"PUBLIC_PATH_NOT_200:{path}:{response.status}")
                    raw = response.read()
                    if sha256(raw).hexdigest() != expected_sha:
                        raise RuntimeError(f"PUBLIC_BYTES_MISMATCH:{path}")
                checked_files += 1
                checked_bytes += len(raw)
                if path.endswith(".html"):
                    mobile = Request(url, headers={
                        "User-Agent": "Mozilla/5.0 (Linux; Android 17; SM-S928B) AppleWebKit/537.36 Chrome/140 Mobile Safari/537.36",
                        "Accept-Language": "de-DE,de;q=0.9,en;q=0.6",
                    })
                    with urlopen(mobile, timeout=6) as response:
                        if response.status != 200 or sha256(response.read()).hexdigest() != expected_sha:
                            raise RuntimeError(f"MOBILE_UA_HTTP_BYTES_MISMATCH:{path}")
                    html_mobile_checks += 1

            blocked_checks = []
            for path in bad_targets + ["drafts/RC20_NONSECRET_CANARY_DRAFT.json"]:
                url = base + quote(path, safe="/")
                try:
                    with urlopen(Request(url), timeout=6) as response:
                        raise RuntimeError(f"EXCLUDED_TARGET_UNEXPECTEDLY_AVAILABLE:{path}:{response.status}")
                except HTTPError as exc:
                    if exc.code != 404:
                        raise RuntimeError(f"EXCLUDED_TARGET_WRONG_HTTP_STATUS:{path}:{exc.code}") from exc
                    blocked_checks.append(path)
        finally:
            srv.shutdown()
            srv.server_close()
            thread.join(timeout=2)

    result = {
        "schema": "universelab.rc20.local-http-prefix-smoke.v1",
        "status": "HTTP_TRANSPORT_PASS_RUNTIME_BROWSER_NOT_PROVEN",
        "host": "127.0.0.1 ephemeral ephemeral-port (not public Pages)",
        "prefix": "/UniverseLab/",
        "desktop_sha256_200": checked_files,
        "bytes_identical_to_manifest": checked_bytes,
        "mobile_user_agent_html_200": html_mobile_checks,
        "excluded_router_target_http_404": bad_targets,
        "synthetic_draft_http_404": True,
        "javascript_executed": False,
        "real_android_device_executed": False,
        "actual_github_pages_artifact_verified": False,
        "physical_evidence_effect": "NONE",
    }
    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({k: result[k] for k in (
        "status", "desktop_sha256_200", "mobile_user_agent_html_200",
        "bytes_identical_to_manifest", "synthetic_draft_http_404")}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
