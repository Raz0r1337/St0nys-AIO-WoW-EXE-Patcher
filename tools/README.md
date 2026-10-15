# Werkzeuge (nur st0ny-dev)

Hilfsskripte aus den Claude-Sitzungen, mit denen die Patches entwickelt und
getestet wurden: Code-Generatoren, Emulator, Testsuiten, Analyse-Skripte und
Notizen. Sie gehören nicht zum Patcher und kommen **nie nach `st0ny-main`**.

## Wichtige Ordner

| Ordner | Inhalt |
|---|---|
| `ol2/` | Umrandung Nr. 68: Generator `outline10.py` und `mkoutline10.py` (erzeugt `outline10_ps.txt`), Assembler `psasm.py`, Tests `test_outline10.py`, Integrationstests `itest_*.sh`, Parser-Prüfung `parse.ps1` |
| `gen/` | gemeinsame Bausteine: `asmgen.py`, `emitps.py`, Lichter-Generator `lights.py`/`mklights.py`, Glyphen-Fix, Gedrückt halten |
| `lgt/` | „Mehr Lichter“ mit Boden-Teil (st0ny-dev-lights): `lights.py`, `mklights.py`, `test_ter.py`, `test_lights.py` |
| `tm/` | Emulator `emu2.py` (Unicorn) und Tests einzelner Patches |
| `raychk/` | Test der Kollisionsstrahlen gegen das echte TraceLine |
| `rmcam/run_suite.sh` | Suite: alle Presets, jeder Patch einzeln, Erkennung, Zurücknehmen |
| `rce/`, `rcechk/` | RCE-Fix v2: Umstiegstest v1 → v2 (`itest_rce.sh`) und die Verträglichkeitsprüfung aller Patches: Stellen in den geänderten Funktionen (`sites_in_rce.py`), Sprünge/Aufrufe aus neuem Code (`xref_rce.py`), 32-Bit-Zeiger (`ptrscan.py`), Aufrufgraph bis Tiefe N (`cgdepth.py`), Verweise in `.zdata` (`zdata_refs.py`); `rce/itest_rce_old.sh` prüft den Umstieg in Zweigen ohne „Neu patchen“-Abfrage |
| `rcb/` | `port_rce_v2.py`: überträgt die RCE-v2-Änderungen aus dev über Anker in einen anderen Zweig (Skript und Doku) |
| `dllchk/`, `awl/` | Emulation aller DLL-Lader: lädt jeder Lader seine DLL (auch zusammen mit Nr. 10)? `emu_loaders.py <Wow.exe>` |
| `agent_*/` | Analysen und Prototypen der Hilfs-Agenten, mit Berichten (`*.md`) |
| `lights/`, `outline/` | Analyse-Skripte und Berichte zu Lichtern, Shadern, Rahmen und d3d9 |
| Rest | einmalige Bearbeitungs- und Prüfskripte (z. B. `e*.py`, `readme_*.py`), Commit-Nachrichten `msg*.txt`, Notizen |

## Nicht enthalten

- die `Wow.exe` (Original 3.3.5a 12340, SHA256 `AA63A575…E88CB8`) und PowerShell 7,
- fremde Repos und Bibliotheken, Disassembler-Ausgaben, Kopien des Patchers, Logs,
- der CameraReforged-Port (bis zur Erlaubnis entfernt).

## Benutzung

Die Skripte haben die Pfade der Sitzung fest eingetragen, in der sie
entstanden sind. `relocate.sh` passt sie in einer Kopie an:

    cp -r tools /arbeit/tools
    tools/relocate.sh /arbeit/tools /pfad/zur/Wow.exe [/pfad/zu/pwsh]

Voraussetzungen: Python 3.11 mit `unicorn` 2, `capstone` 5 und `keystone`,
für die `.sh`-Tests außerdem PowerShell 7 (`pwsh`).

`collect.py` sammelt die Werkzeuge aus einem Arbeitsordner wieder ein, mit
denselben Filtern: `collect.py <Arbeitsordner> --copy <Ziel>`.
