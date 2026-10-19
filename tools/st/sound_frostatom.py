#!/usr/bin/env python3
# Sound-Patch: den 126-Kanal-Teil FrostAtom zuordnen - Liste in PATCHES DE/EN und Kommentar im Patcher.
# Den Autor selbst setzt set_author.py (sound "St0ny / FrostAtom").
# Aufruf: sound_frostatom.py <Ordner>
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
def edit(rel, a, b, crlf=False):
    p = os.path.join(D, rel); s = rd(p, crlf); assert s.count(a) == 1, (rel, a[:60], s.count(a)); wr(p, s.replace(a, b), crlf)
edit('apply_patches.ps1', "        Patch 0x0C77C2 @(",
     "        # Hardware-Limit der Sound-Kanaele auf 126 (FrostAtom)\n        Patch 0x0C77C2 @(", crlf=True)
edit(os.path.join('docs', 'PATCHES.de.md'), "- Sound-Kanal-Hardware-Limit auf 126 angehoben\n",
     "- Sound-Kanal-Hardware-Limit auf 126 angehoben (von FrostAtom)\n")
edit(os.path.join('docs', 'PATCHES.en.md'), "- Sound channel hardware limit raised to 126\n",
     "- Sound channel hardware limit raised to 126 (by FrostAtom)\n")
print('sound: 126 Kanaele -> FrostAtom')
