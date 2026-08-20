/* UniverseLab Curated English Legacy Adapter v1.0
 * Presentation-only adapter for legacy interactive pages.
 * German source remains canonical. The adapter fetches the canonical German page,
 * applies a governed literal translation map (including dynamic UI strings), and
 * renders the same executable page under the curated English URL.
 */
(function(){
  'use strict';
  const ROOT='https://stefanhasselm74314-byte.github.io/UniverseLab/';
  const page=(location.pathname.split('/').pop()||'').replace(/-en\.html$/,'.html');
  const COMMON=[
    ['lang="de"','lang="en"'],['de-DE','en-US'],
    ['Forschungsstatus','Research status'],['Zum Portal','Open portal'],['Zum Labor','Open lab'],
    ['Speichern','Save'],['Laden','Load'],['Leeren','Clear'],['Neustart','Restart'],['Einzelschritt','Single step'],
    ['Wissenschaftlicher Status','Scientific status'],['Heute','Today'],['Zukunft','Future'],
    ['Strahlung','Radiation'],['Materie','Matter'],['Vakuum','Vacuum'],['Krümmung','Curvature'],
    ['beschleunigt','accelerating'],['abgebremst','decelerating'],['dominante Komponente','dominant component'],
    ['Skalenfaktor','scale factor'],['Rotverschiebung','redshift'],['kosmisches Alter','cosmic age'],
    ['Photonentemperatur','photon temperature'],['Beschleunigung','acceleration'],
    ['erste Sterne','first stars'],['Erste Sterne','First stars'],['ferne Zukunft','far future'],
    ['frühes Universum','early universe'],['Heutiges Universum','Present-day universe'],
    ['Ferne Zukunft','Far future'],['Dunkles Zeitalter','Dark Ages'],['Galaxienwachstum','Galaxy growth'],
    ['Strahlungsära','Radiation era'],['Materieära','Matter era'],['Vakuumära','Vacuum era'],['Krümmungsära','Curvature era'],
    ['Plasmaära','Plasma era'],['Rekombination','Recombination'],['Gleichheit','Equality'],
    ['Jahre','years'],['Tsd. Jahre','kyr'],['Mio. Jahre','Myr'],['Mrd. Jahre','Gyr']
  ];
  const MAPS={
    'about.html':[
      ['Über UniverseLab und Stefan Hasselmeyer','About UniverseLab and Stefan Hasselmeyer'],
      ['UniverseLab von Stefan Hasselmeyer','UniverseLab by Stefan Hasselmeyer'],
      ['Das Universum sichtbar machen.','Making the universe visible.'],
      ['UniverseLab ist eine interaktive Forschungs- und Visualisierungsplattform für Kosmologie. Sie verbindet etablierte Standardmodelle, reproduzierbare Numerik und klar gekennzeichnete experimentelle Forschungsansätze.','UniverseLab is an interactive research and visualization platform for cosmology. It combines established standard models, reproducible numerics, and clearly labelled experimental research approaches.'],
      ['„Kann man das Universum nicht nur berechnen, sondern auch sichtbar und erfahrbar machen?“','“Can we not only calculate the universe, but also make it visible and explorable?”'],
      ['Unsere Mission','Our mission'],['Das Team','The team'],['Wissenschaftliche Leitlinien','Scientific guidelines'],['Entwicklung','Development'],['Roadmap','Roadmap'],['Offenes Forschungsverständnis','Open research philosophy'],
      ['Verständlichkeit','Clarity'],['Reproduzierbarkeit','Reproducibility'],['Transparenz','Transparency'],['Falsifizierbarkeit','Falsifiability'],['Offene Neugier','Open curiosity'],
      ['Initiator und Projektleitung','Initiator and project lead'],['KI-gestützte Entwicklungsunterstützung','AI-assisted development support'],
      ['Etabliert','Established'],['Analyse','Analysis'],['Modellabhängig','Model-dependent'],['Spekulativ','Speculative'],['Ursprung','Origins'],['In Entwicklung','In development'],['Langfristig','Long term']
    ],
    'journey.html':[
      ['Cosmic Journey · interaktive kosmische Zeitreise','Cosmic Journey · interactive cosmic time travel'],
      ['Kosmische Zeitleiste','Cosmic timeline'],['Reise starten','Start journey'],['Pause','Pause'],['Dichteanteile','Density fractions'],
      ['Verzögerungsparameter q','deceleration parameter q'],['Expansionsregime','expansion regime'],['Warum verändert sich das Universum?','Why does the universe change?'],
      ['Hyperzeit ist hier bewusst nur als gekennzeichneter Demonstrationsmodus vorbereitet. Es werden noch keine belastbaren 6D-Vorhersagen behauptet.','Hyperzeit is intentionally provided here only as a labelled demonstration mode. No robust 6D predictions are claimed.'],
      ['Physikstatus: Der ΛCDM-Hintergrund übernimmt H₀, Ωₘ, ΩΛ und w aus dem zentralen UniverseLab-Modell. Das Alter wird numerisch aus der Friedmann-Gleichung integriert. Epochenbeschreibungen und Hintergrundgrafik sind didaktisch.','Physics status: the ΛCDM background inherits H₀, Ωₘ, ΩΛ and w from the central UniverseLab model. Age is numerically integrated from the Friedmann equation. Epoch descriptions and background graphics are didactic.'],
      ['Das Universum wird transparent; Photonen entkoppeln von Materie und bilden die kosmische Hintergrundstrahlung.','The universe becomes transparent; photons decouple from matter and form the cosmic microwave background.'],
      ['Ein extrem heißes, dichtes Universum, in dem Strahlung die Dynamik dominiert.','An extremely hot, dense universe in which radiation dominates the dynamics.'],
      ['Materie und Strahlung sind eng gekoppelt; freie Elektronen streuen Photonen fortlaufend.','Matter and radiation are tightly coupled; free electrons continuously scatter photons.'],
      ['Noch existieren kaum Sterne. Dichtefluktuationen wachsen gravitativ an.','There are hardly any stars yet. Density fluctuations grow gravitationally.'],
      ['Die ersten leuchtenden Objekte ionisieren zunehmend ihre Umgebung.','The first luminous objects increasingly ionize their surroundings.'],
      ['Galaxien, Gruppen und Filamente bilden das kosmische Netz.','Galaxies, groups and filaments form the cosmic web.'],
      ['Materie strukturiert den Kosmos, während die Expansion bereits beschleunigt.','Matter structures the cosmos while expansion is already accelerating.'],
      ['Vakuumenergie dominiert zunehmend; weit entfernte Strukturen entfernen sich immer schneller.','Vacuum energy increasingly dominates; distant structures recede ever faster.']
    ],
    'emergence.html':[
      ['ΛCDM · Epochen · lineares Wachstum','ΛCDM · epochs · linear growth'],['Kosmologische Zeitreihen','Cosmological time series'],['Lineare Strukturbildung','Linear structure formation'],['Kosmologische Epochen','Cosmological epochs'],
      ['Abweichung der Näherung','approximation deviation'],['dominante Komponente','dominant component'],['Expansionsregime','expansion regime'],['Beschleunigungsbeginn','onset of acceleration'],
      ['Zufallsuniversum','Random universe'],['Urknall-Keim','Big Bang seed'],['Symmetriebruch','Symmetry breaking'],['Gleiterfeld','Glider field'],
      ['Geschwindigkeit','Speed'],['Schritte pro Sekunde','steps per second'],['Anfangsdichte','initial density'],['Fluktuation','fluctuation'],
      ['Physikalisch: ΛCDM','Physical: ΛCDM'],['Heuristische Gitterexpansion','Heuristic grid expansion'],['Expansion aus','Expansion off'],['Zeitverstärkung','time amplification'],['Expansionsstärke','expansion strength'],['CSV exportieren','Export CSV'],['App installieren','Install app'],
      ['Die Wachstumsrechnung ist die skalenunabhängige lineare GR-Gleichung für drucklose Materie auf einem homogenen ΛCDM-Hintergrund. Sie ist nicht für Strahlungsperturbationen, nichtlineare Strukturen, baryonische Rückkopplung oder 6D-Modifikationen gültig. Die Zellgitterdarstellung bleibt davon getrennt.','The growth calculation is the scale-independent linear GR equation for pressureless matter on a homogeneous ΛCDM background. It is not valid for radiation perturbations, nonlinear structure, baryonic feedback, or 6D modifications. The cellular-grid representation remains separate from it.']
    ],
    'universe3d.html':[
      ['3D Cosmic Flight · räumliche Kosmologie','3D Cosmic Flight · spatial cosmology'],['kosmische Zeit','cosmic time'],['Flugtempo','flight speed'],['Flug','Flight'],['Kosmisches Netz','Cosmic web'],['Zeitreise','Time travel'],['Modelle','Models'],['Alter','Age'],
      ['Epochen besitzen eigene Populationen, Bewegungsregime und Morphologien. Die Szene ist wissenschaftlich inspiriert, aber keine direkte N‑Körper-Simulation.','Epochs have distinct populations, motion regimes and morphologies. The scene is scientifically inspired, but it is not a direct N-body simulation.'],
      ['Dunkles Z.','Dark Ages'],['Galaxien','Galaxies']
    ]
  };
  const target=page.replace(/\.html$/, '-en.html');
  const canonical=ROOT+target;
  const de=ROOT+page;
  function injectMeta(html){
    html=html.replace(/<link\s+rel=["']canonical["'][^>]*>/gi,'').replace(/<link\s+rel=["']alternate["'][^>]*hreflang=["'](?:de|en|x-default)["'][^>]*>/gi,'');
    const meta='\n<link rel="canonical" href="'+canonical+'">\n<link rel="alternate" hreflang="de" href="'+de+'">\n<link rel="alternate" hreflang="en" href="'+canonical+'">\n<link rel="alternate" hreflang="x-default" href="'+de+'">\n<meta name="ul-curated-translation" content="de-canonical; en-curated; presentation-only">\n';
    return html.replace('</head>',meta+'</head>');
  }
  function translate(html){
    const pairs=(MAPS[page]||[]).concat(COMMON).sort((a,b)=>b[0].length-a[0].length);
    for(const [from,to] of pairs) html=html.split(from).join(to);
    html=html.replace(/href=["']\.\/about\.html["']/g,'href="./about-en.html"')
             .replace(/href=["']\.\/journey\.html["']/g,'href="./journey-en.html"')
             .replace(/href=["']\.\/emergence\.html["']/g,'href="./emergence-en.html"')
             .replace(/href=["']\.\/universe3d\.html["']/g,'href="./universe3d-en.html"')
             .replace(/href=["']\.\/research-status\.html["']/g,'href="./research-status-en.html"')
             .replace(/href=["']\.\/index\.html["']/g,'href="./index-en.html"')
             .replace(/href=["']\.\/compare(?:-safe)?\.html["']/g,'href="./compare-en.html"');
    return injectMeta(html);
  }
  const fallback='<main style="max-width:780px;margin:12vh auto;padding:24px;font:16px/1.6 system-ui;color:#eef1ff;background:#101326;border-radius:18px"><h1>UniverseLab · Curated English edition</h1><p>The canonical German page could not be loaded. No scientific content has been modified.</p><p><a style="color:#bcb2ff" href="'+de+'">Open canonical German source</a></p></main>';
  fetch('./'+page,{cache:'no-cache'}).then(r=>{if(!r.ok)throw new Error('HTTP '+r.status);return r.text()}).then(html=>{document.open();document.write(translate(html));document.close()}).catch(()=>{document.body.innerHTML=fallback});
})();
