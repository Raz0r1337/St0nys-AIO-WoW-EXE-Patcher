#!/usr/bin/env python3
# st0ny-dev-y38fix wie st0ny-dev (79f4ffd): Nr. 10 (RCE v2) "riskant - online ungetestet" statt "ingame ungetestet",
# ohne [BETA] (inzwischen in main); Orange-Legende nennt auch die geblockten Patches.
# Aufruf: status_y38.py <y38fix-Ordner>
import sys, os
D = sys.argv[1]
def rd(p, crlf=False):
    s = open(p, encoding='utf-8', newline='').read()
    if crlf: assert '\r\n' in s; s = s.replace('\r\n', '\n')
    else: assert '\r' not in s
    return s
def wr(p, s, crlf=False):
    if crlf: s.encode('ascii'); s = s.replace('\n', '\r\n')
    open(p, 'w', encoding='utf-8', newline='').write(s)
def edit(rel, pairs, crlf=False):
    p = os.path.join(D, rel); s = rd(p, crlf)
    for a, b in pairs:
        assert s.count(a) == 1, (rel, a[:90], s.count(a)); s = s.replace(a, b)
    wr(p, s, crlf)
edit('apply_patches.ps1', [
    ("    @{ Id = 'rce'; Cat = 'security'; On = $false; Blocked = $true; GameUntested = $true\n",
     "    @{ Id = 'rce'; Cat = 'security'; On = $false; Blocked = $true; PublicUntested = $true\n"),
    ("       De = 'Remote Code Execution Exploit Fix v2 [BETA]'\n", "       De = 'Remote Code Execution Exploit Fix v2'\n"),
    ("       En = 'Remote code execution exploit fix v2 [BETA]'\n", "       En = 'Remote code execution exploit fix v2'\n"),
], crlf=True)
edit(os.path.join('docs', 'PATCHES.de.md'), [
    ("**Remote Code Execution Exploit Fix v2 [BETA]** *(Nr. 10, Autor: Brady Russell (original by stoneharry / Robinsch))* 🟠 **[riskant - ingame ungetestet]**",
     "**Remote Code Execution Exploit Fix v2** *(Nr. 10, Autor: Brady Russell (original by stoneharry / Robinsch))* 🟠 **[riskant - online ungetestet]**"),
    ("> Addons sollten nicht betroffen sein. Er hat damit selbst aber noch wenig\n> gespielt, und auch hier ist die v2 im Spiel noch ungetestet – deshalb\n> [BETA]. Außerdem gibt es laut Autor sehr wahrscheinlich noch weitere\n> Angriffswege. Am sichersten ist es, nur Servern zu vertrauen, die du kennst.\n",
     "> Addons sollten nicht betroffen sein. Er hat damit selbst aber noch wenig\n> gespielt. Im Spiel ist die v2 hier inzwischen getestet, auf öffentlichen\n> Servern noch nicht. Außerdem gibt es laut Autor sehr wahrscheinlich noch\n> weitere Angriffswege. Am sichersten ist es, nur Servern zu vertrauen, die du\n> kennst.\n"),
])
edit(os.path.join('docs', 'PATCHES.en.md'), [
    ("**Remote code execution exploit fix v2 [BETA]** *(No. 10, Author: Brady Russell (original by stoneharry / Robinsch))* 🟠 **[risky - untested ingame]**",
     "**Remote code execution exploit fix v2** *(No. 10, Author: Brady Russell (original by stoneharry / Robinsch))* 🟠 **[risky - untested online]**"),
    ("> should not be affected. He has not played much with them himself, though,\n> and v2 has not been tested in game here either – hence [BETA]. The author\n> also says there are almost certainly more attack paths. The safest option is\n> to trust only servers you know.\n",
     "> should not be affected. He has not played much with them himself, though.\n> v2 has since been tested in game here, but not yet on public servers. The\n> author also says there are almost certainly more attack paths. The safest\n> option is to trust only servers you know.\n"),
])
edit(os.path.join('docs', 'README.de.md'), [
    ("| Remote Code Execution Exploit Fix v2 [BETA] | 🟠 **[riskant - ingame ungetestet]** |",
     "| Remote Code Execution Exploit Fix v2 | 🟠 **[riskant - online ungetestet]** |"),
    ("kann zu Kick/Bann führen: Nr. 26, 29, 39, 44, 51, 62, 68, 71–73 und 86\n",
     "kann zu Kick/Bann führen: Nr. 10, 26, 29, 39, 44, 51, 62, 68, 71–73 und 86\n"),
    ("möglicherweise verbuggt: Nr. 10, 25, 26, 29, 44, 51, 62 und 86 (orange Warnung).",
     "möglicherweise verbuggt: Nr. 25, 26, 29, 44, 51, 62 und 86 (orange Warnung)."),
    ("Warnung tragen – rot bei Bann-Gefahr, orange bei Patches, die auf öffentlichen\nServern oder im Spiel noch ungetestet sind, und gelb bei vergrößerter\n`Wow.exe` (siehe [Hinweise](#hinweise)).",
     "Warnung tragen – rot bei Bann-Gefahr, orange bei Patches, die auf manchen\nServern geblockt werden oder auf öffentlichen Servern oder im Spiel noch\nungetestet sind, und gelb bei vergrößerter `Wow.exe` (siehe\n[Hinweise](#hinweise))."),
])
edit(os.path.join('docs', 'README.md'), [
    ("| Remote code execution exploit fix v2 [BETA] | 🟠 **[risky - untested ingame]** |",
     "| Remote code execution exploit fix v2 | 🟠 **[risky - untested online]** |"),
    ("you kicked or banned: No. 26, 29, 39, 44, 51, 62, 68, 71–73 and 86\n",
     "you kicked or banned: No. 10, 26, 29, 39, 44, 51, 62, 68, 71–73 and 86\n"),
    ("possibly buggy: No. 10, 25, 26, 29, 44, 51, 62 and 86 (orange warning).",
     "possibly buggy: No. 25, 26, 29, 44, 51, 62 and 86 (orange warning)."),
    ("red for ban risk, orange for patches that are still untested on public\nservers or in game, and yellow for a larger `Wow.exe` (see [Notes](#notes)).",
     "red for ban risk, orange for patches that get blocked on some servers or are\nstill untested on public servers or in game, and yellow for a larger\n`Wow.exe` (see [Notes](#notes))."),
])
print('status y38 ok')
