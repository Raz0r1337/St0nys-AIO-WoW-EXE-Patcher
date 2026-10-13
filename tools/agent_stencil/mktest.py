# Derives test_fix.py (this directory) from ol2/test_outline10.py for outline10_fix.py: expectations for the
# U-bit stencil values, the new SMODE state, post masks, plus new checks for the DrawPrimitive hook (dp).
# ol2/test_outline10.py is only read. usage: python3 -B mktest.py ; then python3 -B test_fix.py emu/Wow_fix.exe
import os, difflib
HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(os.path.dirname(HERE), 'ol2', 'test_outline10.py')
s = open(SRC).read(); orig = s
def rep(old, new, count=1):
    global s
    assert s.count(old) == count, (s.count(old), old[:90])
    s = s.replace(old, new)
rep("import outline10 as o\n", "sys.path.insert(0, %r)\nimport outline10_fix as o\nSMON = [(52, 1), (56, 8), (55, 2), (53, 1), (54, 1), (59, 0xC0)]   # SMODE: ALWAYS, ZERO, KEEP, KEEP, Schreibmaske 0xC0\n" % HERE)
rep("names = {0x148: 'DIP', ", "names = {0x148: 'DIP', 0x144: 'DP', ")
rep("nargs = {0x148: 7, ", "nargs = {0x148: 7, 0x144: 4, ")
# 8) / 9) marked parts
rep("ok((57, 0x80) in b0 and (54, 1) in b0 and (55, 3) in b0, 'normal: Figur Stencil 0x80, ZFAIL KEEP')",
    "ok((57, 0xC0) in b0 and (54, 1) in b0 and (55, 3) in b0, 'normal: Figur Stencil 0xC0, ZFAIL KEEP')")
rep("ok((56, 3) in b1 and (57, 0x83) in b1 and (58, 0x7F) in b1 and (23, 8) in b1, 'Ring: EQUAL Ref 0x83, Maske 0x7F, ZFUNC ALWAYS')",
    "ok((56, 3) in b1 and (57, 0xC3) in b1 and (58, 0x7F) in b1 and (23, 8) in b1, 'Ring: EQUAL Ref 0xC3, Maske 0x7F, ZFUNC ALWAYS')")
rep("(57, 3) in b2 and (14, 1) in b2 and (168, 0) in b2, 'Kopien: ZFUNC 4, GREATER Ref 3, Tiefe schreiben, keine Farbe')",
    "(57, 0x43) in b2 and (14, 1) in b2 and (168, 0) in b2, 'Kopien: ZFUNC 4, GREATER Ref 0x43, Tiefe schreiben, keine Farbe')")
rep("(56, 5) in b1 and (57, 1) in b1, 'verdeckt: Kopien mit ZFUNC GREATER, ohne Tiefe, GREATER Ref 1')",
    "(56, 5) in b1 and (57, 0x41) in b1, 'verdeckt: Kopien mit ZFUNC GREATER, ohne Tiefe, GREATER Ref 0x41')")
# 11) later geometry
rep("else: ok((52, 1) in srs and (56, 2) in srs and (57, 0) in srs and (55, 2) in srs and e.r32(DO['SMODE']) == 1, 'normal: Tiefe schreibendes loescht den Rand (LESS gegen 0, ZERO)')",
    "else: ok(srs == SMON and e.r32(DO['SMODE']) == 1, 'normal: Tiefe schreibendes loescht den Rand (ALWAYS, ZERO, Schreibmaske 0xC0) %s' % srs)")
# 13) post
rep("ok(refs == [4, 3, 2, 1], 'Vierecke fuer alle 4 Einheiten (%s)' % refs)",
    "ok(refs == [0x44, 0x43, 0x42, 0x41], 'Vierecke fuer alle 4 Einheiten, Ref 0x40|Kategorie (%s)' % refs)\n"
    "masks = [[c[2] for c in calls[:k] if c[0] == 'SRS' and c[1] == 58][-1] for k in dp]\n"
    "ok(masks == [0xFF] * 4, 'ohne WPROT: Maske 0xFF fuer alle (%s)' % masks)")
# 15) pulse colours keyed by category
rep("    return dict(zip(refs, [struct.unpack('<I', calls[k][5][16:20])[0] for k in dp]))",
    "    return dict(zip([r & 0x3F for r in refs], [struct.unpack('<I', calls[k][5][16:20])[0] for k in dp]))")
# 16) later geometry with WPROT / GMODE 2
rep("srs = later(); ok((56, 2) in srs and (57, 1) in srs and (55, 2) in srs, 'spaeter Gezeichnetes loescht nur Raender ueber 1 (LESS gegen WPROT, ZERO)')",
    "srs = later(); ok(srs == SMON, 'spaeter Gezeichnetes: derselbe Zustand wie ohne WPROT (Schutz ueber die Post-Maske) %s' % srs)")
rep("srs = later(); ok((57, 0) in srs, 'GMODE 2: spaeter Gezeichnetes loescht alle Raender (Ref 0)')",
    "srs = later(); ok(srs == SMON, 'GMODE 2: spaeter Gezeichnetes, Zustand wie immer')")
# 20) glow sequence
rep("for cat in (4, 3, 2, 1): SRC += [('SRS', 57, cat), ('DPUP', 5, 2, '&VERTS', 20)]",
    "for cat in (4, 3, 2, 1): SRC += [('SRS', 57, 0x40 | cat), ('SRS', 58, 0xFF), ('DPUP', 5, 2, '&VERTS', 20)]")
rep("('SRS', 56, 5), ('SRS', 57, 0x80), ('SRS', 27, 1),", "('SRS', 56, 5), ('SRS', 57, 0x80), ('SRS', 58, 0xFF), ('SRS', 27, 1),")
rep("for cat in (4, 3, 2, 1): RING += [('SRS', 57, cat), ('DPUP', 5, 2, '&VERTS', 20)]",
    "for cat in (4, 3, 2, 1): RING += [('SRS', 57, 0x40 | cat), ('SRS', 58, 0xFF), ('DPUP', 5, 2, '&VERTS', 20)]")
rep("EXP += RING + [('Clear', 0, 0, 4, 0, 0x3F800000, 0), ('SRS', 52, 0)]",
    "EXP += RING + [('SRS', 59, 0xFF), ('Clear', 0, 0, 4, 0, 0x3F800000, 0), ('SRS', 52, 0)]")
rep("ok(refs == [4, 3, 2, 1] and rc == [light(cols[c]) for c in (4, 3, 2, 1)],", "ok(refs == [0x44, 0x43, 0x42, 0x41] and rc == [light(cols[c]) for c in (4, 3, 2, 1)],")
# 26) mixed thin lines
rep("ok(src == [('SRS', 57, 3), ('SRS', 57, 2)] and", "ok(src == [('SRS', 57, 0x43), ('SRS', 57, 0x42)] and")
rep("ok(refs == [3, 2, 1] and rc ==", "ok(refs == [0x43, 0x42, 0x41] and rc ==")
# 30) new: DrawPrimitive hook, shared SMODE, protected masks in post
rep("print('FAILS', fails)", r'''# 30) stencilfix: DrawPrimitive-Zweig (VA 0x6A3706) laeuft durch dieselbe Pruefung (smode) wie DIP
DPH = OUT + o.LAB['dp']
fo = lambda va: va - 0x400C00
ok(D[fo(0x6A36C8)] == 0x52 and D[fo(0x6A36C9)] == 0xE8 and (struct.unpack('<i', D[fo(0x6A36CA):fo(0x6A36CE)])[0] + 0x6A36CE) & 0xFFFFFFFF == DIP and D[fo(0x6A36CE):fo(0x6A36D1)] == b'\x90\x90\x90', 'DIP-Stelle 0x6A36C8: push edx; call dip; 3x nop')
ok(D[fo(0x6A3706)] == 0x52 and D[fo(0x6A3707)] == 0xE8 and (struct.unpack('<i', D[fo(0x6A3708):fo(0x6A370C)])[0] + 0x6A370C) & 0xFFFFFFFF == DPH and D[fo(0x6A370C):fo(0x6A370F)] == b'\x90\x90\x90', 'DP-Stelle 0x6A3706: push edx; call dp; 3x nop')
dargs = [D3D, 4, 7, 33]
def dpcall(cur=0, marked=1, zw=1, smode=None):
    calls.clear(); e.w32(DO['CUR'], cur); e.w32(DO['MARKED'], marked); e.w32(DEV + 0x3E70, zw)
    if smode is not None: e.w32(DO['SMODE'], smode)
    sp = run(DPH, RET, {UC_X86_REG_EBX: 1, UC_X86_REG_ESI: 2, UC_X86_REG_EDI: 3, UC_X86_REG_EBP: 4}, [RET] + dargs)
    good = mu.reg_read(UC_X86_REG_ESP) == sp + 4 + 16 and [mu.reg_read(r) for r in (UC_X86_REG_EBX, UC_X86_REG_ESI, UC_X86_REG_EDI, UC_X86_REG_EBP)] == [1, 2, 3, 4]
    return good, [c[1:3] for c in calls if c[0] == 'SRS'], [c for c in calls if c[0] in ('DP', 'DIP')]
for k in FL: flag(k, 0)
g1, srs, dr = dpcall(smode=0)
ok(g1 and srs == SMON and dr == [('DP', 4, 7, 33)] and e.r32(DO['SMODE']) == 1, 'DP mit Tiefe nach Markiertem: ALWAYS, ZERO, Schreibmaske 0xC0, dann DrawPrimitive (Stack ret 0x10, Register) %s' % srs)
g1, srs, dr = dpcall(); ok(g1 and srs == [] and dr == [('DP', 4, 7, 33)], 'DP: Zustand schon gesetzt, nur DrawPrimitive')
g1, srs, dr = dpcall(zw=0); ok(g1 and srs == [(52, 0)] and dr == [('DP', 4, 7, 33)] and e.r32(DO['SMODE']) == 0, 'DP ohne Tiefe: Stencil aus')
g1, srs, dr = dpcall(marked=0, smode=0); ok(g1 and srs == [] and dr == [('DP', 4, 7, 33)], 'DP ohne Markiertes im Bild: unveraendert')
flag('FWALLS', 1); g1, srs, dr = dpcall(smode=0); ok(g1 and srs == [] and dr == [('DP', 4, 7, 33)], 'DP mit durch Waende (alle): unveraendert'); flag('FWALLS', 0)
g1, srs, dr = dpcall(cur=2, smode=0); ok(g1 and srs == [] and dr == [('DP', 4, 7, 33)] and e.r32(DO['SMODE']) == 0, 'DP waehrend CUR (umrandetes Teil): unveraendert')
g1, srs, dr = dpcall(cur=2, smode=1); ok(g1 and srs == [(52, 0)] and dr == [('DP', 4, 7, 33)] and e.r32(DO['SMODE']) == 0, 'DP waehrend CUR mit SMODE an: erst Stencil aus (wie d_mark), dann DrawPrimitive')
dpcall(smode=0); calls.clear(); e.w32(DO['CUR'], 0)
run(DIP, RET, {}, [RET] + args); ok([c[0] for c in calls] == ['DIP'], 'DIP nach DP mit Tiefe: SMODE geteilt, nur DIP')
e.w32(DEV + 0x3E70, 0); calls.clear(); run(DIP, RET, {}, [RET] + args); ok([c[1:3] for c in calls if c[0] == 'SRS'] == [(52, 0)] and e.r32(DO['SMODE']) == 0, 'DIP ohne Tiefe danach: Stencil aus')
flag('FPARTY', 1); flag('FWALLSGRP', 1); raid([]); guid(0xBD1948, 0x444); guid(0xBD07B0, 0x111); guid(0xBD07A0, 0x222)
gl0 = e.r32(DO['GLFAIL']); e.w32(DO['GLFAIL'], D3D)
newframe(); batch(OTHER); calls.clear(); e.w32(DO['MARKED'], 1)
run(POST, RET, regs, [RET])
dq = [k for k, c in enumerate(calls) if c[0] == 'DPUP']
rm = [([c[2] for c in calls[:k] if c[0] == 'SRS' and c[1] == 57][-1], [c[2] for c in calls[:k] if c[0] == 'SRS' and c[1] == 58][-1]) for k in dq]
ok(e.r32(DO['WPROT']) == 1 and rm == [(0x43, 0xFF), (0x42, 0xFF), (0x41, 0x3F)], 'Post mit WPROT 1: Ref 0x40|Kategorie, Maske 0x3F fuer den Gruppen-Rand %s' % [(hex(a), hex(b)) for a, b in rm])
cl = [k for k, c in enumerate(calls) if c[0] == 'Clear']
ok(cl and calls[cl[-1] - 1][:3] == ('SRS', 59, 0xFF) and calls[cl[-1] + 1][:3] == ('SRS', 52, 0), 'vor dem Stencil-Leeren Schreibmaske 0xFF, danach Stencil aus')
e.w32(DO['GLFAIL'], gl0)
for k in FL: flag(k, 0)
print('FAILS', fails)''')
open(os.path.join(HERE, 'test_fix.py'), 'w').write(s)
open(os.path.join(HERE, 'test_fix.diff'), 'w').writelines(difflib.unified_diff(orig.splitlines(True), s.splitlines(True), 'ol2/test_outline10.py', 'agent_stencil/test_fix.py'))
print('wrote test_fix.py')
