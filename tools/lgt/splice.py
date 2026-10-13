import sys
p, blk = sys.argv[1], sys.argv[2]
raw = open(p, 'rb').read(); s = raw.decode('ascii').replace('\r\n', '\n')
a = s.index('function Add-MoreLights {'); b = s.index('\n}\n', a) + 3
new = open(blk).read()
s = s[:a] + new + s[b:]
old = '''#    Original-Fehler, dass bei 4 Lichtern ausgerechnet das naechste fehlte.
# ============================================================'''
add = '''#    Original-Fehler, dass bei 4 Lichtern ausgerechnet das naechste fehlte.
#  - Boden (Shader-Weg, VA 0x7D0050): Der Boden-Shader bekommt je
#    Bodenstueck wie bisher Licht 1-3 in c28-c36. Vor deren Upload (VA
#    0x7D0292) gehen Licht 4 (4. Platz der Liste) und Licht 5-8 (Zusatzliste)
#    im Boden-Format nach VS c236-c250: Position Welt minus Kamera
#    ([0xCD8F5C], w = 1), Farbe (w = 0), Abschwaechung (w = 0); freie Plaetze
#    alles 0, Abschwaechung x = 1. Nur wenn die Karte mindestens 251
#    VS-Register hat. Fest an diesen Patch gekoppelt: Modelle und Boden
#    schreiben beide ab c236, jeder Shader liest direkt nach seinem Upload.
# ============================================================'''
assert s.count(old) == 1; s = s.replace(old, add)
s.encode('ascii')
open(p, 'wb').write(s.replace('\n', '\r\n').encode('ascii'))
