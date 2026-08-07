# ULSH-04 · Constraint / Dirac-Bergmann Solver Roadmap v1.0

## Ziel
Die vollständige Zwangsstruktur des relevanten 6D-/reduzierten perturbativen Systems bestimmen und die tatsächlichen physikalischen Freiheitsgrade isolieren.

## Aktueller Stand
`PLANNED`. Architekturziel; keine geschlossene kanonische Constraint-Pipeline ist freigegeben.

## Upstream
ULSH-01 MD2S-BVP sowie die kanonische Parentwirkung.

## Fehlende Theorie-/Vertragsarbeit
1. ADM-/Hamilton-Zerlegung mit eindeutiger Zeitwahl festlegen.
2. Kanonische Variablen und Momenta herleiten.
3. Primärzwänge bestimmen.
4. Konsistenzbedingungen und Sekundär-/höhere Zwänge ableiten.
5. Poisson-/Dirac-Algebra und first-/second-class Klassifikation schließen.

## Implementierungspakete
1. Symbolisches Constraint-Register erzeugen.
2. Constraint-Poissonmatrix aufbauen.
3. Rang und Klassifikation kontrolliert bestimmen.
4. Gauge-Generatoren und eliminierbare Variablen ausweisen.
5. Physische Freiheitsgrade sektorspezifisch zählen und exportieren.

## Kontrollen
- bekannte GR-/Maxwell-Testsysteme
- künstlich first-class/second-class gemischte Systeme
- Rangstabilität unter zulässigen Variablentransformationen
- Dimensions- und Vorzeichenhygiene

## Pflicht-Outputs
Kanonische Variablen, Primär-/Sekundärzwänge, Constraint-Matrix, Klassen, Gauge-Generatoren, Dirac-Matrix falls nötig, physischer DOF-Count und Provenienz.

## Freigabegate
`CLOSED_CONSTRAINT_ALGEBRA_AND_PHYSICAL_DOF_COUNT_ON_RELEASED_BACKGROUND`.

## Downstream
ULSH-05 Perturbation, ULSH-06 Ghost, ULSH-08 Radion und ULSH-14 MOND/RAR.
