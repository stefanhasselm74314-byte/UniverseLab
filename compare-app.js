(()=>{
  'use strict';

  const CANONICAL_URL='./compare-safe.html?v=safe2';
  const provenance=Object.freeze({
    eq:'Δ(a)=βτ·𝓘B·exp[−(a/a_c)²]',
    status:'Modellabhängig',
    unit:'dimensionslos',
    note:'Keine freigegebene fundamentale 6D-Vorhersage.'
  });
  const api=Object.freeze({
    version:'1.0.0-retired',
    status:'RETIRED_DUPLICATE_ENGINE',
    canonicalUrl:CANONICAL_URL,
    provenance,
    physicalGateEffect:'NONE',
    physicalEvidenceEffect:'NONE',
    openCanonical(){
      const target=new URL(CANONICAL_URL,location.href);
      target.hash=location.hash;
      location.assign(target.href);
    }
  });

  globalThis.UniverseLabCompareLegacy=api;
  globalThis.dispatchEvent(new CustomEvent('universelab:compare-legacy-retired',{detail:api}));
})();
