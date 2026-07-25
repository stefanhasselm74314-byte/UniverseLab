(()=>{
  'use strict';
  if(window.__UNIVERSELAB_NAV_LABELS__)return;
  window.__UNIVERSELAB_NAV_LABELS__=true;
  const apply=()=>{
    document.querySelectorAll('a[href*="compare.html"],a[href*="compare-safe.html"],a[href*="compare-direct.html"]').forEach(link=>{
      const spans=link.querySelectorAll('span');
      const label=spans.length?spans[spans.length-1]:null;
      if(label)label.textContent='Vergleichsrechner';
      else if(/^(Modelle|Modellvergleich|Vergleichsrechner)$/i.test(link.textContent.trim()))link.textContent='Vergleichsrechner';
      link.href='./compare-direct.html?v=22';
      link.setAttribute('aria-label','UniverseLab Vergleichsrechner öffnen');
      link.title='Vergleichsrechner im Direktmodus mit Tafelwerk';
    });
  };
  const init=()=>{apply();const observer=new MutationObserver(apply);observer.observe(document.documentElement,{subtree:true,childList:true});setTimeout(()=>observer.disconnect(),8000);};
  if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',init,{once:true});else init();
})();