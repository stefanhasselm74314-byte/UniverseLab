# HZT-M0 Lensing — A1 / MACS J0308.9+2645 False-Anomaly Control v1.0

Date: 2026-08-12  
Case: `HZT-M0-LENS-DS-A1-MACSJ0308-20260812-A`  
Bucket: `Lensing / Data-Systematics / False-Anomaly-Control`

## Canonical classification

A1 is **not** registered as an early-Universe anomaly and is **not** evidence for HZT-M0. It is registered as a methodological control case showing how a catalogue-photometry mismatch for an extended source can create a spurious high-redshift interpretation.

Status:

- high-redshift `z_phot ~ 4.4` interpretation: **falsified as a photometric systematic within the current analysis**;
- corrected redshift: **conditional photometric estimate**, adopted `z ~ 1.4`, plausible range `1.2–1.7`, pending spectroscopy;
- gravitational-arc nature: **strong candidate, not definitive**;
- direct HZT evidence: **NONE**;
- physical evidence effect: **NONE**.

## Source hierarchy

Primary scientific source: current arXiv manuscript `2607.12129`, *Discovery of a gravitational arc candidate at z_phot approximately 1.4 in MACS J0308.9+2645 from a catalogue-based search of JWST imaging*.

Secondary contextual source: Universe Today, *Astronomers Find a New Object from the Early Universe Using Webb Data*, 2026-08-07.

The primary manuscript governs the scientific state. The media headline does not determine anomaly status.

## Reproducible false-anomaly sequence

The initial catalogue fit used `aper_total` photometry although A1 is an extended source. In F200W the catalogue gives `aper_total_abmag = 24.53` versus `isophotal_abmag = 20.87`, so the small-aperture measurement captures only about 3% of the isophotal light. The captured fraction also changes with wavelength, producing an artificial red continuum. A photometric-redshift fit to those biased colours yields the apparently high-redshift solution near `z ~ 4.4`.

Four morphology-aware extended-source photometry methods agree on a much lower solution. The six-band EAZY fit gives `z = 1.53` with 16–84% interval `[1.22, 1.74]` and `P(z>3)=0.0001`; adding HST photometry leads to an adopted `z ~ 1.4`, plausible range `1.2–1.7`.

The HST/ACS F435W detection independently rejects the `z ~ 4.4` Lyman-dropout interpretation. At the adopted lower redshift, the public lens model predicts a single image and no counterimage, consistent with observation. Spectroscopy and a dedicated JWST-era lens model remain required for definitive physical identification.

## UniverseLab gate

The control rule is:

`CATALOGUE RESULT != PHYSICAL IDENTIFICATION`

Before any catalogue-selected high-redshift source can be promoted to a cosmological anomaly, UniverseLab requires morphology-aware photometry, wavelength-consistent aperture treatment, independent band/instrument checks, dropout consistency, lens-model counterimage checks when applicable, and spectroscopic confirmation for evidential promotion.

## HZT relevance

A1 can become a **conditional future lensing test object** only after an explicit lensing forward model is preregistered. A future analysis could connect lensing observables to combinations of `Phi + Psi`, `Sigma`, or `eta`, but no such inference is licensed by this control record.

This case therefore changes no solver, parameter, topology, likelihood, release gate, K1 state, or physical-evidence state.

## Governance firewall

- `WP4 = BLOCKED`
- `K1-D = NOT_RELEASED`
- `K1-E = NOT_ADMISSIBLE`
- `physical_evidence_effect = NONE`

Forbidden: treating the original catalogue redshift as a robust early-Universe detection; treating corrected photometry as spectroscopy; treating candidate lens morphology as definitive lens identification; treating A1 as HZT or modified-gravity evidence; advancing any HPVS/HZT release gate from this case alone.
