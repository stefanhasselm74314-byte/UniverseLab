(()=>{
  'use strict';

  if(window.__UNIVERSELAB_COMPARE_MOBILE__)return;
  window.__UNIVERSELAB_COMPARE_MOBILE__=true;

  const init=()=>{
    if(!/compare\.html$/i.test(location.pathname))return;
    const controls=document.querySelector('.controls');
    const tabs=document.querySelector('.tabs');
    if(!controls||!tabs)return;

    const style=document.createElement('style');
    style.id='ul-compare-mobile-style';
    style.textContent=`
      .ul-compare-control-head{display:flex;align-items:center;justify-content:space-between;gap:9px;margin-bottom:8px}
      .ul-compare-control-head h2{margin:0}
      .ul-compare-collapse{display:none;width:auto;min-height:36px;padding:7px 10px;white-space:nowrap}
      .ul-compare-summary{display:none;grid-template-columns:repeat(3,minmax(0,1fr));gap:6px;margin:8px 0}
      .ul-compare-summary span{padding:7px 8px;border:1px solid #2d3959;border-radius:9px;background:#080e1c;color:#aeb8d2;font-size:9px;line-height:1.3}
      .ul-compare-summary b{display:block;color:#f4f6ff;font-size:11px;font-variant-numeric:tabular-nums;overflow-wrap:anywhere}
      .ul-density-warning{display:none;margin:7px 0;padding:8px 9px;border:1px solid #70532c;border-radius:10px;background:#291e10;color:#ffe1a7;font-size:10px;line-height:1.4}
      .ul-density-warning.show{display:block}
      @media(max-width:1100px){
        .ul-compare-collapse{display:block}
        .ul-compare-summary{display:grid}
        .controls.ul-collapsed>.group,.controls.ul-collapsed>.button-row,.controls.ul-collapsed>.warning{display:none!important}
        .controls.ul-collapsed{padding-bottom:10px}
      }
      @media(max-width:700px){
        .comparison-table{min-width:0!important;background:transparent}
        .comparison-table thead{display:none}
        .comparison-table,.comparison-table tbody,.comparison-table tr,.comparison-table td{display:block;width:100%}
        .comparison-table tbody{padding:7px}
        .comparison-table tr{margin:0 0 8px;border:1px solid #2b3757;border-radius:12px;background:#080e1b;overflow:hidden}
        .comparison-table tr:last-child{margin-bottom:0}
        .comparison-table td{display:grid;grid-template-columns:minmax(92px,34%) minmax(0,1fr);gap:9px;text-align:left!important;padding:8px 10px;border-bottom:1px solid #24304b;overflow-wrap:anywhere}
        .comparison-table td:last-child{border-bottom:0}
        .comparison-table td::before{color:#8fa3c7;font-size:9px;font-weight:800;letter-spacing:.03em;text-transform:uppercase}
        .comparison-table td:nth-child(1)::before{content:'Bereich'}
        .comparison-table td:nth-child(2)::before{content:'ΛCDM / GR'}
        .comparison-table td:nth-child(3)::before{content:'Erweiterung'}
        .comparison-table td:nth-child(4)::before{content:'UniverseLab-Status'}
        .comparison-table.closest-mobile-table{}
        #view-compare .table-wrap{overflow:visible;max-height:none;border:0;background:transparent}
      }
      @media(max-width:430px){
        .ul-compare-summary{grid-template-columns:repeat(2,minmax(0,1fr))}
        .ul-compare-control-head{align-items:flex-start}
        .ul-compare-collapse{font-size:10px}
      }
    `;
    document.head.appendChild(style);

    const originalTitle=controls.querySelector(':scope > h2');
    const head=document.createElement('div');
    head.className='ul-compare-control-head';
    const title=document.createElement('h2');
    title.textContent=originalTitle?.textContent||'Globale Parameter';
    const toggle=document.createElement('button');
    toggle.type='button';
    toggle.className='ul-compare-collapse';
    toggle.setAttribute('aria-controls','ul-compare-parameter-content');
    head.append(title,toggle);
    originalTitle?.remove();
    controls.prepend(head);

    const summary=document.createElement('div');
    summary.className='ul-compare-summary';
    summary.setAttribute('aria-label','Aktuelle Parameterzusammenfassung');
    head.after(summary);

    const warning=document.createElement('div');
    warning.className='ul-density-warning';
    summary.after(warning);

    [...controls.children].forEach((child,index)=>{
      if(index>2)child.dataset.ulParameterContent='true';
    });
    controls.id=controls.id||'ul-compare-parameter-content';

    const number=id=>Number(document.getElementById(id)?.value);
    const de=(value,digits=3)=>Number.isFinite(value)
      ?value.toLocaleString('de-DE',{minimumFractionDigits:digits,maximumFractionDigits:digits})
      :'–';

    const updateSummary=()=>{
      const H0=number('H0'),Om=number('Om'),Ol=number('Ol'),w=number('w');
      const beta=number('beta'),ib=number('ib');
      const Or=9.2e-5;
      const Ok=1-Or-Om-Ol;
      const A=beta*ib;
      summary.innerHTML=`
        <span>H₀<b>${de(H0,1)}</b></span>
        <span>Ωₘ,0<b>${de(Om)}</b></span>
        <span>ΩDE,0<b>${de(Ol)}</b></span>
        <span>Ωₖ,0<b>${de(Ok)}</b></span>
        <span>w<b>${de(w)}</b></span>
        <span>βτ·𝓘B<b>${de(A,4)}</b></span>
      `;
      const nonFlat=Math.abs(Ok)>0.02;
      warning.classList.toggle('show',nonFlat);
      warning.innerHTML=nonFlat
        ?`<b>Hinweis:</b> Dieses Modell besitzt Ωₖ,0=${de(Ok)}. Das ist ein gekrümmter beziehungsweise nicht dichteabgeschlossener Vergleichsfall. „Referenzwerte“ lädt die nahezu flache ΛCDM-Konfiguration.`
        :'';
    };

    let collapsed=false;
    try{collapsed=localStorage.getItem('universelab:compare:parameters-collapsed')==='1';}catch{}
    const setCollapsed=value=>{
      collapsed=Boolean(value);
      controls.classList.toggle('ul-collapsed',collapsed);
      toggle.textContent=collapsed?'Parameter anzeigen':'Parameter einklappen';
      toggle.setAttribute('aria-expanded',String(!collapsed));
      try{localStorage.setItem('universelab:compare:parameters-collapsed',collapsed?'1':'0');}catch{}
    };
    toggle.addEventListener('click',()=>setCollapsed(!collapsed));
    setCollapsed(collapsed);

    controls.addEventListener('input',updateSummary);
    addEventListener('universelab:modelchange',()=>setTimeout(updateSummary,0));
    updateSummary();

    tabs.addEventListener('click',event=>{
      const button=event.target.closest('button[data-view]');
      if(!button||innerWidth>1100)return;
      setCollapsed(true);
      requestAnimationFrame(()=>tabs.scrollIntoView({block:'start',behavior:'smooth'}));
    });

    const comparison=document.querySelector('.comparison-table');
    if(comparison)comparison.classList.add('closest-mobile-table');
  };

  if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',init,{once:true});
  else init();
})();
