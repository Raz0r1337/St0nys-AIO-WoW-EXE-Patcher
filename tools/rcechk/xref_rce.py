#!/usr/bin/env python3
# Welche unserer Patches springen in Funktionen, die RCE-Fix v2 (Nr. 10) veraendert?
# Aufruf: xref_rce.py <Original-Wow.exe> <gepatchte Wow.exe ohne Nr. 10> <apply_patches.ps1>
import sys, struct, re, capstone
orig = open(sys.argv[1], 'rb').read(); pat = open(sys.argv[2], 'rb').read()
src = open(sys.argv[3]).read().replace('\r', '')
ids = re.findall(r"^    @\{ Id = '(\w+)'; Cat", src, re.M)
rows = [(m.group(1), int(m.group(2), 16), len(m.group(3)) // 2) for m in re.finditer(r'^(\w+);([0-9A-F]+);([0-9A-F]+);[01]$', src, re.M)]
def secs(d):
    e = struct.unpack_from('<I', d, 0x3C)[0]; n = struct.unpack_from('<H', d, e + 6)[0]
    base = e + 24 + struct.unpack_from('<H', d, e + 20)[0]; out = []
    for i in range(n):
        o = base + 40 * i
        name = d[o:o + 8].rstrip(b'\0').decode('latin1')
        vs, va, rs, ra = struct.unpack_from('<IIII', d, o + 8)
        out.append((name, 0x400000 + va, vs, ra, rs))
    return out
SP = secs(pat)
def off2va(o):
    for name, va, vs, ra, rs in SP:
        if ra <= o < ra + rs: return va + (o - ra)
def va2off(v, d=orig):
    for name, va, vs, ra, rs in secs(d):
        if va <= v < va + max(vs, rs): return ra + (v - va)
# Funktionsgrenzen um jede RCE-Stelle (Heuristik: Prolog 55 8B EC nach CC/C3/90-Fuellung)
def fstart(o):
    for x in range(o, max(o - 0x4000, 0x400), -1):
        if orig[x:x + 3] == b'\x55\x8b\xec' and orig[x - 1] in (0xCC, 0xC3, 0x90): return x
def fend(o):
    for x in range(o + 1, o + 0x4000):
        if orig[x:x + 3] == b'\x55\x8b\xec' and orig[x - 1] in (0xCC, 0xC3, 0x90): return x
SITES = {'P1': 0x14A842, 'P2': 0x14A85C, 'P3': 0x364D40, 'P4': 0x46B8E0, 'P5': 0x614A0, 'P6': 0x46AC43}
FR = {}
for k, o in SITES.items():
    a, b = fstart(o), fend(o); FR[k] = (off2va(a), off2va(b)); print(k, 'Funktion VA %X-%X' % FR[k])
# geaenderte Bereiche (innerhalb der Originalgroesse) + angehaengte Sektionen
ranges = []; i = 0; n = len(orig)
while i < n:
    if pat[i] != orig[i]:
        j = i
        while j < n and pat[j] != orig[j]: j += 1
        ranges.append((max(i - 8, 0), j)); i = j
    else: i += 1
for name, va, vs, ra, rs in SP:
    if ra >= n: ranges.append((ra, ra + rs))
def owner(o):
    for id_, off, ln in rows:
        if off <= o < off + ln: return id_
    return '?'
md = capstone.Cs(capstone.CS_ARCH_X86, capstone.CS_MODE_32)
hits = set()
for a, b in ranges:
    va = off2va(a)
    if va is None: continue
    for ins in md.disasm(pat[a:b], va):
        vals = []
        if ins.mnemonic in ('call', 'jmp') or ins.mnemonic.startswith('j'):
            if ins.op_str.startswith('0x'): vals.append(int(ins.op_str, 16))
        for m in re.finditer(r'0x[0-9a-f]{6,8}', ins.op_str): vals.append(int(m.group(0), 16))
        for t in vals:
            for k, (fa, fb) in FR.items():
                if fa <= t < fb:
                    o = a + (ins.address - va)
                    who = owner(o) if o < n else 'Sektion %s' % next((s[0] for s in SP if s[3] <= o < s[3] + s[4]), '?')
                    hits.add((k, ins.address, ins.mnemonic, ins.op_str, who))
for h in sorted(hits): print('%s: VA %X %s %s  <- %s' % h)
print('Treffer:', len(hits))
