/* UniverseLab Site Print & Export Bootstrap v1.0.9
 * Loads the floating page utility, document/source link router and site language switcher.
 * Navigation recovery: the former root-scope HTML-injection service worker is no longer
 * registered because intercepting every navigation can stall links in some Opera runtimes.
 * Existing registrations of that worker are removed fail-safe. Presentation layer only;
 * no scientific, solver, governance or evidence effect.
 */
(function(){
  'use strict';
  const qs=new URLSearchParams(location.search);
  if(qs.get('include-iframe')==='1')return;
  const ROOT='/UniverseLab/';
  const TOOL=ROOT+'assets/2026-08-19_UniverseLab_SitePrintExport_v1.0.js?v=1.0.6';
  const DOCUMENT_ROUTER=ROOT+'assets/2026-08-27_UniverseLab_DocumentLinkRouter_v1.0.js?v=1.1.0';
  const LANGUAGE=ROOT+'assets/2026-08-18_UniverseLab_SiteLanguageSwitcher_v1.1.js?v=1.1.1';
  const RETIRED_SW_MARKER='/2026-08-19_UniverseLab_SitePrintExportServiceWorker_v1.0.js';

  if(!document.querySelector('script[data-ul-language-switcher-loader]')&&!document.querySelector('script[src*="UniverseLab_SiteLanguageSwitcher"]')){
    const lang=document.createElement('script');
    lang.src=LANGUAGE;
    lang.defer=true;
    lang.dataset.ulLanguageSwitcherLoader='1';
    (document.head||document.documentElement).appendChild(lang);
  }

  if(!document.querySelector('script[data-ul-document-link-router]')&&!document.querySelector('script[src*="UniverseLab_DocumentLinkRouter"]')){
    const router=document.createElement('script');
    router.src=DOCUMENT_ROUTER;
    router.defer=true;
    router.dataset.ulDocumentLinkRouter='1';
    (document.head||document.documentElement).appendChild(router);
  }

  if(!document.querySelector('script[data-ul-print-export-v10]')){
    const s=document.createElement('script');
    s.src=TOOL;
    s.defer=true;
    s.dataset.ulPrintExportV10='1';
    (document.head||document.documentElement).appendChild(s);
  }

  if('serviceWorker' in navigator&&location.protocol==='https:'&&location.pathname.startsWith(ROOT)){
    navigator.serviceWorker.getRegistrations().then(registrations=>{
      registrations.forEach(reg=>{
        const workers=[reg.installing,reg.waiting,reg.active].filter(Boolean);
        if(workers.some(worker=>(worker.scriptURL||'').includes(RETIRED_SW_MARKER))){
          reg.unregister().catch(()=>{});
        }
      });
    }).catch(err=>{
      console.warn('[UniverseLab print/export] retired service-worker cleanup failed',err);
    });
  }
})();
