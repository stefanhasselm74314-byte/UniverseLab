'use strict';
const CACHE_NAME='universelab-ui-2.0.7';
const APP_SHELL=[
  './',
  './index.html',
  './emergence.html',
  './portal.html',
  './journey.html',
  './observatory.html',
  './compare.html',
  './hyperlab.html',
  './universe3d.html',
  './validation.html',
  './about.html',
  './app-shell.js',
  './model-state.js',
  './cinema-mode.js',
  './lab-snapshots.js',
  './emergence-touch.js',
  './portal-live.js',
  './manifest.webmanifest'
];

self.addEventListener('install',event=>{
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then(cache=>cache.addAll(APP_SHELL))
      .then(()=>self.skipWaiting())
  );
});

self.addEventListener('activate',event=>{
  event.waitUntil(
    caches.keys()
      .then(keys=>Promise.all(keys.filter(key=>key!==CACHE_NAME).map(key=>caches.delete(key))))
      .then(()=>self.clients.claim())
  );
});

async function enhanceNavigation(response,url){
  if(!response||!response.ok||!url.pathname.endsWith('/universe3d.html'))return response;
  const type=response.headers.get('content-type')||'';
  if(!type.includes('text/html'))return response;
  const html=await response.text();
  const enhanced=html.includes('cinema-mode.js')
    ?html.replace(/cinema-mode\.js\?v=\d+/g,'cinema-mode.js?v=085')
    :html.replace('</body>','<script src="./cinema-mode.js?v=085"></script></body>');
  const headers=new Headers(response.headers);
  headers.delete('content-length');
  headers.set('cache-control','no-cache');
  return new Response(enhanced,{status:response.status,statusText:response.statusText,headers});
}

self.addEventListener('fetch',event=>{
  if(event.request.method!=='GET')return;
  const url=new URL(event.request.url);
  if(url.origin!==self.location.origin)return;

  if(event.request.mode==='navigate'){
    event.respondWith((async()=>{
      try{
        let response=await fetch(event.request);
        response=await enhanceNavigation(response,url);
        if(response&&response.ok){
          const cache=await caches.open(CACHE_NAME);
          cache.put(event.request,response.clone());
        }
        return response;
      }catch(error){
        let fallback=await caches.match(event.request)
          ||await caches.match('./')
          ||await caches.match('./index.html');
        if(fallback)return await enhanceNavigation(fallback,url);
        return new Response('UniverseLab ist derzeit offline und noch nicht vollständig zwischengespeichert.',{
          status:503,
          headers:{'Content-Type':'text/plain; charset=utf-8'}
        });
      }
    })());
    return;
  }

  event.respondWith((async()=>{
    const cached=await caches.match(event.request);
    if(cached)return cached;
    try{
      const response=await fetch(event.request);
      if(response&&response.ok&&response.type!=='opaque'){
        const cache=await caches.open(CACHE_NAME);
        cache.put(event.request,response.clone());
      }
      return response;
    }catch(error){
      return new Response('',{status:504,statusText:'Offline'});
    }
  })());
});
