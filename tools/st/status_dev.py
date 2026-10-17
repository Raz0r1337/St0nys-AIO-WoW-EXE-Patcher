#!/usr/bin/env python3
# Status in st0ny-dev vor dem Uebertrag nach main: Nr. 10 (RCE v2) "riskant - online ungetestet" statt
# "ingame ungetestet", Nr. 69/70 (Lichter) online getestet und sicher - jeweils ohne [BETA].
# Aufruf: status_dev.py <dev-Ordner>
import sys, os, re
D = sys.argv[1]
def rd(p, crlf=False):
    s = open(p, encoding='utf-8', newline='').read()
    if crlf: assert '\r\n' in s; s = s.replace('\r\n', '\n')
    else: assert '\r' not in s
    return s
def wr(p, s, crlf=False):
    if crlf: s.encode('ascii'); s = s.replace('\n', '\r\n')
    open(p, 'w', encoding='utf-8', newline='').write(s)
def once(s, a, b, tag=''):
    assert s.count(a) == 1, (tag, a[:90], s.count(a)); return s.replace(a, b)
# ---------------- apply_patches.ps1 ----------------
p = os.path.join(D, 'apply_patches.ps1'); s = rd(p, True)
for a, b in [
    ("    @{ Id = 'rce'; Cat = 'security'; On = $false; Blocked = $true; GameUntested = $true\n",
     "    @{ Id = 'rce'; Cat = 'security'; On = $false; Blocked = $true; PublicUntested = $true\n"),
    ("       De = 'Remote Code Execution Exploit Fix v2 [BETA]'\n", "       De = 'Remote Code Execution Exploit Fix v2'\n"),
    ("       En = 'Remote code execution exploit fix v2 [BETA]'\n", "       En = 'Remote code execution exploit fix v2'\n"),
    ("    @{ Id = 'lights'; Cat = 'graphics'; On = $false; GrowsExe = $true; PublicUntested = $true\n",
     "    @{ Id = 'lights'; Cat = 'graphics'; On = $false; GrowsExe = $true\n"),
    ("(Grundlage fuer neue Shader) [BETA]'\n", "(Grundlage fuer neue Shader)'\n"),
    ("(groundwork for new shaders) [BETA]'\n", "(groundwork for new shaders)'\n"),
    ("    @{ Id = 'lightstay'; Cat = 'graphics'; On = $false; PublicUntested = $true\n",
     "    @{ Id = 'lightstay'; Cat = 'graphics'; On = $false\n"),
    ("ausserhalb des Bildes ist [BETA]'\n", "ausserhalb des Bildes ist'\n"),
    ("source is off-screen [BETA]'\n", "source is off-screen'\n"),
    ("# Nr. 69 und 70 (im Spiel getestet, online noch nicht). Im Menue mit R, ueber\n# -Select reforged; gilt beim ersten Start und fuer neue Patches.\n",
     "# Nr. 69 und 70 (im Spiel und online getestet, sicher; Nr. 69 vergroessert\n# die Wow.exe ebenfalls). Im Menue mit R, ueber -Select reforged; gilt beim\n# ersten Start und fuer neue Patches.\n"),
]: s = once(s, a, b, 'ps1')
wr(p, s, True)
# ---------------- PATCHES ----------------
BETA_DE = "> [!WARNING]\n> **BETA** – dieser Patch ist noch in der Testphase und deshalb vorerst nur in\n> den dev-Zweigen, nicht in `st0ny-main`.\n\n"
BETA_EN = "> [!WARNING]\n> **BETA** – this patch is still being tested and is therefore only in the dev\n> branches for now, not in `st0ny-main`.\n\n"
p = os.path.join(D, 'docs', 'PATCHES.de.md'); s = rd(p)
assert s.count(BETA_DE) == 2; s = s.replace(BETA_DE, '')
for a, b in [
    ("**Remote Code Execution Exploit Fix v2 [BETA]** *(Nr. 10, Autor: Brady Russell (original by stoneharry / Robinsch))* 🟠 **[riskant - ingame ungetestet]**",
     "**Remote Code Execution Exploit Fix v2** *(Nr. 10, Autor: Brady Russell (original by stoneharry / Robinsch))* 🟠 **[riskant - online ungetestet]**"),
    ("> Addons sollten nicht betroffen sein. Er hat damit selbst aber noch wenig\n> gespielt, und auch hier ist die v2 im Spiel noch ungetestet – deshalb\n> [BETA]. Außerdem gibt es laut Autor sehr wahrscheinlich noch weitere\n> Angriffswege. Am sichersten ist es, nur Servern zu vertrauen, die du kennst.\n",
     "> Addons sollten nicht betroffen sein. Er hat damit selbst aber noch wenig\n> gespielt. Im Spiel ist die v2 hier inzwischen getestet, auf öffentlichen\n> Servern noch nicht. Außerdem gibt es laut Autor sehr wahrscheinlich noch\n> weitere Angriffswege. Am sichersten ist es, nur Servern zu vertrauen, die du\n> kennst.\n"),
    ("**Mehr Lichter: 8 statt 4 Punktlichter (Grundlage für neue Shader) [BETA]** *(Nr. 69, Autor: St0ny)* 🟠 **[online ungetestet - Exe wird größer]**",
     "**Mehr Lichter: 8 statt 4 Punktlichter (Grundlage für neue Shader)** *(Nr. 69, Autor: St0ny)* 🟡 **[sicher - Exe wird größer]**"),
    ("> Zum Testen am besten zusammen mit Nr. 70: Ohne ihn schaltet der Client das\n> Licht einer Quelle ab,",
     "> Am besten zusammen mit Nr. 70 nutzen: Ohne ihn schaltet der Client das\n> Licht einer Quelle ab,"),
    ("**Lichter bleiben an, wenn ihre Quelle außerhalb des Bildes ist [BETA]** *(Nr. 70, Autor: St0ny)* 🟠 **[online ungetestet]**",
     "**Lichter bleiben an, wenn ihre Quelle außerhalb des Bildes ist** *(Nr. 70, Autor: St0ny)* 🟢 **[sicher]**"),
]: s = once(s, a, b, 'PATCHES.de')
wr(p, s)
p = os.path.join(D, 'docs', 'PATCHES.en.md'); s = rd(p)
assert s.count(BETA_EN) == 2; s = s.replace(BETA_EN, '')
for a, b in [
    ("**Remote code execution exploit fix v2 [BETA]** *(No. 10, Author: Brady Russell (original by stoneharry / Robinsch))* 🟠 **[risky - untested ingame]**",
     "**Remote code execution exploit fix v2** *(No. 10, Author: Brady Russell (original by stoneharry / Robinsch))* 🟠 **[risky - untested online]**"),
    ("> should not be affected. He has not played much with them himself, though,\n> and v2 has not been tested in game here either – hence [BETA]. The author\n> also says there are almost certainly more attack paths. The safest option is\n> to trust only servers you know.\n",
     "> should not be affected. He has not played much with them himself, though.\n> v2 has since been tested in game here, but not yet on public servers. The\n> author also says there are almost certainly more attack paths. The safest\n> option is to trust only servers you know.\n"),
    ("**More lights: 8 instead of 4 point lights (groundwork for new shaders) [BETA]** *(No. 69, Author: St0ny)* 🟠 **[untested online - exe grows]**",
     "**More lights: 8 instead of 4 point lights (groundwork for new shaders)** *(No. 69, Author: St0ny)* 🟡 **[safe - exe grows]**"),
    ("> Best tested together with No. 70: without it,", "> Best used together with No. 70: without it,"),
    ("**Lights stay on when their source is off-screen [BETA]** *(No. 70, Author: St0ny)* 🟠 **[untested online]**",
     "**Lights stay on when their source is off-screen** *(No. 70, Author: St0ny)* 🟢 **[safe]**"),
]: s = once(s, a, b, 'PATCHES.en')
wr(p, s)
# ---------------- README ----------------
p = os.path.join(D, 'docs', 'README.de.md'); s = rd(p)
for a, b in [
    ("| Remote Code Execution Exploit Fix v2 [BETA] | 🟠 **[riskant - ingame ungetestet]** |",
     "| Remote Code Execution Exploit Fix v2 | 🟠 **[riskant - online ungetestet]** |"),
    ("(Grundlage für neue Shader) [BETA] *(benötigt", "(Grundlage für neue Shader) *(benötigt"),
    ("in den `Data`-Ordner entpacken)* | 🟠 **[online ungetestet - Exe wird größer]** |",
     "in den `Data`-Ordner entpacken)* | 🟡 **[sicher - Exe wird größer]** |"),
    ("| Lichter bleiben an, wenn ihre Quelle außerhalb des Bildes ist [BETA] | 🟠 **[online ungetestet]** |",
     "| Lichter bleiben an, wenn ihre Quelle außerhalb des Bildes ist | 🟢 **[sicher]** |"),
    ("kann zu Kick/Bann führen: Nr. 26, 31, 32, 42, 47, 54, 65, 68–70, 74, 77–79 und 86\n",
     "kann zu Kick/Bann führen: Nr. 10, 26, 31, 32, 42, 47, 54, 65, 68, 74, 77–79 und 86\n"),
    ("möglicherweise verbuggt: Nr. 10, 25, 26, 31, 32, 47, 54, 65, 68 und 86 (orange Warnung).",
     "möglicherweise verbuggt: Nr. 25, 26, 31, 32, 47, 54, 65, 68 und 86 (orange Warnung)."),
    ("Die Licht-Patches\nsind im Spiel getestet, auf öffentlichen Servern aber noch nicht. Nr. 69\nvergrößert die `Wow.exe` ebenfalls",
     "Die Licht-Patches\nsind im Spiel und online getestet und sicher. Nr. 69 vergrößert die\n`Wow.exe` ebenfalls"),
    ("Warnung tragen – rot bei Bann-Gefahr, orange bei Patches, die auf öffentlichen\nServern oder im Spiel noch ungetestet sind, und gelb bei vergrößerter\n`Wow.exe` (siehe [Hinweise](#hinweise)).",
     "Warnung tragen – rot bei Bann-Gefahr, orange bei Patches, die auf manchen\nServern geblockt werden oder auf öffentlichen Servern oder im Spiel noch\nungetestet sind, und gelb bei vergrößerter `Wow.exe` (siehe\n[Hinweise](#hinweise))."),
]: s = once(s, a, b, 'README.de')
wr(p, s)
p = os.path.join(D, 'docs', 'README.md'); s = rd(p)
for a, b in [
    ("| Remote code execution exploit fix v2 [BETA] | 🟠 **[risky - untested ingame]** |",
     "| Remote code execution exploit fix v2 | 🟠 **[risky - untested online]** |"),
    ("(groundwork for new shaders) [BETA] *(requires", "(groundwork for new shaders) *(requires"),
    ("into the `Data` folder)* | 🟠 **[untested online - exe grows]** |", "into the `Data` folder)* | 🟡 **[safe - exe grows]** |"),
    ("| Lights stay on when their source is off-screen [BETA] | 🟠 **[untested online]** |",
     "| Lights stay on when their source is off-screen | 🟢 **[safe]** |"),
    ("you kicked or banned: No. 26, 31, 32, 42, 47, 54, 65, 68–70, 74, 77–79 and 86\n",
     "you kicked or banned: No. 10, 26, 31, 32, 42, 47, 54, 65, 68, 74, 77–79 and 86\n"),
    ("possibly buggy: No. 10, 25, 26, 31, 32, 47, 54, 65, 68 and 86 (orange warning).",
     "possibly buggy: No. 25, 26, 31, 32, 47, 54, 65, 68 and 86 (orange warning)."),
    ("The light patches are tested in game, but not yet on public servers.\nNo. 69 makes",
     "The light patches are tested in game and online and are safe.\nNo. 69 makes"),
    ("red for ban risk, orange for patches that are still untested on public\nservers or in game, and yellow for a larger `Wow.exe` (see [Notes](#notes)).",
     "red for ban risk, orange for patches that get blocked on some servers or are\nstill untested on public servers or in game, and yellow for a larger\n`Wow.exe` (see [Notes](#notes))."),
]: s = once(s, a, b, 'README.en')
wr(p, s)
# Nr. 31 (Lux) ist seit der Umstellung "sicher - DLL riskant" - aus den beiden Ungetestet-Listen nehmen
for f, pairs in (('README.de.md', [("kann zu Kick/Bann führen: Nr. 10, 26, 31, 32, 42,", "kann zu Kick/Bann führen: Nr. 10, 26, 32, 42,"), ("möglicherweise verbuggt: Nr. 25, 26, 31, 32, 47,", "möglicherweise verbuggt: Nr. 25, 26, 32, 47,")]),
                 ('README.md', [("you kicked or banned: No. 10, 26, 31, 32, 42,", "you kicked or banned: No. 10, 26, 32, 42,"), ("possibly buggy: No. 25, 26, 31, 32, 47,", "possibly buggy: No. 25, 26, 32, 47,")])):
    p = os.path.join(D, 'docs', f); s = rd(p)
    for a, b in pairs: s = once(s, a, b, f)
    wr(p, s)
print('status ok')
