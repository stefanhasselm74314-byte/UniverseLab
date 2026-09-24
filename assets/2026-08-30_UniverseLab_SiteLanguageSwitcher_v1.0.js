(()=>{'use strict';
const VERSION='1.0.4';
const LANGS=[['de','Deutsch'],['en','English'],['fr','Français'],['es','Español'],['it','Italiano'],['nl','Nederlands'],['pl','Polski'],['cs','Čeština'],['pt','Português'],['ja','日本語'],['zh-CN','中文']];
const PAIRS={
'index.html':'index-en.html','navigator.html':'navigator-en.html','research-status.html':'research-status-en.html','solver-hub.html':'solver-hub-en.html','hyperzeit-methods.html':'hyperzeit-methods-en.html','hyperzeit-material-v2.html':'hyperzeit-material-v2-en.html','sci-001-002-parent-closure-v0.1.html':'sci-001-002-parent-closure-v0.1-en.html','hyperlab.html':'hyperlab-en.html','observatory.html':'observatory-en.html','validation.html':'validation-en.html','guide.html':'guide-en.html','tafelwerk.html':'tafelwerk-en.html','compare-safe.html':'compare-en.html','about.html':'about-en.html','journey.html':'journey-en.html','emergence.html':'emergence-en.html','universe3d.html':'universe3d-en.html'};
const ALIASES={'navigator-app.html':'navigator-en.html','compare-desktop.html':'compare-en.html'};
const REVERSE=Object.fromEntries(Object.entries(PAIRS).map(([de,en])=>[en,de]));
function englishTarget(f){return PAIRS[f]||ALIASES[f]||null}
function injectStyle(){if(document.getElementById('ul-language-style'))return;const s=document.createElement('style');s.id='ul-language-style';s.textContent='.ul-shell__language{position:static!important;inset:auto!important;left:auto!important;right:auto!important;top:auto!important;bottom:auto!important;transform:none!important;z-index:auto!important;float:none!important;margin:0!important;display:inline-flex!important;align-items:center;gap:6px;min-height:36px;padding:3px 6px;border:1px solid #6657b8;border-radius:10px;background:#13162b;color:#fff;flex:0 0 auto}.ul-shell__language-icon{font-size:16px;line-height:1}.ul-shell__language select{position:static!important;min-height:30px;max-width:150px;border:0;outline:0;background:transparent;color:#fff;font:800 12px/1.2 system-ui,-apple-system,"Segoe UI",sans-serif}.ul-shell__language option{background:#101522;color:#fff}@media(max-width:760px){.ul-shell__gates{align-items:center}.ul-shell__language{order:99!important}}@media(max-width:480px){.ul-shell__language{min-height:38px;padding:4px 7px}.ul-shell__language select{max-width:132px;font-size:12px}}';(document.head||document.documentElement).appendChild(s)}
function file(){return location.pathname.split('/').pop()||'index.html'}
function baseGermanUrl(){const f=file();if(REVERSE[f])return new URL('./'+REVERSE[f],location.href).href;return location.href}
function go(lang){try{localStorage.setItem('universelab:language',lang)}catch{}
 const f=file();
 if(lang==='de'){
   if(REVERSE[f])location.href=new URL('./'+REVERSE[f],location.href).href;
   return;
 }
 const en=englishTarget(f);
 if(lang==='en'&&en){location.href=new URL('./'+en,location.href).href;return}
 const src=baseGermanUrl();
 location.href='https://translate.google.com/translate?sl=de&tl='+encodeURIComponent(lang)+'&u='+encodeURIComponent(src);
}
function mount(){const gates=document.querySelector('.ul-shell__gates');const expectsGates=!!document.querySelector('script[src*="2026-08-16_UniverseLab_GlobalShell_v1.1.js"]');
 const existing=[...document.querySelectorAll('[data-ul-language-switcher]')];
 if(gates){
   existing.filter(node=>!gates.contains(node)).forEach(node=>node.remove());
   const canonical=existing.find(node=>gates.contains(node)&&node.classList.contains('ul-shell__language'));
   if(canonical){existing.filter(node=>node!==canonical).forEach(node=>node.remove());return true}
   existing.filter(node=>gates.contains(node)).forEach(node=>node.remove());
 }else{
   if(expectsGates)return false;
   const canonical=existing.find(node=>node.classList.contains('ul-shell__language'));
   if(canonical){existing.filter(node=>node!==canonical).forEach(node=>node.remove());return true}
   existing.forEach(node=>node.remove());
 }
 const host=gates||document.querySelector('.shell')||document.querySelector('header')||document.querySelector('nav')||document.body;if(!host)return false;injectStyle();
 const wrap=document.createElement('label');wrap.className='ul-shell__language';wrap.dataset.ulLanguageSwitcher=VERSION;wrap.title='Sprache auswählen';
 const icon=document.createElement('span');icon.className='ul-shell__language-icon';icon.textContent='🌐';icon.setAttribute('aria-hidden','true');
 const select=document.createElement('select');select.setAttribute('aria-label','Sprache auswählen');
 LANGS.forEach(([value,label])=>{const o=document.createElement('option');o.value=value;o.textContent=label;select.appendChild(o)});
 select.value=REVERSE[file()]?'en':'de';select.addEventListener('change',()=>go(select.value));
 wrap.append(icon,select);host.appendChild(wrap);return true}
const initialMount=mount();
if(!initialMount){
 const mo=new MutationObserver(()=>{if(mount())mo.disconnect()});mo.observe(document.documentElement,{childList:true,subtree:true});setTimeout(()=>mo.disconnect(),10000)
}
if(document.documentElement){
 let cleaning=false;
 const guard=new MutationObserver(()=>{
   if(cleaning||document.querySelectorAll('[data-ul-language-switcher]').length<=1)return;
   cleaning=true;
   try{mount()}finally{cleaning=false}
 });
 guard.observe(document.documentElement,{childList:true,subtree:true});
 setTimeout(()=>guard.disconnect(),10000);
}
window.UniverseLabLanguageSwitcher={version:VERSION,languages:LANGS.map(x=>x[0])};
})();
