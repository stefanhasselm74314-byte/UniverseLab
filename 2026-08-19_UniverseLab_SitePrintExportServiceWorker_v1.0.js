/* UniverseLab Site Print & Export Service Worker v1.0.9 — RETIRED
 * Navigation recovery 2026-09-09.
 *
 * The previous v1.0.8 intercepted every same-origin navigation under /UniverseLab/ in
 * order to inject presentation scripts. UniverseLab already had an earlier Opera-specific
 * reset because navigation-intercepting workers could leave requests hanging. The shared
 * presentation utilities are now loaded explicitly by the page/bootstrap path instead.
 *
 * This worker intentionally has NO fetch handler. It activates, unregisters itself and
 * tells controlled clients that the obsolete navigation interceptor was removed.
 * No scientific, solver, governance or evidence effect.
 */
'use strict';

self.addEventListener('install',event=>{
  event.waitUntil(self.skipWaiting());
});

self.addEventListener('activate',event=>{
  event.waitUntil((async()=>{
    await self.registration.unregister();
    const clients=await self.clients.matchAll({type:'window',includeUncontrolled:true});
    clients.forEach(client=>client.postMessage({
      type:'UNIVERSELAB_PRESENTATION_SW_RETIRED',
      version:'1.0.9'
    }));
  })());
});

// Absichtlich kein fetch-Handler: Navigationen werden direkt vom Browser/GitHub Pages geladen.
