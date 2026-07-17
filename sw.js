'use strict';
const CACHE_NAME='universelab-ui-1.3.0';
const APP_SHELL=[
  './',
  './index.html',
  './portal.html',
  './journey.html',
  './observatory.html',
  './compare.html',
  './hyperlab.html',
  './universe3d.html',
  './validation.html',
  './app-shell.js',
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
    event.respondWith(
      fetch(event.request)
        .then(response=>{
          const copy=response.clone();
          caches.open(CACHE_NAME).then(cache=>cache.put(event.request,copy));
          return response;
        })
        .catch(async()=>{
          const hit=await caches.match(event.request);
          return hit||caches.match('./portal.html')||caches.match('./index.html');
        })
    );
    return;
  }

  event.respondWith(
    caches.match(event.request).then(hit=>hit||fetch(event.request).then(response=>{
      if(response&&response.status===200&&response.type!=='opaque'){
        const copy=response.clone();
        caches.open(CACHE_NAME).then(cache=>cache.put(event.request,copy));
      }
      return response;
    }))
  );
});