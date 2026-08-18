/* UniverseLab Site Language Switcher v1.0
 * Canonical source language: German (de).
 * Non-German options use Google Translate's full-page website translation.
 * Scientific status: presentation layer only; no evidence or formula changes.
 */
(function(){
  'use strict';

  const LANGUAGES = [
    ['de','Deutsch'],
    ['en','English'],
    ['fr','Français'],
    ['es','Español'],
    ['it','Italiano'],
    ['nl','Nederlands'],
    ['pl','Polski'],
    ['cs','Čeština'],
    ['pt','Português'],
    ['ja','日本語'],
    ['zh-CN','中文']
  ];

  function canonicalUrl(){
    const canonical = document.querySelector('link[rel="canonical"]');
    if (canonical && canonical.href) return canonical.href;
    const url = new URL(window.location.href);
    url.searchParams.delete('_x_tr_sl');
    url.searchParams.delete('_x_tr_tl');
    url.searchParams.delete('_x_tr_hl');
    return url.href;
  }

  function translateUrl(lang){
    return 'https://translate.google.com/translate?sl=de&tl=' +
      encodeURIComponent(lang) + '&u=' + encodeURIComponent(canonicalUrl());
  }

  function installStyles(){
    const style = document.createElement('style');
    style.textContent = `
      .ul-language-switcher{display:flex;align-items:center;gap:6px;flex:0 0 auto;margin-left:2px}
      .ul-language-switcher label{position:absolute;width:1px;height:1px;padding:0;margin:-1px;overflow:hidden;clip:rect(0,0,0,0);white-space:nowrap;border:0}
      .ul-language-switcher .ul-lang-icon{font-size:15px;line-height:1;opacity:.92}
      .ul-language-switcher select{min-height:38px;max-width:132px;padding:6px 30px 6px 9px;border:1px solid #47547c;border-radius:10px;background:#11182d;color:#f5f6ff;font:750 11px/1.2 system-ui,-apple-system,"Segoe UI",sans-serif;cursor:pointer;color-scheme:dark}
      .ul-language-switcher select:hover,.ul-language-switcher select:focus-visible{border-color:#8d7cff;outline:none;background:#171f39}
      @media(max-width:760px){.ul-language-switcher select{max-width:91px;padding-left:7px}.ul-language-switcher .ul-lang-icon{display:none}}
      @media(max-width:520px){.ul-language-switcher{position:fixed;right:7px;bottom:8px;z-index:80;padding:4px;border:1px solid #303a61;border-radius:12px;background:#080b17f2;box-shadow:0 8px 28px #0008}.ul-language-switcher select{max-width:112px}}
    `;
    document.head.appendChild(style);
  }

  function install(){
    if (document.querySelector('[data-ul-language-switcher]')) return;
    const host = document.querySelector('.shell') || document.querySelector('header') || document.body;
    if (!host) return;

    installStyles();

    const wrap = document.createElement('div');
    wrap.className = 'ul-language-switcher';
    wrap.dataset.ulLanguageSwitcher = '1';
    wrap.title = 'Sprache wählen · Nicht-deutsche Fassungen werden automatisch übersetzt.';

    const icon = document.createElement('span');
    icon.className = 'ul-lang-icon';
    icon.textContent = '🌐';
    icon.setAttribute('aria-hidden','true');

    const label = document.createElement('label');
    label.htmlFor = 'ul-site-language';
    label.textContent = 'Sprache';

    const select = document.createElement('select');
    select.id = 'ul-site-language';
    select.setAttribute('aria-label','Sprache wählen');

    LANGUAGES.forEach(([code,name]) => {
      const option = document.createElement('option');
      option.value = code;
      option.textContent = name;
      select.appendChild(option);
    });

    let stored = 'de';
    try { stored = localStorage.getItem('universelab-language') || 'de'; } catch(_e) {}
    if (LANGUAGES.some(([code]) => code === stored)) select.value = stored;

    select.addEventListener('change', function(){
      const lang = select.value;
      try { localStorage.setItem('universelab-language', lang); } catch(_e) {}
      if (lang === 'de') {
        window.location.href = canonicalUrl();
      } else {
        window.location.href = translateUrl(lang);
      }
    });

    wrap.append(icon,label,select);
    host.appendChild(wrap);
  }

  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', install, {once:true});
  else install();
})();
