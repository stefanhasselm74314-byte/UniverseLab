/* UniverseLab Site Language Switcher v1.0 compatibility loader.
 * Superseded by v1.1. Kept so existing pages automatically receive curated
 * English routing without requiring immediate HTML rewrites.
 * Also chains the site-wide print/export bootstrap so existing pages using this
 * shared loader receive the utility without page-by-page rewrites.
 */
(function(){
  'use strict';
  const current=document.currentScript&&document.currentScript.src;
  const assetBase=current?new URL('.',current):new URL('/UniverseLab/assets/',location.origin);
  function add(src,marker){
    if(document.querySelector('script['+marker+']'))return;
    const s=document.createElement('script');s.src=new URL(src,assetBase).href;s.defer=true;s.setAttribute(marker,'1');(document.head||document.documentElement).appendChild(s);
  }
  add('2026-08-18_UniverseLab_SiteLanguageSwitcher_v1.1.js','data-ul-lang-v11');
  add('2026-08-19_UniverseLab_SitePrintExportBootstrap_v1.0.js','data-ul-print-export-bootstrap-v10');
})();
