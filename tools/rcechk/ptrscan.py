#!/usr/bin/env python3
# Sucht in allen von Patches geschriebenen Bytes (auch angehaengte Sektionen) nach 32-Bit-Zeigern in RCE-Funktionen.
# Aufruf: ptrscan.py <Original-Wow.exe> <gepatchte Wow.exe ohne Nr. 10> <apply_patches.ps1>
import sys, struct, re
orig = open(sys.argv[1], 'rb').read(); pat = open(sys.argv[2], 'rb').read(); src = open(sys.argv[3]).read().replace('\r', '')
rows = [(m.group(1), int(m.group(2), 16), len(m.group(3)) // 2) for m in re.finditer(r'^(\w+);([0-9A-F]+);([0-9A-F]+);[01]$', src, re.M)]
def fstart(o):
    for x in range(o, max(o - 0x4000, 0x400), -1):
        if orig[x:x + 3] == b'\x55\x8b\xec' and orig[x - 1] in (0xCC, 0xC3, 0x90): return x
def fend(o):
    for x in range(o + 1, o + 0x4000):
        if orig[x:x + 3] == b'\x55\x8b\xec' and orig[x - 1] in (0xCC, 0xC3, 0x90): return x
FR = sorted({(fstart(o) + 0x400C00, fend(o) + 0x400C00) for o in [0x14A842, 0x14A85C, 0x364D40, 0x46B8E0, 0x614A0, 0x46AC43, 0x3D9D7C]})
def secs(d):
    e = struct.unpack_from('<I', d, 0x3C)[0]; n = struct.unpack_from('<H', d, e + 6)[0]; base = e + 24 + struct.unpack_from('<H', d, e + 20)[0]
    return [(d[base + 40 * i:base + 40 * i + 8].rstrip(b'\0').decode('latin1'),) + struct.unpack_from('<IIII', d, base + 40 * i + 8) for i in range(n)]
ranges = []; i = 0; n = len(orig)
while i < n:
    if pat[i] != orig[i]:
        j = i
        while j < n and pat[j] != orig[j]: j += 1
        ranges.append((i, j)); i = j
    else: i += 1
for name, vs, va, rs, ra in secs(pat):
    if ra >= n: ranges.append((ra, ra + rs))
def owner(o):
    for id_, off, ln in rows:
        if off <= o < off + ln: return id_
    for name, vs, va, rs, ra in secs(pat):
        if ra <= o < ra + rs and ra >= n: return 'Sektion ' + name
    return '?'
hits = []
for a, b in ranges:
    for o in range(a, b - 3):
        v = struct.unpack_from('<I', pat, o)[0]
        if any(fa <= v < fb for fa, fb in FR):
            hits.append((hex(o), hex(v), owner(o)))
print('geschriebene Bereiche:', len(ranges), ' Zeiger in RCE-Funktionen:', [h for h in hits if h[2] != 'rce'] or 'keine')
