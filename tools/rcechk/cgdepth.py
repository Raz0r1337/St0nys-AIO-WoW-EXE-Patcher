#!/usr/bin/env python3
# Aufrufgraph: Erreicht der neue Code eines Patches (ueber direkte Aufrufe, bis Tiefe D) eine Funktion, die RCE-Fix v2 veraendert?
# Und: Liegt eine Patch-Stelle in einer Funktion, die (bis Tiefe D) eine RCE-Funktion aufruft?
# Aufruf: cgdepth.py <Original-Wow.exe> <gepatchte Wow.exe ohne Nr. 10> <apply_patches.ps1> [Tiefe=4]
import sys, struct, re, bisect, capstone
orig = open(sys.argv[1], 'rb').read(); pat = open(sys.argv[2], 'rb').read(); src = open(sys.argv[3]).read().replace('\r', '')
D = int(sys.argv[4]) if len(sys.argv) > 4 else 4
IB = 0x400000; TXT_RAW, TXT_VA, TXT_END = 0x400, 0x401000, 0x9DE3B3
rows = [(m.group(1), int(m.group(2), 16), len(m.group(3)) // 2) for m in re.finditer(r'^(\w+);([0-9A-F]+);([0-9A-F]+);[01]$', src, re.M)]
o2v = lambda o: o - TXT_RAW + TXT_VA
v2o = lambda v: v - TXT_VA + TXT_RAW
def fstart(o):
    for x in range(o, max(o - 0x4000, 0x400), -1):
        if orig[x:x + 3] == b'\x55\x8b\xec' and orig[x - 1] in (0xCC, 0xC3, 0x90): return x
def fend(o):
    for x in range(o + 1, o + 0x4000):
        if orig[x:x + 3] == b'\x55\x8b\xec' and orig[x - 1] in (0xCC, 0xC3, 0x90): return x
RCE_SITES = [0x14A842, 0x14A85C, 0x364D40, 0x46B8E0, 0x614A0, 0x46AC43, 0x3D9D7C]
RCE_FN = sorted({o2v(fstart(o)) for o in RCE_SITES})
md = capstone.Cs(capstone.CS_ARCH_X86, capstone.CS_MODE_32)
# --- Original .text linear durchgehen: Funktionsanfaenge (Prolog + Aufrufziele), Kanten call/jmp ---
text = orig[TXT_RAW:TXT_RAW + (TXT_END - TXT_VA)]
starts = set(); edges = []   # (insn_va, target_va, kind)
for m in re.finditer(rb'[\xCC\xC3\x90]\x55\x8B\xEC', text): starts.add(TXT_VA + m.start() + 1)
pos = 0; L = len(text)
while pos < L:
    last = pos
    for addr, size, mn, ops in md.disasm_lite(text[pos:], TXT_VA + pos):
        last = addr - TXT_VA + size
        if ops.startswith('0x') and (mn == 'call' or mn == 'jmp' or mn[0] == 'j'):
            try: t = int(ops, 16)
            except ValueError: continue
            if TXT_VA <= t < TXT_END:
                edges.append((addr, t, mn))
                if mn == 'call': starts.add(t)
    pos = last + 1 if last == pos else last
starts = sorted(starts)
def fn_of(va):
    i = bisect.bisect_right(starts, va) - 1
    return starts[i] if i >= 0 else None
cg = {}
for a, t, mn in edges:
    f = fn_of(a)
    if f is None: continue
    tf = fn_of(t)
    if mn == 'call' or (mn == 'jmp' and tf != f):   # jmp in eine andere Funktion = Tail-Call
        cg.setdefault(f, set()).add(tf if mn == 'call' else tf)
rce_set = set(fn_of(v) for v in RCE_FN)
# --- Kuerzeste Pfade zu RCE-Funktionen bis Tiefe D (Rueckwaerts-BFS von den RCE-Funktionen) ---
rev = {}
for f, ts in cg.items():
    for t in ts: rev.setdefault(t, set()).add(f)
dist = {f: (0, [f]) for f in rce_set}; frontier = list(rce_set)
for depth in range(1, D + 1):
    nxt = []
    for f in frontier:
        for c in rev.get(f, ()):
            if c not in dist: dist[c] = (depth, [c] + dist[f][1]); nxt.append(c)
    frontier = nxt
# --- Neuer Code der Patches: direkte Ziele in den Original-Code ---
def secs(d):
    e = struct.unpack_from('<I', d, 0x3C)[0]; n = struct.unpack_from('<H', d, e + 6)[0]; base = e + 24 + struct.unpack_from('<H', d, e + 20)[0]
    return [(d[base + 40 * i:base + 40 * i + 8].rstrip(b'\0').decode('latin1'),) + struct.unpack_from('<IIII', d, base + 40 * i + 8) for i in range(n)]
SP = secs(pat)
def off2va(o):
    for name, vs, va, rs, ra in SP:
        if ra <= o < ra + rs: return IB + va + (o - ra)
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
    for name, vs, va, rs, ra in SP:
        if ra <= o < ra + rs and ra >= n: return 'Sektion ' + name
    return '?'
targets = {}   # patch -> set(target fn)
for a, b in ranges:
    va = off2va(a)
    if va is None: continue
    for ins in md.disasm(pat[a:b], va):
        o = a + (ins.address - va); who = owner(o)
        if who in ('rce', 'pe', 'watermark', '?'): continue
        vals = []
        if ins.mnemonic == 'call' or ins.mnemonic.startswith('j'):
            if ins.op_str.startswith('0x'): vals.append(int(ins.op_str, 16))
        for m in re.finditer(r'0x[0-9a-f]{6,8}', ins.op_str): vals.append(int(m.group(0), 16))
        for t in vals:
            if TXT_VA <= t < TXT_END and not any(x <= v2o(t) < y for x, y in ranges if x < n):
                targets.setdefault(who, set()).add(fn_of(t))
print('Funktionen: %d, Kanten: %d, RCE-Funktionen: %s, erreichbar bis Tiefe %d: %d Funktionen' % (len(starts), len(edges), ['%X' % f for f in sorted(rce_set)], D, len(dist)))
print('--- Neuer Code -> RCE-Funktion (kuerzester Pfad):')
found = False
for who in sorted(targets):
    best = None
    for t in targets[who]:
        if t in dist and (best is None or dist[t][0] < best[0]): best = dist[t]
    if best: found = True; print('  %-14s Tiefe %d: %s' % (who, best[0] + 1, ' -> '.join('%X' % f for f in best[1])))
if not found: print('  keiner')
print('--- Patch-Stelle liegt in einer Funktion, die eine RCE-Funktion erreicht:')
found = False
for id_, off, ln in rows:
    if id_ in ('rce', 'pe', 'watermark') or off < TXT_RAW or off >= TXT_RAW + (TXT_END - TXT_VA): continue
    f = fn_of(o2v(off))
    if f in dist and dist[f][0] > 0:
        found = True; print('  %-14s Stelle %X in %X, Tiefe %d: %s' % (id_, off, f, dist[f][0], ' -> '.join('%X' % x for x in dist[f][1])))
if not found: print('  keine')
