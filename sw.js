'use strict';
const CACHE_NAME='universelab-ui-2.2.3';
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
  './guide.html',
  './about.html',
  './app-shell.js',
  './model-state.js',
  './cinema-mode.js',
  './lab-snapshots.js',
  './cosmic-events.js',
  './emergence-touch.js',
  './compare-mobile.js',
  './navigation-labels.js',
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

function optimiseCompare(html){
  html=html.replace(
    '</head>',
    '<style id="ul-compare-guard">html,body{max-width:100%;overflow-x:hidden}.app{max-width:100%}</style></head>'
  );

  html=html.replace(
    "function updateAll(){updateOutputs();drawMain();updateDistances();renderTable();drawSweep();calcFormula()}",
    "function updateAll(){updateOutputs();const active=document.querySelector('.view.active')?.id;if(active==='view-compare')drawMain();else if(active==='view-distances'||active==='view-growth')updateDistances();else if(active==='view-table')renderTable();else if(active==='view-sweep')drawSweep();else if(active==='view-formulas')calcFormula()}"
  );

  html=html.replace(
    "ids.forEach(id=>$('#'+id).addEventListener('input',updateAll));['zProbe','tableRows','sweepMin','sweepMax','sweepZ'].forEach(id=>$('#'+id).addEventListener('input',updateAll));",
    "let ulUpdateTimer=0;const scheduleUpdate=()=>{clearTimeout(ulUpdateTimer);ulUpdateTimer=setTimeout(updateAll,70)};ids.forEach(id=>$('#'+id).addEventListener('input',scheduleUpdate));['zProbe','tableRows','sweepMin','sweepMax','sweepZ'].forEach(id=>$('#'+id).addEventListener('input',scheduleUpdate));"
  );

  html=html.replace(
    'requestAnimationFrame(()=>{drawMain();drawSweep()})',
    'requestAnimationFrame(updateAll)'
  );

  html=html.replace(
    "renderFormulaList();selectFormula('a_z');updateAll()})();",
    "renderFormulaList();selectFormula('a_z');updateOutputs();drawMain();setTimeout(updateDistances,25);setTimeout(renderTable,90);setTimeout(drawSweep,160)})();"
  );

  return html;
}

async function enhanceNavigation(response,url){
  if(!response||!response.ok)return response;
  const type=response.headers.get('content-type')||'';
  if(!type.includes('text/html'))return response;

  let html=await response.text();
  html=html.includes('navigation-labels.js')
    ?html.replace(/navigation-labels\.js\?v=\d+/g,'navigation-labels.js?v=1')
    :html.replace('</body>','<script src="./navigation-labels.js?v=1"></script></body>');

  if(url.pathname.endsWith('/universe3d.html')){
    html=html.includes('cinema-mode.js')
      ?html.replace(/cinema-mode\.js\?v=\d+/g,'cinema-mode.js?v=085')
      :html.replace('</body>','<script src="./cinema-mode.js?v=085"></script></body>');
  }
  if(url.pathname.endsWith('/emergence.html')){
    html=html.includes('emergence-touch.js')
      ?html.replace(/emergence-touch\.js\?v=\d+/g,'emergence-touch.js?v=07')
      :html.replace('</body>','<script src="./emergence-touch.js?v=07"></script></body>');
  }
  if(url.pathname.endsWith('/compare.html')){
    html=optimiseCompare(html);
    html=html.includes('compare-mobile.js')
      ?html.replace(/compare-mobile\.js\?v=\d+/g,'compare-mobile.js?v=22')
      :html.replace('</body>','<script src="./compare-mobile.js?v=22"></script></body>');
  }

  const headers=new Headers(response.headers);
  headers.delete('content-length');
  headers.set('cache-control','no-cache');
  return new Response(html,{status:response.status,statusText:response.statusText,headers});
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