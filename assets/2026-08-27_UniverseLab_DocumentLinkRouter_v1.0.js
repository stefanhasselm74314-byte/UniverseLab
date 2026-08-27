/* UniverseLab Document Link Router v1.1
 * Presentation/navigation utility only. No scientific, solver or governance status effect.
 * Routes human-facing Markdown/text/YAML and source/config links through same-origin viewers.
 * Explicit raw/download links are preserved.
 */
(function(){
  'use strict';
  if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',init,{once:true});
  else init();

  function init(){
    const ROOT='/UniverseLab/';
    const DOC_VIEWER=ROOT+'2026-08-27_UniverseLab_DocumentViewer_v1.0.html';
    const SOURCE_VIEWER=ROOT+'2026-08-27_UniverseLab_SourceTextViewer_v1.0.html';
    const GH_PREFIX='/stefanhasselm74314-byte/UniverseLab/blob/main/';
    const docs=/[.](md|markdown|txt|yml|yaml)$/i;
    const source=/[.](py|js|mjs|cjs|ts|tsx|jsx|css|scss|sh|bash|zsh|ps1|bat|cmd|toml|ini|cfg|conf|xml|tex|bib|sql|r|jl|java|c|h|cpp|hpp|log|properties)$/i;
    document.querySelectorAll('a[href]').forEach(a=>{
      if(a.hasAttribute('download')||a.dataset.ulRawLink==='1'||a.dataset.ulNoDocumentViewer==='1'||a.dataset.ulNoDataViewer==='1')return;
      try{
        const u=new URL(a.getAttribute('href'),location.href);
        let original='',kind='';
        if(u.origin===location.origin&&u.pathname.startsWith(ROOT)){
          if(docs.test(u.pathname))kind='doc';else if(source.test(u.pathname))kind='source';else return;
          original=u.pathname+u.search;
        }else if(u.hostname==='github.com'&&u.pathname.startsWith(GH_PREFIX)){
          const repoPath=u.pathname.slice(GH_PREFIX.length);
          if(docs.test(repoPath))kind='doc';else if(source.test(repoPath))kind='source';else return;
          original=ROOT+repoPath;
        }else return;
        a.dataset.ulDocumentSource=original;
        a.dataset.ulDocumentKind=kind;
        a.href=(kind==='source'?SOURCE_VIEWER:DOC_VIEWER)+'?src='+encodeURIComponent(original);
      }catch(_e){}
    });
  }
})();
