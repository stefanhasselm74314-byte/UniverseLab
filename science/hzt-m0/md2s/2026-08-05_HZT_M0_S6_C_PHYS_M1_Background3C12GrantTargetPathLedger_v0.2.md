# HZT-M0-S6-C-PHYS-M1 — Background-3C12 Grant and Target-Path Ledger v0.2

**Datum:** 2026-08-05  
**Track:** `MD2S-R1-C-PHYS`  
**Block:** `C-PHYS-R1.0-BACKGROUND-3C12_SINGLE_USE_GRANT_AND_TARGET_PATH_RELEASE_IMPLEMENTATION_ONLY`

## 1. Zweck

Background-3C12 implementiert zwei bislang fehlende technische Schichten, jedoch ausschließlich als nichtoperative Kontrollen:

1. ein synthetisches Single-Use-Grant-Schema mit atomarer Zustandsmaschine,
2. einen quellgebundenen, aber nicht ausführbaren Zielpfad für den eingefrorenen CP01R1-Run mit
   \(a_F=\tfrac14\).

Weder ein operatives Grant noch ein physischer Solverpfad wird freigegeben.

## 2. Pre-Audit-Korrektur

Die Target-Path-Basisschicht v0.1 erzeugte standardmäßig

```text
not_before = issued_at - 1 s
```

obwohl der Grant-Vertrag verlangt:

```text
issued_at <= not_before < expires_at
```

Vor dem ersten Audit- oder Kontrolllauf wurde deshalb append-only die v0.2-Schicht eingeführt. Für sofort gültige synthetische Grants gilt nun:

```text
not_before = issued_at
```

Unverändert bleiben:

- das Zielmodell,
- \(a_F=\tfrac14\),
- der eingefrorene Payload,
- die sieben Seeds,
- die 35 Schedule-Einträge,
- alle Backend-, Dependency-, Resource- und Resultatschema-Bindungen,
- sämtliche No-Execution-Firewalls.

## 3. Grant-Identität

Ein synthetisches Grant enthält mindestens:

- Grant-ID und 128-Bit-Nonce,
- Entscheidungsidentität,
- `operative=false`,
- Ausstellungs-, Not-Before- und Ablaufzeit,
- Target-Run-ID und Zielwert \(a_F=\tfrac14\),
- vollständige Digestbindung,
- genau eine erlaubte synthetische Aktion,
- eine explizite Liste verbotener physischer Aktionen,
- einen SHA-256-Integritätsdigest über das kanonische Grant ohne Digestfeld.

Die Bindungsmenge umfasst:

```text
checkout commit
Target-Release-Paket
eingefrorener Payload
Seed-Spezifikation
35-Einträge-Schedule
Primärquelle
Primärbasis
Independent-Quelle
Dependency-Lock
Resource-Policy
Resultatschema
```

## 4. Atomare Single-Use-Zustandsmaschine

```text
ISSUED_SYNTHETIC
    ↓ atomare Reservierung
RESERVED_SYNTHETIC
    ↓ genau ein irreversibler Abschluss
CONSUMED_SYNTHETIC_SUCCESS
CONSUMED_SYNTHETIC_FAILURE
CONSUMED_SYNTHETIC_TIMEOUT
CONSUMED_SYNTHETIC_SIGNAL
CONSUMED_SYNTHETIC_CRASH
```

Sobald das Grant-Verzeichnis atomar reserviert wurde, ist jeder zweite Reservierungsversuch ein Replay. Das gilt auch nach Fehler, Timeout, Signal und Crash.

Die Zustände werden ausschließlich in externen temporären Kontrollverzeichnissen erzeugt. Repository-Grantinstanzen und Repository-Konsumakten sind verboten.

## 5. Target-Path-Preflight

Die Prüfungen erfolgen in folgender Reihenfolge:

1. rekursive Ablehnung aller Kontroll- und \(a_F=0\)-Overrides,
2. Grant-Feldmenge und `operative=false`,
3. Grant-Integritätsdigest,
4. Zeitfenster,
5. exakte Bindungsmenge,
6. Target-Run-ID und \(a_F=\tfrac14\),
7. Payload-, Seed- und Schedule-Bindung,
8. Backend-, Dependency-, Resource- und Resultatschema-Digests,
9. atomare Grant-Reservierung,
10. ausschließlich synthetisches Worker-Outcome,
11. atomarer Terminalzustand.

Jede Ablehnung vor Punkt 9 darf keinerlei State-Verzeichnis erzeugen.

## 6. Synthetische Kontrollmatrix

Geprüft werden:

- Erfolg,
- expliziter Fehler,
- Timeout,
- Signal,
- Crash,
- parallele Doppelreservierung mit exakt einem Gewinner,
- Replay nach jedem Terminalzustand,
- abgelaufenes Grant,
- noch nicht gültiges Grant,
- Digest- und Bindungsmanipulation,
- `operative=true`,
- Kontroll-Override,
- falsche Target-Identität und falscher Schedule,
- fehlende und unbekannte Grantfelder.

## 7. Harte Firewalls

```text
Backendimport                 = VERBOTEN
CP01R1                        = VERBOTEN
Zielsolve a_F=1/4             = VERBOTEN
Newton                        = VERBOTEN
Shooting/Root                 = VERBOTEN
operatives Grant              = VERBOTEN
physisches Ergebnisartefakt   = VERBOTEN
automatische Autorisierung    = VERBOTEN
```

## 8. Wissenschaftliche Aussagegrenze

Ein PASS darf nur bedeuten:

> Die nichtoperative Grant- und Target-Path-Kontrollschicht ist digestgebunden, atomar, replay-sicher und gegen Kontroll-Overrides abgeschottet.

Nicht ableitbar sind:

- CP01R1-Ausführungsberechtigung,
- Existenz eines physischen Hintergrunds,
- Zielpfad-Korrektheit unter realem Backendimport,
- Existenz, Eindeutigkeit oder Fredholm-Eigenschaft,
- Stabilität oder Ghostfreiheit,
- K1-D, K1-E oder physische Evidenz.

## 9. Nächster zulässiger Block bei PASS

`C-PHYS-R1.0-BACKGROUND-3C13_GRANT_AND_TARGET_PATH_AUTHORIZATION_REVIEW_ONLY`

3C13 bleibt read-only und darf weder ein operatives Grant erzeugen noch ein Backend importieren oder CP01R1 starten.
