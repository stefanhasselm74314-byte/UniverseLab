'use strict';
const CACHE_NAME='universelab-ui-1.8.5';
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

self.addEventListener('fetch',event=>{
  if(event.request.method!=='GET')return;
  const url=new URL(event.request.url);
  if(url.origin!==self.location.origin)return;

  if(event.request.mode==='navigate'){
    event.respondWith((async()=>{
      try{
        const response=await fetch(event.request);
        if(response&&response.ok){
          const cache=await caches.open(CACHE_NAME);
          cache.put(event.request,response.clone());
        }
        return response;
      }catch(error){
        return await caches.match(event.request)
          ||await caches.match('./')
          ||await caches.match('./index.html')
          ||new Response('UniverseLab ist derzeit offline und noch nicht vollständig zwischengespeichert.',{
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