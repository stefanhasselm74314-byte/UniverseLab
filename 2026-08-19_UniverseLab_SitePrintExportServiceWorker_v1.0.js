/* UniverseLab Site Print & Export Service Worker v1.0.3
 * Injects the shared print/export utility into HTML navigation responses within
 * /UniverseLab/ after bootstrap registration. No caching and no scientific-data mutation.
 * v1.0.1: never inject into the Owner Print Export page and inject before the final real
 * </body> tag, not the first textual occurrence inside inline JS.
 * v1.0.2: loads the native-export-aware toolbar with an explicit cache-busting version.
 * v1.0.3: loads the bibliography-link-aware navigation utility.
 */
'use strict';
const ROOT='/UniverseLab/';
const TOOL=ROOT+'assets/2026-08-19_UniverseLab_SitePrintExport_v1.0.js?v=1.0.3';
const OWNER_EXPORT=ROOT+'2026-08-11_UniverseLab_OwnerPrintExport_v1.0.html';
const MARK='data-ul-print-export-v10';

self.addEventListener('install',()=>self.skipWaiting());
self.addEventListener('activate',event=>event.waitUntil(self.clients.claim()));

self.addEventListener('fetch',event=>{
  const req=event.request;
  if(req.method!=='GET'||req.mode!=='navigate')return;
  const url=new URL(req.url);
  if(url.origin!==self.location.origin||!url.pathname.startsWith(ROOT)||url.searchParams.get('include-iframe')==='1')return;
  if(url.pathname===OWNER_EXPORT)return;
  event.respondWith((async()=>{
    const response=await fetch(req);
    const type=(response.headers.get('content-type')||'').toLowerCase();
    if(!response.ok||!type.includes('text/html'))return response;
    let html=await response.text();
    if(html.includes('2026-08-19_UniverseLab_SitePrintExport_v1.0.js')||html.includes('2026-08-19_UniverseLab_SitePrintExportBootstrap_v1.0.js')){
      return rebuild(response,html);
    }
    const injection='<script '+MARK+'="1" src="'+TOOL+'" defer></script><!-- UniverseLab SitePrintExport SW v1.0.3 -->';
    const matches=[...html.matchAll(/<\/body\s*>/ig)];
    if(matches.length){
      const last=matches[matches.length-1];
      html=html.slice(0,last.index)+injection+html.slice(last.index);
    }else{
      html+=injection;
    }
    return rebuild(response,html);
  })().catch(err=>{
    console.warn('[UniverseLab print/export SW] navigation passthrough after error',err);
    return fetch(req);
  }));
});

function rebuild(response,html){
  const headers=new Headers(response.headers);
  ['content-length','content-encoding','etag','last-modified'].forEach(h=>headers.delete(h));
  return new Response(html,{status:response.status,statusText:response.statusText,headers});
}
