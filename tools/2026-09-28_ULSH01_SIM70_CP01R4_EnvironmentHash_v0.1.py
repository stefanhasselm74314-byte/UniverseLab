#!/usr/bin/env python3
"""SIM-70 deterministic environment attestation/hash for CP01R4.

This is a reproducibility instrument only. It does not authorize or execute the
physical solver. The hash binds the exact checked-out commit, dependency
metadata, numerical runtime, CPU/OS metadata, thread controls, and selected
source/configuration files.
"""
from __future__ import annotations

import argparse
import contextlib
import hashlib
import importlib.metadata as metadata
import io
import json
import os
from pathlib import Path
import platform
import subprocess
import sys
from typing import Any

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
POLICY_PATH = ROOT / "registry/2026-08-27_HZT_M0_S6_C_PHYS_M1_ULSH01_WP2_ResourcePolicy_v0.2.json"
RUN_INPUT_PATH = ROOT / "registry/2026-08-27_HZT_M0_S6_C_PHYS_M1_ULSH01_WP2_RunInputRebind_v0.3.json"

SOURCE_BINDINGS = (
    "requirements/2026-08-04_HZT_M0_S6_C_PHYS_M1_Background3C_v0.1.txt",
    "registry/2026-08-27_HZT_M0_S6_C_PHYS_M1_ULSH01_WP2_ResourcePolicy_v0.2.json",
    "registry/2026-08-27_HZT_M0_S6_C_PHYS_M1_ULSH01_WP2_RunInputRebind_v0.3.json",
    "ulsh/ULSH-01/C-PHYS/2026-08-21_ULSH01_M1C1_8x8_TargetContract_v0.1.json",
    "ulsh/ULSH-01/C-PHYS/2026-08-27_ULSH01_M1C1_8x8_ResultSchema_v0.1.json",
    "tools/2026-08-04_hzt_m0_s6_c_phys_m1_background_3c_primary_kernel_v0.1.py",
    "tools/2026-08-04_hzt_m0_s6_c_phys_m1_background_3c_primary_kernel_v0.2.py",
    "tools/2026-08-27_hzt_m0_s6_c_phys_m1_ulsh01_wp2_cp01r4_target_release_v0.1.py",
    "tools/2026-08-27_hzt_m0_s6_c_phys_m1_ulsh01_wp2_cp01r4_target_release_v0.2.py",
)

EXPECTED_VERSIONS = {
    "numpy": "2.1.3",
    "scipy": "1.14.1",
    "sympy": "1.13.3",
    "mpmath": "1.3.0",
}


class EnvironmentAuditError(RuntimeError):
    pass


def canonical_bytes(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def canonical_sha256(value: Any) -> str:
    return hashlib.sha256(canonical_bytes(value)).hexdigest()


def file_sha256(path: str | Path) -> str:
    h = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def git_head_sha(repo_root: Path) -> str:
    proc = subprocess.run(
        ["git", "-C", str(repo_root), "rev-parse", "HEAD"],
        check=False,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        timeout=15,
    )
    if proc.returncode != 0:
        raise EnvironmentAuditError(f"unable to resolve Git HEAD: {proc.stderr.strip()}")
    value = proc.stdout.strip().lower()
    if len(value) != 40 or any(c not in "0123456789abcdef" for c in value):
        raise EnvironmentAuditError("Git HEAD is not a full 40-hex SHA")
    return value


def distribution_record_sha256(name: str) -> str | None:
    dist = metadata.distribution(name)
    record = dist.read_text("RECORD")
    if record is None:
        return None
    return hashlib.sha256(record.encode("utf-8")).hexdigest()


def cpu_model() -> str:
    """Return a descriptive CPU model, never a logical processor index."""
    cpuinfo = Path("/proc/cpuinfo")
    if cpuinfo.is_file():
        parsed: dict[str, str] = {}
        for line in cpuinfo.read_text(encoding="utf-8", errors="replace").splitlines():
            if ":" not in line:
                continue
            key, value = line.split(":", 1)
            key = key.strip().lower()
            value = value.strip()
            if value and key not in parsed:
                parsed[key] = value
        for key in ("model name", "hardware", "cpu model", "machine"):
            if parsed.get(key):
                return parsed[key]
        # Some architectures expose a descriptive processor string.  Reject
        # purely numeric logical-CPU indices such as x86 "processor: 0".
        processor = parsed.get("processor", "")
        if processor and not processor.isdigit():
            return processor
    return platform.processor() or "UNKNOWN"


def numpy_config_text() -> str:
    stream = io.StringIO()
    with contextlib.redirect_stdout(stream):
        np.show_config()
    return stream.getvalue().strip()


def build_attestation(repo_root: Path, *, strict: bool) -> dict[str, Any]:
    policy = json.loads(POLICY_PATH.read_text(encoding="utf-8"))
    run_input = json.loads(RUN_INPUT_PATH.read_text(encoding="utf-8"))
    env_policy = policy["execution_environment"]
    payload = run_input["frozen_run_payload"]

    versions = {name: metadata.version(name) for name in EXPECTED_VERSIONS}
    records = {name: distribution_record_sha256(name) for name in EXPECTED_VERSIONS}

    if strict:
        if sys.version_info[:2] != (3, 12):
            raise EnvironmentAuditError(f"Python drift: {platform.python_version()}")
        if versions != EXPECTED_VERSIONS:
            raise EnvironmentAuditError(f"dependency drift: {versions!r}")
        for key, expected in env_policy["blas_thread_environment"].items():
            if os.environ.get(key) != expected:
                raise EnvironmentAuditError(f"thread environment drift: {key}={os.environ.get(key)!r}")
        if os.environ.get("ULSH01_NETWORK_ISOLATED") != "1":
            raise EnvironmentAuditError("network-isolation attestation flag missing")
        if os.environ.get("ULSH01_GPU_DISABLED") != "1":
            raise EnvironmentAuditError("GPU-disabled attestation flag missing")

    dependency_lock = repo_root / env_policy["dependency_lock"]
    actual_lock_sha = file_sha256(dependency_lock)
    if actual_lock_sha != env_policy["dependency_lock_sha256"]:
        raise EnvironmentAuditError("dependency lock bytes do not match frozen policy")

    source_hashes = {}
    for rel in SOURCE_BINDINGS:
        path = repo_root / rel
        if not path.is_file():
            raise EnvironmentAuditError(f"bound source missing: {rel}")
        source_hashes[rel] = file_sha256(path)

    numpy_config = numpy_config_text()
    uname = platform.uname()

    attestation = {
        "schema": "universelab.ulsh01.sim70.cp01r4.environment-attestation.v0.1",
        "run_id": policy["run_id"],
        "model_spec_id": policy["model_id"],
        "target_contract_digest_sha256": policy["target_contract_digest_sha256"],
        "run_payload_sha256": policy["run_payload_sha256"],
        "repository_commit_sha": git_head_sha(repo_root),
        "python": {
            "version": platform.python_version(),
            "implementation": platform.python_implementation(),
            "implementation_cache_tag": getattr(sys.implementation, "cache_tag", None),
            "executable_basename": Path(sys.executable).name,
        },
        "platform": {
            "system": uname.system,
            "release": uname.release,
            "version": uname.version,
            "machine": uname.machine,
            "libc": list(platform.libc_ver()),
        },
        "hardware": {
            "cpu_model": cpu_model(),
            "logical_cpu_count": os.cpu_count(),
        },
        "dependencies": {
            name: {
                "version": versions[name],
                "installed_record_sha256": records[name],
            }
            for name in sorted(versions)
        },
        "numpy_runtime": {
            "version": np.__version__,
            "show_config_sha256": hashlib.sha256(numpy_config.encode("utf-8")).hexdigest(),
            "show_config": numpy_config,
        },
        "precision": {
            "primary": env_policy["floating_point_primary"],
            "float64_mantissa_bits": int(np.finfo(np.float64).nmant),
            "longdouble_mantissa_bits": int(np.finfo(np.longdouble).nmant),
            "higher_precision_requirement": payload["primary_discretization"]["higher_precision_audit"],
        },
        "thread_environment": {
            key: os.environ.get(key)
            for key in sorted(env_policy["blas_thread_environment"])
        },
        "isolation_attestation_flags": {
            "network_isolated": os.environ.get("ULSH01_NETWORK_ISOLATED") == "1",
            "gpu_disabled": os.environ.get("ULSH01_GPU_DISABLED") == "1",
            "note": "Flags are runtime attestations; this QA tool does not independently prove OS-level network/GPU isolation.",
        },
        "dependency_lock_sha256": actual_lock_sha,
        "source_sha256": source_hashes,
        "physical_interpretation": "NONE",
        "canonical_effect": "NONE",
        "physical_evidence_effect": "NONE_QA_ONLY",
    }

    if attestation["run_id"] != payload["run_id"]:
        raise EnvironmentAuditError("run-id mismatch between resource policy and run payload")
    if attestation["target_contract_digest_sha256"] != payload["target_contract_digest_sha256"]:
        raise EnvironmentAuditError("target digest mismatch between resource policy and run payload")
    return attestation


def build_packet(repo_root: Path, *, strict: bool) -> dict[str, Any]:
    attestation = build_attestation(repo_root, strict=strict)
    return {
        "schema": "universelab.ulsh01.sim70.cp01r4.environment-hash-packet.v0.1",
        "environment_hash_sha256": canonical_sha256(attestation),
        "attestation": attestation,
        "determinism_scope": "SAME_CHECKED_OUT_COMMIT_AND_RUNTIME_METADATA",
        "physical_interpretation": "NONE",
        "canonical_effect": "NONE",
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", default=str(ROOT))
    parser.add_argument("--strict", action="store_true")
    parser.add_argument("--output")
    args = parser.parse_args()

    packet = build_packet(Path(args.repo_root).resolve(), strict=args.strict)
    text = json.dumps(packet, indent=2, sort_keys=True)
    print(text)
    if args.output:
        Path(args.output).write_text(text + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
