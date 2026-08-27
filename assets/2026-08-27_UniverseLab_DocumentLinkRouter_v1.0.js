/* UniverseLab Document Link Router v1.0
 * Presentation/navigation utility only. No scientific, solver or governance status effect.
 * Routes human-facing Markdown, text and YAML links through the same-origin DocumentViewer.
 * Explicit raw/download links are preserved.
 */
(function(){
  'use strict';
  if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',init,{once:true});
  else init();

  function init(){
    const ROOT='/UniverseLab/';
    const VIEWER=ROOT+'2026-08-27_UniverseLab_DocumentViewer_v1.0.html';
    const GH_PREFIX='/stefanhasselm74314-byte/UniverseLab/blob/main/';
    const supported=/[.](md|markdown|txt|yml|yaml)$/i;
    document.querySelectorAll('a[href]').forEach(a=>{
      if(a.hasAttribute('download')||a.dataset.ulRawLink==='1'||a.dataset.ulNoDocumentViewer==='1'||a.dataset.ulNoDataViewer==='1')return;
      try{
        const u=new URL(a.getAttribute('href'),location.href);
        let original='';
        if(u.origin===location.origin&&u.pathname.startsWith(ROOT)&&supported.test(u.pathname)){
          original=u.pathname+u.search;
        }else if(u.hostname==='github.com'&&u.pathname.startsWith(GH_PREFIX)){
          const repoPath=u.pathname.slice(GH_PREFIX.length);
          if(!supported.test(repoPath))return;
          original=ROOT+repoPath;
        }else return;
        a.dataset.ulDocumentSource=original;
        a.href=VIEWER+'?src='+encodeURIComponent(original);
      }catch(_e){}
    });
  }
})();
