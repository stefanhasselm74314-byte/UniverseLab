# HZT‑M0‑S6 C‑PHYS‑M1 — Background‑3C4 Execution Runner Ledger v0.1

## Status

`IMPLEMENTED_AUDIT_ONLY_EXECUTION_NOT_AUTHORIZED`

Dieser Block implementiert ausschließlich die fehlende kontrollierte
Ausführungsschicht. Er führt **keinen** Newton‑, Shooting‑, Jacobian‑ oder
Zielmodelllauf aus.

## Implementierte Komponenten

1. **Quellhashbindung**  
   Der Runner bildet für ein geschlossenes Pfadinventar SHA‑256‑Hashes und
   daraus einen kanonischen Paketdigest. Ein späteres Grant‑Artefakt muss genau
   diesen Digest, `CP01R1` und den eingefrorenen Run‑Payload‑Hash binden.

2. **Umgebungsattestierung**  
   Python‑Version, Plattform, Maschinenarchitektur, Dependency‑Versionen,
   Thread‑Umgebungsvariablen und Paketdigest werden maschinenlesbar erfasst.

3. **Ressourcenhülle**  
   Die eingefrorenen Zeit‑, Speicher‑, Thread‑ und Ergebnisgrößenlimits werden
   validiert. Für einen späteren Subprozess sind POSIX‑Adressraum‑ und
   CPU‑Limits sowie eine Ein‑Thread‑Umgebung implementiert.

4. **Atomarer Result Writer**  
   Es wird ausschließlich in ein neues Geschwister‑Stagingverzeichnis
   geschrieben. Alle JSON‑Artefakte sind kanonisch, gehasht und `fsync`‑bar.
   Erst danach ist ein atomarer Rename auf den finalen, nicht überschreibbaren
   Pfad zulässig.

5. **Abbruch‑ und Teilresultatprotokoll**  
   Ein Abbruch kann nur ein eindeutig als partiell markiertes Verzeichnis
   erzeugen. Der finale Resultatpfad bleibt unberührt.

6. **Geschlossene Klassifikationsmaschine**  
   Nur die im Result‑Schema eingefrorenen Klassen sind zulässig. Eine
   numerische Kandidatenklasse bleibt diagnostisch und besitzt keine
   physikalische Evidenzwirkung.

7. **Primär‑ und unabhängiger Root‑Adapter**  
   Beide Adapter existieren, verlangen aber ein typisiertes, hashgebundenes
   `ExecutionCapability`. Ohne erfolgreich verifiziertes append‑only Grant wird
   kein Backend importiert und keine numerische Funktion aufgerufen.

## Auditpfade

- `audit`: Vertrags‑, Hash‑, Umgebungs‑ und Ressourcenprüfung; keine Backendimporte.
- `self-test`: Writer, Abbruchprotokoll und Klassifikation ausschließlich in
  einem Betriebssystem‑Temporärverzeichnis; keine Repositoryartefakte.
- `run`: ohne zukünftiges Grant sofortiger Exitcode `73`, vor Backendimport und
  vor Erzeugung des Resultatpfads.

## Nicht bewiesen

- keine Hintergrundexistenz,
- keine Eindeutigkeit,
- kein Fredholm‑Resultat,
- kein Kontinuums‑Jacobian,
- keine Stabilität oder Ghostfreiheit,
- keine K1‑D‑Freigabe,
- keine K1‑E‑Zulässigkeit,
- keine physikalische Bestätigung.

## Gatewirkung

```text
BACKGROUND_3C4_EXECUTION_PACKAGE = IMPLEMENTED_AUDIT_ONLY_NO_EXECUTION
BACKGROUND_3C_EXECUTION          = NOT_AUTHORIZED
PHYSICAL_BACKGROUND              = NOT_ESTABLISHED
R1.1                             = BLOCKED
R1.2                             = BLOCKED
K1-D                             = NOT_RELEASED
K1-E                             = NOT_ADMISSIBLE
physical_evidence_effect         = NONE
```

## Nächster zulässiger Block

`C-PHYS-R1.0-BACKGROUND-3C5_EXECUTION_PACKAGE_AUTHORIZATION_REVIEW_ONLY`

Auch dieser Folgeschritt darf nicht automatisch ausführen. Er muss das
vollständige Paket, seinen aktuellen Digest und die verbleibenden fachlichen
Freigabebedingungen neu prüfen.
