/* UniverseLab RC21 — STATIC CANDIDATE ONLY; NOT INSTALLED OR DEPLOYED.
 * Generated from the reviewed RC19 exact-file inventory. The client-side path
 * list only prevents broken presentation redirects; it is NOT access control.
 * Base main: __RC21_BASE_COMMIT__
 * Manifest SHA-256: __RC21_MANIFEST_SHA256__
 * Eligible doc/source paths: __RC21_ELIGIBLE_COUNT__
 */
(function(){
  'use strict';
  const ROOT='/UniverseLab/';
  const GITHUB_PREFIX='/stefanhasselm74314-byte/UniverseLab/blob/main/';
  const DOC_VIEWER=ROOT+'2026-08-27_UniverseLab_DocumentViewer_v1.0.html';
  const SOURCE_VIEWER=ROOT+'2026-08-27_UniverseLab_SourceTextViewer_v1.0.html';
  const ALLOWED=new Set(__RC21_PUBLIC_PATHS_JSON__);
  const DOC_EXT=/[.](?:md|markdown|txt|yml|yaml)$/i;
  const SOURCE_EXT=/[.](?:py|js|mjs|cjs|ts|tsx|jsx|css|scss|sh|bash|zsh|ps1|bat|cmd|toml|ini|cfg|conf|xml|tex|bib|sql|r|jl|java|c|h|cpp|hpp|log|properties)$/i;

  function cleanTarget(url){
    let rel;
    if(/%(?:2f|5c)/i.test(url.pathname))return null; // No encoded separators.
    if(url.origin===location.origin && url.pathname.startsWith(ROOT)){
      rel=url.pathname.slice(ROOT.length);
    }else if(url.origin==='https://github.com' && url.pathname.startsWith(GITHUB_PREFIX)){
      rel=url.pathname.slice(GITHUB_PREFIX.length);
    }else{
      return null;
    }
    try{rel=decodeURIComponent(rel);}catch(_e){return null;}
    if(!rel || rel.includes('\\') || rel.includes('%') || rel.includes('\0'))return null;
    if(rel.split('/').some(part=>!part || part==='.' || part==='..' || part.startsWith('.')))return null;
    if(!ALLOWED.has(rel))return null;
    const kind=DOC_EXT.test(rel)?'doc':SOURCE_EXT.test(rel)?'source':null;
    return kind?{rel,kind}:null;
  }

  function rewrite(anchor){
    if(!anchor || anchor.tagName!=='A' || !anchor.hasAttribute('href'))return;
    let url;
    try{url=new URL(anchor.getAttribute('href'),location.href);}catch(_e){return;}
    if(anchor.dataset.ulSafeDocumentRouter==='1'){
      const prior=anchor.dataset.ulDocumentSource;
      const priorKind=anchor.dataset.ulDocumentKind;
      const expected=(priorKind==='doc'?DOC_VIEWER:SOURCE_VIEWER)+'?src='+encodeURIComponent(prior);
      if(url.href===new URL(expected,location.href).href)return; // Own mutation, idempotent.
      delete anchor.dataset.ulDocumentSource;
      delete anchor.dataset.ulDocumentKind;
      delete anchor.dataset.ulSafeDocumentRouter;
    }
    if(anchor.hasAttribute('download') || anchor.dataset.ulRawLink==='1' ||
       anchor.dataset.ulNoDocumentViewer==='1' || anchor.dataset.ulNoDataViewer==='1')return;
    const target=cleanTarget(url);
    if(!target)return; // Retain the original GitHub URL on an excluded path.
    const encoded=target.rel.split('/').map(encodeURIComponent).join('/');
    const sourcePath=ROOT+encoded+url.search;
    anchor.dataset.ulDocumentSource=sourcePath;
    anchor.dataset.ulDocumentKind=target.kind;
    anchor.dataset.ulSafeDocumentRouter='1';
    const next=(target.kind==='doc'?DOC_VIEWER:SOURCE_VIEWER)+'?src='+encodeURIComponent(sourcePath);
    if(anchor.href!==new URL(next,location.href).href)anchor.href=next;
  }

  function visit(node){
    if(!node || node.nodeType!==1)return;
    if(node.tagName==='A')rewrite(node);
    if(typeof node.querySelectorAll==='function')node.querySelectorAll('a[href]').forEach(rewrite);
  }

  function init(){
    document.querySelectorAll('a[href]').forEach(rewrite);
    if(typeof MutationObserver==='undefined' || !document.documentElement)return;
    const observer=new MutationObserver(records=>{
      for(const record of records){
        if(record.type==='attributes')rewrite(record.target);
        else if(record.type==='childList')for(const node of record.addedNodes)visit(node);
      }
    });
    observer.observe(document.documentElement,{
      subtree:true, childList:true, attributes:true, attributeFilter:['href']
    });
  }

  if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',init,{once:true});
  else init();
})();
