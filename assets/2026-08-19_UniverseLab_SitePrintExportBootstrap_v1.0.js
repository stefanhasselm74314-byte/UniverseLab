/* UniverseLab Site Print & Export Bootstrap v1.0.4
 * Loads the floating page utility and registers the root-scope HTML injector.
 * Presentation/navigation layer only; no scientific status effect.
 */
(function(){
  'use strict';
  const qs=new URLSearchParams(location.search);
  if(qs.get('include-iframe')==='1')return;
  const ROOT='/UniverseLab/';
  const TOOL=ROOT+'assets/2026-08-19_UniverseLab_SitePrintExport_v1.0.js?v=1.0.4';
  const SW=ROOT+'2026-08-19_UniverseLab_SitePrintExportServiceWorker_v1.0.js';

  if(!document.querySelector('script[data-ul-print-export-v10]')){
    const s=document.createElement('script');
    s.src=TOOL;
    s.defer=true;
    s.dataset.ulPrintExportV10='1';
    (document.head||document.documentElement).appendChild(s);
  }

  if('serviceWorker' in navigator&&location.protocol==='https:'&&location.pathname.startsWith(ROOT)){
    navigator.serviceWorker.register(SW,{scope:ROOT}).then(reg=>reg.update()).catch(err=>{
      console.warn('[UniverseLab print/export] service worker registration failed',err);
    });
  }
})();
