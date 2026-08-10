# ULSH Master Build Order Firewall v1.0

Der Master Build Order ist ausschließlich eine Planungs- und Orchestrierungsschicht.

- `ULSH-01` bleibt der primäre kritische Pfad.
- Vorbereitende Parallel-Lanes dürfen nur Herleitungen, Verträge und Manufactured Controls erzeugen.
- Ein abgeschlossenes Work Package erzeugt keine Solverfreigabe.
- Physische Downstream-Ausführung erfordert ein separat freigegebenes Upstream-Gate.
- `K1-D = NOT_RELEASED`.
- `K1-E = NOT_ADMISSIBLE`.
- `physical evidence effect = NONE`.

Diese Datei besitzt keinen Ausführungseffekt und darf nicht als Autorisierung für CP01R1 oder irgendeinen anderen physischen Solverlauf interpretiert werden.
