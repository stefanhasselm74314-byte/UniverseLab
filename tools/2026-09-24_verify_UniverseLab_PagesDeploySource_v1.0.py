#!/usr/bin/env python3
"""Fail-closed source guard for UniverseLab GitHub Pages deployments."""
from __future__ import annotations

import argparse
import re
import subprocess
import sys

SHA_RE = re.compile(r"^[0-9a-f]{40}$")


class GuardError(RuntimeError):
    pass


def _git(*args: str) -> str:
    proc = subprocess.run(
        ["git", *args],
        check=False,
        text=True,
        capture_output=True,
    )
    if proc.returncode != 0:
        raise GuardError(f"GIT_FAILED:{' '.join(args)}:{proc.stderr.strip()}")
    return proc.stdout.strip()


def resolve_deploy_sha() -> str:
    return _git("rev-parse", "HEAD")


def resolve_current_main_sha() -> str:
    output = _git("ls-remote", "--exit-code", "origin", "refs/heads/main")
    rows = [line.split() for line in output.splitlines() if line.strip()]
    exact = [row[0] for row in rows if len(row) >= 2 and row[1] == "refs/heads/main"]
    if len(exact) != 1:
        raise GuardError(f"MAIN_REF_NOT_UNIQUE:{len(exact)}")
    return exact[0]


def verify(deploy_sha: str, current_main_sha: str, run_attempt: int) -> None:
    deploy_sha = deploy_sha.strip().lower()
    current_main_sha = current_main_sha.strip().lower()

    if run_attempt < 1:
        raise GuardError("INVALID_RUN_ATTEMPT")
    if run_attempt > 1:
        raise GuardError(
            "WORKFLOW_RERUN_FORBIDDEN: start a fresh workflow_dispatch from current main"
        )
    if not SHA_RE.fullmatch(deploy_sha):
        raise GuardError("INVALID_DEPLOY_SHA")
    if not SHA_RE.fullmatch(current_main_sha):
        raise GuardError("INVALID_CURRENT_MAIN_SHA")
    if deploy_sha != current_main_sha:
        raise GuardError(
            f"STALE_DEPLOY_SHA:{deploy_sha}:CURRENT_MAIN:{current_main_sha}"
        )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--deploy-sha")
    parser.add_argument("--current-main-sha")
    parser.add_argument("--run-attempt", type=int, default=1)
    args = parser.parse_args()

    try:
        deploy_sha = args.deploy_sha or resolve_deploy_sha()
        current_main_sha = args.current_main_sha or resolve_current_main_sha()
        verify(deploy_sha, current_main_sha, args.run_attempt)
    except GuardError as exc:
        print(f"::error::{exc}", file=sys.stderr)
        return 1

    print(
        f"DEPLOY_SOURCE_VERIFIED deploy_sha={deploy_sha} "
        f"current_main_sha={current_main_sha}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
