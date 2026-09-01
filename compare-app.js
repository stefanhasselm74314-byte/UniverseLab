(()=>{
  'use strict';

  const CANONICAL_URL='./compare-safe.html?v=safe2';
  const api=Object.freeze({
    version:'1.0.0-retired',
    status:'RETIRED_DUPLICATE_ENGINE',
    canonicalUrl:CANONICAL_URL,
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
