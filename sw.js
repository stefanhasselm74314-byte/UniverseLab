'use strict';
const CACHE_NAME='universelab-mvp-0.5.1';
const APP_SHELL=['./','./index.html','./manifest.webmanifest','./src/app.js','./src/cellular.js','./src/cosmology-controller.js','./src/numerics.js','./src/storage.js','./src/chart.js'];
self.addEventListener('install',e=>e.waitUntil(caches.open(CACHE_NAME).then(c=>c.addAll(APP_SHELL)).then(()=>self.skipWaiting())));
self.addEventListener('activate',e=>e.waitUntil(caches.keys().then(keys=>Promise.all(keys.filter(k=>k!==CACHE_NAME).map(k=>caches.delete(k)))).then(()=>self.clients.claim())));
self.addEventListener('fetch',e=>{if(e.request.method!=='GET')return;e.respondWith(fetch(e.request).then(r=>{if(r&&r.status===200&&r.type!=='opaque'){const copy=r.clone();caches.open(CACHE_NAME).then(c=>c.put(e.request,copy))}return r}).catch(()=>caches.match(e.request).then(hit=>hit||caches.match('./index.html'))))});
