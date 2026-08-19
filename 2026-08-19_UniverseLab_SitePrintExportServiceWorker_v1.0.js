/* UniverseLab Site Print & Export Service Worker v1.0.5
 * Injects shared presentation utilities into HTML navigation responses within /UniverseLab/.
 * No caching and no scientific-data mutation.
 * Preserves v1.0.4 machine-data-viewer-aware print/export utility and adds language injection.
 */
'use strict';
const ROOT='/UniverseLab/';
const TOOL=ROOT+'assets/2026-08-19_UniverseLab_SitePrintExport_v1.0.js?v=1.0.4';
const LANGUAGE=ROOT+'assets/2026-08-18_UniverseLab_SiteLanguageSwitcher_v1.1.js?v=1.1.1';
const OWNER_EXPORT=ROOT+'2026-08-11_UniverseLab_OwnerPrintExport_v1.0.html';
self.addEventListener('install',()=>self.skipWaiting());
self.addEventListener('activate',event=>event.waitUntil(self.clients.claim()));
self.addEventListener('fetch',event=>{
  const req=event.request;if(req.method!=='GET'||req.mode!=='navigate')return;
  const url=new URL(req.url);if(url.origin!==self.location.origin||!url.pathname.startsWith(ROOT)||url.searchParams.get('include-iframe')==='1'||url.pathname===OWNER_EXPORT)return;
  event.respondWith((async()=>{
    const response=await fetch(req);const type=(response.headers.get('content-type')||'').toLowerCase();if(!response.ok||!type.includes('text/html'))return response;
    let html=await response.text();const injections=[];
    const hasLanguage=html.includes('UniverseLab_SiteLanguageSwitcher');
    const hasPrint=html.includes('2026-08-19_UniverseLab_SitePrintExport_v1.0.js')||html.includes('2026-08-19_UniverseLab_SitePrintExportBootstrap_v1.0.js');
    if(!hasLanguage)injections.push('<script data-ul-language-switcher-sw="1" src="'+LANGUAGE+'" defer></script>');
    if(!hasPrint)injections.push('<script data-ul-print-export-v10="1" src="'+TOOL+'" defer></script>');
    if(!injections.length)return rebuild(response,html);
    const injection=injections.join('')+'<!-- UniverseLab shared presentation SW v1.0.5 -->';
    const matches=[...html.matchAll(/<\/body\s*>/ig)];if(matches.length){const last=matches[matches.length-1];html=html.slice(0,last.index)+injection+html.slice(last.index)}else html+=injection;
    return rebuild(response,html);
  })().catch(err=>{console.warn('[UniverseLab shared presentation SW] navigation passthrough after error',err);return fetch(req)}));
});
function rebuild(response,html){const headers=new Headers(response.headers);['content-length','content-encoding','etag','last-modified'].forEach(h=>headers.delete(h));return new Response(html,{status:response.status,statusText:response.statusText,headers})}
