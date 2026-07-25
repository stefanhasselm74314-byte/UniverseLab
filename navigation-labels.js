(()=>{
  'use strict';
  if(window.__UNIVERSELAB_NAV_LABELS__)return;
  window.__UNIVERSELAB_NAV_LABELS__=true;

  const desktop=()=>matchMedia('(min-width:901px)').matches;
  const target=()=>desktop()?'./compare-desktop.html?v=2':'./compare-safe.html?v=safe1';

  const apply=()=>{
    document.querySelectorAll('a[href*="compare.html"],a[href*="compare-safe.html"],a[href*="compare-direct.html"],a[href*="compare-desktop.html"]').forEach(link=>{
      const spans=link.querySelectorAll('span');
      const label=spans.length?spans[spans.length-1]:null;
      if(label)label.textContent='Vergleichsrechner';
      else if(/^(Modelle|Modellvergleich|Vergleichsrechner)$/i.test(link.textContent.trim()))link.textContent='Vergleichsrechner';
      link.href=target();
      link.setAttribute('aria-label',desktop()?'Kompakten UniverseLab Vergleichsrechner öffnen':'Stabilen UniverseLab Vergleichsrechner öffnen');
      link.title=desktop()?'Vergleichsrechner in kompakter Desktopansicht':'Stabiler Vergleichsrechner mit interaktivem Tafelwerk';
    });
  };

  const init=()=>{
    apply();
    const observer=new MutationObserver(apply);
    observer.observe(document.documentElement,{subtree:true,childList:true});
    addEventListener('resize',apply,{passive:true});
    setTimeout(()=>observer.disconnect(),8000);
  };

  if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',init,{once:true});
  else init();
})();