#!/usr/bin/env python3
# Nr. 69 "Mehr Lichter" und Nr. 70 "Lichter bleiben an" ins Reforged-Preset (dev), Texte wie im frueheren Lichter-Zweig.
# Aufruf: reforged_lights.py <Ordner mit apply_patches.ps1 und docs/>
import sys, os
root = sys.argv[1]
REL = 'https://github.com/Raz0r1337/WoW-lights-patch-shader/releases'
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
p = os.path.join(root, 'apply_patches.ps1'); s = rd(p, True)
s = once(s, """# Lexara-Lader (Nr. 30, Patch sicher, DLL riskant). Im Menue mit R, ueber
# -Select reforged; gilt beim ersten Start und fuer neue Patches.
""", """# Lexara-Lader (Nr. 30, Patch sicher, DLL riskant) und die Licht-Patches
# Nr. 69 und 70 (im Spiel getestet, online noch nicht). Im Menue mit R, ueber
# -Select reforged; gilt beim ersten Start und fuer neue Patches.
""", 'comment')
s = once(s, """    'occluder', 'bluemoon', 'notransparency', 'hdportraits', 'iconsnap',
    'tracker', 'worldmap', 'castbars', 'charrandom', 'bubblerange',
""", """    'occluder', 'bluemoon', 'notransparency', 'hdportraits', 'iconsnap',
    'lights', 'lightstay',
    'tracker', 'worldmap', 'castbars', 'charrandom', 'bubblerange',
""", 'preset')
wr(p, s, True)
p = os.path.join(root, 'docs', 'README.de.md'); s = rd(p)
s = once(s, """Dazu kommt der Lexara-Lader (Nr. 30) für Stormhands HD-Schriften. Der Patch
selbst ist sicher, die `Lexara.dll` kann auf öffentlichen Servern aber erkannt
oder blockiert werden; ohne `Lexara.dll` im WoW-Ordner bewirkt er nichts.
""", """Dazu kommen der Lexara-Lader (Nr. 30) für Stormhands HD-Schriften und die
Licht-Patches Nr. 69 und 70. Beim Lexara-Lader ist der Patch selbst sicher,
die `Lexara.dll` kann auf öffentlichen Servern aber erkannt oder blockiert
werden; ohne `Lexara.dll` im WoW-Ordner bewirkt er nichts. Die Licht-Patches
sind im Spiel getestet, auf öffentlichen Servern aber noch nicht. Nr. 69
vergrößert die `Wow.exe` ebenfalls und wirkt erst mit den Shadern aus
[WoW-lights-patch-shader](%s).
""" % REL, 'readme de')
for a in ('| [69](PATCHES.de.md#patch-lights)', '| [70](PATCHES.de.md#patch-lightstay)'):
    row = [l for l in s.split('\n') if l.startswith(a)]; assert len(row) == 1
    s = once(s, row[0], once(row[0], '| St0ny | – | – | – |', '| St0ny | ✅ | – | – |', a), a)
wr(p, s)
p = os.path.join(root, 'docs', 'README.md'); s = rd(p)
s = once(s, """other servers may check the file size. On top of that comes the Lexara loader
(No. 30) for Stormhand's HD fonts. The patch itself is safe, but `Lexara.dll`
may be detected or blocked on public servers; without `Lexara.dll` in the WoW
folder it does nothing. The "Reforged" column in the
""", """other servers may check the file size. On top of that come the Lexara loader
(No. 30) for Stormhand's HD fonts and the light patches No. 69 and 70. For the
Lexara loader the patch itself is safe, but `Lexara.dll` may be detected or
blocked on public servers; without `Lexara.dll` in the WoW folder it does
nothing. The light patches are tested in game, but not yet on public servers.
No. 69 makes `Wow.exe` larger as well and only takes effect with the shaders
from [WoW-lights-patch-shader](%s). The "Reforged" column in the
""" % REL, 'readme en')
for a in ('| [69](PATCHES.en.md#patch-lights)', '| [70](PATCHES.en.md#patch-lightstay)'):
    row = [l for l in s.split('\n') if l.startswith(a)]; assert len(row) == 1
    s = once(s, row[0], once(row[0], '| St0ny | – | – | – |', '| St0ny | ✅ | – | – |', a), a)
wr(p, s)
print('ok')
