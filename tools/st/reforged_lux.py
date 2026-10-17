#!/usr/bin/env python3
# Lux-Lader (Nr. 31) ins Preset "Reforged" - neben dem Lexara-Lader (Nr. 30), der schon drin ist.
# Patcher: $PRESET_REFORGED + Kommentar; README DE/EN: Spalte "Reforged" bei Nr. 31 und der Absatz zum Preset.
# PATCHES bleibt: die Preset-Zuordnung steht nur in der README.
# Aufruf: reforged_lux.py <Ordner> <Nr. Mehr Lichter> <Nr. Lichter bleiben an> <Nr. 1-3 der Exe-vergroessernden Patches, z.B. 9,66,67>
import sys, os
D, NL, NS, G = sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4].split(',')
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
    ("# Warmane getestet (Nr. %s, %s und %s vergroessern die Wow.exe); dazu der\n"
     "# Lexara-Lader (Nr. 30, Patch sicher, DLL riskant) und die Licht-Patches\n"
     "# Nr. %s und %s (im Spiel und online getestet, sicher; Nr. %s vergroessert\n"
     "# die Wow.exe ebenfalls). Im Menue mit R, ueber -Select reforged; gilt beim\n"
     "# ersten Start und fuer neue Patches.\n" % (G[0], G[1], G[2], NL, NS, NL),
     "# Warmane getestet (Nr. %s, %s und %s vergroessern die Wow.exe); dazu der\n"
     "# Lexara- und der Lux-Lader (Nr. 30 und 31, Patch sicher, DLL riskant; Lexara\n"
     "# laedt Lux ohnehin mit, der Lux-Lader auch ohne Lexara) und die\n"
     "# Licht-Patches Nr. %s und %s (im Spiel und online getestet, sicher; Nr. %s\n"
     "# vergroessert die Wow.exe ebenfalls). Im Menue mit R, ueber -Select\n"
     "# reforged; gilt beim ersten Start und fuer neue Patches.\n" % (G[0], G[1], G[2], NL, NS, NL)),
    ("    'glue', 'lexara',\n", "    'glue', 'lexara', 'lux',\n"),
], crlf=True)
def row31(s, tag):
    lines = s.split('\n'); hit = [i for i, l in enumerate(lines) if l.startswith('| [31](%s#patch-lux) |' % tag)]
    assert len(hit) == 1, hit; l = lines[hit[0]]
    assert l.endswith(' | – | – | – |'), l[-40:]
    lines[hit[0]] = l[:-len(' | – | – | – |')] + ' | ✅ | – | – |'
    return '\n'.join(lines)
p = os.path.join(D, 'docs', 'README.de.md'); s = row31(rd(p), 'PATCHES.de.md'); wr(p, s)
edit(os.path.join('docs', 'README.de.md'), [
    ("Dazu kommen der Lexara-Lader (Nr. 30) für Stormhands HD-Schriften und die\n"
     "Licht-Patches Nr. %s und %s. Beim Lexara-Lader ist der Patch selbst sicher,\n"
     "die `Lexara.dll` kann auf öffentlichen Servern aber erkannt oder blockiert\n"
     "werden; ohne `Lexara.dll` im WoW-Ordner bewirkt er nichts. Die Licht-Patches\n"
     "sind im Spiel und online getestet und sicher. Nr. %s vergrößert die\n"
     "`Wow.exe` ebenfalls und wirkt erst mit den Shadern aus\n" % (NL, NS, NL),
     "Dazu kommen der Lexara-Lader (Nr. 30) für Stormhands HD-Schriften, der\n"
     "Lux-Lader (Nr. 31) für die Schulterkamera LuxShoulderCam und die\n"
     "Licht-Patches Nr. %s und %s. Bei den beiden Ladern ist der Patch selbst\n"
     "sicher, die geladene DLL kann auf öffentlichen Servern aber erkannt oder\n"
     "blockiert werden; ohne die DLL im WoW-Ordner bewirken sie nichts. Lexara\n"
     "lädt die `LuxShoulderCam.dll` selbst mit, der Lux-Lader lädt sie auch ohne\n"
     "Lexara – beide zusammen schaden nicht. Die Licht-Patches sind im Spiel und\n"
     "online getestet und sicher. Nr. %s vergrößert die `Wow.exe` ebenfalls und\n"
     "wirkt erst mit den Shadern aus\n" % (NL, NS, NL)),
])
p = os.path.join(D, 'docs', 'README.md'); s = row31(rd(p), 'PATCHES.en.md'); wr(p, s)
edit(os.path.join('docs', 'README.md'), [
    ("other servers may check the file size. On top of that come the Lexara loader\n"
     "(No. 30) for Stormhand's HD fonts and the light patches No. %s and %s. For the\n"
     "Lexara loader the patch itself is safe, but `Lexara.dll` may be detected or\n"
     "blocked on public servers; without `Lexara.dll` in the WoW folder it does\n"
     "nothing. The light patches are tested in game and online and are safe.\n"
     "No. %s makes `Wow.exe` larger as well and only takes effect with the shaders\n" % (NL, NS, NL),
     "other servers may check the file size. On top of that come the Lexara loader\n"
     "(No. 30) for Stormhand's HD fonts, the Lux loader (No. 31) for the\n"
     "LuxShoulderCam shoulder camera and the light patches No. %s and %s. For both\n"
     "loaders the patch itself is safe, but the loaded DLL may be detected or\n"
     "blocked on public servers; without the DLL in the WoW folder they do nothing.\n"
     "Lexara loads `LuxShoulderCam.dll` by itself, the Lux loader also loads it\n"
     "without Lexara – both together do no harm. The light patches are tested in\n"
     "game and online and are safe. No. %s makes `Wow.exe` larger as well and only\n"
     "takes effect with the shaders\n" % (NL, NS, NL)),
])
print('reforged lux ok')
