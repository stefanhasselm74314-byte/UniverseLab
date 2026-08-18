/* UniverseLab Site Language Switcher v1.0 compatibility loader.
 * Superseded by v1.1. Kept so existing pages automatically receive curated
 * English routing without requiring immediate HTML rewrites.
 */
(function(){'use strict';if(document.querySelector('script[data-ul-lang-v11]'))return;var s=document.createElement('script');s.src='./assets/2026-08-18_UniverseLab_SiteLanguageSwitcher_v1.1.js';s.defer=true;s.dataset.ulLangV11='1';document.head.appendChild(s)})();
