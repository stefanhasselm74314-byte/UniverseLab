# UniverseLab Production Smoke Audit v1.0

Status: PRESENTATION / DEPLOYMENT QA ONLY

This contract verifies the public GitHub Pages deployment without changing formulas, numerical algorithms, solver states, physical claims, evidence classes, K1-D/K1-E states, or release gates.

## Live checks

- all 17 governed DE↔EN route pairs return HTTP 200 from the public GitHub Pages origin;
- English routes report `lang=en`;
- static canonical and hreflang metadata, when present, agree with the multilingual route registry;
- the four curated runtime mirrors (`about`, `journey`, `emergence`, `universe3d`) expose the governed adapter and curated-source metadata;
- the live site-language-switcher asset is reachable and contains the governed route tokens.

## Scientific firewall

The HTTP smoke audit establishes deployment identity and multilingual route consistency. It does not by itself prove numerical DE↔EN equivalence in a browser. The four runtime English mirrors are structurally constrained to execute the canonical German page, preventing a duplicated numerical implementation. Independent browser-level numerical parity remains a separate QA layer.
