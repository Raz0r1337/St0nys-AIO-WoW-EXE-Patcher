#!/usr/bin/env python3
# Nr. 69 "Mehr Lichter": Hinweis, dass ein Release von WoW-lights-patch-shader gebraucht wird (wie bei awesome_wotlk, Lexara usw.).
# Aufruf: needs_shader.py <Ordner mit apply_patches.ps1 und docs/>
import sys, os
root = sys.argv[1]
REPO = 'https://github.com/Raz0r1337/WoW-lights-patch-shader'; REL = REPO + '/releases'
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
s = once(s, """       NoteDe = 'sichtbar nur mit neuen Shadern oder mit fixedFunction 1'
       NoteEn = 'visible only with new shaders or with fixedFunction 1'
""", """       NoteDe = 'benoetigt WoW-lights-patch-shader - patch-5.MPQ.zip aus dem Release in den Data-Ordner entpacken'
       NoteEn = 'requires WoW-lights-patch-shader - unpack patch-5.MPQ.zip from the release into the Data folder'
       Url = '%s'
""" % REL, 'ps1 note')
wr(p, s, True)
p = os.path.join(root, 'docs', 'PATCHES.de.md'); s = rd(p)
s = once(s, """Er ist die Exe-Grundlage für neue Shader, die mehr Lichter darstellen.
""", """Er ist die Exe-Grundlage für neue Shader, die mehr Lichter darstellen.

**Benötigt** die neuen Shader aus
[WoW-lights-patch-shader](%s): `patch-5.MPQ.zip`
von der [Releases-Seite](%s)
in den `Data`-Ordner des Spiels entpacken, sodass es
`Data\\patch-5.MPQ\\Shaders\\Vertex\\vs_3_0\\Diffuse_T1.bls` gibt. Die Shader
wirken nur mit `gxApi d3d9` und `fixedFunction 0`. Ohne sie sind die
zusätzlichen Lichter nur im Weg ohne Shader (`fixedFunction 1`) zu sehen.
""" % (REPO, REL), 'patches de')
wr(p, s)
p = os.path.join(root, 'docs', 'PATCHES.en.md'); s = rd(p)
s = once(s, """the exe groundwork for new shaders that show more lights.
""", """the exe groundwork for new shaders that show more lights.

**Requires** the new shaders from
[WoW-lights-patch-shader](%s): unpack
`patch-5.MPQ.zip` from the [releases page](%s)
into the game's `Data` folder so that
`Data\\patch-5.MPQ\\Shaders\\Vertex\\vs_3_0\\Diffuse_T1.bls` exists. The shaders
only take effect with `gxApi d3d9` and `fixedFunction 0`. Without them the
extra lights are only visible on the path without shaders (`fixedFunction 1`).
""" % (REPO, REL), 'patches en')
wr(p, s)
for f, a, b in (('README.de.md', '*(sichtbar nur mit neuen Shadern oder mit fixedFunction 1)*',
                 '*(benötigt [WoW-lights-patch-shader](%s) – `patch-5.MPQ.zip` aus dem Release in den `Data`-Ordner entpacken)*' % REL),
                ('README.md', '*(visible only with new shaders or with fixedFunction 1)*',
                 '*(requires [WoW-lights-patch-shader](%s) – unpack `patch-5.MPQ.zip` from the release into the `Data` folder)*' % REL)):
    p = os.path.join(root, 'docs', f); s = rd(p)
    s = once(s, a, b, f)
    wr(p, s)
print('ok')
