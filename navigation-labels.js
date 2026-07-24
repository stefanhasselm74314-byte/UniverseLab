(()=>{
  'use strict';

  if(window.__UNIVERSELAB_NAV_LABELS__)return;
  window.__UNIVERSELAB_NAV_LABELS__=true;

  const apply=()=>{
    document.querySelectorAll('a[href*="compare.html"]').forEach(link=>{
      const spans=link.querySelectorAll('span');
      const label=spans.length?spans[spans.length-1]:null;
      if(label&&/^(Modelle|Modellvergleich)$/i.test(label.textContent.trim())){
        label.textContent='Vergleichsrechner';
      }else if(!spans.length&&/^(Modelle|Modellvergleich)$/i.test(link.textContent.trim())){
        link.textContent='Vergleichsrechner';
      }
      link.setAttribute('aria-label','UniverseLab Vergleichsrechner öffnen');
      link.title='Vergleichsrechner mit interaktivem Tafelwerk';
    });

    if(/compare\.html$/i.test(location.pathname)){
      const current=document.querySelector('.ul-current span:last-child');
      if(current)current.textContent='Vergleichsrechner';

      const help=document.querySelector('.ul-drawer-help span:last-child');
      if(help)help.textContent='Hilfe zum Vergleichsrechner';
    }
  };

  const init=()=>{
    apply();
    const observer=new MutationObserver(apply);
    observer.observe(document.documentElement,{subtree:true,childList:true});
    setTimeout(()=>observer.disconnect(),8000);
  };

  if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',init,{once:true});
  else init();
})();