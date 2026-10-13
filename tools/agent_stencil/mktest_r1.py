# Derives test_fix_r1.py from ol2/test_outline10.py for the two-pass alternative outline10_fix_r1.py.
# usage: python3 -B mktest_r1.py ; python3 -B test_fix_r1.py emu/Wow_fix_r1.exe
import os
HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(os.path.dirname(HERE), 'ol2', 'test_outline10.py')
s = open(SRC).read()
def rep(old, new, count=1):
    global s
    assert s.count(old) == count, (s.count(old), old[:90])
    s = s.replace(old, new)
rep("import outline10 as o\n", "sys.path.insert(0, %r)\nimport outline10_fix_r1 as o\n"
    "S1ON = [(52, 1), (56, 8), (55, 2), (53, 1), (54, 1), (59, 0xFF)]\n"
    "TWO_ON = [(168, 0), (14, 0), (23, 3), (52, 1), (56, 2), (57, 'W'), (55, 2), (53, 1), (54, 1), (58, 0xFF), (59, 0xFF)]\n"
    "def two_on(w): return [(a, w if b == 'W' else b) for a, b in TWO_ON]\n" % HERE)
rep("names = {0x148: 'DIP', ", "names = {0x148: 'DIP', 0x144: 'DP', ")
rep("nargs = {0x148: 7, ", "nargs = {0x148: 7, 0x144: 4, ")
rep("else: ok((52, 1) in srs and (56, 2) in srs and (57, 0) in srs and (55, 2) in srs and e.r32(DO['SMODE']) == 1, 'normal: Tiefe schreibendes loescht den Rand (LESS gegen 0, ZERO)')",
    "else: ok(srs == S1ON and e.r32(DO['SMODE']) == 1, 'normal (WPROT 0): ALWAYS, ZERO, ein Durchgang %s' % srs)")
rep("srs = later(); ok((56, 2) in srs and (57, 1) in srs and (55, 2) in srs, 'spaeter Gezeichnetes loescht nur Raender ueber 1 (LESS gegen WPROT, ZERO)')",
    "ST['dirty'] = []; srs = later(); seq = [c[0] for c in calls]; dd = [c for c in calls if c[0] == 'DIP']\n"
    "ok(seq == ['DIP'] + ['SRS'] * 11 + ['DIP'] + ['SRS'] * 2 and srs == two_on(1) + [(52, 0), (23, 4)] and dd[0] == dd[1] and ST['dirty'] == [15, 16] and e.r32(DEV + 0x3E70) == 0xFFFFFFFF and e.r32(DO['SMODE']) == 0,\n"
    "   'WPROT 1: Durchgang 1 unveraendert, Durchgang 2 nur Stencil (keine Farbe/Tiefe, ZFUNC EQUAL, LESS gegen 1, ZERO), danach ZFUNC aus dem Cache, ZWRITE/COLORWRITE neu %s' % srs)")
rep("srs = later(); ok((57, 0) in srs, 'GMODE 2: spaeter Gezeichnetes loescht alle Raender (Ref 0)')",
    "srs = later(); ok(srs == S1ON, 'GMODE 2 (WPROT 0): ein Durchgang, ALWAYS, ZERO')")
rep("print('FAILS', fails)", r'''# 30) zwei Durchgaenge auch fuer DrawPrimitive
DPH = OUT + o.LAB['dp']
dargs = [D3D, 4, 7, 33]
def dpcall(cur=0, marked=1, zw=1, smode=0):
    calls.clear(); ST['dirty'] = []; e.w32(DO['CUR'], cur); e.w32(DO['MARKED'], marked); e.w32(DEV + 0x3E70, zw); e.w32(DO['SMODE'], smode); e.w32(DEV + 0x3E88, 4)
    sp = run(DPH, RET, {UC_X86_REG_EBX: 1, UC_X86_REG_ESI: 2, UC_X86_REG_EDI: 3, UC_X86_REG_EBP: 4}, [RET] + dargs)
    good = mu.reg_read(UC_X86_REG_ESP) == sp + 4 + 16 and [mu.reg_read(r) for r in (UC_X86_REG_EBX, UC_X86_REG_ESI, UC_X86_REG_EDI, UC_X86_REG_EBP)] == [1, 2, 3, 4]
    return good, [c[1:3] for c in calls if c[0] == 'SRS'], [c for c in calls if c[0] in ('DP', 'DIP')]
for k in FL: flag(k, 0)
flag('FPARTY', 1); flag('FWALLSGRP', 1); raid([]); guid(0xBD1948, 0x444); guid(0xBD07B0, 0x111); guid(0xBD07A0, 0x222)
newframe(); batch(OTHER); ok(e.r32(DO['WPROT']) == 1, 'WPROT 1 fuer die DP-Pruefung')
g1, srs, dr = dpcall(); ok(g1 and dr == [('DP', 4, 7, 33)] * 2 and srs == two_on(1) + [(52, 0), (23, 4)] and ST['dirty'] == [15, 16], 'DP mit WPROT 1: zwei Durchgaenge, Stack (ret 0x10) und Register %s' % srs)
g1, srs, dr = dpcall(zw=0); ok(g1 and dr == [('DP', 4, 7, 33)] and srs == [], 'DP ohne Tiefe mit WPROT 1: einmal, unveraendert')
g1, srs, dr = dpcall(cur=2); ok(g1 and dr == [('DP', 4, 7, 33)] and srs == [], 'DP waehrend CUR: unveraendert')
g1, srs, dr = dpcall(cur=2, smode=1); ok(g1 and dr == [('DP', 4, 7, 33)] and srs == [(52, 0)] and e.r32(DO['SMODE']) == 0, 'DP waehrend CUR mit SMODE an: erst Stencil aus')
flag('FWALLSGRP', 0); newframe(); batch(OTHER); ok(e.r32(DO['WPROT']) == 0, 'WPROT 0')
g1, srs, dr = dpcall(); ok(g1 and dr == [('DP', 4, 7, 33)] and srs == S1ON and e.r32(DO['SMODE']) == 1, 'DP mit WPROT 0: ein Durchgang, ALWAYS, ZERO %s' % srs)
g1, srs, dr = dpcall(zw=0, smode=1); ok(g1 and dr == [('DP', 4, 7, 33)] and srs == [(52, 0)], 'DP ohne Tiefe: Stencil aus')
for k in FL: flag(k, 0)
print('FAILS', fails)''')
open(os.path.join(HERE, 'test_fix_r1.py'), 'w').write(s)
print('wrote test_fix_r1.py')
