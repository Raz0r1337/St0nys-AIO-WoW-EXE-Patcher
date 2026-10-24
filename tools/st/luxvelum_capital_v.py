#!/usr/bin/env python3
# Nr. 32: Name mit grossem V - "LuxVelum" statt "Luxvelum" in Patcher-Texten, Kommentaren, Doku und im DLL-Namen in der
# Exe ("LuxVelum.dll", gleiche Laenge). Die Id 'luxvelum' und der Anker patch-luxvelum bleiben klein (gespeicherte
# Auswahl, Links). Set-ClientDate erkennt den Lader-Namen jetzt ohne Ruecksicht auf Gross/Klein (auch alte Exes).
# Aufruf: luxvelum_capital_v.py <Ordner des Zweigs> [Test-Skript ...]
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
def once(s, a, b, tag):
    assert s.count(a) == 1, (tag, a[:80], s.count(a)); return s.replace(a, b)
p = os.path.join(D, 'apply_patches.ps1'); s = rd(p, True)
s = once(s, 'Patch 0x2D1463 @(0x4C, 0x75, 0x78, 0x76, 0x65, 0x6C, 0x75, 0x6D, 0x2E, 0x64, 0x6C, 0x6C, 0x00)',
            'Patch 0x2D1463 @(0x4C, 0x75, 0x78, 0x56, 0x65, 0x6C, 0x75, 0x6D, 0x2E, 0x64, 0x6C, 0x6C, 0x00)', 'DLL-Name')
s = once(s, '-ceq "Luxvelum.dll`0") { return }', '-ieq "LuxVelum.dll`0") { return }', 'Set-ClientDate')
n = s.count('Luxvelum'); s = s.replace('Luxvelum', 'LuxVelum')
assert "Id = 'luxvelum'" in s and 'Luxvelum' not in s
wr(p, s, True); print('apply_patches.ps1: %d Stellen' % (n + 2))
for f in ('README.de.md', 'README.md', 'PATCHES.de.md', 'PATCHES.en.md'):
    q = os.path.join(D, 'docs', f); t = rd(q); n = t.count('Luxvelum')
    t = t.replace('Luxvelum', 'LuxVelum'); assert 'patch-luxvelum' in t
    wr(q, t); print('%s: %d Stellen' % (f, n))
for q in sys.argv[2:]:
    t = rd(q); n = t.count('Luxvelum'); wr(q, t.replace('Luxvelum', 'LuxVelum')); print('%s: %d Stellen' % (os.path.basename(q), n))
