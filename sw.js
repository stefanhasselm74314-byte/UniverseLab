'use strict';

// UniverseLab PWA reset 2026-07-25:
// Der frühere Network-/Cache-Worker konnte in einzelnen Opera-Installationen
// Navigationen und Skriptanforderungen dauerhaft offen halten. Dieser Worker
// räumt alle alten Caches auf und meldet sich anschließend selbst ab.

self.addEventListener('install',event=>{
  event.waitUntil(self.skipWaiting());
});

self.addEventListener('activate',event=>{
  event.waitUntil((async()=>{
    const keys=await caches.keys();
    await Promise.all(keys.map(key=>caches.delete(key)));
    await self.registration.unregister();
    const clients=await self.clients.matchAll({type:'window',includeUncontrolled:true});
    clients.forEach(client=>client.postMessage({type:'UNIVERSELAB_SW_REMOVED'}));
  })());
});

// Absichtlich kein fetch-Handler: alle Dateien werden wieder direkt
// über GitHub Pages geladen und keine Anfrage kann im Worker hängen bleiben.
