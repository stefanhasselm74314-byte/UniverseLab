#!/usr/bin/env python3
import importlib.util
import json
import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "registry/2026-08-15_HZT-M0_S6_C-PHYS_H4R4B_GlobalControlWitness_ParentEquivalence_v0.1.json"
DOC = ROOT / "science/hzt-m0/md2s/2026-08-15_HZT-M0_S6_C-PHYS_H4R4B_GlobalControlWitness_ParentEquivalence_v0.1.md"
VALIDATOR = ROOT / "tools/2026-08-15_validate_hzt_m0_s6_c_phys_h4r4b_global_control_witness_v0.1.py"


def load_validator():
    spec = importlib.util.spec_from_file_location("h4r4b_validator", VALIDATOR)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def require(cond, msg):
    if not cond:
        raise AssertionError(msg)


def main():
    require(REGISTRY.exists(), "registry missing")
    require(DOC.exists(), "science document missing")
    require(VALIDATOR.exists(), "validator missing")

    d = json.loads(REGISTRY.read_text(encoding="utf-8"))
    mod = load_validator()
    mod.validate_registry(d)
    mod.validate_numeric_witness(d)

    text = DOC.read_text(encoding="utf-8")
    required_phrases = [
        "nichtleerer global zulässiger M1-Untersektor",
        "constraintsatisfizierender Anfangsdatensatz",
        "D2N-Q-Selektion",
        "PHYSICAL_PARENT_SOLVE_AUTHORIZED = FALSE",
        "K1-D = NOT_RELEASED",
        "K1-E = NOT_ADMISSIBLE",
        "WP4 = BLOCKED",
        "PHYSICAL_EVIDENCE = NONE",
        "EXTERNAL_UNVERIFIED_GEMINI_DRAFT",
    ]
    for phrase in required_phrases:
        require(phrase in text, f"missing governance/document phrase: {phrase}")

    # Exact source-binding paths must exist in this repository checkout.
    for binding in d["source_bindings"]:
        require((ROOT / binding["path"]).exists(), f"missing source binding: {binding['path']}")

    # The control witness must not silently become a generic theorem or a D2N-Q result.
    forbidden = set(d["forbidden_inferences"])
    require("NO_EXPLICIT_CONTROL_WITNESS_AS_GENERIC_M1_PARAMETER_EXISTENCE_THEOREM" in forbidden, "generic-existence firewall")
    require("NO_B_SQUARED_ZERO_CONTROL_SOLUTION_AS_NONTRIVIAL_D2NQ_SELECTION" in forbidden, "D2N-Q firewall")
    require(d["gate_disposition"]["generic_M1_global_background_existence"] == "OPEN", "generic M1 must remain open")
    require(d["gate_disposition"]["full_ghost_freedom"] == "OPEN", "ghost freedom must remain open")

    print("H4R4B contract tests: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
