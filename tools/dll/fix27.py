# st0ny-dev: Nr. 27 (wow_optimize-Lader) -> [sicher - DLL riskant]
# Aufruf: python3 fix27.py <worktree>
import sys

wt = sys.argv[1]
PS = wt + '/apply_patches.ps1'
D = wt + '/docs/'

def rep(s, old, new, label):
    n = s.count(old)
    assert n == 1, '%s: %d Treffer' % (label, n)
    return s.replace(old, new)

# Skript (ASCII, CRLF bleibt erhalten)
raw = open(PS, encoding='ascii', newline='').read()
assert raw.count('\r\n') == raw.count('\n') and raw.count('\r\r') == 0
s = raw.replace('\r\n', '\n')
s = rep(s,
"    @{ Id = 'wowoptimize'; Cat = 'dll'; On = $false; BanRisk = $true; GameUntested = $true\n",
"    @{ Id = 'wowoptimize'; Cat = 'dll'; On = $false; DllRisky = $true\n", 'wowoptimize Flags')
open(PS, 'w', encoding='ascii', newline='').write(s.replace('\n', '\r\n'))

def rd(fn):
    t = open(D + fn, encoding='utf-8', newline='').read()
    assert '\r' not in t
    return t

def wr(fn, t):
    open(D + fn, 'w', encoding='utf-8', newline='').write(t)

def row(t, md, pid, old, new, label):
    lines = t.split('\n')
    hit = [i for i, l in enumerate(lines) if l.startswith('| [') and '(%s#patch-%s)' % (md, pid) in l]
    assert len(hit) == 1, label
    assert lines[hit[0]].count(old) == 1, label + ' Badge'
    lines[hit[0]] = lines[hit[0]].replace(old, new)
    return '\n'.join(lines)

# README.de.md
t = rd('README.de.md')
t = row(t, 'PATCHES.de.md', 'wowoptimize', '| 🔴 **[unsicher - ingame ungetestet]** |', '| 🟡 **[sicher - DLL riskant]** |', 'de Zeile')
t = rep(t, "    11, 23–25, 27, 43, 44, 47–52, 76 und 84–88 (rote Warnung).\n",
           "    11, 23–25, 43, 44, 47–52, 76 und 84–88 (rote Warnung).\n", 'de unsicher')
t = rep(t, "    möglicherweise verbuggt: Nr. 25–27, 30, 31, 46, 53 und 64 (orange Warnung).\n",
           "    möglicherweise verbuggt: Nr. 25, 26, 30, 31, 46, 53 und 64 (orange Warnung).\n", 'de ingame')
t = rep(t, "    auf öffentlichen Servern erkannt oder blockiert werden kann: Nr. 28 und 29\n",
           "    auf öffentlichen Servern erkannt oder blockiert werden kann: Nr. 27–29\n", 'de DLL')
wr('README.de.md', t)

# README.md
t = rd('README.md')
t = row(t, 'PATCHES.en.md', 'wowoptimize', '| 🔴 **[unsafe - untested ingame]** |', '| 🟡 **[safe - DLL risky]** |', 'en Zeile')
t = rep(t, "    27, 43, 44, 47–52, 76 and 84–88 (red warning).\n",
           "    43, 44, 47–52, 76 and 84–88 (red warning).\n", 'en unsafe')
t = rep(t, "    possibly buggy: No. 25–27, 30, 31, 46, 53 and 64 (orange warning).\n",
           "    possibly buggy: No. 25, 26, 30, 31, 46, 53 and 64 (orange warning).\n", 'en ingame')
t = rep(t, "    detected or blocked on public servers: No. 28 and 29 (yellow note). Only\n",
           "    detected or blocked on public servers: No. 27–29 (yellow note). Only\n", 'en DLL')
wr('README.md', t)

# PATCHES.de.md
t = rd('PATCHES.de.md')
t = rep(t, "*(Nr. 27, Autor: St0ny)* 🔴 **[unsicher - ingame ungetestet]**\n",
           "*(Nr. 27, Autor: St0ny)* 🟡 **[sicher - DLL riskant]**\n", 'de Kopf')
t = rep(t,
"> [!CAUTION]\n"
"> Laut dem Autor von wow_optimize wertet **Warmane** die DLL als verbotene\n"
"> Software – die Folge ist ein **dauerhafter Bann**. Auf **WoW Circle** führt\n"
"> sie zum Disconnect. Nur auf Servern verwenden, die das erlauben.\n",
"> [!CAUTION]\n"
"> Der Patch selbst ist sicher, er lädt nur eine DLL, die hier nicht enthalten\n"
"> ist. Die geladene `wow_optimize.dll` kann aber auf öffentlichen Servern\n"
"> erkannt oder blockiert werden: Laut dem Autor von wow_optimize wertet\n"
"> **Warmane** die DLL als verbotene Software – die Folge ist ein **dauerhafter\n"
"> Bann**. Auf **WoW Circle** führt sie zum Disconnect. Nur auf Servern\n"
"> verwenden, die das erlauben.\n", 'de Kasten')
wr('PATCHES.de.md', t)

# PATCHES.en.md
t = rd('PATCHES.en.md')
t = rep(t, "*(No. 27, Author: St0ny)* 🔴 **[unsafe - untested ingame]**\n",
           "*(No. 27, Author: St0ny)* 🟡 **[safe - DLL risky]**\n", 'en Kopf')
t = rep(t,
"> [!CAUTION]\n"
"> According to the author of wow_optimize, **Warmane** treats the DLL as\n"
"> prohibited software – the result is a **permanent ban**. On **WoW Circle** it\n"
"> gets you disconnected. Only use it on servers that allow it.\n",
"> [!CAUTION]\n"
"> The patch itself is safe, it only loads a DLL that is not included here.\n"
"> The loaded `wow_optimize.dll`, however, may be detected or blocked on public\n"
"> servers: according to the author of wow_optimize, **Warmane** treats the DLL\n"
"> as prohibited software – the result is a **permanent ban**. On **WoW Circle**\n"
"> it gets you disconnected. Only use it on servers that allow it.\n", 'en Kasten')
wr('PATCHES.en.md', t)
print('fix27 OK')
