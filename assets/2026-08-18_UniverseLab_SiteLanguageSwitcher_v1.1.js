/* UniverseLab Site Language Switcher v1.1.3
 * German is the canonical research language.
 * Curated English routes are preferred where explicitly registered.
 * Other languages use full-page automatic translation from the German source.
 * Presentation layer only: no formula, data, status or evidence changes.
 */
(function(){
  'use strict';
  const LANGUAGES=[['de','Deutsch'],['en','English'],['fr','Français'],['es','Español'],['it','Italiano'],['nl','Nederlands'],['pl','Polski'],['cs','Čeština'],['pt','Português'],['ja','日本語'],['zh-CN','中文']];
  const CURATED={
    '/UniverseLab/':{de:'/UniverseLab/',en:'/UniverseLab/index-en.html'},
    '/UniverseLab/index.html':{de:'/UniverseLab/',en:'/UniverseLab/index-en.html'},
    '/UniverseLab/index-en.html':{de:'/UniverseLab/',en:'/UniverseLab/index-en.html'},
    '/UniverseLab/research-status.html':{de:'/UniverseLab/research-status.html',en:'/UniverseLab/research-status-en.html'},
    '/UniverseLab/research-status-en.html':{de:'/UniverseLab/research-status.html',en:'/UniverseLab/research-status-en.html'},
    '/UniverseLab/solver-hub.html':{de:'/UniverseLab/solver-hub.html',en:'/UniverseLab/solver-hub-en.html'},
    '/UniverseLab/solver-hub-en.html':{de:'/UniverseLab/solver-hub.html',en:'/UniverseLab/solver-hub-en.html'},
    '/UniverseLab/hyperzeit-methods.html':{de:'/UniverseLab/hyperzeit-methods.html',en:'/UniverseLab/hyperzeit-methods-en.html'},
    '/UniverseLab/hyperzeit-methods-en.html':{de:'/UniverseLab/hyperzeit-methods.html',en:'/UniverseLab/hyperzeit-methods-en.html'},
    '/UniverseLab/hyperzeit-material-v2.html':{de:'/UniverseLab/hyperzeit-material-v2.html',en:'/UniverseLab/hyperzeit-material-v2-en.html'},
    '/UniverseLab/hyperzeit-material-v2-en.html':{de:'/UniverseLab/hyperzeit-material-v2.html',en:'/UniverseLab/hyperzeit-material-v2-en.html'},
    '/UniverseLab/sci-001-002-parent-closure-v0.1.html':{de:'/UniverseLab/sci-001-002-parent-closure-v0.1.html',en:'/UniverseLab/sci-001-002-parent-closure-v0.1-en.html'},
    '/UniverseLab/sci-001-002-parent-closure-v0.1-en.html':{de:'/UniverseLab/sci-001-002-parent-closure-v0.1.html',en:'/UniverseLab/sci-001-002-parent-closure-v0.1-en.html'},
    '/UniverseLab/navigator.html':{de:'/UniverseLab/navigator.html',en:'/UniverseLab/navigator-en.html'},
    '/UniverseLab/navigator-app.html':{de:'/UniverseLab/navigator.html',en:'/UniverseLab/navigator-en.html'},
    '/UniverseLab/navigator-en.html':{de:'/UniverseLab/navigator.html',en:'/UniverseLab/navigator-en.html'},
    '/UniverseLab/hyperlab.html':{de:'/UniverseLab/hyperlab.html',en:'/UniverseLab/hyperlab-en.html'},
    '/UniverseLab/hyperlab-en.html':{de:'/UniverseLab/hyperlab.html',en:'/UniverseLab/hyperlab-en.html'},
    '/UniverseLab/guide.html':{de:'/UniverseLab/guide.html',en:'/UniverseLab/guide-en.html'},
    '/UniverseLab/guide-en.html':{de:'/UniverseLab/guide.html',en:'/UniverseLab/guide-en.html'},
    '/UniverseLab/tafelwerk.html':{de:'/UniverseLab/tafelwerk.html',en:'/UniverseLab/tafelwerk-en.html'},
    '/UniverseLab/tafelwerk-en.html':{de:'/UniverseLab/tafelwerk.html',en:'/UniverseLab/tafelwerk-en.html'},
    '/UniverseLab/compare-safe.html':{de:'/UniverseLab/compare-safe.html',en:'/UniverseLab/compare-en.html'},
    '/UniverseLab/compare-desktop.html':{de:'/UniverseLab/compare-safe.html',en:'/UniverseLab/compare-en.html'},
    '/UniverseLab/compare-en.html':{de:'/UniverseLab/compare-safe.html',en:'/UniverseLab/compare-en.html'},
    '/UniverseLab/observatory.html':{de:'/UniverseLab/observatory.html',en:'/UniverseLab/observatory-en.html'},
    '/UniverseLab/observatory-en.html':{de:'/UniverseLab/observatory.html',en:'/UniverseLab/observatory-en.html'},
    '/UniverseLab/validation.html':{de:'/UniverseLab/validation.html',en:'/UniverseLab/validation-en.html'},
    '/UniverseLab/validation-en.html':{de:'/UniverseLab/validation.html',en:'/UniverseLab/validation-en.html'},
    '/UniverseLab/about.html':{de:'/UniverseLab/about.html',en:'/UniverseLab/about-en.html'},
    '/UniverseLab/about-en.html':{de:'/UniverseLab/about.html',en:'/UniverseLab/about-en.html'},
    '/UniverseLab/journey.html':{de:'/UniverseLab/journey.html',en:'/UniverseLab/journey-en.html'},
    '/UniverseLab/journey-en.html':{de:'/UniverseLab/journey.html',en:'/UniverseLab/journey-en.html'},
    '/UniverseLab/emergence.html':{de:'/UniverseLab/emergence.html',en:'/UniverseLab/emergence-en.html'},
    '/UniverseLab/emergence-en.html':{de:'/UniverseLab/emergence.html',en:'/UniverseLab/emergence-en.html'},
    '/UniverseLab/universe3d.html':{de:'/UniverseLab/universe3d.html',en:'/UniverseLab/universe3d-en.html'},
    '/UniverseLab/universe3d-en.html':{de:'/UniverseLab/universe3d.html',en:'/UniverseLab/universe3d-en.html'}
  };
  function pair(){return CURATED[location.pathname]||null;}
  function germanSource(){const p=pair();if(p)return location.origin+p.de;const c=document.querySelector('link[rel="alternate"][hreflang="de"]');if(c&&c.href)return c.href;const canonical=document.querySelector('link[rel="canonical"]');if(canonical&&canonical.href&&!/-en\.html(?:$|\?)/.test(canonical.href))return canonical.href;const u=new URL(location.href);u.search='';u.hash='';return u.href;}
  function target(lang){const p=pair();if((lang==='de'||lang==='en')&&p)return location.origin+p[lang];if(lang==='de')return germanSource();if(lang==='en'&&p)return location.origin+p.en;return 'https://translate.google.com/translate?sl=de&tl='+encodeURIComponent(lang)+'&u='+encodeURIComponent(germanSource());}
  function detected(){if(/-en\.html$/.test(location.pathname))return'en';return document.documentElement.lang&&document.documentElement.lang.toLowerCase().startsWith('en')?'en':'de';}
  function styles(){const s=document.createElement('style');s.textContent='.ul-language-switcher{display:flex;align-items:center;gap:6px;flex:0 0 auto;margin-left:2px}.ul-language-switcher label{position:absolute;width:1px;height:1px;padding:0;margin:-1px;overflow:hidden;clip:rect(0,0,0,0);white-space:nowrap;border:0}.ul-language-switcher .ul-lang-icon{font-size:15px;line-height:1;opacity:.92}.ul-language-switcher select{min-height:38px;max-width:132px;padding:6px 30px 6px 9px;border:1px solid #47547c;border-radius:10px;background:#11182d;color:#f5f6ff;font:750 11px/1.2 system-ui,-apple-system,"Segoe UI",sans-serif;cursor:pointer;color-scheme:dark}.ul-language-switcher select:hover,.ul-language-switcher select:focus-visible{border-color:#8d7cff;outline:none;background:#171f39}@media(max-width:760px){.ul-language-switcher select{max-width:91px;padding-left:7px}.ul-language-switcher .ul-lang-icon{display:none}}@media(max-width:520px){.ul-language-switcher{position:fixed;right:7px;bottom:8px;z-index:80;padding:4px;border:1px solid #303a61;border-radius:12px;background:#080b17f2;box-shadow:0 8px 28px #0008}.ul-language-switcher select{max-width:112px}}';document.head.appendChild(s);}
  function install(){if(document.querySelector('[data-ul-language-switcher]'))return;const host=document.querySelector('.shell')||document.querySelector('header')||document.querySelector('nav')||document.body;if(!host)return;styles();const w=document.createElement('div');w.className='ul-language-switcher';w.dataset.ulLanguageSwitcher='1';w.title='Language · English is curated on registered research pages; other languages are automatically translated from German.';const icon=document.createElement('span');icon.className='ul-lang-icon';icon.textContent='🌐';icon.setAttribute('aria-hidden','true');const label=document.createElement('label');label.htmlFor='ul-site-language';label.textContent='Language';const sel=document.createElement('select');sel.id='ul-site-language';sel.setAttribute('aria-label','Choose language');LANGUAGES.forEach(([c,n])=>{const o=document.createElement('option');o.value=c;o.textContent=n;sel.appendChild(o)});sel.value=detected();sel.addEventListener('change',()=>{try{localStorage.setItem('universelab-language',sel.value)}catch(_e){} location.href=target(sel.value)});w.append(icon,label,sel);host.appendChild(w)}
  if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',install,{once:true});else install();
})();
