#!/usr/bin/env python3
"""ULSH-01 WP2 CP01R4 grant-gated primary target release v0.1.

Safe audit/self-test modes never import the numerical backend. A future operational
run requires exact package/source bindings, a separate authorization decision, a
matching active single-use grant, and atomic reservation before backend import.
This module creates neither an authorization decision nor an operative grant.
"""
from __future__ import annotations

import argparse
import ast
from datetime import datetime, timezone
import hashlib
import importlib.metadata
import importlib.util
import json
import math
import os
from pathlib import Path
import platform
import signal
import sys
import time
from typing import Any, Iterable

EXIT_NOT_AUTHORIZED = 73
EXIT_PREFLIGHT_FAILURE = 74
EXIT_EXECUTION_FAILURE = 75
TARGET_DIGEST = "237c4b5e08a2106e13e985c4af7925f1899e2ae2e4b7253c7ab73cc2db5f1823"
RUN_ID = "HZT-M0-S6-C-PHYS-M1-ULSH01-WP2-CP01R4"
RUN_PAYLOAD_SHA256 = "8e5976a22c4be78b5e4fe7834c9947de8a4acea7781363c7aeb83aa73982ac8c"
DEPENDENCY_LOCK_SHA256 = "4f0095cc5e8c2a9eff7f22140c05cadb571a4809b87ce74aa79f460cfa2ab95f"
PRIMARY_SHA256 = "8ce1c0eceed64245d091d4bed492f3cf2a9c8314f631a03045aaa9696fb11c92"
PRIMARY_BASE_SHA256 = "830d4b4fdd28c8888876125479df3542eeb3864d4328764feb96b5d34bd91599"

RUN_INPUT_PATH = Path("registry/2026-08-27_HZT_M0_S6_C_PHYS_M1_ULSH01_WP2_RunInputRebind_v0.3.json")
RESOURCE_POLICY_PATH = Path("registry/2026-08-27_HZT_M0_S6_C_PHYS_M1_ULSH01_WP2_ResourcePolicy_v0.2.json")
BACKEND_REBIND_PATH = Path("registry/2026-08-27_HZT_M0_S6_C_PHYS_M1_ULSH01_WP2_BackendRebindContract_v0.2.json")
GRANT_SCHEMA_PATH = Path("registry/2026-08-27_HZT_M0_S6_C_PHYS_M1_ULSH01_WP2_SingleUseGrantSchema_v0.2.json")
DECISION_SCHEMA_PATH = Path("registry/2026-08-27_HZT_M0_S6_C_PHYS_M1_ULSH01_WP2_AuthorizationDecisionSchema_v0.1.json")
TRANSACTION_CONTRACT_PATH = Path("registry/2026-08-27_HZT_M0_S6_C_PHYS_M1_ULSH01_WP2_TargetTransactionContract_v0.2.json")
TARGET_PATH = Path("ulsh/ULSH-01/C-PHYS/2026-08-21_ULSH01_M1C1_8x8_TargetContract_v0.1.json")
INTERFACE_PATH = Path("ulsh/ULSH-01/C-PHYS/2026-08-27_ULSH01_M1C1_8x8_BackendInterfaceContract_v0.1.json")
RESULT_SCHEMA_PATH = Path("ulsh/ULSH-01/C-PHYS/2026-08-27_ULSH01_M1C1_8x8_ResultSchema_v0.1.json")
PRIMARY_ADAPTER_PATH = Path("tools/2026-08-04_hzt_m0_s6_c_phys_m1_background_3c_primary_kernel_v0.2.py")
PRIMARY_BASE_PATH = Path("tools/2026-08-04_hzt_m0_s6_c_phys_m1_background_3c_primary_kernel_v0.1.py")
DEPENDENCY_LOCK_PATH = Path("requirements/2026-08-04_HZT_M0_S6_C_PHYS_M1_Background3C_v0.1.txt")
BACKEND_IMPORT_COUNT = 0
SOLVER_CALL_COUNT = 0

class ReleaseError(RuntimeError): pass
class AuthorizationError(ReleaseError): pass
class ReplayError(AuthorizationError): pass
class SolveTimeout(ReleaseError): pass

def require(condition: bool, message: str) -> None:
    if not condition: raise ReleaseError(message)

def load_json(path: str | Path) -> dict[str, Any]:
    value = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(value, dict): raise ReleaseError(f"JSON root must be an object: {path}")
    return value

def canonical_bytes(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")

def canonical_sha256(value: Any) -> str:
    return hashlib.sha256(canonical_bytes(value)).hexdigest()

def file_sha256(path: str | Path) -> str:
    h = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""): h.update(chunk)
    return h.hexdigest()

def parse_utc(value: Any) -> datetime:
    if not isinstance(value, str): raise AuthorizationError("UTC timestamp must be a string")
    try: parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc: raise AuthorizationError(f"invalid UTC timestamp: {value!r}") from exc
    if parsed.tzinfo is None: raise AuthorizationError("timestamp must be timezone-aware")
    return parsed.astimezone(timezone.utc)

def verify_time_window(not_before: Any, expires_at: Any, now: datetime) -> None:
    start, stop, current = parse_utc(not_before), parse_utc(expires_at), now.astimezone(timezone.utc)
    if stop <= start: raise AuthorizationError("authorization time window is inverted")
    if current < start or current >= stop: raise AuthorizationError("authorization is outside its active time window")

def verify_target(target: dict[str, Any]) -> None:
    semantics = target.get("target_semantics")
    require(isinstance(semantics, dict), "target_semantics missing")
    require(canonical_sha256(semantics) == TARGET_DIGEST, "target digest mismatch")
    require(target.get("target_contract_digest", {}).get("sha256") == TARGET_DIGEST, "recorded target digest mismatch")
    require(target.get("solver_authorized") is False, "target freeze unexpectedly authorizes execution")

def verify_run_input(run_input: dict[str, Any]) -> dict[str, Any]:
    require(run_input.get("status") == "RUN_INPUT_FROZEN_CP01R4_EXECUTION_NOT_AUTHORIZED", "CP01R4 status mismatch")
    payload = run_input.get("frozen_run_payload")
    require(isinstance(payload, dict), "frozen_run_payload missing")
    require(canonical_sha256(payload) == RUN_PAYLOAD_SHA256, "CP01R4 canonical payload digest mismatch")
    require(run_input.get("frozen_run_payload_sha256") == RUN_PAYLOAD_SHA256, "CP01R4 recorded payload digest mismatch")
    require(payload.get("run_id") == RUN_ID and payload.get("target_contract_digest_sha256") == TARGET_DIGEST, "CP01R4 identity mismatch")
    require(payload.get("model_parameters_ordered", {}).get("a_F") == "1/4", "target a_F must equal 1/4")
    require(payload.get("dimensional_anchor", {}).get("physical_value_assigned") is False, "M6 physical value must remain unassigned")
    require(payload.get("primary_discretization", {}).get("regional_node_counts") == [24,32,48,64,96], "mesh schedule drift")
    prolong = payload.get("mesh_prolongation", {})
    require(prolong.get("interpolant") == "CHEBYSHEV_LOBATTO_BARYCENTRIC_POLYNOMIAL_INTERPOLATION", "mesh prolongation not frozen")
    require(prolong.get("node_transition_order") == [[24,32],[32,48],[48,64],[64,96]], "mesh transition order drift")
    tracking = payload.get("candidate_tracking", {})
    require(tracking.get("lowest_residual_cherry_pick") is False and tracking.get("all_distinct_candidates_retained") is True, "candidate tracking firewall drift")
    firewall = run_input.get("execution_firewall", {})
    require(firewall.get("solver_authorized") is False and firewall.get("target_solve_allowed") is False, "run-input firewall drift")
    return payload

def verify_resource_policy(policy: dict[str, Any]) -> None:
    require(policy.get("run_id") == RUN_ID and policy.get("run_payload_sha256") == RUN_PAYLOAD_SHA256, "resource binding mismatch")
    require(policy.get("target_contract_digest_sha256") == TARGET_DIGEST, "resource target mismatch")
    env = policy.get("execution_environment", {})
    require(env.get("dependency_lock_sha256") == DEPENDENCY_LOCK_SHA256, "dependency-lock binding mismatch")
    require(env.get("python") == "3.12.x" and env.get("numpy") == "2.1.3" and env.get("scipy") == "1.14.1", "runtime dependency policy drift")
    require(env.get("thread_count") == 1 and env.get("gpu_allowed") is False and env.get("network_access") is False, "resource isolation policy drift")
    order = policy.get("execution_order", {})
    require(order.get("primary_node_counts") == [24,32,48,64,96] and order.get("independent_backend_in_WP2") is False, "WP2 execution-order drift")
    current = policy.get("current_state", {})
    require(current.get("execution_authorized") is False and current.get("backend_imported") is False, "resource policy unexpectedly records execution")

def verify_backend_rebind(repo_root: Path, rebind: dict[str, Any]) -> None:
    require(rebind.get("run_id") == RUN_ID and rebind.get("run_payload_sha256") == RUN_PAYLOAD_SHA256, "backend rebind identity mismatch")
    require(rebind.get("target_contract_digest_sha256") == TARGET_DIGEST, "backend target mismatch")
    bindings = rebind.get("audited_source_bindings", {})
    for key, expected in (("primary_adapter", PRIMARY_SHA256), ("primary_base", PRIMARY_BASE_SHA256)):
        item = bindings.get(key, {})
        require(item.get("sha256") == expected, f"{key} recorded source digest mismatch")
        require(file_sha256(repo_root / item["path"]) == expected, f"{key} source bytes changed")
    require(rebind.get("compatibility", {}).get("Sigma_FT_present") is False and rebind.get("compatibility", {}).get("augmented_10x10_present") is False, "noncanonical target leaked into rebind")
    bind = rebind.get("cp01r4_execution_binding", {})
    require(bind.get("control_a_F_override_allowed") is False and bind.get("independent_backend_call_in_WP2") is False, "backend execution binding drift")
    firewall = rebind.get("firewall", {})
    require(firewall.get("backend_import_authorized") is False and firewall.get("cp01r4_execution_authorized") is False, "backend rebind unexpectedly authorizes")

def verify_interface_and_result(interface: dict[str, Any], result: dict[str, Any]) -> None:
    require(interface.get("authority", {}).get("target_digest_sha256") == TARGET_DIGEST and result.get("target_contract_digest_sha256") == TARGET_DIGEST, "interface/result target mismatch")
    expected = ["R_A","R_ell","R_varphi","R_patch","R_4d","R_chi","R_scalar","R_gauge_local"]
    require(interface.get("interface", {}).get("boundary_residual_order") == expected and result.get("solution", {}).get("boundary_residual_order") == expected, "boundary order drift")
    require(interface.get("patch_binding", {}).get("representation") == "a_chi_Sigma := a_chi_S(cap)", "patch binding drift")
    require(interface.get("firewall", {}).get("solver_authorized") is False and result.get("governance", {}).get("solver_authorized") is False, "schema firewall drift")

def verify_nonoperative_templates(grant_schema: dict[str, Any], decision_schema: dict[str, Any]) -> None:
    require(grant_schema.get("status") == "TEMPLATE_ONLY_NO_GRANT_CREATED", "grant template status drift")
    grant = grant_schema.get("grant", {})
    require(grant.get("authorized") is False and grant.get("automatic_authorization") is False and grant.get("run_payload_sha256") == RUN_PAYLOAD_SHA256, "grant template unexpectedly operative")
    require(decision_schema.get("status") == "TEMPLATE_ONLY_NOT_AUTHORIZED", "decision template status drift")
    require(decision_schema.get("decision", {}).get("decision_status") == "NOT_AUTHORIZED", "decision template unexpectedly operative")
    require(decision_schema.get("firewall", {}).get("solver_execution_allowed") is False, "decision template firewall drift")

def _numeric_ast(node: ast.AST) -> float | int:
    if isinstance(node, ast.Constant) and isinstance(node.value, (int,float)): return node.value
    if isinstance(node, ast.UnaryOp) and isinstance(node.op, (ast.UAdd,ast.USub)):
        value = _numeric_ast(node.operand); return value if isinstance(node.op, ast.UAdd) else -value
    if isinstance(node, ast.BinOp) and isinstance(node.op, (ast.Add,ast.Sub,ast.Mult,ast.Div,ast.Pow)):
        left,right = _numeric_ast(node.left),_numeric_ast(node.right)
        if isinstance(node.op, ast.Add): return left+right
        if isinstance(node.op, ast.Sub): return left-right
        if isinstance(node.op, ast.Mult): return left*right
        if isinstance(node.op, ast.Div): return left/right
        return left**right
    raise ReleaseError(f"unsupported default expression: {ast.dump(node)}")

def _function_defaults(tree: ast.Module, name: str) -> dict[str,float|int]:
    fn = next((n for n in tree.body if isinstance(n,(ast.FunctionDef,ast.AsyncFunctionDef)) and n.name==name), None)
    require(fn is not None, f"function missing from primary base: {name}")
    out: dict[str,float|int] = {}
    for arg,default in zip(fn.args.kwonlyargs, fn.args.kw_defaults):
        if default is not None: out[arg.arg] = _numeric_ast(default)
    if fn.args.defaults:
        for arg,default in zip(fn.args.args[-len(fn.args.defaults):], fn.args.defaults): out[arg.arg] = _numeric_ast(default)
    return out

def verify_primary_method_defaults(repo_root: Path, payload: dict[str, Any]) -> None:
    tree = ast.parse((repo_root / PRIMARY_BASE_PATH).read_text(encoding="utf-8"))
    defaults = _function_defaults(tree, "damped_newton"); method = payload["nonlinear_method"]
    expected = {"maximum_iterations":method["maximum_newton_iterations_per_mesh"],"maximum_backtracking_steps":method["maximum_backtracking_steps"],"armijo_parameter":method["armijo_parameter"],"minimum_step_fraction":method["minimum_step_fraction"],"trust_radius_initial":method["trust_region_initial_radius"],"trust_radius_minimum":method["trust_region_minimum_radius"],"residual_tolerance":method["residual_tolerance"],"step_tolerance":method["step_tolerance"],"stagnation_window_iterations":method["stagnation_window_iterations"],"stagnation_relative_improvement_floor":method["stagnation_relative_improvement_floor"]}
    for key,value in expected.items(): require(key in defaults and float(defaults[key])==float(value), f"damped_newton default drift: {key}")
    require(float(_function_defaults(tree,"complex_step_jacobian").get("step",math.nan))==float(method["complex_step_size"]), "complex-step default drift")
    require(float(_function_defaults(tree,"rrqr_step").get("rank_rtol",math.nan))==float(method["rrqr_rank_rtol"]), "RRQR tolerance drift")
    adm = _function_defaults(tree,"admissible")
    require(float(adm.get("rho_min",math.nan))==float(payload["acceptance_thresholds"]["minimum_rho_N"]), "rho admissibility drift")
    require(float(adm.get("ell_margin",math.nan))==float(payload["acceptance_thresholds"]["minimum_interior_ell_margin"]), "ell admissibility drift")

def build_release_manifest(repo_root: Path, transaction: dict[str, Any]) -> dict[str, Any]:
    members = transaction.get("release_package_members"); require(isinstance(members,list) and members, "release package members missing")
    hashes: dict[str,str] = {}
    for rel in members:
        require(isinstance(rel,str) and rel, "invalid release member"); path = repo_root/rel; require(path.is_file(), f"release member missing: {rel}"); hashes[rel]=file_sha256(path)
    return {"schema":"universelab.hzt-m0-s6-c-phys-m1.ulsh01-wp2-cp01r4-release-package-manifest.v0.1","classification":"GENERATED_IMPLEMENTATION_QA_ARTIFACT_NO_PHYSICAL_RESULT","run_id":RUN_ID,"target_contract_digest_sha256":TARGET_DIGEST,"run_payload_sha256":RUN_PAYLOAD_SHA256,"member_sha256":hashes,"package_digest_sha256":canonical_sha256(hashes),"backend_imported":False,"solver_executed":False,"physical_evidence_effect":"NONE"}

def preflight(repo_root: Path):
    target=load_json(repo_root/TARGET_PATH); run_input=load_json(repo_root/RUN_INPUT_PATH); policy=load_json(repo_root/RESOURCE_POLICY_PATH); rebind=load_json(repo_root/BACKEND_REBIND_PATH); grant_schema=load_json(repo_root/GRANT_SCHEMA_PATH); decision_schema=load_json(repo_root/DECISION_SCHEMA_PATH); transaction=load_json(repo_root/TRANSACTION_CONTRACT_PATH); interface=load_json(repo_root/INTERFACE_PATH); result=load_json(repo_root/RESULT_SCHEMA_PATH)
    verify_target(target); payload=verify_run_input(run_input); verify_resource_policy(policy); verify_backend_rebind(repo_root,rebind); verify_interface_and_result(interface,result); verify_nonoperative_templates(grant_schema,decision_schema); verify_primary_method_defaults(repo_root,payload)
    require(file_sha256(repo_root/DEPENDENCY_LOCK_PATH)==DEPENDENCY_LOCK_SHA256, "dependency lock bytes changed")
    require(transaction.get("run_id")==RUN_ID and transaction.get("run_payload_sha256")==RUN_PAYLOAD_SHA256 and transaction.get("firewall",{}).get("physical_execution_authorized") is False, "transaction binding/firewall drift")
    manifest=build_release_manifest(repo_root,transaction)
    bindings={"target_contract_file_sha256":file_sha256(repo_root/TARGET_PATH),"resource_policy_sha256":file_sha256(repo_root/RESOURCE_POLICY_PATH),"backend_rebind_contract_sha256":file_sha256(repo_root/BACKEND_REBIND_PATH),"result_schema_sha256":file_sha256(repo_root/RESULT_SCHEMA_PATH),"backend_interface_contract_sha256":file_sha256(repo_root/INTERFACE_PATH),"dependency_lock_sha256":file_sha256(repo_root/DEPENDENCY_LOCK_PATH),"primary_source_sha256":file_sha256(repo_root/PRIMARY_ADAPTER_PATH),"primary_base_source_sha256":file_sha256(repo_root/PRIMARY_BASE_PATH)}
    return payload,policy,manifest,bindings

def tau_nodes(node_count: int) -> list[float]:
    require(node_count>=2,"node_count must be >=2"); return [(1.0-math.cos(i*math.pi/(node_count-1)))/2.0 for i in range(node_count)]

def barycentric_weights(node_count: int) -> list[float]:
    return [((-1.0)**i)*(0.5 if i in (0,node_count-1) else 1.0) for i in range(node_count)]

def barycentric_interpolate(source_values: Iterable[float], old_count: int, new_count: int) -> list[float]:
    values=[float(v) for v in source_values]; require(len(values)==old_count,"source profile length mismatch"); old=tau_nodes(old_count); new=tau_nodes(new_count); weights=barycentric_weights(old_count); coincidence=16.0*sys.float_info.epsilon; out=[]
    for target in new:
        copied=None
        for i,source in enumerate(old):
            if abs(target-source)<=coincidence: copied=values[i]; break
        if copied is not None: out.append(copied); continue
        num=den=0.0
        for source,value,weight in zip(old,values,weights): term=weight/(target-source); num+=term*value; den+=term
        out.append(num/den)
    return out

def validate_synthetic_prolongation() -> None:
    for old_count,new_count in ((24,32),(32,48),(48,64),(64,96)):
        source=tau_nodes(old_count); values=[1-2*t+3*t*t-0.5*t*t*t for t in source]; got=barycentric_interpolate(values,old_count,new_count); expected=[1-2*t+3*t*t-0.5*t*t*t for t in tau_nodes(new_count)]; error=max(abs(a-b) for a,b in zip(got,expected)); require(error<=2e-12,f"synthetic barycentric QA failed {old_count}->{new_count}: {error}")

def verify_decision(decision: dict[str,Any], manifest: dict[str,Any], bindings: dict[str,str], commit: str, now: datetime) -> str:
    require(decision.get("schema")=="universelab.hzt-m0-s6-c-phys-m1.ulsh01-wp2-authorization-decision.v0.1", "decision schema mismatch")
    require(decision.get("status")=="AUTHORIZED_SINGLE_USE_WP2_CP01R4_PRIMARY_TARGET_EXECUTION", "decision is not operative")
    data=decision.get("decision"); require(isinstance(data,dict),"decision body missing")
    require(data.get("decision_status")==decision.get("status") and data.get("authorized_run_id")==RUN_ID and data.get("authorized_scope")=="PRIMARY_TARGET_EXECUTION_ONLY", "decision scope/status mismatch")
    require(data.get("repository_commit_sha")==commit and data.get("target_contract_digest_sha256")==TARGET_DIGEST and data.get("run_payload_sha256")==RUN_PAYLOAD_SHA256, "decision identity binding mismatch")
    require(data.get("release_package_manifest_sha256")==manifest["package_digest_sha256"], "decision package mismatch")
    for key in ("resource_policy_sha256","backend_rebind_contract_sha256","result_schema_sha256","backend_interface_contract_sha256"): require(data.get(key)==bindings[key],f"decision {key} mismatch")
    require(data.get("single_use_grant_required") is True and data.get("automatic_execution") is False, "decision execution semantics mismatch")
    require(data.get("wp3_authorized") is False and data.get("wp4_authorized") is False and data.get("physical_response_rank_authorized") is False and data.get("K1_D_release_authorized") is False, "decision overreach")
    verify_time_window(data.get("not_before_utc"),data.get("expires_at_utc"),now); decision_id=data.get("authorization_decision_id"); require(isinstance(decision_id,str) and decision_id,"decision id missing"); return decision_id

def verify_grant(grant_doc: dict[str,Any], decision_id: str, decision_sha: str, manifest: dict[str,Any], bindings: dict[str,str], commit: str, now: datetime, *, control_only: bool) -> dict[str,Any]:
    grant=grant_doc.get("grant",grant_doc); require(isinstance(grant,dict),"grant body missing")
    require(grant.get("target_contract_digest_sha256")==TARGET_DIGEST and grant.get("run_payload_sha256")==RUN_PAYLOAD_SHA256 and grant.get("release_package_manifest_sha256")==manifest["package_digest_sha256"],"grant target/payload/package mismatch")
    require(grant.get("repository_commit_sha")==commit and grant.get("authorization_decision_id")==decision_id and grant.get("authorization_decision_sha256")==decision_sha,"grant decision/commit mismatch")
    require(grant.get("dependency_lock_sha256")==DEPENDENCY_LOCK_SHA256 and grant.get("primary_source_sha256")==PRIMARY_SHA256 and grant.get("primary_base_source_sha256")==PRIMARY_BASE_SHA256,"grant source/dependency mismatch")
    for key in ("resource_policy_sha256","backend_rebind_contract_sha256","result_schema_sha256","backend_interface_contract_sha256","target_contract_file_sha256"): require(grant.get(key)==bindings[key],f"grant {key} mismatch")
    require(grant.get("target_a_F")=="1/4" and grant.get("control_override_allowed") is False and grant.get("single_use") is True and grant.get("automatic_authorization") is False,"grant target/single-use semantics mismatch")
    require(isinstance(grant.get("grant_id"),str) and grant.get("grant_id") and isinstance(grant.get("nonce"),str) and grant.get("nonce"),"grant identity missing")
    if control_only: require(grant.get("control_only") is True and grant.get("scope")=="SYNTHETIC_CONTROL_ONLY_NO_BACKEND_IMPORT" and grant.get("authorized") is False,"synthetic grant scope mismatch")
    else: require(grant.get("control_only") is False and grant.get("authorized") is True and grant.get("scope")==f"{RUN_ID}_TARGET_ONLY","operative grant scope mismatch")
    verify_time_window(grant.get("not_before_utc"),grant.get("expires_at_utc"),now); return grant

def _exclusive_create(path: Path, content: bytes) -> None:
    flags=os.O_WRONLY|os.O_CREAT|os.O_EXCL
    try: fd=os.open(path,flags,0o600)
    except FileExistsError as exc: raise ReplayError(f"single-use token already consumed: {path.name}") from exc
    with os.fdopen(fd,"wb") as handle: handle.write(content); handle.flush(); os.fsync(handle.fileno())

def atomic_reserve_grant(reservation_dir: str|Path, grant: dict[str,Any], *, control_only: bool) -> Path:
    root=Path(reservation_dir); root.mkdir(parents=True,exist_ok=True); gid=str(grant["grant_id"]); nonce=str(grant["nonce"]); gh=hashlib.sha256(gid.encode()).hexdigest(); nh=hashlib.sha256(nonce.encode()).hexdigest(); ph=hashlib.sha256(f"{gid}\0{nonce}".encode()).hexdigest()
    _exclusive_create(root/f"grant-{gh}.lock",b"CONSUMED\n"); _exclusive_create(root/f"nonce-{nh}.lock",b"CONSUMED\n")
    record_path=root/f"reservation-{ph}.json"; record={"schema":"universelab.hzt-m0-s6-c-phys-m1.ulsh01-wp2-grant-reservation.v0.2","run_id":RUN_ID,"grant_id":gid,"nonce_sha256":nh,"state":"RESERVED","control_only":control_only,"backend_imported":False,"solver_executed":False,"physical_evidence_effect":"NONE"}; _exclusive_create(record_path,canonical_bytes(record)+b"\n"); return record_path

def update_reservation(path: Path, state: str, *, backend_imported: bool, solver_executed: bool) -> None:
    require(state in {"SUCCEEDED","FAILED","TIMED_OUT","SIGNALED","CRASH_RECOVERY_LOCKED"},"invalid reservation state"); record=load_json(path); record["state"]=state; record["backend_imported"]=bool(backend_imported); record["solver_executed"]=bool(solver_executed); tmp=path.with_suffix(path.suffix+".tmp"); tmp.write_bytes(canonical_bytes(record)+b"\n"); os.chmod(tmp,0o600); os.replace(tmp,path)

def environment_attestation(policy: dict[str,Any]) -> dict[str,Any]:
    env=policy["execution_environment"]; require(sys.version_info[:2]==(3,12),"runtime Python must be 3.12.x"); versions={name:importlib.metadata.version(name) for name in ("numpy","scipy","sympy","mpmath")}
    for name,expected in (("numpy","2.1.3"),("scipy","1.14.1"),("sympy","1.13.3"),("mpmath","1.3.0")): require(versions[name]==expected,f"runtime dependency drift: {name}")
    for key,value in env["blas_thread_environment"].items(): require(os.environ.get(key)==value,f"thread environment missing: {key}={value}")
    require(os.environ.get("ULSH01_NETWORK_ISOLATED")=="1","network isolation attestation missing"); require(os.environ.get("ULSH01_GPU_DISABLED")=="1","GPU-disabled attestation missing")
    files=importlib.metadata.files("numpy") or []; blas=sorted(str(item) for item in files if ".libs" in str(item) and ("blas" in str(item).lower() or "openblas" in str(item).lower()))
    return {"schema":"universelab.hzt-m0-s6-c-phys-m1.ulsh01-wp2-environment-attestation.v0.1","python":platform.python_version(),"platform":platform.platform(),"machine":platform.machine(),"processor":platform.processor(),"logical_cpu_count":os.cpu_count(),"dependency_versions":versions,"numpy_blas_library_files":blas,"thread_environment":{k:os.environ.get(k) for k in env["blas_thread_environment"]},"network_isolated_attested":True,"gpu_disabled_attested":True}

def _load_primary_backend(repo_root: Path):
    global BACKEND_IMPORT_COUNT; BACKEND_IMPORT_COUNT+=1; path=repo_root/PRIMARY_ADAPTER_PATH; spec=importlib.util.spec_from_file_location("ulsh01_cp01r4_primary_backend",path)
    if spec is None or spec.loader is None: raise ReleaseError("unable to construct primary backend import")
    module=importlib.util.module_from_spec(spec); sys.modules[spec.name]=module; spec.loader.exec_module(module); return module

def prolong_state(backend: Any, state: Any, old_count: int, new_count: int):
    regions,parameters=backend.unpack_state(state,old_count); new_regions=[]
    for region in regions: new_regions.append([backend.np.asarray(barycentric_interpolate(field.tolist(),old_count,new_count),dtype=float) for field in region])
    return backend.pack_state(new_regions,parameters.copy())

def state_distance(backend: Any, left: Any, right: Any) -> float: return float(backend.np.max(backend.np.abs(backend.np.asarray(left)-backend.np.asarray(right))))

def evaluate_state(backend: Any, state: Any, n: int, model: Any, sector: Any):
    vector,info=backend.residual(state,n,model,sector); np=backend.np; bulk=vector[:-8]; boundary=vector[-8:]; constraint=np.concatenate((info["north"].constraint,info["south"].constraint)); ell_sigma=0.5*(info["north"].ell[-1]+info["south"].ell[-1]); d_chi=sector.N_sigma-sector.m_sigma*model.q_hat*info["south"].a_chi[-1]; y_sigma=model.z_sigma_hat*d_chi**2/ell_sigma**2
    metrics={"bulk_residual_inf":float(np.max(np.abs(bulk))),"boundary_residual_inf":float(np.max(np.abs(boundary))),"constraint_inf":float(np.max(np.abs(constraint))),"boundary_residual_vector":[float(v) for v in boundary],"admissible":bool(backend.admissible(state,n)),"finite":bool(np.all(np.isfinite(state)) and np.all(np.isfinite(vector)) and np.all(np.isfinite(constraint))),"ell_sigma":float(ell_sigma),"Y_hat_sigma":float(y_sigma),"positive_winding_gate":bool(y_sigma>=-1e-12)}; return metrics,info

def _timeout_handler(signum,frame): raise SolveTimeout("per-seed-per-level wall-clock limit exceeded")
def run_newton(backend: Any, initial: Any, n: int, model: Any, sector: Any, method: dict[str,Any], timeout: float):
    global SOLVER_CALL_COUNT; SOLVER_CALL_COUNT+=1; old=signal.signal(signal.SIGALRM,_timeout_handler); signal.setitimer(signal.ITIMER_REAL,timeout)
    try: return backend.damped_newton(initial,n,model,sector,maximum_iterations=method["maximum_newton_iterations_per_mesh"],maximum_backtracking_steps=method["maximum_backtracking_steps"],armijo_parameter=method["armijo_parameter"],minimum_step_fraction=method["minimum_step_fraction"],trust_radius_initial=method["trust_region_initial_radius"],trust_radius_minimum=method["trust_region_minimum_radius"],residual_tolerance=method["residual_tolerance"],step_tolerance=method["step_tolerance"],stagnation_window_iterations=method["stagnation_window_iterations"],stagnation_relative_improvement_floor=method["stagnation_relative_improvement_floor"])
    finally: signal.setitimer(signal.ITIMER_REAL,0.0); signal.signal(signal.SIGALRM,old)

def deduplicate_tracks(backend: Any, tracks: list[dict[str,Any]], threshold: float) -> list[dict[str,Any]]:
    retained=[]
    for track in sorted(tracks,key=lambda item:min(item["seed_origins"])):
        for existing in retained:
            if state_distance(backend,track["state"],existing["state"])<=threshold: existing["seed_origins"]=sorted(set(existing["seed_origins"]+track["seed_origins"])); break
        else: retained.append(track)
    return retained

def spectral_tail_audit(backend: Any, state: Any, n: int) -> dict[str,Any]:
    np=backend.np; regions,_=backend.unpack_state(state,n); x=np.asarray([2*t-1 for t in tau_nodes(n)],dtype=float); records=[]; all_pass=True
    for ri,region in enumerate(regions):
        for fi,field in enumerate(region):
            coeff=np.polynomial.chebyshev.chebfit(x,field,deg=n-1); tail=np.abs(coeff[-8:]); previous4=float(np.max(tail[:4])); last4=float(np.max(tail[4:])); tail_max=float(np.max(tail)); passed=bool(last4<=previous4 and tail_max<=1e-9); all_pass=all_pass and passed; records.append({"region_index":ri,"field_index":fi,"last8_abs":[float(v) for v in tail],"max_previous4":previous4,"max_last4":last4,"tail_max":tail_max,"pass":passed})
    return {"pass":bool(all_pass),"records":records}

def candidate_final_qa(backend: Any, track: dict[str,Any], payload: dict[str,Any]) -> dict[str,Any]:
    thresholds=payload["acceptance_thresholds"]; records=track["levels"]; failures=[]
    for level in payload["convergence_requirements"]["required_successful_levels"]:
        rec=records.get(str(level))
        if rec is None or not rec["converged"]: failures.append(f"N{level}_not_converged"); continue
        m=rec["metrics"]
        if m["bulk_residual_inf"]>thresholds["bulk_residual_max"]: failures.append(f"N{level}_bulk")
        if m["boundary_residual_inf"]>thresholds["boundary_residual_max"]: failures.append(f"N{level}_boundary")
        if m["constraint_inf"]>thresholds["rr_constraint_max"]: failures.append(f"N{level}_constraint")
        if not m["admissible"] or not m["finite"] or not m["positive_winding_gate"]: failures.append(f"N{level}_admissibility")
    for low,high in ((48,64),(64,96)):
        if str(low) in records and str(high) in records:
            for channel in ("bulk_residual_inf","boundary_residual_inf","constraint_inf"):
                if records[str(high)]["metrics"][channel]>1.25*records[str(low)]["metrics"][channel]: failures.append(f"monotonicity_{channel}_{low}_{high}")
    if "64" in records and "96" in records:
        p64=prolong_state(backend,records["64"]["state"],64,96); r64,p64aug=backend.unpack_state(p64,96); r96,p96aug=backend.unpack_state(records["96"]["state"],96); profile_distance=max(float(backend.np.max(backend.np.abs(a-b))) for ra,rb in zip(r64,r96) for a,b in zip(ra,rb)); augmented_distance=float(backend.np.max(backend.np.abs(p64aug-p96aug)))
        if profile_distance>thresholds["fine_mesh_profile_difference_max"]: failures.append("fine_pair_profile")
        if augmented_distance>thresholds["fine_mesh_augmented_difference_max"]: failures.append("fine_pair_augmented")
    else: profile_distance=augmented_distance=math.inf; failures.append("fine_pair_missing")
    if "96" in records:
        spectral=spectral_tail_audit(backend,records["96"]["state"],96)
        if not spectral["pass"]: failures.append("spectral_tail")
        history=records["96"].get("history",[]); last=history[-1] if history else {}; smin=float(last.get("sigma_min",0.0)); smax=float(last.get("sigma_max",math.inf)); condition=math.inf if smin<=0 else smax/smin
        if condition>thresholds["maximum_reported_discrete_condition_number_without_high_precision_audit"]: failures.append("high_precision_audit_required")
    else: spectral={"pass":False,"records":[]}; condition=math.inf
    return {"pass":len(failures)==0,"failures":failures,"fine_pair_profile_distance":profile_distance,"fine_pair_augmented_distance":augmented_distance,"spectral_tail":spectral,"N96_discrete_condition_estimate":condition}

def serialize_candidate(backend: Any, track: dict[str,Any], model: Any, sector: Any) -> dict[str,Any]:
    state=track["levels"]["96"]["state"]; metrics,info=evaluate_state(backend,state,96,model,sector); regions,params=backend.unpack_state(state,96); north,south=info["north"],info["south"]; ell_sigma=0.5*(north.ell[-1]+south.ell[-1]); field_names=("u_A","u_ell","u_varphi","u_g")
    mesh_records={}
    for level,rec in track["levels"].items(): mesh_records[level]={"converged":rec.get("converged",False),"failure":rec.get("failure"),"metrics":rec.get("metrics"),"history":rec.get("history",[])}
    return {"seed_origins":track["seed_origins"],"continuous_unknown_vector":[float(v) for v in params],"boundary_residual_vector":metrics["boundary_residual_vector"],"rr_constraint_trace":{"N":[float(v) for v in north.constraint],"S":[float(v) for v in south.constraint]},"interface_traces_provisional_not_WP4_frozen":{"A_N_x_cap":float(north.A_x[-1]),"A_S_x_cap":float(south.A_x[-1]),"ell_N_x_over_ellSigma_cap":float(north.ell_x[-1]/ell_sigma),"ell_S_x_over_ellSigma_cap":float(south.ell_x[-1]/ell_sigma),"A_hat_Sigma":float(north.A_x[-1]+south.A_x[-1]),"L_hat_Sigma":float((north.ell_x[-1]+south.ell_x[-1])/ell_sigma)},"regularized_profiles_N96":{"N":{name:[float(v) for v in field] for name,field in zip(field_names,regions[0])},"S":{name:[float(v) for v in field] for name,field in zip(field_names,regions[1])}},"tau_N96":tau_nodes(96),"mesh_records":mesh_records,"metrics_N96":metrics}

def execute_primary_target(repo_root: Path, payload: dict[str,Any], policy: dict[str,Any]) -> dict[str,Any]:
    require(hasattr(signal,"SIGALRM") and hasattr(signal,"setitimer"),"POSIX timer required"); backend=_load_primary_backend(repo_root); model=backend.model_from_payload(payload,control_a_F=False); sector=backend.sector_from_payload(payload); require(float(model.a_F)==0.25,"backend target a_F drift"); method=payload["nonlinear_method"]; per_call=float(policy["resource_limits"]["maximum_wall_clock_seconds_per_seed_per_level"]); total=float(policy["resource_limits"]["maximum_wall_clock_seconds_total"]); started=time.monotonic(); seeds=backend.seven_seeds(24); require(len(seeds)==7,"seed count drift"); tracks=[]; seed_logs=[]
    for seed_index,seed in enumerate(seeds):
        if time.monotonic()-started>=total: raise SolveTimeout("total WP2 wall-clock limit exceeded")
        try: result=run_newton(backend,seed,24,model,sector,method,min(per_call,total-(time.monotonic()-started)))
        except SolveTimeout: seed_logs.append({"seed_index":seed_index,"node_count":24,"status":"TIMED_OUT"}); continue
        rec={"seed_index":seed_index,"node_count":24,"converged":bool(result.get("converged")),"failure":result.get("failure"),"history":result.get("history",[])}
        if result.get("converged"):
            state=result["state"]; metrics,_=evaluate_state(backend,state,24,model,sector); rec["metrics"]=metrics
            if metrics["finite"] and metrics["admissible"] and metrics["positive_winding_gate"]: tracks.append({"seed_origins":[seed_index],"state":state,"levels":{"24":{"state":state,"converged":True,"metrics":metrics,"history":result.get("history",[])}}})
        seed_logs.append(rec)
    tracks=deduplicate_tracks(backend,tracks,float(payload["candidate_tracking"]["distinctness_threshold"]))
    for new_count in (32,48,64,96):
        next_tracks=[]
        for track in tracks:
            if time.monotonic()-started>=total: raise SolveTimeout("total WP2 wall-clock limit exceeded")
            old=max(int(k) for k in track["levels"]); initial=prolong_state(backend,track["state"],old,new_count)
            try: result=run_newton(backend,initial,new_count,model,sector,method,min(per_call,total-(time.monotonic()-started)))
            except SolveTimeout: track["levels"][str(new_count)]={"converged":False,"failure":"TIMED_OUT","history":[]}; continue
            if not result.get("converged"): track["levels"][str(new_count)]={"converged":False,"failure":result.get("failure"),"history":result.get("history",[])}; continue
            state=result["state"]; metrics,_=evaluate_state(backend,state,new_count,model,sector); track["levels"][str(new_count)]={"state":state,"converged":True,"metrics":metrics,"history":result.get("history",[])}
            if metrics["finite"] and metrics["admissible"] and metrics["positive_winding_gate"]: track["state"]=state; next_tracks.append(track)
        tracks=deduplicate_tracks(backend,next_tracks,float(payload["candidate_tracking"]["distinctness_threshold"]))
        if not tracks: break
    evaluated=[{"track":track,"qa":candidate_final_qa(backend,track,payload)} for track in tracks]; passing=[item for item in evaluated if item["qa"]["pass"]]
    classification="NO_PRIMARY_CANDIDATE_FOUND_UNDER_PREREGISTERED_PROTOCOL" if not passing else ("PRIMARY_NUMERICAL_CANDIDATE_PENDING_WP3_INDEPENDENT_CROSSCHECK" if len(passing)==1 else "MULTIPLE_PRIMARY_NUMERICAL_CANDIDATES_PENDING_WP3")
    candidates=[]
    for item in passing: c=serialize_candidate(backend,item["track"],model,sector); c["primary_qa"]=item["qa"]; candidates.append(c)
    return {"classification":classification,"primary_candidate_count":len(candidates),"candidates":candidates,"rejected_tracks":[{"seed_origins":item["track"]["seed_origins"],"primary_qa":item["qa"]} for item in evaluated if not item["qa"]["pass"]],"initial_seed_logs":seed_logs,"independent_backend_executed":False,"WP3_started":False,"WP4_started":False}

def review(repo_root: Path, manifest_output: Path|None=None) -> dict[str,Any]:
    payload,policy,manifest,bindings=preflight(repo_root); validate_synthetic_prolongation()
    if manifest_output is not None: manifest_output.parent.mkdir(parents=True,exist_ok=True); manifest_output.write_bytes(canonical_bytes(manifest)+b"\n")
    return {"status":"PASS_CP01R4_RELEASE_PREFLIGHT_IMPLEMENTATION_ONLY","run_id":RUN_ID,"target_contract_digest_sha256":TARGET_DIGEST,"run_payload_sha256":RUN_PAYLOAD_SHA256,"release_package_manifest_sha256":manifest["package_digest_sha256"],"method_freeze_complete":True,"barycentric_prolongation_synthetic_QA":"PASS","primary_source_hashes_verified":True,"backend_imported":False,"solver_executed":False,"physical_execution_authorized":False,"operative_grant_created":False,"operative_authorization_decision_created":False,"WP2_closed":False,"WP3_started":False,"WP4_started":False,"physical_background":"NOT_ESTABLISHED","K1-D":"NOT_RELEASED","K1-E":"NOT_ADMISSIBLE","physical_evidence_effect":"NONE","bindings":bindings}

def make_synthetic_control_decision(manifest,bindings,commit):
    return {"schema":"universelab.hzt-m0-s6-c-phys-m1.ulsh01-wp2-authorization-decision.v0.1","status":"AUTHORIZED_SINGLE_USE_WP2_CP01R4_PRIMARY_TARGET_EXECUTION","decision":{"authorization_decision_id":"SYNTHETIC-CONTROL-DECISION-CP01R4","decision_status":"AUTHORIZED_SINGLE_USE_WP2_CP01R4_PRIMARY_TARGET_EXECUTION","authorized_run_id":RUN_ID,"authorized_scope":"PRIMARY_TARGET_EXECUTION_ONLY","repository_commit_sha":commit,"target_contract_digest_sha256":TARGET_DIGEST,"run_payload_sha256":RUN_PAYLOAD_SHA256,"release_package_manifest_sha256":manifest["package_digest_sha256"],"resource_policy_sha256":bindings["resource_policy_sha256"],"backend_rebind_contract_sha256":bindings["backend_rebind_contract_sha256"],"result_schema_sha256":bindings["result_schema_sha256"],"backend_interface_contract_sha256":bindings["backend_interface_contract_sha256"],"not_before_utc":"2026-08-27T00:00:00Z","expires_at_utc":"2026-08-28T00:00:00Z","single_use_grant_required":True,"automatic_execution":False,"wp3_authorized":False,"wp4_authorized":False,"physical_response_rank_authorized":False,"K1_D_release_authorized":False,"K1_E_admissible":False}}

def make_synthetic_control_grant(manifest,bindings,commit,decision_id,decision_sha):
    return {"grant_id":"SYNTHETIC-CONTROL-GRANT-CP01R4","authorization_decision_id":decision_id,"authorization_decision_sha256":decision_sha,"nonce":"synthetic-control-nonce-cp01r4","not_before_utc":"2026-08-27T00:00:00Z","expires_at_utc":"2026-08-28T00:00:00Z","single_use":True,"scope":"SYNTHETIC_CONTROL_ONLY_NO_BACKEND_IMPORT","control_only":True,"authorized":False,"repository_commit_sha":commit,"target_contract_digest_sha256":TARGET_DIGEST,"run_payload_sha256":RUN_PAYLOAD_SHA256,"release_package_manifest_sha256":manifest["package_digest_sha256"],"backend_rebind_contract_sha256":bindings["backend_rebind_contract_sha256"],"resource_policy_sha256":bindings["resource_policy_sha256"],"result_schema_sha256":bindings["result_schema_sha256"],"backend_interface_contract_sha256":bindings["backend_interface_contract_sha256"],"target_contract_file_sha256":bindings["target_contract_file_sha256"],"dependency_lock_sha256":DEPENDENCY_LOCK_SHA256,"primary_source_sha256":PRIMARY_SHA256,"primary_base_source_sha256":PRIMARY_BASE_SHA256,"target_a_F":"1/4","control_override_allowed":False,"automatic_authorization":False}

def synthetic_authorization_replay_qa(repo_root: Path, reservation_dir: Path) -> dict[str,Any]:
    _,_,manifest,bindings=preflight(repo_root); commit="a"*40; now=datetime(2026,8,27,12,0,tzinfo=timezone.utc); decision=make_synthetic_control_decision(manifest,bindings,commit); decision_id=verify_decision(decision,manifest,bindings,commit,now); decision_sha=canonical_sha256(decision); grant=make_synthetic_control_grant(manifest,bindings,commit,decision_id,decision_sha); verified=verify_grant(grant,decision_id,decision_sha,manifest,bindings,commit,now,control_only=True); record=atomic_reserve_grant(reservation_dir,verified,control_only=True); replay=False
    try: atomic_reserve_grant(reservation_dir,verified,control_only=True)
    except ReplayError: replay=True
    require(replay and BACKEND_IMPORT_COUNT==0 and SOLVER_CALL_COUNT==0,"synthetic replay/backend firewall failed")
    return {"status":"PASS_SYNTHETIC_DECISION_GRANT_BINDING_AND_REPLAY_QA","reservation_record":str(record),"replay_rejected":True,"backend_imported":False,"solver_executed":False,"physical_evidence_effect":"NONE"}

def execute_authorized(repo_root: Path, decision_path: Path, grant_path: Path, reservation_dir: Path, result_output: Path, commit: str, now: datetime) -> dict[str,Any]:
    payload,policy,manifest,bindings=preflight(repo_root); decision=load_json(decision_path); decision_id=verify_decision(decision,manifest,bindings,commit,now); decision_sha=file_sha256(decision_path); grant=verify_grant(load_json(grant_path),decision_id,decision_sha,manifest,bindings,commit,now,control_only=False); attestation=environment_attestation(policy); attestation_sha=canonical_sha256(attestation); reservation=atomic_reserve_grant(reservation_dir,grant,control_only=False)
    try:
        result=execute_primary_target(repo_root,payload,policy); output={"schema":"universelab.hzt-m0-s6-c-phys-m1.ulsh01-wp2-cp01r4-primary-result.v0.1","run_id":RUN_ID,"repository_commit_sha":commit,"target_contract_digest_sha256":TARGET_DIGEST,"run_payload_sha256":RUN_PAYLOAD_SHA256,"release_package_manifest_sha256":manifest["package_digest_sha256"],"authorization_decision_id":decision_id,"authorization_decision_sha256":decision_sha,"grant_id":grant["grant_id"],"environment_attestation":attestation,"environment_attestation_sha256":attestation_sha,"primary_execution":result,"solver_call_count":SOLVER_CALL_COUNT,"backend_import_count":BACKEND_IMPORT_COUNT,"physical_background":"NOT_ESTABLISHED_UNTIL_RESULT_INTERPRETATION_AND_WP3_CROSSCHECK","WP3_authorized":False,"WP4_authorized":False,"physical_response_rank":"NOT_EXECUTED","K1-D":"NOT_RELEASED","K1-E":"NOT_ADMISSIBLE","physical_evidence_effect":"PRIMARY_NUMERICAL_DIAGNOSTIC_ONLY_IF_AUTHORIZED_RUN_OCCURRED","forbidden_inferences":["A primary numerical candidate is not a continuum existence or uniqueness proof.","WP2 does not establish Fredholmness, stability, ghost freedom or physical viability.","WP2 does not authorize WP3, WP4, the 41-job response evaluation, K1-D or K1-E.","Provisional one-sided cap traces are not WP4-frozen interface data."]}; encoded=canonical_bytes(output)+b"\n"; require(len(encoded)<=int(policy["resource_limits"]["maximum_result_bytes"]),"result exceeds frozen size limit"); result_output.parent.mkdir(parents=True,exist_ok=True); tmp=result_output.with_suffix(result_output.suffix+".tmp"); tmp.write_bytes(encoded); os.chmod(tmp,0o600); os.replace(tmp,result_output); update_reservation(reservation,"SUCCEEDED",backend_imported=True,solver_executed=SOLVER_CALL_COUNT>0); return output
    except SolveTimeout: update_reservation(reservation,"TIMED_OUT",backend_imported=BACKEND_IMPORT_COUNT>0,solver_executed=SOLVER_CALL_COUNT>0); raise
    except BaseException:
        try: update_reservation(reservation,"FAILED",backend_imported=BACKEND_IMPORT_COUNT>0,solver_executed=SOLVER_CALL_COUNT>0)
        finally: raise

def parse_args(argv: Iterable[str]|None=None) -> argparse.Namespace:
    p=argparse.ArgumentParser(description=__doc__); p.add_argument("command",choices=("audit","self-test","run")); p.add_argument("--repo-root",default="."); p.add_argument("--manifest-output"); p.add_argument("--reservation-dir"); p.add_argument("--decision"); p.add_argument("--grant"); p.add_argument("--result-output"); p.add_argument("--repository-commit-sha"); p.add_argument("--json",action="store_true"); return p.parse_args(argv)
def emit(value: dict[str,Any], as_json: bool) -> None: print(json.dumps(value,indent=2,sort_keys=True) if as_json else value["status"])
def main(argv: Iterable[str]|None=None) -> int:
    args=parse_args(argv); root=Path(args.repo_root).resolve()
    try:
        if args.command=="audit": emit(review(root,Path(args.manifest_output) if args.manifest_output else None),args.json); return 0
        if args.command=="self-test": require(args.reservation_dir is not None,"--reservation-dir required for self-test"); validate_synthetic_prolongation(); emit(synthetic_authorization_replay_qa(root,Path(args.reservation_dir)),args.json); return 0
        required={"--decision":args.decision,"--grant":args.grant,"--reservation-dir":args.reservation_dir,"--result-output":args.result_output,"--repository-commit-sha":args.repository_commit_sha}; missing=[k for k,v in required.items() if not v]
        if missing: raise AuthorizationError("operative execution denied; missing "+", ".join(missing))
        result=execute_authorized(root,Path(args.decision),Path(args.grant),Path(args.reservation_dir),Path(args.result_output),str(args.repository_commit_sha),datetime.now(timezone.utc)); print(json.dumps(result,indent=2,sort_keys=True) if args.json else result["primary_execution"]["classification"]); return 0
    except AuthorizationError as exc: emit({"status":"NOT_AUTHORIZED","error":str(exc),"backend_import_count":BACKEND_IMPORT_COUNT,"solver_call_count":SOLVER_CALL_COUNT,"physical_evidence_effect":"NONE"},args.json); return EXIT_NOT_AUTHORIZED
    except ReleaseError as exc: emit({"status":"FAIL_CLOSED_RELEASE_ERROR","error":str(exc),"backend_import_count":BACKEND_IMPORT_COUNT,"solver_call_count":SOLVER_CALL_COUNT,"physical_evidence_effect":"NONE" if SOLVER_CALL_COUNT==0 else "EXECUTION_ATTEMPT_DIAGNOSTIC_ONLY"},args.json); return EXIT_PREFLIGHT_FAILURE
    return EXIT_EXECUTION_FAILURE
if __name__=="__main__": raise SystemExit(main())
