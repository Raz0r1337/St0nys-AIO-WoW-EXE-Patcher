#!/usr/bin/env python3
# Welche Patch-Stellen (Tabellenzeilen) liegen in Funktionen, die RCE-Fix v2 veraendert?
# Aufruf: sites_in_rce.py <Original-Wow.exe> <apply_patches.ps1> [...]
import sys, re
orig = open(sys.argv[1], 'rb').read()
def fstart(o):
    for x in range(o, max(o - 0x4000, 0x400), -1):
        if orig[x:x + 3] == b'\x55\x8b\xec' and orig[x - 1] in (0xCC, 0xC3, 0x90): return x
def fend(o):
    for x in range(o + 1, o + 0x4000):
        if orig[x:x + 3] == b'\x55\x8b\xec' and orig[x - 1] in (0xCC, 0xC3, 0x90): return x
SITES = [0x14A842, 0x14A85C, 0x364D40, 0x46B8E0, 0x614A0, 0x46AC43, 0x3D9D7C]
FR = sorted({(fstart(o), fend(o)) for o in SITES})
print('RCE-Funktionen (Dateioffsets):', ['%X-%X' % f for f in FR])
for p in sys.argv[2:]:
    src = open(p).read().replace('\r', '')
    rows = [(m.group(1), int(m.group(2), 16), len(m.group(3)) // 2) for m in re.finditer(r'^(\w+);([0-9A-F]+);([0-9A-F]+);[01]$', src, re.M)]
    hits = [(i, hex(o), n) for i, o, n in rows if i not in ('rce', 'pe', 'watermark') for a, b in FR if o < b and a < o + n]
    print('%s: %d Zeilen, in RCE-Funktionen: %s' % (p.split('/')[-2], len(rows), hits or 'keine'))
