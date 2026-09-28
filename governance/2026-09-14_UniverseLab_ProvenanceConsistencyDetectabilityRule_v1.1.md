# UniverseLab: Provenienz-, Konsistenz- und Nachweisbarkeitsregel v1.1

Kennung: UL-PKNR-v1.1
Überarbeitung: 2026-09-15  
Beschlussdatum: 2026-09-14  
Fachlicher Beschluss: USER_RATIFIED_METHOD_RULE  
Integrationsstatus: REVIEW_CANDIDATE_SEE_PULL_REQUEST_NOT_A_MERGE_CLAIM  
Physical gate effect: NONE  
Physical evidence effect: NONE  
Solver authorized: false

## 1. Beschluss und Geltung

Der Nutzer hat am 14.09.2026 den zuvor formulierten Prüfablauf ausdrücklich als verbindliche Provenienz-, Konsistenz- und Nachweisbarkeitsregel für künftige UniverseLab-Evaluierungen übernommen. Dieses Dokument hält den fachlichen Beschluss fest. Die lokale Vorgängerfassung v1.0 dokumentiert einen blockierten Schreibversuch. Diese Fassung v1.1 bereitet die erneute Repository-Integration vor. Der tatsächliche Integrations- und Reviewzustand ist am Pull Request und Commit zu prüfen; weder ein bereits erfolgter Merge noch globale automatische Durchsetzung werden durch den Dokumenttext behauptet.

Die Regel gilt entlang HPVS -> HZT-M0 -> HZT-Full und symmetrisch für Referenzmodelle und Alternativmodelle. Sie autorisiert keine physikalische Ausführung, keinen Backend-Import, keine AuthorizationDecision und keinen SingleUseGrant. Sie ist auch keine kryptographische Autoritätsattestierung.

## 2. Übernommener Regelkern

> Ein Modellzweig darf erst dann als durch Beobachtungen gestützt bezeichnet werden, wenn seine Datenprovenienz, seine physikalische Identität und seine Vorhersagekette bis zur verwendeten Messgröße dokumentiert sind. Alle für den beanspruchten Gültigkeitsbereich notwendigen beobachtbaren Konsequenzen sind gemeinsam zu prüfen. Ein guter Teilfit darf einen belastbaren Widerspruch nicht verdecken. Eine Nichtdetektion erhält Ausschlusswirkung nur bei quantifizierter Nachweisbarkeit und kontrollierten Zusatzannahmen. Fehlende Herleitung oder fehlende Empfindlichkeit bedeutet offene Prüfung, nicht Bestätigung und nicht Widerlegung.

## 3. Verbindlicher Prüfablauf

### P1: Quellen- und Datenprovenienz

Aussage und Messprodukt benötigen Quelle, Version, Datenkennung und nach Möglichkeit Prüfsumme. Versions-, Beobachtungs-, Publikations- und Abrufdatum werden getrennt geführt. Nicht erreichbare Primärquellen bleiben nicht verifiziert. Ein Abruffehler beweist weder Nichtexistenz noch wissenschaftliche Widerlegung.

Kalibrierung, Apertur- und Hintergrundbehandlung, Quellzuordnung, Fensterung, Filter, Rauschmodell und Kovarianzen werden produktbezogen dokumentiert. Pixel-/Strain-Messprodukte, rekonstruierte Wellenformen und modellkonditionierte Posterioren sind unterschiedliche Datenebenen. GR-gestützte Verarbeitung wird konkret geprüft, nicht pauschal als Signallöschung unterstellt.

### P2: Modellidentität und Gültigkeit

Wirkung, Signatur, Freiheitsgrade, Quellen, Topologie, Randdomäne, Erhaltungsgrößen und Näherungsregime müssen zur beanspruchten Aussage passen. Gemeinsame Bulkfunktionen identifizieren nicht automatisch verschiedene globale Quellen- und Randmodelle. Ein Kontrollbenchmark ist kein freigegebener physikalischer Hintergrund.

### P3: Notwendige Vorhersagen

Ein Ausschlusskanal benötigt eine nachvollziehbar hergeleitete Signalerwartung im bezeichneten Parameterbereich. Topologie allein erzwingt weder ein Gegenbild noch ein Echo. Ein guter Schattenradiusfit ersetzt keine übrigen notwendigen Folgerungen. Fehlende Herleitung ist ein offener Test, kein bestandenes Veto.

### P4: Nachweisbarkeit

Vorhersage, Instrumentantwort und tatsächlich eingesetzte Suchpipeline werden gemeinsam geprüft. Detektionsstatistik, Schwelle, Suchraum und Fehlerkontrolle werden vor der Entscheidung festgelegt. Injection-Recovery setzt vor derjenigen Verarbeitung ein, deren Empfindlichkeit beurteilt werden soll.

p_det(theta, eta) = P(T >= T_star | H, theta, eta).

Für genau diese binäre Entscheidung gilt:

P(Nichtdetektion | H, theta, eta) = 1 - p_det(theta, eta).

Eine nominelle Amplitude oder ein optimaler Signal-Rausch-Abstand allein ist kein empirisch validierter p_det-Wert. Kalibrierung, Anregung, Kopplungen und weitere Zusatzparameter werden mitgeführt. Marginalisierte Ergebnisse und Robustheitsprüfungen über einen angegebenen zulässigen Zusatzparameterbereich sind unterschiedlich zu berichten. Ein universeller p_det- oder Konfidenz-Grenzwert für alle Analysen wird nicht festgelegt.

### P5: Gemeinsame Gegenprüfung

Geteilte Pixel, Kalibrierungen, Linsenmodelle, Templates und bereits verwendete Bandflüsse erzeugen Abhängigkeiten. Bereits im Fit enthaltene Daten dürfen nicht als unabhängige Bayes-Faktoren wiederverwendet werden. Verschiedene Methoden auf denselben Daten sind nicht automatisch unabhängige Experimente.

Jeder Ausschluss nennt Parameterbereich, Zusatzannahmen und statistisches Verfahren. Nachträgliche Modelländerungen erhalten eine neue Version und neue Prüfung; sie dürfen nicht stillschweigend einen bereits untersuchten Modellpunkt ersetzen.

## 4. Explizite fachliche Präzisierungen: eigener Vorschlag, nicht zusätzliche Nutzer-Ratifikation

Die folgenden Erläuterungen sind getrennt vom übernommenen Regelkern dokumentiert und bleiben als redaktionelle Präzisierungen für den Repository-Review erkennbar.

1. Der Ausdruck „deterministisch“ in der Nutzerzusammenfassung darf nicht unbemerkt mit jeder gültigen physikalischen Vorhersage gleichgesetzt werden. Auch eine modellbegründete Wahrscheinlichkeitsverteilung kann geprüft werden. Beispielsweise folgt aus einem vollständig angegebenen Poisson-Modell P(N=0 | nu)=exp(-nu). Unbekannte Anregung oder frei eingesetzte Verteilungen bleiben hingegen offene Lücken.
2. Eine noch nicht hergeleitete reale HZT-Love-/QNM-/Echo-Vorhersage bleibt OFFEN. Ein bereits nachgewiesener Kettenregel-, Dimensions- oder Vorfaktorfehler bleibt für genau den geprüften Ausdruck widerlegt. Der offene Status einer gesamten Vorhersagekette setzt einzelne bewiesene Fehler nicht zurück.
3. Die Ratifikation reproduziert oder bestätigt keinen EH-3-Spin-2-Nullmodus. Dafür bleiben Originaloperator, normierte Profile, Randdaten und Konvergenznachweise erforderlich.
4. Eine positive homogene Zweifeld-Massenmatrix ist weder vollständige Hintergrundstabilität noch Ghostfreiheit. Ein marginaler Eigenwert ist nicht automatisch tachyonisch. Glatte Pole erzwingen nicht allgemein verschwindenden Stress auf einer codimension-1-Kappe; das gilt erst bei zusätzlich geforderter vollständig glatter Verklebung.

## 5. Revisions- und Statushygiene

Fehlendes Prüfresultat ist kein bestandenes Prüfresultat. Unzureichende Empfindlichkeit liefert keinen belastbaren Ausschluss dieses Bereichs. Ein Pipelinefehler entwertet zunächst die davon abhängigen Aussagen, nicht automatisch die gesamte Theorie. Ein ausgeschlossener Modellpunkt ist nicht automatisch eine ausgeschlossene Modellfamilie.

Eine revidierte Quelle löst eine Prüfung ihrer abhängigen Aussagen aus. Historische Fassungen und ihre frühere Verwendung bleiben nachvollziehbar. Statusmarker werden einer ausdrücklich bezeichneten Aussage und ihrem Gültigkeitsbereich zugeordnet.

## 6. A1-Watch: bekannter Ausgangsstand und erlaubte Meldungen

Objekt: A1 hinter MACS J0308.9+2645. Bekannte photometrische Neubewertung: ungefähr z=4,4 auf ungefähr z=1,4, nicht z=10. Diese bekannte Reanalyse wird nicht erneut als Neuigkeit gemeldet.

Der Nutzer nennt arXiv:2607.12129v2 vom 07.08.2026. Diese Versionsdatierung und die Detailzahlen sind bei dieser Übergabe nicht direkt primärquellenverifiziert: arXiv-Abs/HTML/PDF-Abrufe waren nicht verfügbar. Die autornahe Veröffentlichung vom 28.08.2026 stützt die korrigierte Interpretation, ersetzt aber keine verifizierte Versionshistorie. Der übermittelte Plausibilitätsbereich 1,2-1,7 ist entsprechend als übermittelt markiert.

Nur drei Ergebnisgruppen lösen eine neue Meldung aus:

- neue spektroskopische Rotverschiebungsergebnisse, einschließlich Widerlegung;
- publizierte dedizierte A1-Linsenmodelle mit materiell neuem Ergebnis;
- neue oder materiell veränderte Gegenbild- beziehungsweise Vergrößerungsbefunde.

Wiederholte Presseberichte, bloße Versionsnummern, reine Metadatenänderungen und temporäre Abruffehler sind keine neuen astronomischen Ergebnisse. Identische Resultate werden publikationsübergreifend dedupliziert. Ein A1-Befund hat keine automatische HZT-Evidenz- oder Gatewirkung.

Quellen zur Nachprüfung:

- https://arxiv.org/abs/2607.12129v2
- https://skycr.org/2026/08/28/universe-today-gravitational-arc-macs-j0308/

## 7. Physikalische Gates: Referenz statt Überschreiben

Basis-Commit: e444d84efeb398e582a9ca84d61e0c55931ae586.

Gelesene Gatequelle:

registry/2026-09-14_UniverseLab_ULSH05_WP1D2_KinematicInvariantProjectorSolvabilityPreflight_v0.1.json

Dieser Methodenvertrag ist kein physikalischer Gate-Snapshot. Verbraucher müssen den vollständigen einschlägigen kanonischen Vertrag lesen und spätere Änderungen an ihrer eigenen Provenienz prüfen. Kein geerbtes Gate wird durch eine verkürzte Auswahl ersetzt oder angehoben.

Physical gate effect = NONE. Physical evidence effect = NONE. Solver authorized = false.

## 8. Technischer Umfang

Die Begleitregistry dokumentiert Regeln, Pflichtfelder und Quellenbezüge. Sie ist keine automatische wissenschaftliche Bewertungsmaschine und kein nachgerüsteter Validator sämtlicher früherer Datenprodukte. Fachlicher Beschluss, technische Integration, QA und physikalische Evidenz bleiben getrennt.

## 9. Änderungsprovenienz v1.1

Keine Änderung des übernommenen Regelkerns, der P1–P5-Kriterien oder der ausdrücklich gesonderten fachlichen Präzisierungen. Geändert sind Versions-/Publikationsmetadaten und Repository-Pfade. Die A1-Angaben in Abschnitt 6 bleiben der historische Ausgangsstand der Übergabe vom 14.09.2026; sie wurden für diese Dokumentintegration nicht neu astronomisch verifiziert.

Lokale Vorgängerdatei: `2026-09-14_UniverseLab_ProvenanceConsistencyDetectabilityRule_v1.0.md`.

Begleitvertrag: `../registry/2026-09-14_UniverseLab_ProvenanceConsistencyDetectabilityContract_v1.1.json`.
