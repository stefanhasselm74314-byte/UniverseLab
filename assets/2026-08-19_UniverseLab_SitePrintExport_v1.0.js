/* UniverseLab Site Print & Export v1.0.3
 * Presentation/navigation utility only. No scientific, solver or governance status effect.
 * Provides current-page print/PDF, HTML snapshot, direct-link copy and access to the
 * existing Owner Print Export hub. Hidden in include-iframe export views and on print.
 * v1.0.2: suppresses the global control when a page already provides a native export UI.
 * v1.0.3: upgrades legacy human-facing 50-Quellen-Katalog JSON links to the HTML catalog.
 */
(function(){
  'use strict';
  const qs=new URLSearchParams(location.search);
  if(qs.get('include-iframe')==='1')return;
  if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',init,{once:true});
  else init();

  function init(){
    upgradeLegacyBibliographyLinks();
    if(document.querySelector('[data-ul-print-export-host]'))return;
    if(hasNativeExport()){
      document.documentElement.dataset.ulGlobalExport='suppressed-native-export';
      return;
    }

    const ROOT='/UniverseLab/';
    const OWNER_EXPORT=ROOT+'2026-08-11_UniverseLab_OwnerPrintExport_v1.0.html?owner=1';
    const host=document.createElement('div');
    host.dataset.ulPrintExportHost='1';
    host.setAttribute('aria-label','UniverseLab Druck und Export');
    host.style.cssText='position:fixed;left:10px;bottom:10px;z-index:2147483000;display:block';
    const shadow=host.attachShadow({mode:'open'});
    shadow.innerHTML=`
      <style>
        :host{all:initial;font-family:system-ui,-apple-system,"Segoe UI",sans-serif;color-scheme:dark}
        *,*::before,*::after{box-sizing:border-box}
        .wrap{position:relative;display:flex;align-items:flex-end;gap:8px}
        .trigger{min-height:42px;padding:9px 12px;border:1px solid #48557b;border-radius:13px;background:#0a1020f2;color:#f7f8ff;box-shadow:0 8px 28px #0009;backdrop-filter:blur(14px);font:800 12px/1.15 system-ui,-apple-system,"Segoe UI",sans-serif;cursor:pointer}
        .trigger:hover,.trigger:focus-visible{outline:none;border-color:#8d7cff;background:#151d36}
        .panel{position:absolute;left:0;bottom:50px;width:min(290px,calc(100vw - 20px));padding:8px;border:1px solid #394668;border-radius:15px;background:#080d1bf7;box-shadow:0 18px 55px #000c;backdrop-filter:blur(18px)}
        .panel[hidden]{display:none}
        .title{padding:5px 7px 8px;color:#aab5d5;font:800 10px/1.2 system-ui,-apple-system,"Segoe UI",sans-serif;letter-spacing:.08em;text-transform:uppercase}
        button.action,a.action{display:flex;width:100%;min-height:42px;align-items:center;gap:9px;padding:9px 10px;border:0;border-radius:10px;background:transparent;color:#f6f7ff;text-decoration:none;text-align:left;font:750 12px/1.3 system-ui,-apple-system,"Segoe UI",sans-serif;cursor:pointer}
        button.action:hover,button.action:focus-visible,a.action:hover,a.action:focus-visible{outline:none;background:#18213a}
        .icon{display:grid;place-items:center;width:26px;height:26px;flex:0 0 26px;border:1px solid #3c496a;border-radius:8px;background:#0d1428;font-size:14px}
        .sub{display:block;margin-top:2px;color:#9ea9c8;font-size:10px;font-weight:600}
        .sep{height:1px;margin:5px 4px;background:#27334f}
        .toast{position:absolute;left:0;bottom:50px;max-width:280px;padding:8px 10px;border:1px solid #326b58;border-radius:10px;background:#0d2a22f5;color:#c9f7e6;font:750 11px/1.3 system-ui,-apple-system,"Segoe UI",sans-serif;box-shadow:0 10px 32px #0009}
        .toast[hidden]{display:none}
        @media(max-width:520px){.trigger{min-height:40px;padding:8px 10px}.panel{bottom:47px}.label{display:none}}
        @media print{:host{display:none!important}}
      </style>
      <div class="wrap">
        <button class="trigger" type="button" aria-haspopup="menu" aria-expanded="false" title="Drucken und exportieren">🖨️ <span class="label">Druck / Export</span></button>
        <div class="panel" role="menu" hidden>
          <div class="title">Diese Seite</div>
          <button class="action" type="button" data-action="print" role="menuitem"><span class="icon">🖨️</span><span>Drucken / als PDF speichern<span class="sub">Öffnet den Browser-Druckdialog</span></span></button>
          <button class="action" type="button" data-action="html" role="menuitem"><span class="icon">⬇️</span><span>HTML-Snapshot speichern<span class="sub">Aktueller DOM-Stand mit Live-Asset-Basis</span></span></button>
          <button class="action" type="button" data-action="copy" role="menuitem"><span class="icon">🔗</span><span>Direktlink kopieren<span class="sub">Aktuelle URL inklusive Parameter</span></span></button>
          <div class="sep"></div>
          <a class="action" data-action="all" role="menuitem"><span class="icon">📚</span><span>Gesamtexport öffnen<span class="sub">Mehrere UniverseLab-Seiten wählen, A4/PDF/HTML</span></span></a>
        </div>
        <div class="toast" role="status" aria-live="polite" hidden></div>
      </div>`;

    const trigger=shadow.querySelector('.trigger');
    const panel=shadow.querySelector('.panel');
    const toast=shadow.querySelector('.toast');
    const all=shadow.querySelector('[data-action="all"]');
    all.href=new URL(OWNER_EXPORT,location.origin).href;

    function setOpen(open){panel.hidden=!open;trigger.setAttribute('aria-expanded',String(open));}
    function notify(text){toast.textContent=text;toast.hidden=false;clearTimeout(notify.t);notify.t=setTimeout(()=>{toast.hidden=true},1900)}
    function filename(){
      const raw=(document.title||location.pathname.split('/').pop()||'UniverseLab').replace(/[<>:"/\\|?*\u0000-\u001f]/g,' ').replace(/\s+/g,' ').trim();
      return (raw||'UniverseLab')+'.html';
    }
    function saveHtml(){
      try{
        const clone=document.documentElement.cloneNode(true);
        clone.querySelectorAll('[data-ul-print-export-host]').forEach(n=>n.remove());
        let base=clone.querySelector('base');
        if(!base){base=document.createElement('base');clone.querySelector('head')?.prepend(base)}
        if(base)base.setAttribute('href',location.href);
        const blob=new Blob(['<!doctype html>\n'+clone.outerHTML],{type:'text/html;charset=utf-8'});
        const url=URL.createObjectURL(blob);const a=document.createElement('a');a.href=url;a.download=filename();a.style.display='none';document.body.appendChild(a);a.click();a.remove();setTimeout(()=>URL.revokeObjectURL(url),1500);notify('HTML-Snapshot gespeichert');
      }catch(e){console.warn('[UniverseLab print/export] HTML snapshot failed',e);notify('HTML-Export nicht möglich')}
    }
    async function copyLink(){
      try{await navigator.clipboard.writeText(location.href);notify('Direktlink kopiert')}
      catch(_e){
        try{const ta=document.createElement('textarea');ta.value=location.href;ta.style.position='fixed';ta.style.opacity='0';document.body.appendChild(ta);ta.select();document.execCommand('copy');ta.remove();notify('Direktlink kopiert')}
        catch(e){console.warn('[UniverseLab print/export] copy failed',e);notify('Kopieren nicht möglich')}
      }
    }

    trigger.addEventListener('click',()=>setOpen(panel.hidden));
    shadow.querySelector('[data-action="print"]').addEventListener('click',()=>{setOpen(false);window.print()});
    shadow.querySelector('[data-action="html"]').addEventListener('click',()=>{setOpen(false);saveHtml()});
    shadow.querySelector('[data-action="copy"]').addEventListener('click',()=>{setOpen(false);copyLink()});
    all.addEventListener('click',()=>setOpen(false));
    document.addEventListener('pointerdown',e=>{if(!e.composedPath().includes(host))setOpen(false)});
    document.addEventListener('keydown',e=>{if(e.key==='Escape')setOpen(false)});
    window.addEventListener('beforeprint',()=>setOpen(false));
    (document.body||document.documentElement).appendChild(host);
    document.documentElement.dataset.ulGlobalExport='active';
  }

  function upgradeLegacyBibliographyLinks(){
    const catalog='/UniverseLab/2026-08-19_UniverseLab_BibliographyCatalog_v1.0.html';
    document.querySelectorAll('a[href]').forEach(a=>{
      const label=(a.textContent||'').replace(/\s+/g,' ').trim().toLowerCase();
      if(!label.includes('50-quellen-katalog'))return;
      try{
        const u=new URL(a.getAttribute('href'),location.href);
        if(u.origin===location.origin&&u.pathname.endsWith('/hyperzeit-bibliography.json')){
          a.href=catalog;
          a.dataset.ulBibliographyView='html-catalog';
          a.removeAttribute('download');
        }
      }catch(_e){}
    });
  }

  function hasNativeExport(){
    const body=document.body;
    if(body?.dataset.ulForceGlobalExport==='1')return false;
    if(document.querySelector('[data-ul-native-export],body[data-ul-export-title],.ul-export-trigger,[data-ul-export-trigger]'))return true;
    return Array.from(document.scripts).some(script=>{
      const src=script.getAttribute('src')||'';
      return /UniverseLab_(?:Export|TafelwerkAllFormulaExport)_/i.test(src);
    });
  }
})();
