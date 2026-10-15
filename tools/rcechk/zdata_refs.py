#!/usr/bin/env python3
# Verweist neuer Patch-Code (Sprungziele, Aufrufe, Adressen) in die Sektion .zdata (VA 0xDD1000-0xDD2000)? P0 nimmt ihr das Ausfuehrungsrecht.
# Aufruf: zdata_refs.py <Original-Wow.exe> <gepatchte Wow.exe> <apply_patches.ps1>
import sys, struct, re, capstone
orig = open(sys.argv[1], 'rb').read(); pat = open(sys.argv[2], 'rb').read(); src = open(sys.argv[3]).read().replace('\r', '')
rows = [(m.group(1), int(m.group(2), 16), len(m.group(3)) // 2) for m in re.finditer(r'^(\w+);([0-9A-F]+);([0-9A-F]+);[01]$', src, re.M)]
ZA, ZB = 0xDD1000, 0xDD2000
def secs(d):
    e = struct.unpack_from('<I', d, 0x3C)[0]; n = struct.unpack_from('<H', d, e + 6)[0]; base = e + 24 + struct.unpack_from('<H', d, e + 20)[0]
    return [(d[base + 40 * i:base + 40 * i + 8].rstrip(b'\0').decode('latin1'),) + struct.unpack_from('<IIII', d, base + 40 * i + 8) for i in range(n)]
SP = secs(pat)
def off2va(o):
    for name, vs, va, rs, ra in SP:
        if ra <= o < ra + rs: return 0x400000 + va + (o - ra)
ranges = []; i = 0; n = len(orig)
while i < n:
    if pat[i] != orig[i]:
        j = i
        while j < n and pat[j] != orig[j]: j += 1
        ranges.append((max(i - 8, 0), j)); i = j
    else: i += 1
for name, vs, va, rs, ra in SP:
    if ra >= n: ranges.append((ra, ra + rs))
def owner(o):
    for id_, off, ln in rows:
        if off <= o < off + ln: return id_
    return next(('Sektion ' + s[0] for s in SP if s[4] <= o < s[4] + s[3] and s[4] >= n), '?')
md = capstone.Cs(capstone.CS_ARCH_X86, capstone.CS_MODE_32)
hits = set()
for a, b in ranges:
    va = off2va(a)
    if va is None: continue
    for ins in md.disasm(pat[a:b], va):
        for m in re.finditer(r'0x[0-9a-f]{6,8}', ins.op_str):
            v = int(m.group(0), 16)
            if ZA <= v < ZB: hits.add((owner(a + ins.address - va), '%X' % ins.address, ins.mnemonic + ' ' + ins.op_str))
    for o in range(a, b - 3):
        v = struct.unpack_from('<I', pat, o)[0]
        if ZA <= v < ZB: hits.add((owner(o), '%X' % o, 'Zeiger %X' % v))
print('Verweise in .zdata:', sorted(hits) or 'keine')
