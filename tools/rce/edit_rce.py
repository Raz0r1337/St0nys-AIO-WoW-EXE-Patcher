#!/usr/bin/env python3
# RCE-Fix v2 (Nr. 10): Eintrag, Nr.-11-Hinweis und Doku umbauen.
# Aufruf: edit_rce.py <Ordner mit apply_patches.ps1 und docs/>
import sys, os
root = sys.argv[1]

def edit_ps1(p, pairs):
    raw = open(p, 'rb').read()
    s = raw.decode('ascii')
    assert '\r\n' in s and '\n' not in s.replace('\r\n', '') and '\r' not in s.replace('\r\n', ''), 'nur CRLF erwartet'
    s = s.replace('\r\n', '\n')
    for a, b in pairs:
        assert s.count(a) == 1, (p, a[:80], s.count(a))
        s = s.replace(a, b)
    s.encode('ascii')
    open(p, 'wb').write(s.replace('\n', '\r\n').encode('ascii'))

def edit_md(p, pairs):
    s = open(p, encoding='utf-8').read()
    assert '\r' not in s
    for a, b in pairs:
        assert s.count(a) == 1, (p, a[:80], s.count(a))
        s = s.replace(a, b)
    open(p, 'w', encoding='utf-8', newline='\n').write(s)

# ---------------- apply_patches.ps1 ----------------
edit_ps1(os.path.join(root, 'apply_patches.ps1'), [
("""    @{ Id = 'rce'; Cat = 'security'; On = $false; BanRisk = $true
       Author = 'Robinsch'
       De = 'Remote Code Execution Exploit Fix'
       En = 'Remote code execution exploit fix'
       Code = {
        Patch 0x2A7 @(0xC0)
        Patch 0x3D9D7C @(0x90, 0x90)
    }}
""",
"""    @{ Id = 'rce'; Cat = 'security'; On = $false; BanRisk = $true; GameUntested = $true
       Author = 'Brady Russell (original by stoneharry / Robinsch)'
       De = 'Remote Code Execution Exploit Fix v2 [BETA]'
       En = 'Remote code execution exploit fix v2 [BETA]'
       Code = {
        # v2 = die 7 Stellen aus RCEPatcher v2.0 von Brady Russell plus
        # Robinschs Warden-Stelle aus v1. Eine Wow.exe mit v1 erkennt der
        # Patcher weiter als rce (0x2A7 und 0x3D9D7C sind eigene Stellen).
        # P0 (stoneharry, RCEPatcher v1): .zdata nicht mehr ausfuehrbar
        # (Sektions-Flags E0 -> C0).
        Patch 0x2A7 @(0xC0)
        # Robinsch: Warden-Module nicht aus dem lokalen Cache laden.
        Patch 0x3D9D7C @(0x90, 0x90)
        # P1-P6 (Brady Russell): weitere Angriffswege, die den .zdata-Fix
        # umgehen. Die Details veroeffentlicht der Autor erst nach einer
        # Schutzfrist - die Bytes sind so uebernommen, wie er sie verteilt.
        Patch 0x14A842 @(0x83, 0xFF, 0x50, 0x90, 0x90, 0x90)
        Patch 0x14A85C @(0x83, 0xF8, 0x50, 0x7F, 0x5F)
        Patch 0x364D40 @(0xEB)
        Patch 0x46B8E0 @(0x33, 0xC0, 0xC3)
        Patch 0x614A0 @(0x33, 0xC0, 0xC3)
        Patch 0x46AC43 @(0x90, 0x90)
    }}
"""),
("""    @{ Id = 'wardenoff'; Cat = 'security'; On = $false; Obsoletes = @('rce'); BanRisk = $true
""",
"""    @{ Id = 'wardenoff'; Cat = 'security'; On = $false; BanRisk = $true
"""),
("""        # Warden - Server mit aktivem Warden koennen deshalb kicken.
        # Macht den RCE-Fix (rce) ueberfluessig, beide zusammen schaden nicht.
""",
"""        # Warden - Server mit aktivem Warden koennen deshalb kicken.
        # Ersetzt den RCE-Fix (rce) seit dessen v2 nicht mehr: Ob das auch die
        # neuen Wege aus v2 abdeckt, ist offen, solange die Details nicht
        # veroeffentlicht sind - fuer den besten Schutz beide zusammen.
"""),
])

# ---------------- PATCHES.de.md ----------------
edit_md(os.path.join(root, 'docs', 'PATCHES.de.md'), [
("""**Remote Code Execution Exploit Fix** *(Nr. 10, Autor: Robinsch)* 🔴 **[unsicher]**

Schließt eine Sicherheitslücke, die Remote-Code-Ausführung über manipulierte
Pakete ermöglichen konnte: Die Sektion `.zdata` verliert ihr Ausführungsrecht,
und Warden-Module werden nicht mehr aus dem lokalen Cache geladen. Warden selbst
läuft weiter.

> [!WARNING]
> Öffentliche Server können die Änderung über Warden erkennen – auf
> öffentlichen Servern besteht Bann-Gefahr.

> [!NOTE]
> „Warden komplett abschalten“ (Nr. 11) schließt die Lücke ebenfalls und macht
> diesen Patch überflüssig. Wählst du beide, weist der Patcher darauf hin;
> schaden tun sie zusammen nicht.
""",
"""**Remote Code Execution Exploit Fix v2 [BETA]** *(Nr. 10, Autor: Brady Russell (original by stoneharry / Robinsch))* 🔴 **[unsicher - ingame ungetestet]**

Schließt Sicherheitslücken, über die ein bösartiger Server Code auf deinem PC
ausführen kann. v2 vereint zwei Fixes:

- **RCEPatcher v2.0** von Brady Russell
  ([bradyrussell/RCEPatcher2](https://github.com/bradyrussell/RCEPatcher2)),
  7 Stellen: Die erste nimmt der Sektion `.zdata` das Ausführungsrecht – das
  ist der klassische Fix aus RCEPatcher v1 von stoneharry. Die sechs weiteren
  schließen laut Autor zusätzliche Angriffswege, mit denen sich der
  `.zdata`-Fix umgehen lässt. Wie diese Wege funktionieren, veröffentlicht er
  erst nach einer Schutzfrist, damit vorher möglichst viele Spieler
  aktualisieren können.
- **Robinschs Fix** aus v1: Warden-Module werden nicht mehr aus dem lokalen
  Cache geladen. Warden selbst läuft weiter. RCEPatcher v2.0 enthält diese
  Stelle nicht.

> [!WARNING]
> Öffentliche Server können die Änderung über Warden erkennen – auf
> öffentlichen Servern besteht Bann-Gefahr.

> [!NOTE]
> Laut Brady Russell schalten die neuen Stellen ein paar ungenutzte oder selten
> genutzte Funktionen des Clients ab; Login, Charakterauswahl, Kampf, Chat und
> Addons sollten nicht betroffen sein. Er hat damit selbst aber noch wenig
> gespielt, und auch hier ist die v2 im Spiel noch ungetestet – deshalb
> [BETA]. Außerdem gibt es laut Autor sehr wahrscheinlich noch weitere
> Angriffswege. Am sichersten ist es, nur Servern zu vertrauen, die du kennst.

> [!NOTE]
> Eine `Wow.exe` mit dem bisherigen RCE-Fix (v1) erkennt der Patcher weiterhin
> als Nr. 10. Wählst du wieder dieselben Patches, bekommt sie die v2 mit
> „Neu patchen“ (`J`).

> [!NOTE]
> „Warden komplett abschalten“ (Nr. 11) schließt den Weg über Warden-Module
> vollständig. Ob das auch die neuen Wege aus v2 abdeckt, ist offen, solange
> die Details nicht veröffentlicht sind. Für den besten Schutz beide zusammen
> nutzen.
"""),
("""Patch ist das überhaupt nicht mehr möglich, auch nicht über künftige Tricks.
Macht den RCE-Fix (Nr. 10) überflüssig; beide zusammen schaden nicht, der
Patcher weist dann nur darauf hin.
""",
"""Patch ist das überhaupt nicht mehr möglich, auch nicht über künftige Tricks.
Ob das auch die neuen Wege aus dem RCE-Fix v2 (Nr. 10) abdeckt, ist offen,
solange deren Details nicht veröffentlicht sind. Für den besten Schutz beide
zusammen nutzen.
"""),
])

# ---------------- PATCHES.en.md ----------------
edit_md(os.path.join(root, 'docs', 'PATCHES.en.md'), [
("""**Remote code execution exploit fix** *(No. 10, Author: Robinsch)* 🔴 **[unsafe]**

Closes a vulnerability that could allow remote code execution through crafted
packets: the `.zdata` section loses its execute permission and Warden modules
are no longer loaded from the local cache. Warden itself keeps working.

> [!WARNING]
> Public servers can detect the change through Warden – there is a risk of a
> ban on public servers.

> [!NOTE]
> "Disable Warden completely" (No. 11) closes the hole as well and makes this
> patch unnecessary. If you select both, the patcher points it out; together
> they do no harm.
""",
"""**Remote code execution exploit fix v2 [BETA]** *(No. 10, Author: Brady Russell (original by stoneharry / Robinsch))* 🔴 **[unsafe - untested ingame]**

Closes security holes that let a malicious server run code on your PC. v2
combines two fixes:

- **RCEPatcher v2.0** by Brady Russell
  ([bradyrussell/RCEPatcher2](https://github.com/bradyrussell/RCEPatcher2)),
  7 places: the first one takes the execute permission away from the `.zdata`
  section – the classic fix from RCEPatcher v1 by stoneharry. According to
  the author, the other six close additional attack paths that get around
  the `.zdata` fix. He will publish how these paths work only after a
  disclosure period, so that as many players as possible can update first.
- **Robinsch's fix** from v1: Warden modules are no longer loaded from the
  local cache. Warden itself keeps working. RCEPatcher v2.0 does not contain
  this place.

> [!WARNING]
> Public servers can detect the change through Warden – there is a risk of a
> ban on public servers.

> [!NOTE]
> According to Brady Russell, the new places turn off a few unused or rarely
> used client features; login, character selection, combat, chat and addons
> should not be affected. He has not played much with them himself, though,
> and v2 has not been tested in game here either – hence [BETA]. The author
> also says there are almost certainly more attack paths. The safest option is
> to trust only servers you know.

> [!NOTE]
> The patcher still detects a `Wow.exe` with the previous RCE fix (v1) as
> No. 10. If you select the same patches again, "patch again" (`Y`) gives it
> v2.

> [!NOTE]
> "Disable Warden completely" (No. 11) closes the path through Warden modules
> entirely. Whether that also covers the new paths of v2 is open as long as
> the details are not published. For the best protection use both together.
"""),
("""that is no longer possible at all, including future tricks. Makes the RCE fix
(No. 10) unnecessary; both together do no harm, the patcher just points it out.
""",
"""that is no longer possible at all, including future tricks. Whether that also
covers the new paths of the RCE fix v2 (No. 10) is open as long as their
details are not published. For the best protection use both together.
"""),
])

# ---------------- README.de.md ----------------
edit_md(os.path.join(root, 'docs', 'README.de.md'), [
("""(Warden komplett abschalten ersetzt den RCE-Fix) und wenn gewählte Patches eine
""",
"""(der vollständige LUA-Unlock ersetzt den einfachen) und wenn gewählte Patches eine
"""),
("""| [10](PATCHES.de.md#patch-rce) | Remote Code Execution Exploit Fix | 🔴 **[unsicher]** | Robinsch | – | – | – |
""",
"""| [10](PATCHES.de.md#patch-rce) | Remote Code Execution Exploit Fix v2 [BETA] | 🔴 **[unsicher - ingame ungetestet]** | Brady Russell (original by stoneharry / Robinsch) | – | – | – |
"""),
("""    möglicherweise verbuggt: Nr. 25, 26, 31, 32, 47, 54, 65, 68, 69 und 85 (orange Warnung).
""",
"""    möglicherweise verbuggt: Nr. 10, 25, 26, 31, 32, 47, 54, 65, 68, 69 und 85 (orange Warnung).
"""),
("""- Danke an **Zendevve**, den Autor von CameraReforged, für die Idee hinter
  Visus – ShoulderCam.
""",
"""- Danke an **Zendevve**, den Autor von CameraReforged, für die Idee hinter
  Visus – ShoulderCam.
- Danke an **Brady Russell** für die Erlaubnis, seinen RCEPatcher v2.0 in den
  RCE-Fix v2 (Nr. [10](PATCHES.de.md#patch-rce)) zu übernehmen.
"""),
])

# ---------------- README.md ----------------
edit_md(os.path.join(root, 'docs', 'README.md'), [
("""CVar unlocks), when one patch makes another unnecessary (disabling Warden
completely replaces the RCE fix) and when selected patches carry a warning –
""",
"""CVar unlocks), when one patch makes another unnecessary (the complete LUA
unlock replaces the basic one) and when selected patches carry a warning –
"""),
("""| [10](PATCHES.en.md#patch-rce) | Remote code execution exploit fix | 🔴 **[unsafe]** | Robinsch | – | – | – |
""",
"""| [10](PATCHES.en.md#patch-rce) | Remote code execution exploit fix v2 [BETA] | 🔴 **[unsafe - untested ingame]** | Brady Russell (original by stoneharry / Robinsch) | – | – | – |
"""),
("""    possibly buggy: No. 25, 26, 31, 32, 47, 54, 65, 68, 69 and 85 (orange warning).
""",
"""    possibly buggy: No. 10, 25, 26, 31, 32, 47, 54, 65, 68, 69 and 85 (orange warning).
"""),
("""- Thanks to **Zendevve**, the author of CameraReforged, for the idea behind
  Visus – ShoulderCam.
""",
"""- Thanks to **Zendevve**, the author of CameraReforged, for the idea behind
  Visus – ShoulderCam.
- Thanks to **Brady Russell** for the permission to include his RCEPatcher
  v2.0 in the RCE fix v2 (No. [10](PATCHES.en.md#patch-rce)).
"""),
])
print('edits ok')
