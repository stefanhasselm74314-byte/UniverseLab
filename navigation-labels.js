(()=>{
  'use strict';
  if(window.__UNIVERSELAB_NAV_LABELS__)return;
  window.__UNIVERSELAB_NAV_LABELS__=true;

  const desktop=()=>matchMedia('(min-width:901px)').matches;
  const compareTarget=()=>desktop()?'./compare-desktop.html?v=3':'./compare-safe.html?v=safe1';

  const setLinkLabel=(link,text)=>{
    const spans=link.querySelectorAll('span');
    const label=spans.length?spans[spans.length-1]:null;
    if(label)label.textContent=text;
    else link.textContent=text;
  };

  const apply=()=>{
    document.querySelectorAll('a[href*="compare.html"],a[href*="compare-safe.html"],a[href*="compare-direct.html"],a[href*="compare-desktop.html"]').forEach(link=>{
      setLinkLabel(link,'Vergleichsrechner');
      link.href=compareTarget();
      link.setAttribute('aria-label',desktop()?'Kompakten UniverseLab Vergleichsrechner öffnen':'Stabilen UniverseLab Vergleichsrechner öffnen');
      link.title=desktop()?'Vergleichsrechner in kompakter Desktopansicht':'Stabiler Vergleichsrechner mit interaktivem Tafelwerk';
    });

    document.querySelectorAll('a[href*="emergence.html"],a[href*="conway.html"],a[href*="index.html?lab=1"]').forEach(link=>{
      setLinkLabel(link,'Conway · Emergenz-Labor');
      link.href='./conway.html?v=1';
      link.setAttribute('aria-label','Conways Game of Life und Emergenz-Labor öffnen');
      link.title='Conway-Zellautomat, Muster, Expansion und kosmologische Kopplung';
    });

    if(/emergence\.html$|conway\.html$/i.test(location.pathname)){
      document.title='Conway · Emergenz-Labor · UniverseLab';
      const heading=document.querySelector('h1');
      if(heading&&/^(UniverseLab|Emergenz)/i.test(heading.textContent.trim()))heading.textContent='Conway · Emergenz-Labor';
      const current=document.querySelector('.ul-current span:last-child');
      if(current)current.textContent='Conway · Emergenz-Labor';
      const help=document.querySelector('.ul-drawer-help span:last-child');
      if(help)help.textContent='Hilfe zu Conway und Emergenz';
    }
  };

  const init=()=>{
    apply();
    const observer=new MutationObserver(apply);
    observer.observe(document.documentElement,{subtree:true,childList:true});
    addEventListener('resize',apply,{passive:true});
    setTimeout(()=>observer.disconnect(),10000);
  };

  if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',init,{once:true});
  else init();
})();