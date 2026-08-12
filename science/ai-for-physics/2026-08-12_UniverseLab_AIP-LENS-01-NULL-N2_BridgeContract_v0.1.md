# UniverseLab AIP-LENS-01-NULL-N2 — Bridge Contract v0.1

Date: 2026-08-12  
Bridge: `AIP-LENS-01-NULL-N2-BRIDGE`  
Status: `BRIDGE_CONTRACT_DEFINED_EXECUTABLE_VALIDATION_ONLY_PHYSICAL_SIMULATOR_NOT_YET_VALIDATED_NO_REAL_DATA_EXECUTION`

## Purpose

This stage defines the physical and semantic bridge required between cosmological simulations and the frozen KiDS-1000 fiducial COSEBIs real-data control. It is a methods/contract stage only. No real KiDS measurements are downloaded, opened, trained on or inferred here.

The central firewall remains:

`synthetic feature similarity != physical observable equivalence`.

N1 toy features and N1 weights are therefore not reusable on KiDS data.

## Required physical forward chain

The bridge must implement or validate the following chain before any real-data authorization:

`cosmology + nuisance parameters -> P_delta(k,z) -> C_ell^{ij} -> xi_+/-^{ij}(theta) -> COSEBIs E_n^{ij}, B_n^{ij}`.

The tomographic shear power spectrum is represented by the declared Limber/extended-Limber form

`C_ell^{ij} = integral dchi [q_i(chi) q_j(chi)/chi^2] P_delta((ell+1/2)/chi,z(chi)) + declared IA terms`,

subject to exact agreement with, or explicit quantitative cross-validation against, the frozen KiDS reference implementation.

The real-space shear correlations are

`xi_+(theta) = (1/2pi) integral d ell ell C_ell J_0(ell theta)`

and

`xi_-(theta) = (1/2pi) integral d ell ell C_ell J_4(ell theta)`.

The COSEBI E modes are defined by

`E_n = (1/2) integral_[theta_min,theta_max] dtheta theta [T^+_n(theta) xi_+(theta) + T^-_n(theta) xi_-(theta)]`,

with the corresponding sign change for B modes. Filter basis, angular interval, mode ordering and tomographic ordering must be bound to the KiDS-1000 fiducial observable semantics before real-data execution.

## Authoritative reference route

The non-ML reference remains the KCAP/CosmoSIS configuration distributed with the KiDS-1000 cosmic-shear release. This bridge does not yet freeze or execute those released configuration files. Their exact file hashes, parameterization, priors and numerical settings must be captured in a later `N2-BRIDGE-IMPLEMENTATION-FREEZE` before physical validation begins.

A separate simulator or emulator may be used only if it is independently validated against the authoritative route over the complete declared parameter and nuisance domain.

## Required nuisance/systematics binding

Before physical validation, the bridge must bind source-redshift distributions and uncertainty, multiplicative shear calibration, intrinsic alignments, shape-noise/covariance treatment, baryonic feedback or an explicit scale policy, and survey/window/mask semantics. The exact parameter basis and priors must match the hashed reference configuration.

## Training and calibration firewall

Real KiDS measurements may not enter TRAIN, VALIDATION or CALIBRATION. Published posterior chains and published best-fit values may not be used as labels. Model selection and hyperparameter tuning must be completed on simulations or synthetic controls.

The required independent partitions are:

`TRAIN / VALIDATION / CALIBRATION / FINAL_SIM_TEST / OOD_STRESS`.

Coverage at 68% and 95%, a non-ML baseline, domain-shift diagnostics and an OOD abstention rule are mandatory before real-data access.

## Bridge validation gates

`B0` contract completeness may pass at this stage if CI is green. `B1` reference-config hash freeze, `B2` forward-engine implementation, `B3` reference-grid validation, `B4` COSEBIs semantic equivalence, `B5` independent calibration/coverage, `B6` domain-shift/OOD validation and `B7` independent bridge review remain pending.

Real-data execution remains blocked until B1-B7 all pass and a separate `AIP-LENS-01-NULL-N2-EXECUTION-AUTHORIZATION` is issued.

Numerical tolerances for B3-B6 must be predeclared before those tests execute. They are deliberately not invented in this contract stage.

## Current scientific classification

**Bewiesen:** only the repository contract structure can be mechanically validated by CI.

**Numerisch bestätigt:** no physical weak-lensing forward calculation is performed here.

**Konditional:** the declared forward chain is the required route for later KiDS-semantic validation.

**Offen:** physical simulator fidelity, exact KiDS reference configuration binding, COSEBIs numerical equivalence, coverage, domain shift and OOD performance.

## Governance firewall

`AIP-G2` remains `NOT PASSED`; a contract is not physical-simulator validation. `AIP-G6` remains untested because no real data are executed. No HZT comparison or HZT parameter is introduced.

`WP4 = BLOCKED`  
`K1-D = NOT_RELEASED`  
`K1-E = NOT_ADMISSIBLE`  
`physical evidence effect = NONE`

The next candidate is `AIP-LENS-01-NULL-N2-BRIDGE-IMPLEMENTATION-FREEZE`.
