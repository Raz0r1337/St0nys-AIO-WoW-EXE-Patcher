# Emulationstest fuer Add-Outline (outline10: weicher Schein per Weichzeichner fuer alle; outline8: Sortierung von Pass 0; outline7: Durch Waende nur Gruppe/Schlachtzug; outline6: nur wo verdeckt mit ZFAIL KEEP und Tiefen-Abstand). Aufruf: test_outline5.py <Wow.exe mit Nr. 68>
import sys, os, struct
sys.path.insert(0, '/tmp/claude-0/-home-user-St0nys-WoW-EXE-Patcher/49e16a66-3a63-5e77-ae4f-92ef019273b7/scratchpad/tm')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))   # agent_tips/gen_fix: outline10/psasm with the fix
from emu2 import *
import outline10 as o
SMON = [(52, 1), (56, 8), (55, 2), (53, 1), (54, 1), (59, 0xC0)]   # SMODE: ALWAYS, ZERO, KEEP, KEEP, Schreibmaske 0xC0
import math
D = open(sys.argv[1], 'rb').read()
fails = 0
def ok(c, msg):
    global fails
    print(('OK   ' if c else 'FAIL ') + msg)
    if not c: fails += 1
so = [s for s in sections(D) if s[0] == '.outl'][0]
OUT = so[1]
ok(so[2] == len(o.TPL), '.outl hat die erwartete Groesse (0x%X)' % so[2])
e = Emu2(D)
try: e.mu.mem_map(OUT, 0x2000)
except UcError: pass
e.mu.mem_write(OUT, D[so[4]:so[4] + so[2]])
ok(bytes(e.mu.mem_read(OUT, len(o.TPL)))[:o.CODE_OFF] == bytes(o.data()), 'Datenbereich wie im Generator')
DO = {k: OUT + v for k, v in o.DO.items()}
FL = o.FLAGS
def flag(name, on): e.mu.mem_write(FL[name], b'\x01' if on else b'\xCC')
for k in FL: ok(bytes(e.mu.mem_read(FL[k], 1)) == b'\xCC', 'Schalter %s ohne Option aus (CC)' % k)
H = 0x30000000; e.mu.mem_write(H, b'\0' * 0x100000)
DEV = H + 0x10000; D3D = H + 0x1000; VT = H + 0x2000; STUBS = H + 0x3000; GPU = H + 0x30000
e.w32(0xC5DF88, DEV); e.w32(DEV, 0xA2E718); e.w32(DEV + 0x1CC, 5); e.w32(DEV + 0x397C, D3D); e.w32(DEV + 0x2900, GPU)
e.w32(D3D, VT)
calls = []
names = {0x148: 'DIP', 0x144: 'DP', 0xE4: 'SRS', 0x178: 'SetVSConst', 0x1A8: 'CreatePS', 0x170: 'SetVS', 0x1AC: 'SetPS', 0x164: 'SetFVF', 0x14C: 'DPUP', 0xAC: 'Clear',
         0x98: 'GetRT', 0xA0: 'GetDS', 0x94: 'SetRT', 0x9C: 'SetDS', 0x70: 'CreateRT', 0x5C: 'CreateTex', 0x88: 'StretchRect', 0xBC: 'SetVP',
         0x104: 'SetTex', 0x114: 'SSS', 0x10C: 'TSS'}
nargs = {0x148: 7, 0x144: 4, 0xE4: 3, 0x178: 4, 0x1A8: 3, 0x170: 2, 0x1AC: 2, 0x164: 2, 0x14C: 5, 0xAC: 7,
         0x98: 3, 0xA0: 2, 0x94: 3, 0x9C: 2, 0x70: 9, 0x5C: 9, 0x88: 6, 0xBC: 2, 0x104: 3, 0x114: 4, 0x10C: 4}
# nachgebildete COM-Objekte (Oberflaechen, Texturen, Pixelshader) mit Referenzzaehlern
OBJS = {}; NEXTOBJ = [H + 0xB0000]; FAIL = {}
OVT = {'surf': H + 0x4000, 'tex': H + 0x4100, 'ps': H + 0x4200}
def newobj(kind, **kw):
    p = NEXTOBJ[0]; NEXTOBJ[0] += 0x40; e.w32(p, OVT[kind]); OBJS[p] = dict(kind=kind, refs=1, **kw); return p
def o_release(em, a):
    OBJS[a[0]]['refs'] -= 1; calls.append(('Release', a[0])); return OBJS[a[0]]['refs']
def o_desc(em, a):
    s = OBJS[a[0]]; em.mu.mem_write(a[1], struct.pack('<8I', s['fmt'], 1, s.get('usage', 1), 0, s['ms'], s['mq'], s['w'], s['h']))
    calls.append(('GetDesc', a[0])); return FAIL.pop('GetDesc', 0)
def o_level(em, a):
    t = OBJS[a[0]]
    if 'surf' not in t: t['surf'] = newobj('surf', fmt=21, ms=0, mq=0, w=t['w'], h=t['h'], tex=a[0]); OBJS[t['surf']]['refs'] = 0
    OBJS[t['surf']]['refs'] += 1; em.w32(a[2], t['surf']); calls.append(('GetLevel', a[0], a[1])); return 0
for kind, fns in (('surf', ((8, o_release, 1), (0x30, o_desc, 2))), ('tex', ((8, o_release, 1), (0x48, o_level, 3))), ('ps', ((8, o_release, 1),))):
    for off, fn, n in fns:
        a = OVT[kind] + 0x800 + off; e.w32(OVT[kind] + off, a); e.stub(a, fn, n, 4 * n)
SURF = {}   # aktuelle Oberflaechen des Spiels: 'bb', 'ds'
def d3dcall(em, nm, args):
    if nm == 'CreatePS':
        n = FAIL.get('CreatePS', 0)
        if n:
            FAIL['CreatePS'] = n - 1
            if n == 1: del FAIL['CreatePS']; em.w32(args[2], 0); return 0x8876086C
        p = newobj('ps', code=args[1]); em.w32(args[2], p); return 0
    if nm == 'GetRT':
        if FAIL.pop('GetRT', 0): return 0x8876086C
        OBJS[SURF['bb']]['refs'] += 1; em.w32(args[2], SURF['bb']); return 0
    if nm == 'GetDS':
        if FAIL.pop('GetDS', 0): return 0x8876086C
        OBJS[SURF['ds']]['refs'] += 1; em.w32(args[1], SURF['ds']); return 0
    if nm == 'CreateRT':
        if FAIL.pop('CreateRT', 0): return 0x8007000E
        em.w32(args[7], newobj('surf', fmt=args[3], ms=args[4], mq=args[5], w=args[1], h=args[2])); return 0
    if nm == 'CreateTex':
        n = FAIL.get('CreateTex', 0)
        if n:
            FAIL['CreateTex'] = n - 1
            if n == 1: del FAIL['CreateTex']; return 0x8007000E
        em.w32(args[7], newobj('tex', fmt=args[5], w=args[1], h=args[2], usage=args[4], pool=args[6], levels=args[3])); return 0
    if nm == 'StretchRect': return 0x8876086C if FAIL.pop('StretchRect', 0) else 0
    if nm == 'SetRT' and FAIL.get('SetRT', 0):
        FAIL['SetRT'] -= 1
        if FAIL['SetRT'] == 0: del FAIL['SetRT']; return 0x8876086C
    return 0
for off, nm in names.items():
    a = STUBS + off; e.w32(VT + off, a)
    def mk(nm, off):
        def f(em, args):
            rec = (nm,) + tuple(args[1:])
            if nm == 'SetVSConst': rec = rec + (struct.unpack('<16f', bytes(em.mu.mem_read(args[2], 64))),)
            if nm == 'DPUP': rec = rec + (bytes(em.mu.mem_read(args[3], 4 * args[4])),)
            if nm == 'CreatePS': rec = rec + (bytes(em.mu.mem_read(args[1], 20)),)
            if nm == 'SetVP': rec = rec + (bytes(em.mu.mem_read(args[1], 24)),)
            r = d3dcall(em, nm, args); calls.append(rec); return r
        return f
    e.stub(a, mk(nm, off), nargs[off], 4 * nargs[off])
SURF['bb'] = newobj('surf', fmt=22, ms=4, mq=0, w=1920, h=1080); SURF['ds'] = newobj('surf', fmt=75, ms=4, mq=0, w=1920, h=1080)
P = [1.5, 0, 0, 0, 0, 2.0, 0, 0, 0, 0, 1.001, -0.1, 0, 0, 1.0, 0]
e.mu.mem_write(0xC5F008, struct.pack('<16f', *P))
P32 = struct.unpack('<16f', struct.pack('<16f', *P))   # wie im Speicher (float32)
ST = {}
e.stub(0x8203B0, lambda em, a: ST.setdefault('db', []).append(em.r32(DO['CUR'])), 0, 0)
# Einheiten: Ziel 0x111 (NPC), Mouseover 0x222 (NPC), ich 0x333 (Magier), Gruppe 0x444 (Paladin), 0x555/0x777 (nicht in Reichweite), Raid 0x666 (Priester)
TOBJ = H + 0x40000; MOBJ = H + 0x41000; POBJ = H + 0x42000; GOBJ = H + 0x43000
TM = H + 0x50000; TMOUNT = H + 0x51000; MM = H + 0x52000; WEAP = H + 0x53000; OTHER = H + 0x54000; PM = H + 0x55000; GM = H + 0x56000
PF = H + 0x57000; GF = H + 0x58000; TF = H + 0x59000; ROBJ = H + 0x5A000; RM = H + 0x5B000; RF = H + 0x5C000
e.w32(TOBJ + 0xB4, TM); e.w32(TOBJ + 0x98C, TMOUNT); e.w32(TOBJ + 0xD0, TF); e.mu.mem_write(TF + 0x45, b'\x01')
e.w32(MOBJ + 0xB4, MM); e.w32(MOBJ + 0x98C, 0)
e.w32(POBJ + 0xB4, PM); e.w32(POBJ + 0x98C, 0); e.w32(POBJ + 0xD0, PF); e.mu.mem_write(PF + 0x45, b'\x08')   # Magier
e.w32(GOBJ + 0xB4, GM); e.w32(GOBJ + 0x98C, 0); e.w32(GOBJ + 0xD0, GF); e.mu.mem_write(GF + 0x45, b'\x02')   # Paladin
e.w32(ROBJ + 0xB4, RM); e.w32(ROBJ + 0x98C, 0); e.w32(ROBJ + 0xD0, RF); e.mu.mem_write(RF + 0x45, b'\x05')   # Priester
e.w32(WEAP + 0x48, TM)
OBJ = {0x111: TOBJ, 0x222: MOBJ, 0x333: POBJ, 0x444: GOBJ, 0x666: ROBJ}
PLAYERS = {0x333, 0x444, 0x666}
def objptr(em, a):
    assert a[3] == 0xA22CD4 and a[2] in (0x18, 0x10), a
    if a[2] == 0x10:
        ST.setdefault('pl', []).append(a[0]); return OBJ.get(a[0], 0) if a[0] in PLAYERS else 0
    ST.setdefault('obj', []).append(a[0])
    return OBJ.get(a[0], 0)
e.stub(0x4D4DB0, objptr, 5, 0)
SELC = {0x111: 0xFFFF0000, 0x222: 0xFF00FF00, 0x333: 0xFF0000FF, 0x444: 0xFF0000FE, 0x666: 0xFF0000FD}
def selcol(em, a):
    g = em.r32(a[0]); em.w32(a[1], SELC[g]); ST.setdefault('col', []).append((g, a[2]))
e.stub(0x521BF0, selcol, 3, 0)
e.stub(0x4D3790, lambda em, a: (em.mu.reg_write(UC_X86_REG_EDX, 0x0F000000), 0x333)[1], 0, 0)
# Objektmanager (0x4D3730): erstes Objekt [mgr+0xAC], naechstes [obj+[mgr+0xA4]+4], Deskriptor [obj+8]
MGR = H + 0xC0000; NODES = H + 0xC1000; MGRP = [MGR]; e.w32(MGR + 0xA4, 0x38)
e.stub(0x4D3730, lambda em, a: (ST.__setitem__('mgr', ST.get('mgr', 0) + 1), MGRP[0])[1], 0, 0)
def objlist(lst, term=None):   # (GUID, Typmaske, Offset des Besitzers im Deskriptor, Besitzer)
    if term is None: term = (MGR + 0xA8) | 1
    nodes = []
    for i, (g, tm, off, og) in enumerate(lst):
        n = NODES + 0x100 * i; e.mu.mem_write(n, b'\0' * 0x100); d = n + 0x40
        e.w32(n + 8, d); e.w32(d, g); e.w32(d + 4, 0x0F000000); e.w32(d + 8, tm)
        if off: e.w32(d + off, og); e.w32(d + off + 4, 0x0F000000)
        nodes.append(n)
    for k, n in enumerate(nodes): e.w32(n + 0x3C, nodes[k + 1] if k + 1 < len(nodes) else term)
    e.w32(MGR + 0xAC, nodes[0] if nodes else term)
objlist([])
e.stub(0x685970, lambda em, a: ST.setdefault('dirty', []).append(a[0]), 1, 4)
e.stub(0x685A70, lambda em, a: ST.__setitem__('force', ST.get('force', 0) + 1), 0, 0)
e.stub(0x4F6F90, lambda em, a: ST.__setitem__('circles', em.mu.reg_read(UC_X86_REG_ECX)), 0, 0)
TICK = [0]; GTC = H + 0x3800; e.w32(0x9DF174, GTC)
e.stub(GTC, lambda em, a: (ST.__setitem__('ticks', ST.get('ticks', 0) + 1), TICK[0])[1], 0, 0)
SCENE = H + 0x60000; e.w32(0xCD754C, SCENE)
def guid(a, lo): e.w32(a, lo); e.w32(a + 4, 0x0F000000 if lo else 0)
guid(0xBD07B0, 0x111); guid(0xBD07A0, 0x222)
for i in range(4): guid(0xBD1948 + 8 * i, 0)
RAIDS = H + 0x80000
def raid(lst):
    e.w32(0xBEB608, len(lst))
    for i in range(40): e.w32(0xBEB568 + 4 * i, 0)
    for i, g in enumerate(lst):
        p = RAIDS + 0x20 * i; guid(p, g); e.w32(0xBEB568 + 4 * i, p)
raid([])
e.w32(0xD43020, 1)
mu = e.mu
e.w32(DO['GLFAIL'], D3D)   # Abschnitte 1-18: ohne Schein (wie outline8)
def run(start, stop, regs, stack=()):
    sp = 0x200F0000
    for v in reversed(stack): sp -= 4; mu.mem_write(sp, struct.pack('<I', v))
    for r, v in regs.items(): mu.reg_write(r, v)
    mu.reg_write(UC_X86_REG_ESP, sp)
    mu.emu_start(start, stop, count=400000)
    return sp
# 1) Viewport
FR = 0x200E0000; mu.mem_write(FR - 0x24, struct.pack('<4I2f', 0, 0, 1920, 1080, 0.0, 1.0))
run(0x6A9B10, 0x6A9B16, {UC_X86_REG_EBP: FR, UC_X86_REG_ESI: DEV})
ok(bytes(mu.mem_read(DO['VP'], 24)) == struct.pack('<4I2f', 0, 0, 1920, 1080, 0.0, 1.0), 'Viewport gemerkt')
ok(mu.reg_read(UC_X86_REG_EAX) == D3D, 'eax = D3D-Device nach dem Viewport-Haken')
REN = H + 0x70000
def batch(model, scene=SCENE):
    e.w32(REN + 0x40, scene); e.w32(REN + 0x60, model); ST['db'] = []
    run(0x823A81, 0x823AD3, {UC_X86_REG_ESI: REN, UC_X86_REG_EDI: 7, UC_X86_REG_EBX: 9})
    return ST['db'], mu.reg_read(UC_X86_REG_ESI) == REN and mu.reg_read(UC_X86_REG_EDI) == 7 and mu.reg_read(UC_X86_REG_EBX) == 9
def units():
    n = e.r32(DO['NUNITS']); out = []
    for i in range(n):
        b = DO['UNITS'] + 24 * i
        out.append((e.r32(b), e.r32(b + 8), e.r32(b + 12), e.r32(b + 16), e.r32(b + 20)))
    return out
def newframe(): e.w32(DO['VALID'], 0); ST['obj'] = []; ST['col'] = []; ST['pl'] = []
# 2) Standard (keine Optionen): nur Ziel und Mouseover
newframe()
r, keep = batch(TM); ok(r == [1] and keep, 'Ziel-Modell -> Kategorie 1, Register erhalten')
ok(e.r32(DO['CUR']) == 0, 'CUR nach dem Batch wieder 0')
u = units(); ok([x[0] for x in u] == [0x111, 0x222] and u[0][1:3] == (TM, TMOUNT) and u[1][1:3] == (MM, 0), 'Tabelle: Ziel, Mouseover')
ok(u[0][3] == 0xFFFF0000 and u[1][3] == 0xFF00FF00 and ST['col'] == [(0x111, 1), (0x222, 1)] and ST['pl'] == [0x111, 0x222], 'NPCs: Farbe vom Auswahlkreis (Spieler-Pruefung mit Typmaske 0x10)')
r, _ = batch(TMOUNT); ok(r == [1], 'Reittier -> 1')
r, _ = batch(WEAP); ok(r == [1], 'Waffe (Eltern = Ziel) -> 1')
r, _ = batch(MM); ok(r == [2], 'Mouseover -> 2')
r, _ = batch(PM); ok(r == [0], 'eigener Charakter ohne Option -> 0')
r, _ = batch(OTHER); ok(r == [0], 'anderes Modell -> 0')
r, _ = batch(TM, scene=H + 0x61000); ok(r == [0], 'andere Szene -> 0')
ok(ST['obj'] == [0x111, 0x222], 'keine weiteren Nachschlagungen im selben Bild')
ok(e.r32(DO['SELFCAT']) == 0, 'ohne Option keine eigene Kategorie')
# 3) eigener Charakter + Gruppe
flag('FSELF', 1); flag('FPARTY', 1)
guid(0xBD1948, 0x444); guid(0xBD1950, 0); guid(0xBD1958, 0x111); guid(0xBD1960, 0x555)
newframe(); r, _ = batch(PM)
u = units()
ok([x[0] for x in u] == [0x444, 0x333, 0x111, 0x222], 'Reihenfolge: Gruppe, ich, Ziel, Mouseover (Ziel in der Gruppe nur einmal)')
ok(r == [2] and e.r32(DO['SELFCAT']) == 2, 'eigener Charakter -> 2, SELFCAT 2')
ok(u[0][3] == o.CLASSCOL[2] and u[1][3] == o.CLASSCOL[8], 'Klassenfarben Paladin und Magier')
r, _ = batch(GM); ok(r == [1], 'Gruppenmitglied -> 1')
r, _ = batch(TM); ok(r == [3], 'Ziel (auch in der Gruppe) -> eigener Eintrag 3')
ok(0x555 in ST['obj'] and 0x555 not in [x[0] for x in u], 'nicht sichtbares Mitglied ohne Eintrag')
# 4) Schlachtzug: alle Mitglieder, ohne mich, ohne Ziel, ohne Doppelte
flag('FPARTY', 0); flag('FRAID', 1)
raid([0x666, 0x444, 0x333, 0x777, 0x111])
newframe(); batch(OTHER); u = units()
ok([x[0] for x in u] == [0x666, 0x444, 0x333, 0x111, 0x222], 'Schlachtzug: Priester, Paladin (Gruppe nur einmal), ich, Ziel, Mouseover')
ok(u[0][3] == o.CLASSCOL[5] and e.r32(DO['SELFCAT']) == 3, 'Priester in Klassenfarbe, SELFCAT 3')
r, _ = batch(RM); ok(r == [1], 'Raid-Mitglied -> 1')
e.w32(0xBEB608, 60); newframe(); batch(OTHER); ok(len(units()) == 5, 'Raid-Anzahl ueber 40 wird begrenzt')
e.w32(0xBEB608, 5)
# 5) Spieler als Ziel: Klassenfarbe; Option Gesinnungsfarbe fuer alle
flag('FRAID', 0); raid([]); guid(0xBD1948, 0)
guid(0xBD07B0, 0x444); newframe(); batch(OTHER); u = units()
ok([x[0] for x in u] == [0x333, 0x444, 0x222] and u[1][3] == o.CLASSCOL[2], 'Spieler als Ziel: Klassenfarbe')
flag('FREACT', 1); newframe(); batch(OTHER); u = units()
ok([x[3] for x in u] == [0xFF0000FF, 0xFF0000FE, 0xFF00FF00] and ST['pl'] == [], 'Option Gesinnungsfarbe: alle in Farbe des Auswahlkreises')
flag('FREACT', 0); guid(0xBD07B0, 0x111)
guid(0xBD07B0, 0x333); newframe(); r, _ = batch(PM)
ok(r == [1] and e.r32(DO['SELFCAT']) == 0 and [x[0] for x in units()] == [0x333, 0x222], 'ich als Ziel: Ziel-Eintrag, keine eigene Kategorie')
guid(0xBD07B0, 0x111)
# 6) unbekannte Klasse -> Farbe vom Auswahlkreis
for cls in (10, 12, 0):
    mu.mem_write(PF + 0x45, bytes([cls])); newframe(); batch(PM)
    ok(units()[0][3] == 0xFF0000FF, 'Klasse %d ohne Farbe -> Auswahlkreis-Farbe' % cls)
mu.mem_write(PF + 0x45, b'\x08')
# 7) DIP ohne Markierung
DIP = OUT + o.LAB['dip']; POST = OUT + o.LAB['post']; RET = 0x31000000
args = [D3D, 4, 0, 0, 100, 0, 50]
calls.clear(); e.w32(DO['CUR'], 0); e.w32(DO['MARKED'], 0)
sp = run(DIP, RET, {UC_X86_REG_EBX: 1, UC_X86_REG_ESI: 2, UC_X86_REG_EDI: 3, UC_X86_REG_EBP: 4}, [RET] + args)
ok([c[0] for c in calls] == ['DIP'] and calls[0][1:] == tuple(args[1:]), 'unmarkiert: ein normaler DIP')
ok(mu.reg_read(UC_X86_REG_ESP) == sp + 4 + 28, 'unmarkiert: Stack ausgeglichen (ret 0x1C)')
def marked(cat):
    calls.clear(); e.w32(DO['CUR'], cat); e.w32(DEV + 0x3E60, 0); e.w32(DEV + 0x3E88, 4); ST['dirty'] = []; e.w32(DO['SMODE'], 0)
    sp = run(DIP, RET, {UC_X86_REG_EBX: 1, UC_X86_REG_ESI: 2, UC_X86_REG_EDI: 3, UC_X86_REG_EBP: 4}, [RET] + args)
    return mu.reg_read(UC_X86_REG_ESP) == sp + 4 + 28 and [mu.reg_read(r) for r in (UC_X86_REG_EBX, UC_X86_REG_ESI, UC_X86_REG_EDI, UC_X86_REG_EBP)] == [1, 2, 3, 4]
def parts():
    dips = [k for k, c in enumerate(calls) if c[0] == 'DIP']
    seg = lambda a, b: [c[1:3] for c in calls[a:b] if c[0] == 'SRS']
    return dips, seg
# 8) normal (Ziel = 3 im Bild mit mir als 2)
flag('FSELF', 1); newframe(); batch(PM)
ok(marked(3), 'normal: Stack und Register erhalten')
dips, seg = parts()
ok(len(dips) == 10, 'normal: echtes Teil + Ring + 8 Kopien (%d)' % len(dips))
b0 = seg(0, dips[0]); ok((57, 0xC0) in b0 and (54, 1) in b0 and (55, 3) in b0, 'normal: Figur Stencil 0xC0, ZFAIL KEEP')
b1 = seg(dips[0], dips[1]); ok((56, 3) in b1 and (57, 0xC3) in b1 and (58, 0x7F) in b1 and (23, 8) in b1, 'Ring: EQUAL Ref 0xC3, Maske 0x7F, ZFUNC ALWAYS')
b2 = seg(dips[1], dips[2]); ok(b2[0] == (23, 4) and (56, 5) in b2 and (57, 0x43) in b2 and (14, 1) in b2 and (168, 0) in b2, 'Kopien: ZFUNC 4, GREATER Ref 0x43, Tiefe schreiben, keine Farbe')
ok(seg(dips[-1], len(calls))[-1] == (52, 0) and (54, 3) not in seg(0, len(calls)), 'Ende: Stencil aus, ZFAIL nie REPLACE')
vs = [c for c in calls if c[0] == 'SetVSConst']; mm = vs[0][4]; ox = 2 * 2 / 1920
ok(len(vs) == 9 and all(abs(mm[i] - (P[i] + ox * P[12 + i])) < 1e-6 for i in range(4)), '9 VS-Uploads, Kopie 0 um 2 Pixel verschoben (ohne Schein, GLFAIL = Geraet)')
def copy_offsets(vs):   # (dx, dy) in Pixeln je Kopie aus c2/c3 der Matrix: c2 = C2 + C5 * dx * 2/1920, c3 = C3 + C5 * dy * -2/1080
    return [(round((v[4][2] - P[2]) / P[14] * 1920 / 2, 4), round((v[4][6] - P[6]) / P[14] * 1080 / -2, 4)) for v in vs[:8]]
ok(copy_offsets(vs) == [tuple(float(x) for x in xy) for xy in o.OFFS2] and o.OFFS2 == [(2, 0), (-2, 0), (0, 2), (0, -2), (2, 2), (2, -2), (-2, 2), (-2, -2)], 'ohne Schein: alle 8 Kopien wie frueher 2 Pixel weit %s' % copy_offsets(vs))
e.w32(DO['GLFAIL'], 0); marked(3); vs = [c for c in calls if c[0] == 'SetVSConst']; dips, seg = parts()
ok(len(vs) == 9 and len(dips) == 10 and copy_offsets(vs) == [tuple(float(x) for x in xy) for xy in o.OFFS] and vs[8][4] == P32, 'mit Schein: 8 Kopien nach OFFS (%s), danach Projektion original' % copy_offsets(vs))
e.w32(DO['GLFAIL'], 0x1234); marked(3); vs = [c for c in calls if c[0] == 'SetVSConst']
ok(copy_offsets(vs) == [tuple(float(x) for x in xy) for xy in o.OFFS], 'Schein auf einem anderen Geraet fehlgeschlagen: Kopien nach OFFS')
e.w32(DO['GLFAIL'], D3D); marked(3); dips, seg = parts()
ok(all(v[4][8:12] == P32[8:12] and v[4][12:16] == P32[12:16] for v in vs[:8]) and e.r32(DO['KZ']) == 0, 'normal: Tiefe (c4) und w (c5) der Kopien unveraendert, KZ 0')
ok(e.r32(DEV + 0x3E70) == 0xFFFFFFFF and ST['dirty'] == [15, 16] and e.r32(DO['MARKED']) == 1, 'Zustaende ungueltig, MARKED gesetzt')
# 9) nur wo verdeckt: eigener Charakter (2) -> Kopien mit ZFUNC GREATER; Ziel normal
flag('FSELF', 0); flag('FHIDDEN', 1); newframe(); batch(PM)
ok(e.r32(DO['SELFCAT']) == 1 and [x[0] for x in units()] == [0x333, 0x111, 0x222], 'nur verdeckt: ich in der Tabelle (Kategorie 1)')
ok(marked(1), 'verdeckt: Stack und Register erhalten')
dips, seg = parts()
ok(len(dips) == 9, 'verdeckt: echtes Teil + 8 Kopien, kein Ring (%d)' % len(dips))
ok((54, 3) in seg(0, dips[0]), 'verdeckt: Figur auch verdeckt markiert (ZFAIL REPLACE)')
b1 = seg(dips[0], dips[1]); ok((23, 5) in b1 and (14, 0) in b1 and (56, 5) in b1 and (57, 0x41) in b1, 'verdeckt: Kopien mit ZFUNC GREATER, ohne Tiefe, GREATER Ref 0x41')
zf = [v for (st, v) in b1 if st == 54]; ok(zf == [1], 'verdeckt: Kopien mit ZFAIL KEEP (vorne liegender Rand wird nicht markiert) %s' % zf)
A = (P[8] * P[12] + P[9] * P[13] + P[10] * P[14]) / (P[12] ** 2 + P[13] ** 2 + P[14] ** 2)
kz = o.KAPPA * (P[11] / A - P[15]); kzr = struct.unpack('<f', struct.pack('<I', e.r32(DO['KZ'])))[0]
ok(abs(kzr - kz) < 1e-9 and kz < 0, 'verdeckt: KZ = KAPPA * (c4w / A - c5w) = %.3g (nach vorn)' % kzr)
vs = [c for c in calls if c[0] == 'SetVSConst']
ok(len(vs) == 9 and all(all(abs(v[4][8 + i] - (P[8 + i] + kz * P[12 + i])) < 1e-6 for i in range(4)) and v[4][12:16] == P32[12:16] for v in vs[:8]), 'verdeckt: Tiefe der Kopien c4 + KZ * c5, w unveraendert')
ok(vs[8][4] == P32, 'verdeckt: danach Projektion wieder original')
ok(seg(dips[-1], len(calls))[-3:] == [(23, 4), (54, 1), (52, 0)], 'verdeckt: danach ZFUNC 4, ZFAIL KEEP, Stencil aus')
marked(2); dips, seg = parts(); ok(len(dips) == 10, 'Ziel bleibt normal (10 DIPs)')
# 10) durch Waende: alle mit ZFUNC ALWAYS; mit nur-verdeckt bleibt ich bei GREATER
flag('FWALLS', 1); marked(2); dips, seg = parts()
ok(len(dips) == 9 and (23, 8) in seg(dips[0], dips[1]) and (54, 3) in seg(0, dips[0]), 'Waende: Ziel ohne Ring, Kopien ZFUNC ALWAYS, Figur ZFAIL REPLACE')
ok((54, 1) in seg(dips[0], dips[1]) and e.r32(DO['KZ']) == 0, 'Waende: Kopien ZFAIL KEEP, KZ 0')
marked(1); dips, seg = parts(); ok((23, 5) in seg(dips[0], dips[1]), 'Waende + nur verdeckt: ich weiter mit ZFUNC GREATER')
# 11) Verdecken durch spaeter Gezeichnetes: normal ja, durch Waende nicht
for walls in (0, 1):
    flag('FWALLS', walls); calls.clear(); e.w32(DO['CUR'], 0); e.w32(DO['MARKED'], 1); e.w32(DO['SMODE'], 0); e.w32(DEV + 0x3E70, 1)
    run(DIP, RET, {}, [RET] + args)
    srs = [c[1:3] for c in calls if c[0] == 'SRS']
    if walls: ok([c[0] for c in calls] == ['DIP'] and e.r32(DO['SMODE']) == 0, 'Waende: spaeter Gezeichnetes loescht den Rand nicht')
    else: ok(srs == SMON and e.r32(DO['SMODE']) == 1, 'normal: Tiefe schreibendes loescht den Rand (ALWAYS, ZERO, Schreibmaske 0xC0) %s' % srs)
flag('FWALLS', 0); flag('FHIDDEN', 0); e.w32(DEV + 0x3E70, 0xFFFFFFFF); e.w32(DO['SMODE'], 0)
# 12) ohne Shader / mit Blending
e.w32(0xD43020, 0); flag('FWALLS', 1); marked(1); seq = [c[0] for c in calls]
ok(seq.count('DIP') == 1 and [c[1:3] for c in calls if c[0] == 'SRS'][-2:] == [(54, 1), (52, 0)], 'ohne Shader: nur echtes Teil, ZFAIL zurueck, Stencil aus')
e.w32(0xD43020, 1); flag('FWALLS', 0)
calls.clear(); e.w32(DO['CUR'], 1); e.w32(DEV + 0x3E60, 1); run(DIP, RET, {}, [RET] + args)
ok([c[0] for c in calls] == ['DIP'], 'Blending: nur normal zeichnen'); e.w32(DEV + 0x3E60, 0)
# 13) Post: ein Viereck je Einheit
flag('FSELF', 1); flag('FPARTY', 1); guid(0xBD1948, 0x444)
newframe(); batch(PM); u = units()
calls.clear(); ST['force'] = 0; e.w32(DO['MARKED'], 1)
regs = {UC_X86_REG_EAX: 0xA, UC_X86_REG_EBX: 0xB, UC_X86_REG_ECX: 0xC, UC_X86_REG_EDX: 0xD, UC_X86_REG_ESI: 0xE, UC_X86_REG_EDI: 0xF, UC_X86_REG_EBP: 0x10}
run(POST, RET, regs, [RET])
seq = [c[0] for c in calls]
ok('CreatePS' in seq, 'Pixelshader angelegt')
dp = [k for k, c in enumerate(calls) if c[0] == 'DPUP']
refs = [[c[2] for c in calls[:k] if c[0] == 'SRS' and c[1] == 57][-1] for k in dp]
colors = [struct.unpack('<I', calls[k][5][16:20])[0] for k in dp]
ok(refs == [0x44, 0x43, 0x42, 0x41], 'Vierecke fuer alle 4 Einheiten, Ref 0x40|Kategorie (%s)' % refs)
masks = [[c[2] for c in calls[:k] if c[0] == 'SRS' and c[1] == 58][-1] for k in dp]
ok(masks == [0xFF] * 4, 'ohne WPROT: Maske 0xFF fuer alle (%s)' % masks)
ok(colors == [x[3] for x in reversed(u)], 'jeweils in ihrer Farbe')
ok((56, 3) in [c[1:3] for c in calls if c[0] == 'SRS'] and (58, 0xFF) in [c[1:3] for c in calls if c[0] == 'SRS'], 'Stencil EQUAL, Maske 0xFF')
v = struct.unpack('<4f I 4f I 4f I 4f I', calls[dp[0]][5])
ok(v[0] == -0.5 and v[5] == 1919.5 and v[11] == 1079.5 and v[3] == 1.0, 'Viereck deckt den Viewport ab')
ok(any(c[0] == 'Clear' and c[1:4] == (0, 0, 4) for c in calls), 'Stencil geleert')
ok(e.r32(DO['MARKED']) == 0 and e.r32(DO['VALID']) == 0 and e.r32(DO['SMODE']) == 0, 'MARKED/VALID/SMODE zurueckgesetzt')
ok(ST.get('circles') == 0xC and all(mu.reg_read(r) == v for r, v in regs.items() if r != UC_X86_REG_EAX), 'weiter zu den Auswahlkreisen, Register erhalten')
# 14) Post ohne Markierung, ohne Stencil-Format
calls.clear(); ST['force'] = 0; run(POST, RET, regs, [RET]); seq = [c[0] for c in calls]
ok(seq.count('Clear') == 1 and 'DPUP' not in seq, 'unmarkiertes Bild: nur Stencil leeren')
calls.clear(); e.w32(DEV + 0x1CC, 7); newframe()
r, _ = batch(TM); ok(r == [0], 'kein Stencil (D32): keine Markierung')
run(POST, RET, regs, [RET]); ok(len(calls) == 0, 'kein Stencil: Post macht nichts')
# 15) Feindliche Spieler in Klassenfarbe pulsieren rot
e.w32(DEV + 0x1CC, 5); flag('FSELF', 0); flag('FPARTY', 1); flag('FREACT', 0)
guid(0xBD1948, 0x444); guid(0xBD07B0, 0x666); guid(0xBD07A0, 0x111)
SELC[0x666] = 0xFFFF0000; SELC[0x111] = 0xFFFF0000; SELC[0x444] = 0xFF0000FE
newframe(); batch(OTHER); u = units()
ok([x[0] for x in u] == [0x444, 0x666, 0x111], 'Tabelle: Gruppe, Ziel (feindlicher Priester), Mouseover (feindlicher NPC)')
ok(u[1][3] == o.CLASSCOL[5] and u[1][4] == 0xFFFF0000, 'feindlicher Spieler: Klassenfarbe, Pulsfarbe rot')
ok(u[0][4] == 0 and u[0][3] == o.CLASSCOL[2], 'freundlicher Spieler: kein Puls')
ok(u[2][3] == 0xFFFF0000 and u[2][4] == 0, 'feindlicher NPC: rot, kein Puls (keine Klassenfarbe)')
ok(ST['col'] == [(0x444, 1), (0x666, 1), (0x111, 1)], 'Feindlich-Pruefung ueber den Auswahlkreis (0x521BF0, 1)')
SELC[0x666] = 0xFFFF8000; newframe(); batch(OTHER); ok(units()[1][4] == 0, 'nur rot zaehlt (orange = kein Puls)')
SELC[0x666] = 0xFFFF0000; flag('FREACT', 1); newframe(); batch(OTHER); u = units()
ok(u[1][3] == 0xFFFF0000 and u[1][4] == 0, 'Gesinnungsfarbe: feindlicher Spieler rot, kein Puls')
flag('FREACT', 0)
def post_colors(ms):
    TICK[0] = ms; newframe(); batch(OTHER); calls.clear(); e.w32(DO['MARKED'], 1)
    run(POST, RET, regs, [RET])
    dp = [k for k, c in enumerate(calls) if c[0] == 'DPUP']
    refs = [[c[2] for c in calls[:k] if c[0] == 'SRS' and c[1] == 57][-1] for k in dp]
    return dict(zip([r & 0x3F for r in refs], [struct.unpack('<I', calls[k][5][16:20])[0] for k in dp]))
def mix(a, b, t):
    ch = lambda c, s: (c >> s) & 0xFF
    return 0xFF000000 | sum(((ch(a, s) * (256 - t) + ch(b, s) * t) >> 8) << s for s in (0, 8, 16))
for ms in (0, 375, 750, 1125, 1500, 1500 * 1000 + 250, 0xFFFFFFFF):
    cols = post_colors(ms); t = round((1 - math.cos(2 * math.pi * (ms % 1500) / 1500)) * 128)
    ok(e.r32(DO['T8']) == t and cols == {1: o.CLASSCOL[2], 2: mix(o.CLASSCOL[5], 0xFFFF0000, t), 3: 0xFFFF0000},
       'Puls bei %d ms: Anteil Rot %d/256, nur der feindliche Spieler (%s)' % (ms, t, {k: hex(v) for k, v in cols.items()}))
ok(mix(o.CLASSCOL[5], 0xFFFF0000, 0) == o.CLASSCOL[5] and mix(o.CLASSCOL[5], 0xFFFF0000, 256) == 0xFFFF0000, 'Mischung: 0 = Klassenfarbe, 256 = rot')
SELC[0x666] = 0xFF0000FD; cols = post_colors(750); ok(cols[2] == o.CLASSCOL[5], 'nicht mehr feindlich: alter Puls-Eintrag geloescht')
ok(all(mu.reg_read(r) == v for r, v in regs.items() if r != UC_X86_REG_EAX), 'Post mit Puls: Register erhalten')
# 16) Durch Waende nur Gruppe/Schlachtzug
for k in FL: flag(k, 0)
raid([]); guid(0xBD1948, 0x444); guid(0xBD1950, 0); guid(0xBD1958, 0); guid(0xBD1960, 0)
guid(0xBD07B0, 0x111); guid(0xBD07A0, 0x222); SELC[0x666] = 0xFF0000FD
def gstate(): return (e.r32(DO['GRPN']), e.r32(DO['GMODE']), e.r32(DO['WPROT']))
def later():
    calls.clear(); e.w32(DO['CUR'], 0); e.w32(DO['MARKED'], 1); e.w32(DO['SMODE'], 0); e.w32(DEV + 0x3E70, 1)
    run(DIP, RET, {}, [RET] + args)
    return [c[1:3] for c in calls if c[0] == 'SRS']
flag('FPARTY', 1); flag('FWALLSGRP', 1); newframe(); batch(OTHER)
ok([x[0] for x in units()] == [0x444, 0x111, 0x222] and gstate() == (1, 1, 1), 'Gruppe + Waende-Gruppe: GRPN 1, GMODE 1, WPROT 1 %s' % (gstate(),))
ok(marked(1), 'Gruppe durch Waende: Stack und Register erhalten')
dips, seg = parts()
ok(len(dips) == 9 and (54, 3) in seg(0, dips[0]) and (23, 8) in seg(dips[0], dips[1]) and (54, 1) in seg(dips[0], dips[1]), 'Gruppenmitglied wie durch Waende (9 DIPs, ZFUNC ALWAYS)')
marked(2); dips, seg = parts(); ok(len(dips) == 10 and (54, 3) not in seg(0, len(calls)), 'Ziel bleibt normal (10 DIPs, ZFAIL nie REPLACE)')
srs = later(); ok(srs == SMON, 'spaeter Gezeichnetes: derselbe Zustand wie ohne WPROT (Schutz ueber die Post-Maske) %s' % srs)
flag('FPARTY', 0); newframe(); batch(OTHER)
ok([x[0] for x in units()] == [0x444, 0x111, 0x222] and gstate() == (1, 2, 0), 'ohne Gruppen-Umrandung: Gruppe trotzdem in der Tabelle, GMODE 2, WPROT 0 %s' % (gstate(),))
marked(1); dips, seg = parts()
ok(len(dips) == 9 and (23, 5) in seg(dips[0], dips[1]) and e.r32(DO['KZ']) != 0, 'Gruppenmitglied nur wo verdeckt (ZFUNC GREATER, KZ)')
srs = later(); ok(srs == SMON, 'GMODE 2: spaeter Gezeichnetes, Zustand wie immer')
raid([0x666, 0x444, 0x333]); newframe(); batch(OTHER)
ok([x[0] for x in units()] == [0x666, 0x444, 0x111, 0x222] and gstate() == (2, 2, 0), 'GMODE 2 im Schlachtzug: Schlachtzug ohne mich, GRPN 2 %s' % (gstate(),))
flag('FRAID', 1); newframe(); batch(OTHER)
ok(gstate() == (2, 1, 2), 'Schlachtzug + Waende-Gruppe: GMODE 1, WPROT 2 %s' % (gstate(),))
flag('FSELF', 1); newframe(); batch(PM)
ok(e.r32(DO['SELFCAT']) == 3 and gstate()[0] == 2, 'eigener Charakter nach der Gruppe (SELFCAT 3 > GRPN 2)')
marked(3); dips, seg = parts(); ok(len(dips) == 10, 'eigener Charakter (immer) normal, nicht durch Waende')
flag('FSELF', 0); flag('FWALLSGRP', 0); flag('FRAID', 0); flag('FPARTY', 1); raid([]); newframe(); batch(OTHER)
ok(gstate() == (1, 0, 0), 'ohne Waende-Gruppe: GMODE 0, WPROT 0 %s' % (gstate(),))
marked(1); dips, seg = parts(); ok(len(dips) == 10, 'Gruppenmitglied normal (10 DIPs)')
flag('FWALLS', 1); flag('FWALLSGRP', 1); newframe(); batch(OTHER); marked(2); dips, seg = parts()
ok(len(dips) == 9 and (23, 8) in seg(dips[0], dips[1]), 'Waende alle + Gruppe: Ziel auch durch Waende')
# 17) Sortierung von Pass 0: Teile umrandeter Einheiten ans Ende (outline8)
SORTP = OUT + o.LAB['sortp']
so_ = 0x822FDD - 0x400C00
ok(D[so_] == 0xE8 and (struct.unpack('<i', D[so_ + 1:so_ + 5])[0] + 0x822FE2) & 0xFFFFFFFF == SORTP, 'Sortier-Aufruf bei 0x822FDD zeigt auf sortp')
for k in FL: flag(k, 0)
flag('FHIDDEN', 1); raid([]); guid(0xBD1948, 0); guid(0xBD07B0, 0x111); guid(0xBD07A0, 0x222)
ITEMS = H + 0x90000; LIST = H + 0x98000; OTHER2 = H + 0x5D000
e.w32(SCENE + 0x3C, ITEMS); e.w32(H + 0x61000 + 0x3C, ITEMS)
SPEC = [(0, OTHER, 5), (0, PM, 3), (0, OTHER2, 1), (1, PM, 2), (0, WEAP, 4), (0, PM, 0), (2, OTHER, 9), (0, MM, 7), (0, OTHER, 2)]
SEEN = []
def cmpb(em, a):
    ta, tb = em.r32(a[0]), em.r32(a[1]); SEEN.append((ta, tb))
    ka, kb = em.r32(a[0] + 0x40), em.r32(a[1] + 0x40)
    return 0xFFFFFFFF if ka < kb else (1 if ka > kb else 0)
e.stub(0x81EAD0, cmpb, 2, 0)
def setup(order):
    for i, (t, m, k) in enumerate(SPEC):
        b = ITEMS + 0x44 * i; mu.mem_write(b, b'\0' * 0x44); e.w32(b, t); e.w32(b + 4, m); e.w32(b + 0x40, k)
    for j, i in enumerate(order): e.w32(LIST + 4 * j, i)
def dosort(scene=SCENE, order=(8, 3, 6, 0, 7, 1, 5, 2, 4)):
    setup(order); SEEN.clear()
    sp = run(SORTP, RET, {UC_X86_REG_ESI: 11, UC_X86_REG_EDI: 22, UC_X86_REG_EBX: 33, UC_X86_REG_EBP: 44}, [RET, 0x81EEA0, LIST, len(SPEC), scene])
    good = mu.reg_read(UC_X86_REG_ESP) == sp + 4 and [mu.reg_read(r) for r in (UC_X86_REG_ESI, UC_X86_REG_EDI, UC_X86_REG_EBX, UC_X86_REG_EBP)] == [11, 22, 33, 44]
    lst = [e.r32(LIST + 4 * j) for j in range(len(SPEC))]
    types = [e.r32(ITEMS + 0x44 * i) for i in range(len(SPEC))]
    return good, lst, types
newframe()
good, lst, types = dosort()
ok(good, 'Sortierung: Stack (cdecl) und Register erhalten')
ok(lst == [2, 8, 0, 3, 6, 5, 1, 4, 7], 'umrandete Teile (ich, Waffe des Ziels, Mouseover) am Ende, andere wie bisher %s' % lst)
ok(types == [t for t, _, _ in SPEC], 'Typen danach wieder wie vorher')
ok(SEEN and all(ta in (0, 1) and tb in (0, 1) for ta, tb in SEEN), 'Vergleich 0x81EAD0 sieht nie den Typ 0x10')
ok([x[0] for x in units()] == [0x333, 0x111, 0x222] and e.r32(DO['VALID']) == 1, 'Tabelle schon beim Sortieren angelegt (ich, Ziel, Mouseover)')
ST['obj'] = []; r, _ = batch(PM); ok(r == [1] and ST['obj'] == [], 'Batch im selben Bild nutzt dieselbe Tabelle')
good, lst, _ = dosort(order=(4, 5, 6, 7, 8, 0, 1, 2, 3)); ok(good and lst == [2, 8, 0, 3, 6, 5, 1, 4, 7], 'andere Ausgangsreihenfolge, gleiches Ergebnis')
PLAIN = [5, 2, 8, 1, 4, 0, 7, 3, 6]
newframe(); good, lst, types = dosort(scene=H + 0x61000)
ok(good and lst == PLAIN and types == [t for t, _, _ in SPEC] and e.r32(DO['VALID']) == 0, 'andere Szene: Sortierung wie im Spiel, keine Tabelle %s' % lst)
e.w32(DEV + 0x1CC, 0); newframe(); good, lst, _ = dosort()
ok(good and lst == PLAIN and e.r32(DO['NUNITS']) == 0, 'ohne d3d9-Geraet: Sortierung wie im Spiel %s' % lst)
e.w32(DEV + 0x1CC, 5)
flag('FHIDDEN', 0); guid(0xBD07B0, 0); guid(0xBD07A0, 0); newframe(); good, lst, _ = dosort()
ok(good and lst == PLAIN and e.r32(DO['NUNITS']) == 0, 'niemand umrandet: Sortierung wie im Spiel')
guid(0xBD07B0, 0x111); guid(0xBD07A0, 0x222); newframe(); good, lst, _ = dosort()
ok(good and lst == [5, 2, 8, 1, 0, 3, 6, 4, 7], 'nur Ziel und Mouseover: nur deren Teile ans Ende %s' % lst)
# 18) Zeichnen von Pass 0: Teile umrandeter Einheiten erst nach den gebuendelten Doodads
DR1 = OUT + o.LAB['draw1']; DR2 = OUT + o.LAB['draw2']
def callto(va):
    fo = va - 0x400C00
    return D[fo] == 0xE8 and (struct.unpack('<i', D[fo + 1:fo + 5])[0] + va + 5) & 0xFFFFFFFF
ok(callto(0x823D1F) == DR1 and callto(0x823D3B) == DR2, 'Aufrufe bei 0x823D1F/0x823D3B zeigen auf draw1/draw2')
DL = []
e.stub(0x823130, lambda em, a: DL.append((em.mu.reg_read(UC_X86_REG_ECX),) + tuple(a)), 4, 16)
CTX = H + 0xA0000; CTX2 = H + 0xA1000; LIST48 = H + 0x99000; LIST1 = H + 0x9A000
e.w32(CTX + 0x40, SCENE); e.w32(CTX2 + 0x40, H + 0x61000)
e.w32(SCENE + 0x58, len(SPEC)); e.w32(SCENE + 0x5C, LIST); e.w32(SCENE + 0x48, 2); e.w32(SCENE + 0x4C, LIST48)
def draw(fn, ctx, pas, lst, cnt):
    DL.clear()
    sp = run(fn, RET, {UC_X86_REG_ECX: ctx, UC_X86_REG_ESI: 77, UC_X86_REG_EDI: 88, UC_X86_REG_EBX: 99}, [RET, pas, ITEMS, lst, cnt])
    good = mu.reg_read(UC_X86_REG_ESP) == sp + 4 + 16 and [mu.reg_read(r) for r in (UC_X86_REG_ESI, UC_X86_REG_EDI, UC_X86_REG_EBX)] == [77, 88, 99]
    return good, list(DL)
flag('FHIDDEN', 1); guid(0xBD07B0, 0x111); guid(0xBD07A0, 0x222); newframe(); good, lst, _ = dosort()
N = len(SPEC)
ok(lst == [2, 8, 0, 3, 6, 5, 1, 4, 7] and (e.r32(DO['NMARK']), e.r32(DO['MLIST']), e.r32(DO['MCOUNT'])) == (4, LIST, N), 'nach dem Sortieren: NMARK 4, Liste und Anzahl gemerkt')
good, dl = draw(DR1, CTX, 0, LIST, N)
ok(good and dl == [(CTX, 0, ITEMS, LIST, N - 4)], 'Pass 0, erste Liste: ohne die 4 umrandeten Teile %s' % dl)
good, dl = draw(DR2, CTX, 0, LIST48, 2)
ok(good and dl == [(CTX, 0, ITEMS, LIST48, 2), (CTX, 0, ITEMS, LIST + 4 * (N - 4), 4)], 'danach gebuendelte Doodads, dann die umrandeten Teile %s' % [tuple(hex(x) for x in t) for t in dl])
good, dl = draw(DR1, CTX, 1, LIST1, 3); ok(good and dl == [(CTX, 1, ITEMS, LIST1, 3)], 'Pass 1 unveraendert')
good, dl = draw(DR1, CTX2, 0, LIST, N); ok(good and dl == [(CTX2, 0, ITEMS, LIST, N)], 'andere Szene: erste Liste unveraendert')
good, dl = draw(DR2, CTX2, 0, LIST48, 2); ok(good and dl == [(CTX2, 0, ITEMS, LIST48, 2)], 'andere Szene: zweite Liste unveraendert, nichts extra')
good, lst, _ = dosort(scene=H + 0x61000); ok(e.r32(DO['NMARK']) == 4 and e.r32(DO['MLIST']) == LIST, 'Sortieren einer anderen Szene laesst NMARK der Welt stehen')
e.w32(SCENE + 0x58, N + 1)
good, dl = draw(DR1, CTX, 0, LIST, N + 1); ok(good and dl == [(CTX, 0, ITEMS, LIST, N + 1)], 'andere Anzahl als beim Sortieren: unveraendert')
good, dl = draw(DR2, CTX, 0, LIST48, 2); ok(good and dl == [(CTX, 0, ITEMS, LIST48, 2)], 'andere Anzahl: zweite Liste ohne Extra')
e.w32(SCENE + 0x58, N)
flag('FHIDDEN', 0); guid(0xBD07B0, 0); guid(0xBD07A0, 0); newframe(); dosort()
ok(e.r32(DO['NMARK']) == 0, 'niemand umrandet: NMARK 0')
good, dl = draw(DR1, CTX, 0, LIST, N); ok(good and dl == [(CTX, 0, ITEMS, LIST, N)], 'NMARK 0: erste Liste vollstaendig')
good, dl = draw(DR2, CTX, 0, LIST48, 2); ok(good and dl == [(CTX, 0, ITEMS, LIST48, 2)], 'NMARK 0: zweite Liste ohne Extra')
guid(0xBD07B0, 0x111); newframe(); e.w32(DEV + 0x1CC, 0); dosort(); e.w32(DEV + 0x1CC, 5)
ok(e.r32(DO['NMARK']) == 0, 'ohne d3d9-Geraet: NMARK 0')
# 19) Schlachtzug: alle mit Schein, auch ausserhalb der 5er-Gruppe (kein THIN)
for k in FL: flag(k, 0)
flag('FRAID', 1); guid(0xBD07B0, 0x111); guid(0xBD07A0, 0x222)
guid(0xBD1948, 0x444); guid(0xBD1950, 0); guid(0xBD1958, 0); guid(0xBD1960, 0)
raid([0x666, 0x444, 0x333]); newframe(); batch(OTHER); u = units()
def thins(): return [mu.mem_read(DO['THIN'] + c, 1)[0] for c in range(1, e.r32(DO['NUNITS']) + 1)]
ok([x[0] for x in u] == [0x666, 0x444, 0x111, 0x222] and thins() == [0, 0, 0, 0], 'Schlachtzug: Priester (nicht in der 5er-Gruppe) wie alle ohne THIN %s' % thins())
flag('FRAID', 0); flag('FPARTY', 1); raid([]); guid(0xBD1950, 0); newframe(); batch(OTHER)
ok(thins() == [0] * len(units()), 'ohne Schlachtzug: niemand duenn')
# 20) Weicher Schein: Ablauf im ersten Bild
f32 = lambda x: struct.unpack('<f', struct.pack('<f', x))[0]
O1, O2 = f32(o.BLUR_O[0]), f32(o.BLUR_O[1])
def light(c): return 0xFF000000 | sum((((c >> s) & 0xFF) - (((c >> s) & 0xFF) >> 2) - (((c >> s) & 0xFF) >> 3) + 0x5E) << s for s in (0, 8, 16))
def symmap():
    m = {SURF['bb']: 'BB', SURF['ds']: 'DS', DO['VP']: '&VP', DO['VERTT']: '&VERTT', DO['VERTS']: '&VERTS', DO['DESC']: '&DESC', DO['BBP']: '&BBP', DO['DSP']: '&DSP',
         DO['GPS']: '&GPS', DO['CPS']: '&CPS', DO['PS']: '&PS', DO['GPSCODE']: '&GPSCODE', DO['CPSCODE']: '&CPSCODE', DO['PSCODE']: '&PSCODE',
         DO['TPS']: '&TPS', DO['VPS']: '&VPS', DO['TPSCODE']: '&TPSCODE', DO['VPSCODE']: '&VPSCODE'}
    for i, n in enumerate(o.GLRES_NAMES): m[DO['GLRES'] + 4 * i] = '&' + n
    m.update({DO['LPS']: '&LPS', DO['LCPS']: '&LCPS', DO['LPSCODE']: '&LPSCODE', DO['LCPSCODE']: '&LCPSCODE'})
    for nm, k in (('GPS', 'GPS'), ('CPS', 'CPS'), ('PS', 'PS'), ('TPS', 'TPS'), ('VPS', 'VPS'), ('LPS', 'LPS'), ('LCPS', 'LCPS')):
        if e.r32(DO[k]): m[e.r32(DO[k])] = nm
    for i, n in enumerate(o.GLRES_NAMES):
        if e.r32(DO['GLRES'] + 4 * i): m[e.r32(DO['GLRES'] + 4 * i)] = n
    return m
def sym(cs):
    m = symmap(); return [tuple(m.get(x, x) if isinstance(x, int) else x for x in c) for c in cs]
def nob(cs): return [tuple(x for x in c if not isinstance(x, bytes)) for c in cs]
def verts(b, n=14): return [struct.unpack_from('<%df' % n, b, 4 * n * k) for k in range(4)]
def quad_ok(b, x0, y0, x1, y1, u0, v0, u1, v1, du, dv):
    want = []
    for k in range(4):
        x, y, u, v = (x1 if k & 1 else x0), (y1 if k & 2 else y0), (u1 if k & 1 else u0), (v1 if k & 2 else v0)
        taps = [u, v]
        for oo, sg in ((O1, 1), (O1, -1), (O2, 1), (O2, -1)): taps += [f32(u + sg * du * oo), f32(v + sg * dv * oo)]
        want.append(tuple([f32(x), f32(y), 0.0, 1.0] + [f32(t) for t in taps]))
    got = verts(b); return got == want, got, want
for k in FL: flag(k, 0)
flag('FSELF', 1); flag('FPARTY', 1); raid([]); guid(0xBD1948, 0x444)
guid(0xBD07B0, 0x111); guid(0xBD07A0, 0x222); TICK[0] = 0; SELC[0x111] = 0xFFFF0000; SELC[0x222] = 0xFF00FF00
e.w32(DO['GLFAIL'], 0); mu.mem_write(DO['VP'], struct.pack('<4I2f', 0, 0, 1920, 1080, 0.0, 1.0))
def post():
    newframe(); batch(OTHER); calls.clear(); e.w32(DO['MARKED'], 1); e.w32(DEV + 0xF6C, 0); e.w32(DEV + 0x2534, 0)
    run(POST, RET, regs, [RET]); return list(calls)
def ringpart(cs):   # Vierecke der duennen Linien: nach dem letzten SetFVF 0x44 (nach dem Schein)
    a = max(k for k, c in enumerate(cs) if c[0] == 'SetFVF' and c[1] == 0x44)
    dp = [k for k, c in enumerate(cs) if c[0] == 'DPUP' and k > a]
    refs = [[c[2] for c in cs[:k] if c[0] == 'SRS' and c[1] == 57][-1] for k in dp]
    return refs, [struct.unpack('<I', cs[k][5][16:20])[0] for k in dp]
def glowpart(cs):
    a = [k for k, c in enumerate(cs) if c[0] == 'SetFVF' and c[1] == 0x44][0] + 1
    return cs[a:]
fsw0 = mu.reg_read(UC_X86_REG_FPSW)
cs = post(); u = units()
ok([x[0] for x in u] == [0x444, 0x333, 0x111, 0x222] and thins() == [0, 0, 0, 0], 'Tabelle: Gruppe, ich, Ziel, Mouseover, niemand duenn')
g = sym(glowpart(cs)); gn = nob(g)
cols = {4 - i: x for i, x in enumerate(reversed([x[3] for x in u]))}
SRC = []
for cat in (4, 3, 2, 1): SRC += [('SRS', 57, 0x40 | cat), ('SRS', 58, 0xFF), ('DPUP', 5, 2, '&VERTS', 20)]
TSSL = []
for i in range(5): TSSL += [('TSS', i, 11, i), ('TSS', i, 24, 0)]
EXP = [('CreatePS', '&GPSCODE', '&GPS'), ('CreatePS', '&CPSCODE', '&CPS'), ('CreatePS', '&TPSCODE', '&TPS'), ('CreatePS', '&VPSCODE', '&VPS'),
       ('CreatePS', '&LPSCODE', '&LPS'), ('CreatePS', '&LCPSCODE', '&LCPS'), ('GetRT', 0, '&BBP'), ('GetDesc', 'BB'),
       ('CreateRT', 1920, 1080, 21, 4, 0, 0, '&MSRT', 0),
       ('CreateTex', 1920, 1080, 1, 1, 21, 0, '&TEX0', 0), ('GetLevel', 'TEX0', 0),
       ('CreateTex', 960, 540, 1, 1, 21, 0, '&TEX1', 0), ('GetLevel', 'TEX1', 0),
       ('CreateTex', 960, 540, 1, 1, 21, 0, '&TEX2', 0), ('GetLevel', 'TEX2', 0),
       ('CreateTex', 1920, 1080, 1, 1, 21, 0, '&TEX3', 0), ('GetLevel', 'TEX3', 0),
       ('GetDS', '&DSP'), ('SRS', 174, 0), ('SetRT', 0, 'MSRT'), ('Clear', 0, 0, 1, 0, 0x3F800000, 0)] + SRC + [
       ('StretchRect', 'MSRT', 0, 'TEX0S', 0, 0), ('SetDS', 0), ('SRS', 7, 0), ('SRS', 52, 0), ('SetPS', 'LPS'), ('SetFVF', 0x504),
       ('SSS', 0, 5, 2), ('SSS', 0, 6, 2), ('SSS', 0, 7, 0), ('SSS', 0, 1, 3), ('SSS', 0, 2, 3)] + TSSL + [
       ('SetTex', 0, 'TEX0'), ('SetRT', 0, 'TEX3S'), ('DPUP', 5, 2, '&VERTT', 56), ('SetPS', 'TPS'),
       ('SetTex', 0, 'TEX3'), ('SetRT', 0, 'TEX1S'), ('DPUP', 5, 2, '&VERTT', 56), ('SetPS', 'GPS'),
       ('SetTex', 0, 'TEX1'), ('SetRT', 0, 'TEX2S'), ('DPUP', 5, 2, '&VERTT', 56), ('SetPS', 'VPS'),
       ('SetTex', 0, 'TEX2'), ('SetRT', 0, 'TEX1S'), ('DPUP', 5, 2, '&VERTT', 56),
       ('SetRT', 0, 'BB'), ('SetDS', 'DS'), ('SetVP', '&VP'), ('SRS', 7, 1), ('SRS', 52, 1),
       ('SRS', 56, 5), ('SRS', 57, 0x80), ('SRS', 58, 0xFF), ('SRS', 27, 1), ('SRS', 19, 2), ('SRS', 20, 6), ('SRS', 168, 7), ('SetPS', 'CPS'), ('SetTex', 0, 'TEX1'), ('DPUP', 5, 2, '&VERTT', 56),
       ('SetPS', 'LCPS'), ('SetTex', 0, 'TEX3'), ('DPUP', 5, 2, '&VERTT', 56),
       ('SetTex', 0, 0), ('SRS', 27, 0), ('SRS', 56, 3), ('SRS', 168, 0xF), ('SetPS', 'PS'), ('SetFVF', 0x44)] + [('TSS', i, 24, 0) for i in range(5)] + [('Release', 'DS'), ('Release', 'BB')]
EXP += [('SRS', 59, 0xFF), ('Clear', 0, 0, 4, 0, 0x3F800000, 0), ('SRS', 52, 0)]   # keine Vierecke mehr: die Linie kommt aus TEX3
ok(gn == EXP, 'erstes Bild: Shader und Texturen anlegen, Ringfarben in die Render-Textur, aufloesen, Linie nach TEX3, verkleinern, waagrecht, senkrecht, Schein und Linie einblenden, alles zurueck')
if gn != EXP:
    for k, (a, b) in enumerate(zip(gn, EXP)):
        if a != b: print('   erste Abweichung bei', k, a, b); break
    print('   Laenge', len(gn), len(EXP))
cp = [c for c in g if c[0] == 'CreatePS']
ok(cp[0][3] == o.psasm.blur_ps(*o.BLUR_W)[:20] and cp[1][3] == o.psasm.comp_ps(o.GLOW_GAIN)[:20] and cp[2][3] == o.psasm.tent_ps()[:20] and cp[3][3] == o.psasm.blur_soft_ps(*o.BLUR_W, o.GLOW_K)[:20]
   and cp[4][3] == o.psasm.line_ps(o.LINE_K)[:20] and cp[5][3] == o.psasm.linecomp_ps()[:20], 'Pixelshader-Code aus dem Datenbereich (Weichzeichner, Einblenden, Zelt, senkrecht+Kurve, Linie, Linie einblenden)')
ok(bytes(mu.mem_read(DO['LPSCODE'], o.SIZES['LPSCODE'])) == o.psasm.line_ps(o.LINE_K) and bytes(mu.mem_read(DO['LCPSCODE'], o.SIZES['LCPSCODE'])) == o.psasm.linecomp_ps() and o.LINE_K == 4.0 and o.GLOW_K == 2.0,
   'Shader-Bytes Linie (k = 4) und Linie einblenden wie psasm, GLOW_K 2.0')
lt = o.psasm.disasm(o.psasm.line_ps(o.LINE_K)); lc = o.psasm.disasm(o.psasm.linecomp_ps())
ok(lt[1] == 'def c0, 1, 0, 0, 0' and lt[-5:] == ['max r1.w, r0.wwww, c0.xxxx', 'rcp r1.w, r1.wwww', 'mul r0, r0, r1.wwww', 'mov oC0, r0', 'end'] and sum(1 for x in lt if x.startswith('texld')) == 4,
   'Linie: 4 Abgriffe, Ausgabe = Summe * min(1, 1/Summe.a) (Deckkraft sat(4 * Zelt), Farbe gemittelt)')
ok(lc[1:3] == ['def c0, 0.625, 0.625, 0.625, 1', 'def c1, 0.3686275, 0.3686275, 0.3686275, 0'] and lc[-4:-1] == ['mul r1, r0, c0', 'mad r1, r0.wwww, c1, r1', 'mov oC0, r1'],
   'Linie einblenden: rgb * 5/8 + 0x5E/255 * a (wie die alten Vierecke), Alpha a')
ok(bytes(mu.mem_read(DO['TPSCODE'], o.SIZES['TPSCODE'])) == o.psasm.tent_ps() and bytes(mu.mem_read(DO['VPSCODE'], o.SIZES['VPSCODE'])) == o.psasm.blur_soft_ps(*o.BLUR_W, o.GLOW_K) and o.GLOW_GAIN == 1.0, 'Shader-Bytes Zelt und senkrecht+Kurve wie psasm, Einblenden mit Faktor 1')
ok(bytes(mu.read if False else mu.mem_read(DO['GPSCODE'], o.SIZES['GPSCODE'])) == o.psasm.blur_ps(*o.BLUR_W) and bytes(mu.mem_read(DO['CPSCODE'], o.SIZES['CPSCODE'])) == o.psasm.comp_ps(o.GLOW_GAIN), 'Shader-Bytes vollstaendig wie psasm')
dps = [c for c in g if c[0] == 'DPUP']
srcq = dps[:4]; ok([struct.unpack('<I', c[5][16:20])[0] for c in srcq] == [cols[c] | 0xFF000000 for c in (4, 3, 2, 1)], 'Render-Textur: Ringfarben in voller Deckkraft')
pz = [c for c in dps if c[4] == 56]
ok(len(pz) == 6, 'sechs Durchgaenge mit 5 Texturkoordinaten: Linie, Zelt, waagrecht, senkrecht, Schein einblenden, Linie einblenden (%d)' % len(pz))
TL = f32(o.LINE_T / o.BLUR_O[0]); dl0 = f32(TL / 1920); dl1 = f32(TL / 1080)
r0 = quad_ok(pz[0][5], -0.5, -0.5, 1919.5, 1079.5, 0.0, 0.0, 1.0, 1.0, dl0, dl1)
ok(r0[0], 'Linie: Viereck ueber 1920x1080 (volle Aufloesung), t1/t2 = (u,v) +/- (TL/1920, TL/1080) * O1 %s' % (r0[1][:1] if not r0[0] else ''))
vv = verts(pz[0][5]); ok(all(abs((v[6] - v[4]) * 1920 - 0.5) < 1e-3 and abs((v[4] - v[8]) * 1920 - 0.5) < 1e-3 and abs((v[7] - v[5]) * 1080 - 0.5) < 1e-3 for v in vv[1:]), 'Linien-Abgriffe +/- 0.5 Texel von TEX0 diagonal %s' % [round((v[6] - v[4]) * 1920, 5) for v in vv])
pz = pz[1:]
TQ = f32(o.TENT / o.BLUR_O[0]); du0 = f32(TQ / 1920); dv0 = f32(TQ / 1080)
r1 = quad_ok(pz[0][5], -0.5, -0.5, 959.5, 539.5, 0.0, 0.0, 1.0, 1.0, du0, dv0)
ok(r1[0], 'Verkleinern (Zelt): Viereck ueber 960x540, t1/t2 = (u,v) +/- (TQ/1920, TQ/1080) * O1 %s' % (r1[1][:1] if not r1[0] else ''))
vv = verts(pz[0][5]); ok(all(abs((v[6] - v[4]) * 1920 - 0.75) < 1e-3 and abs((v[4] - v[8]) * 1920 - 0.75) < 1e-3 and abs((v[7] - v[5]) * 1080 - 0.75) < 1e-3 for v in vv[1:]), 'Zelt-Abgriffe +/- 0.75 Texel von TEX3 diagonal %s' % [round((v[6] - v[4]) * 1920, 5) for v in vv])
du = f32(1 / 960); dv = f32(1 / 540)
r2 = quad_ok(pz[1][5], -0.5, -0.5, 959.5, 539.5, 0.0, 0.0, 1.0, 1.0, du, 0.0)
ok(r2[0], 'Waagrecht: Abgriffe u +/- 1.3846 und 3.2308 Texel (1/960) %s' % ((r2[1][1], r2[2][1]) if not r2[0] else ''))
r3 = quad_ok(pz[2][5], -0.5, -0.5, 959.5, 539.5, 0.0, 0.0, 1.0, 1.0, 0.0, dv)
ok(r3[0], 'Senkrecht: Abgriffe v +/- 1.3846 und 3.2308 Texel (1/540) %s' % ((r3[1][2], r3[2][2]) if not r3[0] else ''))
r4 = quad_ok(pz[3][5], -0.5, -0.5, 1919.5, 1079.5, 0.0, 0.0, 1.0, 1.0, 0.0, 0.0)
ok(r4[0], 'Einblenden: Viereck ueber den Viewport, Textur 0..1')
ok(pz[4][5] == pz[3][5], 'Linie einblenden: dasselbe Viereck (gleiche Stencil-, Blend- und Farbmaske wie der Schein)')
vp = [c for c in g if c[0] == 'SetVP'][0]; ok(vp[2] == struct.pack('<4I2f', 0, 0, 1920, 1080, 0.0, 1.0), 'Viewport wieder gesetzt')
refs, rc = ringpart(cs)
ok(refs == [] and rc == [], 'keine Vierecke mehr fuer Einheiten mit Schein (Linie aus TEX3) %s' % [hex(x) for x in rc])
ok(e.r32(DO['GLOK']) == 1 and e.r32(DEV + 0xF6C) == 1 and e.r32(DEV + 0x2534) == 1, 'GLOK 1, Viewport und Scissor beim Spiel als geaendert markiert')
ok(OBJS[SURF['bb']]['refs'] == 1 and OBJS[SURF['ds']]['refs'] == 1, 'Render-Target und Tiefenpuffer wieder freigegeben (Referenzen wie vorher)')
res = [e.r32(DO['GLRES'] + 4 * i) for i in range(len(o.GLRES_NAMES))]
ok(all(OBJS[p]['refs'] == 1 for p in res) and e.r32(DO['RTDEV']) == D3D and (e.r32(DO['RTW2']), e.r32(DO['RTH2'])) == (960, 540), 'Texturen gehalten (je 1 Referenz), RTDEV, halbe Groesse 960x540')
ok(len(res) == 9 and o.GLRES_NAMES[-2:] == ['TEX3', 'TEX3S'] and OBJS[e.r32(DO['TEX3'] if 'TEX3' in DO else DO['GLRES'] + 28)]['w'] == 1920, 'TEX3 (Linie) in voller Aufloesung, 9 Objekte in GLRES')
ok(all(mu.reg_read(r) == v for r, v in regs.items() if r != UC_X86_REG_EAX) and ST.get('circles') == 0xC, 'Post mit Schein: Register erhalten, weiter zu den Auswahlkreisen')
ok((mu.reg_read(UC_X86_REG_FPSW) >> 11) & 7 == (fsw0 >> 11) & 7, 'FPU-Stapel ausgeglichen')
# 21) zweites Bild: nichts neu anlegen
cs = post(); g = nob(sym(glowpart(cs)))
ok(not any(c[0] in ('CreatePS', 'CreateRT', 'CreateTex', 'GetLevel') for c in g) and g[:3] == [('GetRT', 0, '&BBP'), ('GetDesc', 'BB'), ('GetDS', '&DSP')], 'zweites Bild: Shader und Texturen wiederverwendet')
ok(OBJS[SURF['bb']]['refs'] == 1 and OBJS[SURF['ds']]['refs'] == 1 and all(OBJS[p]['refs'] == 1 for p in res), 'zweites Bild: Referenzen ausgeglichen')
# 22) Viewport mit Versatz
mu.mem_write(DO['VP'], struct.pack('<4I2f', 100, 50, 800, 600, 0.0, 1.0)); cs = post(); g = sym(glowpart(cs))
pz = [c for c in g if c[0] == 'DPUP' and c[4] == 56]
r = quad_ok(pz[4][5], 99.5, 49.5, 899.5, 649.5, f32(100 / 1920), f32(50 / 1080), f32(900 / 1920), f32(650 / 1080), 0.0, 0.0)
ok(r[0] and pz[5][5] == pz[4][5], 'Viewport 100,50 800x600: Viereck und Texturkoordinaten passend (Schein und Linie) %s' % (r[1][0] if not r[0] else ''))
r = quad_ok(pz[0][5], -0.5, -0.5, 1919.5, 1079.5, 0.0, 0.0, 1.0, 1.0, f32(TL / 1920), f32(TL / 1080))
ok(r[0], 'Viewport mit Versatz: Linie trotzdem ueber die ganze Textur')
ok([c for c in g if c[0] == 'SetVP'][0][2] == struct.pack('<4I2f', 100, 50, 800, 600, 0.0, 1.0), 'versetzter Viewport wiederhergestellt')
mu.mem_write(DO['VP'], struct.pack('<4I2f', 0, 0, 1920, 1080, 0.0, 1.0))
# 23) andere Groesse / Kantenglaettung: alte Texturen frei, neue an
old = res
OBJS[SURF['bb']].update(w=1281, h=721, ms=8, mq=2); cs = post(); g = nob(sym(glowpart(cs)))
ok(all(OBJS[p]['refs'] == 0 for p in old) and len(old) == 9, 'Groesse geaendert: alte 9 Objekte freigegeben')
cr = [c for c in g if c[0] in ('CreateRT', 'CreateTex')]
ok(cr == [('CreateRT', 1281, 721, 21, 8, 2, 0, '&MSRT', 0), ('CreateTex', 1281, 721, 1, 1, 21, 0, '&TEX0', 0), ('CreateTex', 641, 361, 1, 1, 21, 0, '&TEX1', 0), ('CreateTex', 641, 361, 1, 1, 21, 0, '&TEX2', 0),
         ('CreateTex', 1281, 721, 1, 1, 21, 0, '&TEX3', 0)],
   'neu: 1281x721 mit 8x/Qualitaet 2, halbe Groesse aufgerundet 641x361 %s' % cr)
res = [e.r32(DO['GLRES'] + 4 * i) for i in range(len(o.GLRES_NAMES))]
OBJS[SURF['bb']].update(w=1920, h=1080, ms=4, mq=0); cs = post()
ok(all(OBJS[p]['refs'] == 0 for p in res) and e.r32(DO['RTW']) == 1920, 'zurueck auf 1920x1080: wieder neu angelegt')
res = [e.r32(DO['GLRES'] + 4 * i) for i in range(len(o.GLRES_NAMES))]
# 24) Reset/Abbau: Freigabe ueber die drei Aufrufe von 0x690150
ok(all(callto(va) == OUT + o.LAB['glrel'] for va in o.RESETSITES), 'Aufrufe bei 0x69029D, 0x6A337F, 0x69040B zeigen auf glrel')
RF = []
e.stub(0x690150, lambda em, a: RF.append((em.mu.reg_read(UC_X86_REG_ECX), a[0])), 1, 4)
e.w32(DO['GLFAIL'], 0x1234)
sp = run(0x69029D, 0x6902A2, {UC_X86_REG_ECX: DEV, UC_X86_REG_ESI: 5, UC_X86_REG_EDI: 6, UC_X86_REG_EBX: 7}, [0])
ok(RF == [(DEV, 0)] and mu.reg_read(UC_X86_REG_ESP) == sp + 4 and [mu.reg_read(r) for r in (UC_X86_REG_ESI, UC_X86_REG_EDI, UC_X86_REG_EBX)] == [5, 6, 7], 'glrel: weiter zu 0x690150 mit ecx und Argument, Stack ausgeglichen')
ok(all(OBJS[p]['refs'] == 0 for p in res) and all(e.r32(DO['GLRES'] + 4 * i) == 0 for i in range(len(o.GLRES_NAMES))) and e.r32(DO['RTDEV']) == 0 and e.r32(DO['GLFAIL']) == 0, 'vor Reset: alle 9 Objekte frei, GLFAIL geloescht')
ok(e.r32(DO['GPS']) != 0 and e.r32(DO['PS']) != 0 and e.r32(DO['GPSDEV']) == D3D, 'vor Reset: Pixelshader bleiben')
cs = post(); g = nob(sym(glowpart(cs)))
ok(sum(1 for c in g if c[0] in ('CreateRT', 'CreateTex')) == 5 and not any(c[0] == 'CreatePS' for c in g) and e.r32(DO['GLOK']) == 1, 'nach Reset: Texturen neu, Shader weiter')
shaders = [e.r32(DO['GPS']), e.r32(DO['CPS']), e.r32(DO['PS']), e.r32(DO['TPS']), e.r32(DO['VPS']), e.r32(DO['LPS']), e.r32(DO['LCPS'])]; res = [e.r32(DO['GLRES'] + 4 * i) for i in range(len(o.GLRES_NAMES))]
RF.clear(); sp = run(0x69040B, 0x690410, {UC_X86_REG_ECX: DEV}, [1])
ok(RF == [(DEV, 1)] and all(OBJS[p]['refs'] == 0 for p in shaders + res) and e.r32(DO['GPSDEV']) == 0 and e.r32(DO['PSDEV']) == 0 and e.r32(DO['PS']) == 0 and e.r32(DO['TPS']) == 0 and e.r32(DO['VPS']) == 0 and e.r32(DO['LPS']) == 0 and e.r32(DO['LCPS']) == 0 and len(set(shaders)) == 7, 'Abbau (Argument 1): auch die 7 Pixelshader frei')
RF.clear(); run(0x6A337F, 0x6A3384, {UC_X86_REG_ECX: DEV}, [0]); ok(RF == [(DEV, 0)], 'verlorenes Geraet (0x6A337F): ebenso ueber glrel')
cs = post(); ok(sum(1 for c in cs if c[0] == 'CreatePS') == 7 and e.r32(DO['GLOK']) == 1, 'nach dem Abbau: alle 7 Shader neu')
# 25) Fehler: Textur laesst sich nicht anlegen -> nur duenne Linien
run(0x69029D, 0x6902A2, {UC_X86_REG_ECX: DEV}, [0])
FAIL['CreateTex'] = 2; cs = post(); g = nob(sym(glowpart(cs)))
made = [c for c in g if c[0] in ('CreateRT', 'CreateTex')]
ok(len(made) == 3 and e.r32(DO['GLFAIL']) == D3D and e.r32(DO['GLOK']) == 0 and all(e.r32(DO['GLRES'] + 4 * i) == 0 for i in range(len(o.GLRES_NAMES))), 'TEX1 fehlt: Angelegtes frei, GLFAIL = Geraet')
ok(not any(c[0] in ('GetDS', 'SetRT', 'StretchRect') for c in g) and OBJS[SURF['bb']]['refs'] == 1, 'TEX1 fehlt: kein Umschalten, Render-Target freigegeben')
refs, rc = ringpart(cs); u = units()
ok(rc == [x[3] | 0 for x in reversed(u)], 'TEX1 fehlt: duenne Linien in normaler Farbe')
cs = post(); ok(not any(c[0] == 'GetRT' for c in cs) and e.r32(DO['GLOK']) == 0, 'naechstes Bild: kein neuer Versuch auf diesem Geraet')
run(0x6A337F, 0x6A3384, {UC_X86_REG_ECX: DEV}, [0]); ok(e.r32(DO['GLFAIL']) == 0, 'Reset loescht GLFAIL (neuer Versuch danach)')
FAIL['CreateRT'] = 1; cs = post(); ok(e.r32(DO['GLFAIL']) == D3D and not any(c[0] == 'CreateTex' for c in cs), 'Render-Textur fehlt: GLFAIL, keine Texturen')
run(0x6A337F, 0x6A3384, {UC_X86_REG_ECX: DEV}, [0])
FAIL['StretchRect'] = 1; cs = post(); g = nob(sym(glowpart(cs)))
k = g.index(('StretchRect', 'MSRT', 0, 'TEX0S', 0, 0))
ok(g[k + 1:k + 6] == [('SetRT', 0, 'BB'), ('SetDS', 'DS'), ('SetVP', '&VP'), ('SRS', 7, 1), ('SRS', 52, 1)] and e.r32(DO['GLFAIL']) == D3D and e.r32(DO['GLOK']) == 0, 'StretchRect schlaegt fehl: alles zurueck, GLFAIL')
ok(not any(c == ('SetPS', 'CPS') for c in g) and OBJS[SURF['bb']]['refs'] == 1 and OBJS[SURF['ds']]['refs'] == 1, 'StretchRect-Fehler: kein Einblenden, Referenzen ausgeglichen')
run(0x6A337F, 0x6A3384, {UC_X86_REG_ECX: DEV}, [0])
FAIL['GetDS'] = 1; cs = post(); g = nob(sym(glowpart(cs)))
ok(not any(c[0] == 'SetRT' for c in g) and ('Release', 'BB') in g and e.r32(DO['GLOK']) == 0 and e.r32(DO['GLFAIL']) == 0, 'kein Tiefenpuffer: nichts umgeschaltet, Render-Target frei, kein GLFAIL')
FAIL['GetRT'] = 1; cs = post(); g = nob(sym(glowpart(cs)))
ok(not any(c[0] in ('GetDesc', 'GetDS') for c in g) and e.r32(DO['GLOK']) == 0, 'GetRenderTarget schlaegt fehl: nur duenne Linien')
FAIL['GetDesc'] = 0x8876086C; cs = post(); g = nob(sym(glowpart(cs)))
ok(not any(c[0] == 'GetDS' for c in g) and ('Release', 'BB') in g and OBJS[SURF['bb']]['refs'] == 1, 'GetDesc schlaegt fehl: Render-Target frei')
FAIL['CreatePS'] = 3; run(0x69040B, 0x690410, {UC_X86_REG_ECX: DEV}, [1]); cs = post()
ok(e.r32(DO['GLFAIL']) == D3D and e.r32(DO['GLOK']) == 0 and not any(c[0] == 'GetRT' for c in cs) and len(ringpart(cs)[0]) == 4, 'Pixelshader zum Einblenden fehlt: GLFAIL, nur duenne Linien')
run(0x6A337F, 0x6A3384, {UC_X86_REG_ECX: DEV}, [0]); run(0x69040B, 0x690410, {UC_X86_REG_ECX: DEV}, [1])
# 26) Schlachtzug ausserhalb der 5er-Gruppe: Schein wie alle
for k in FL: flag(k, 0)
flag('FRAID', 1); guid(0xBD1948, 0); guid(0xBD07B0, 0); guid(0xBD07A0, 0); raid([0x666])
cs = post(); g = nob(sym(glowpart(cs)))
ok(thins() == [0] and any(c[0] == 'GetRT' for c in cs) and e.r32(DO['GLOK']) == 1 and ringpart(cs)[1] == [] and ('SetPS', 'LCPS') in g and [struct.unpack('<I', c[5][16:20])[0] for c in sym(glowpart(cs)) if c[0] == 'DPUP' and c[4] == 20] == [o.CLASSCOL[5] | 0xFF000000],
   'Schlachtzug-Mitglied allein: Ring in Klassenfarbe in die Render-Textur, Schein und Linie aus TEX3 (aufgehellt im Shader), kein Viereck')
guid(0xBD1948, 0x444); raid([0x666, 0x444]); guid(0xBD07B0, 0x111); cs = post(); u = units(); g = nob(sym(glowpart(cs)))
ok([x[0] for x in u] == [0x666, 0x444, 0x111] and thins() == [0, 0, 0], 'gemischt: Priester, Paladin und Ziel mit Schein')
src = [c for c in g if c[0] == 'SRS' and c[1] == 57][:3]
ok(src == [('SRS', 57, 0x43), ('SRS', 57, 0x42), ('SRS', 57, 0x41)] and sum(1 for c in g if c[0] == 'DPUP' and c[4] == 20) == 3, 'Render-Textur mit Ziel, Paladin und Priester, keine Vierecke danach')
refs, rc = ringpart(cs); cl = [x[3] for x in u]
ok(refs == [] and g.count(('SetPS', 'LCPS')) == 1, 'Linien: alle drei aus TEX3 in einem Durchgang %s' % [hex(x) for x in rc])
guid(0xBD07B0, 0x666); cs = post(); u = units()
ok([x[0] for x in u] == [0x444, 0x666] and thins() == [0, 0] and ringpart(cs)[1] == [] and e.r32(DO['GLOK']) == 1, 'Schlachtzug-Mitglied als Ziel: Schein statt duenner Linie')
guid(0xBD07B0, 0); guid(0xBD07A0, 0x666); cs = post(); u = units()
ok([x[0] for x in u] == [0x444, 0x666] and thins() == [0, 0] and e.r32(DO['GLOK']) == 1, 'Schlachtzug-Mitglied unter der Maus: Schein')
guid(0xBD07A0, 0)
# 27) anderes Geraet: Shader und Texturen neu
D3D2 = H + 0x1800; e.w32(D3D2, VT); e.w32(DEV + 0x397C, D3D2); old = [e.r32(DO['GLRES'] + 4 * i) for i in range(len(o.GLRES_NAMES))]
cs = post(); g = nob(sym(glowpart(cs)))
ok(sum(1 for c in cs if c[0] == 'CreatePS') == 7 and sum(1 for c in g if c[0] in ('CreateRT', 'CreateTex')) == 5 and all(OBJS[p]['refs'] == 0 for p in old) and e.r32(DO['RTDEV']) == D3D2, 'neues Geraet: 7 Shader und Texturen neu, alte frei')
e.w32(DEV + 0x397C, D3D)
# 28) WoWs Zustands-Cache: nur die geaenderten Eintraege ungueltig, TEXTURETRANSFORMFLAGS 0-4 zurueck
HC = DEV + 0x3BC4
for k in range(0xB6): e.w32(HC + 4 * k, 0x1000 + k)
e.w32(HC + 4 * (0x52 + 2), 0xFFFFFFFF)
for i in range(5): mu.mem_write(DEV + 0x100C + 0x118 * i, b'\0')
for k in FL: flag(k, 0)
flag('FSELF', 1); guid(0xBD1948, 0); raid([]); guid(0xBD07B0, 0x111); guid(0xBD07A0, 0x222)
cs = post(); g = nob(sym(glowpart(cs)))
ok(e.r32(DO['GLOK']) == 1, 'Cache-Test: Schein gezeichnet')
bad = [k for k in range(0xB6) if (e.r32(HC + 4 * k) == 0xFFFFFFFF) != (k in o.HWCACHE_DIRTY) and k != 0x54]
ok(bad == [], 'nur SRCBLEND/DESTBLEND, Sampler 0, TEXCOORDINDEX 0-4, ALPHABLEND, ALPHATEST, FOG, ZWRITE, COLORWRITE, CULL, ZFUNC ungueltig %s' % [hex(k) for k in bad])
ok(e.r32(HC + 4 * 0xA6) == 0x10A6, 'D3DRS_AMBIENT (0xA6) im Cache unangetastet')
ok(all(e.r32(HC + 4 * (0x52 + i)) == (0xFFFFFFFF if i == 2 else 0x1052 + i) for i in range(5)), 'TEXTURETRANSFORMFLAGS im Cache unangetastet')
tt = [c for c in g if c[0] == 'TSS' and c[2] == 24]
ok(tt[:5] == [('TSS', i, 24, 0) for i in range(5)] and tt[5:] == [('TSS', i, 24, 0x1052 + i) for i in (0, 1, 3, 4)], 'TEXTURETRANSFORMFLAGS: fuer den Schein 0, danach wieder wie im Cache (Stufe 2 unbekannt) %s' % tt[5:])
dirty = [mu.mem_read(DEV + 0x100C + 0x118 * i, 1)[0] for i in range(5)]
ok(dirty == [0, 0, 1, 0, 0], 'Stufe 2 (Cache unbekannt): Texturmatrix beim Spiel als geaendert markiert %s' % dirty)
k = g.index(('SetPS', 'CPS'))
ok(('SRS', 168, 7) in g[k - 3:k] and g.index(('SRS', 168, 0xF)) > k, 'Einblenden schreibt nur RGB (COLORWRITE 7), danach wieder 0xF')
for k2 in range(0xB6): e.w32(HC + 4 * k2, 0)
# 29) SetRenderTarget schlaegt in einem Durchgang fehl -> kein Einblenden, alles zurueck
FAIL['SetRT'] = 4; cs = post(); g = nob(sym(glowpart(cs)))
ok(e.r32(DO['GLFAIL']) == D3D and e.r32(DO['GLOK']) == 0 and ('SetPS', 'CPS') not in g, 'SetRenderTarget-Fehler im Durchgang: GLFAIL, kein Einblenden')
ok(('SetRT', 0, 'BB') in g and ('SetDS', 'DS') in g and OBJS[SURF['bb']]['refs'] == 1 and OBJS[SURF['ds']]['refs'] == 1, 'SetRenderTarget-Fehler: Render-Target und Tiefenpuffer zurueck, Referenzen ausgeglichen')
k = g.index(('SetRT', 0, 'TEX2S'))
ok(g[k + 1:k + 3] == [('SetPS', 'VPS'), ('SetRT', 0, 'BB')] and not any(c[0] == 'DPUP' and c[4] == 56 for c in g[k:]), 'nach dem Fehler (nur noch SetPixelShader VPS) kein Zeichnen und kein weiterer Durchgang (keine Rueckkopplung TEX1 -> TEX1S)')
run(0x6A337F, 0x6A3384, {UC_X86_REG_ECX: DEV}, [0])
FAIL['SetRT'] = 2; cs = post(); g = nob(sym(glowpart(cs)))
k = g.index(('SetRT', 0, 'TEX3S'))
ok(e.r32(DO['GLFAIL']) == D3D and e.r32(DO['GLOK']) == 0 and g[k + 1:k + 5] == [('SetPS', 'TPS'), ('SetPS', 'GPS'), ('SetPS', 'VPS'), ('SetRT', 0, 'BB')] and not any(c[0] == 'DPUP' and c[4] == 56 for c in g[k:]),
   'SetRenderTarget-Fehler schon bei der Linie (TEX3S): kein weiterer Durchgang, kein Einblenden, GLFAIL')
ok(ringpart(cs)[1] == [x[3] for x in reversed(units())] and OBJS[SURF['bb']]['refs'] == 1 and OBJS[SURF['ds']]['refs'] == 1, 'dann duenne Linien als Vierecke in normaler Farbe, Referenzen ausgeglichen')
marked(2); vs = [c for c in calls if c[0] == 'SetVSConst']
ok(copy_offsets(vs) == [tuple(float(x) for x in xy) for xy in o.OFFS2], 'naechstes Bild nach dem Fehler: Kopien wieder 2 Pixel weit (GLFAIL)')
run(0x6A337F, 0x6A3384, {UC_X86_REG_ECX: DEV}, [0])
marked(2); vs = [c for c in calls if c[0] == 'SetVSConst']
ok(e.r32(DO['GLFAIL']) == 0 and copy_offsets(vs) == [tuple(float(x) for x in xy) for xy in o.OFFS], 'nach Reset (GLFAIL 0): Kopien wieder nach OFFS')
# 30) stencilfix: DrawPrimitive-Zweig (VA 0x6A3706) laeuft durch dieselbe Pruefung (smode) wie DIP
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
# 31) Begleiter: Pets der Gruppe mit Farbe/THIN des Besitzers (PETF 1), eigene nur zum Sortieren (PETF 2)
e.w32(DO['GLFAIL'], D3D)
P1O = H + 0xD0000; P2O = H + 0xD1000; P3O = H + 0xD2000; PXO = H + 0xD3000
P1M = H + 0xD8000; P2M = H + 0xD8400; P3M = H + 0xD8800; PXM = H + 0xD8C00
for ob, mdl in ((P1O, P1M), (P2O, P2M), (P3O, P3M), (PXO, PXM)): e.w32(ob + 0xB4, mdl); e.w32(ob + 0x98C, 0)
OBJ.update({0x881: P1O, 0x882: P2O, 0x883: P3O})
SELC.update({0x881: 0xFF00FF00, 0x882: 0xFF00FF00, 0x883: 0xFF00FF00})
UNIT, PLAYER = 0x9, 0x19
PETS = [(0x444, PLAYER, 0, 0), (0x884, UNIT, 0, 0), (0x881, UNIT, 0x38, 0x444), (0x885, PLAYER, 0x30, 0x444), (0x882, UNIT, 0x40, 0x333), (0x883, UNIT, 0x30, 0x666)]
def petf(): return [mu.mem_read(DO['PETF'] + c, 1)[0] for c in range(1, e.r32(DO['NUNITS']) + 1)]
def hx(lst): return [hex(x) for x in lst]
objlist(PETS)
raid([]); guid(0xBD1948, 0x444); guid(0xBD1950, 0); guid(0xBD1958, 0); guid(0xBD1960, 0); guid(0xBD07B0, 0x111); guid(0xBD07A0, 0x222)
flag('FPARTY', 1); newframe(); ST['mgr'] = 0; batch(OTHER); u = units()
ok([x[0] for x in u] == [0x444, 0x881, 0x111, 0x222] and petf() == [0, 1, 0, 0] and e.r32(DO['GRPN']) == 2, 'Gruppe: Pet des Paladins (SUMMONEDBY) nach ihm, zaehlt zur Gruppe (GRPN 2); Spieler (auch mit CHARMEDBY), fremde NPCs, eigenes Pet nicht %s' % hx([x[0] for x in u]))
ok(u[1][3] == o.CLASSCOL[2] and u[1][4] == 0 and thins()[1] == 0, 'Pet in der Farbe des Besitzers (Paladin), kein Puls, THIN 0 (Schein)')
r, _ = batch(P1M); ok(r == [2], 'Pet-Modell -> Kategorie 2 (wird umrandet)')
ok(ST.get('mgr', 0) == 1, 'Objektliste einmal je Bild')
flag('FHIDDEN', 1); newframe(); batch(OTHER); u = units()
ok([x[0] for x in u] == [0x444, 0x881, 0x333, 0x111, 0x222, 0x882] and petf() == [0, 1, 0, 0, 0, 2], 'nur wo verdeckt: eigenes Pet (CREATEDBY) am Ende nur zum Sortieren (PETF 2) %s %s' % (hx([x[0] for x in u]), petf()))
ok(thins()[5] == 1 and e.r32(DO['GRPN']) == 2 and e.r32(DO['SELFCAT']) == 3, 'eigenes Pet: THIN 1 (kein Schein), GRPN 2, SELFCAT 3')
r, _ = batch(P2M); ok(r == [0], 'eigenes Pet: keine Umrandung (CUR 0)')
r, _ = batch(P1M); ok(r == [2], 'Gruppen-Pet weiter umrandet')
calls.clear(); e.w32(DO['MARKED'], 1); run(POST, RET, regs, [RET])
dq = [k for k, c in enumerate(calls) if c[0] == 'DPUP']
refs = [[c[2] for c in calls[:k] if c[0] == 'SRS' and c[1] == 57][-1] for k in dq]
ok(refs == [0x45, 0x44, 0x43, 0x42, 0x41], 'Post: kein Viereck fuer das eigene Pet (PETF 2) %s' % hx(refs))
guid(0xBD07B0, 0x881); newframe(); batch(OTHER); u = units()
ok([x[0] for x in u] == [0x444, 0x333, 0x881, 0x222, 0x882] and petf() == [0, 0, 0, 0, 2] and e.r32(DO['GRPN']) == 1, 'Pet als Ziel: Ziel-Eintrag statt Pet-Eintrag %s %s' % (hx([x[0] for x in u]), petf()))
guid(0xBD07B0, 0x111)
# Einstellung des Testers: eigener Charakter nur wo verdeckt, durch Waende nur Gruppe (GMODE 2), Schlachtzug
flag('FWALLSGRP', 1); flag('FPARTY', 0); raid([0x666, 0x444, 0x333]); newframe(); batch(OTHER); u = units()
ok([x[0] for x in u] == [0x666, 0x444, 0x881, 0x883, 0x333, 0x111, 0x222, 0x882] and petf() == [0, 0, 1, 1, 0, 0, 0, 2], 'GMODE 2 im Schlachtzug: Pets beider Besitzer, eigenes nur zum Sortieren %s %s' % (hx([x[0] for x in u]), petf()))
ok(thins() == [0, 0, 0, 0, 0, 0, 0, 1] and u[3][3] == o.CLASSCOL[5] and gstate() == (4, 2, 0), 'Pet des Priesters in Priesterfarbe, alle mit Schein ausser dem eigenen Pet (nur Sortieren), GRPN 4 %s %s' % (thins(), gstate()))
marked(3); dips, seg = parts()
ok(len(dips) == 9 and (23, 5) in seg(dips[0], dips[1]), 'Gruppen-Pet bei GMODE 2 nur wo verdeckt (wie die Gruppe)')
flag('FHIDDEN', 0); newframe(); batch(OTHER); u = units()
ok([x[0] for x in u] == [0x666, 0x444, 0x881, 0x883, 0x111, 0x222, 0x882] and petf() == [0, 0, 1, 1, 0, 0, 2], 'GMODE 2 ohne eigenen Charakter: eigenes Pet trotzdem nur zum Sortieren (loest die Gruppe nicht aus) %s %s' % (hx([x[0] for x in u]), petf()))
flag('FPARTY', 1); newframe(); batch(OTHER); u = units()
ok([x[0] for x in u] == [0x444, 0x881, 0x111, 0x222] and gstate()[1] == 1, 'GMODE 1 (nur 5er-Gruppe) ohne eigenen Charakter: eigenes Pet nicht in der Tabelle %s' % hx([x[0] for x in u]))
flag('FPARTY', 0); flag('FHIDDEN', 1)
SPEC_OLD = SPEC
SPEC = [(0, P1M, 1), (0, PM, 3), (0, OTHER, 5), (0, P2M, 0), (0, MM, 7), (0, P3M, 2)]
newframe(); good, lst, types = dosort(order=(0, 1, 2, 3, 4, 5))
ok(good and lst == [2, 1, 4, 3, 0, 5] and e.r32(DO['NMARK']) == 5, 'Sortierung: Pets (0x11) nach allen anderen umrandeten Teilen (0x10), untereinander nach dem Spiel %s' % lst)
ok(types == [0] * 6 and SEEN and all(ta == 0 and tb == 0 for ta, tb in SEEN), 'Typen danach wieder 0, Vergleich sieht nie 0x10/0x11')
SPEC = SPEC_OLD
PXS = [(0x900 + i, UNIT, 0x38, 0x444) for i in range(50)]
for i in range(50): OBJ[0x900 + i] = PXO; SELC[0x900 + i] = 0xFF00FF00
objlist(PXS); flag('FWALLSGRP', 0); flag('FHIDDEN', 0); flag('FPARTY', 1); raid([]); newframe(); batch(OTHER); u = units()
ok(len(u) == 47 and [x[0] for x in u[:2]] == [0x444, 0x900] and u[44][0] == 0x900 + 43 and [x[0] for x in u[45:]] == [0x111, 0x222], 'viele Pets: nur bis Eintrag 45, Platz fuer Ziel und Mouseover (%d)' % len(u))
objlist(PETS[:3], term=0); newframe(); batch(OTHER); ok([x[0] for x in units()] == [0x444, 0x881, 0x111, 0x222], 'Listenende 0 statt Markierung')
MGRP[0] = 0; newframe(); batch(OTHER); ok([x[0] for x in units()] == [0x444, 0x111, 0x222], 'kein Objektmanager: keine Pets'); MGRP[0] = MGR
objlist(PETS); flag('FPARTY', 0); newframe(); batch(OTHER)
ok([x[0] for x in units()] == [0x111, 0x222], 'ohne Gruppe keine Pets')
# 32) Aussortierte Figuren (VA 0x7934C6): echte 0x793450 mit dem Haken
CULL = OUT + o.LAB['cull']
ok(D[fo(0x7934C6)] == 0xE9 and (struct.unpack('<i', D[fo(0x7934C7):fo(0x7934CB)])[0] + 0x7934CB) & 0xFFFFFFFF == CULL, 'Stelle 0x7934C6: jmp cull')
CB = 0x4F9F70; CBL = []
def cbstub(em, a): CBL.append((a[1], a[2])); return 1
e.stub(CB, cbstub, 5, 0)
OTHERCB = H + 0xEE000; mu.mem_write(OTHERCB, bytes([0xB8, 1, 0, 0, 0, 0xC3]))
M2S = H + 0xEF000
fw = lambda a, v: mu.mem_write(a, struct.pack('<f', v))
e.w32(0xCD8798, 0)
for i, pl in enumerate([(1, 0, 0), (-1, 0, 0), (0, 1, 0), (0, -1, 0), (0, 0, 1), (0, 0, -1)]):
    for j, v in enumerate(pl + (1000.0,)): fw(0xCDB168 + 16 * i + 4 * j, v)
for a_ in (0xCD8F5C, 0xCD8F60, 0xCD8F64): fw(a_, 0.0)
CENTS = [dict(guid=0x444, pos=(50, 0, 0)),               # 0 Gruppe, im Sichtkegel, weit weg
         dict(guid=0x999, pos=(10, 0, 0)),               # 1 nicht in der Tabelle
         dict(guid=0x444, pos=(5000, 0, 0)),             # 2 Gruppe, ausserhalb des Sichtkegels
         dict(guid=0x444, pos=(60, 0, 0), cb=OTHERCB),   # 3 kein Einheiten-Objekt
         dict(guid=0x111, pos=(70, 0, 0)),               # 4 Ziel (nicht Gruppe)
         dict(guid=0x881, pos=(20, 0, 0), parent=1),     # 5 Pet der Gruppe, angehaengtes Modell
         dict(guid=0x444, pos=(30, 0, 0), f7c=0x8804)]   # 6 Gruppe, Flag 4 an [E+0x7C]
def cullrun(ents=CENTS):
    for L in (0xCDB0A4, 0xCDB098): e.w32(L, 0xC8); e.w32(L + 4, L + 4); e.w32(L + 8, (L + 4) | 1)
    mu.mem_write(M2S, b'\0' * 0x100); CBL.clear(); E = []
    for i, en in enumerate(ents):
        ea = H + 0xE0000 + 0x1000 * i; ma = H + 0xE8000 + 0x400 * i
        mu.mem_write(ea, b'\0' * 0x100); mu.mem_write(ma, b'\0' * 0x300)
        e.w32(ea + 0x34, ma)
        for j, v in enumerate(en['pos'] + (1.0,)): fw(ea + 0x38 + 4 * j, v)
        mu.mem_write(ea + 0x25, b'\x02'); e.w32(ea + 0x7C, en.get('f7c', 0x8800)); e.w32(ea + 0x90, en.get('cb', CB))
        guid(ea + 0x98, en['guid'])
        e.w32(ma + 0x10, 0x2001); e.w32(ma + 0x28, M2S); e.w32(ma + 0x48, en.get('parent', 0))
        E.append((ea, ma))
        run(0x6DED60, RET, {UC_X86_REG_ECX: 0xCDB0A4}, [RET, ea])
    sp = run(0x793450, RET, {UC_X86_REG_EBX: 0x11, UC_X86_REG_ESI: 0x22, UC_X86_REG_EDI: 0x33, UC_X86_REG_EBP: 0x44}, [RET])
    good = mu.reg_read(UC_X86_REG_ESP) == sp + 4 and [mu.reg_read(r) for r in (UC_X86_REG_EBX, UC_X86_REG_ESI, UC_X86_REG_EDI, UC_X86_REG_EBP)] == [0x11, 0x22, 0x33, 0x44]
    vis = []; x = e.r32(0xCDB098 + 8)
    while x and not (x & 1) and len(vis) < 20: vis.append(x); x = e.r32(x + 0xC8 + 4)
    forced = sorted(i for i, (ea, ma) in enumerate(E) if ea in vis)
    empty = (e.r32(0xCDB0A4 + 8) & 1) == 1
    flags = [e.r32(ma + 0x10) for ea, ma in E]
    light = [e.r32(ma + 0x2AC) == 0x780CD0 and e.r32(ma + 0x2B0) == ea for ea, ma in E]
    return good and empty, forced, flags, light, list(CBL)
for k in FL: flag(k, 0)
raid([]); guid(0xBD1948, 0x444); guid(0xBD07B0, 0x111); guid(0xBD07A0, 0x222); objlist(PETS)
flag('FHIDDEN', 1); flag('FWALLSGRP', 1); newframe()
good, forced, flags, light, cbl = cullrun()
ok(good, 'Culling: Stack, Register erhalten, Liste der Aussortierten abgearbeitet')
ok(forced == [0, 5], 'GMODE 2: Gruppe und ihr Pet trotzdem sichtbar, nicht: fremd, ausserhalb des Sichtkegels, kein Einheiten-Objekt, Ziel, Flag 4 %s' % forced)
ok(flags[0] == 0x12009 and flags[5] == 0x22081 and light[0] and light[5] and not any(light[i] for i in (1, 2, 3, 4, 6)), 'erzwungen: Modell-Flags 0x10008 bzw. 0x20080 (angehaengt), Licht-Rueckruf wie im sichtbaren Zweig %s' % hx(flags))
ok(sorted(r for r, g in cbl if r == 5) == [5, 5] and all(r != 5 for r, g in cbl if g not in (0x444, 0x881)), 'Rueckruf mit Grund 5 (sichtbar) nur fuer die erzwungenen %s' % [(r, hex(g)) for r, g in cbl])
ok(e.r32(DO['VALID']) == 1 and [x[0] for x in units()][:2] == [0x444, 0x881], 'Tabelle schon beim Culling angelegt')
ST['obj'] = []; r, _ = batch(GM); ok(r == [1] and ST['obj'] == [], 'Batch im selben Bild nutzt dieselbe Tabelle')
flag('FWALLSGRP', 0); newframe(); good, forced, flags, light, cbl = cullrun()
ok(good and forced == [], 'ohne Durch-Waende-Gruppe (GMODE 0): nichts erzwungen %s' % forced)
flag('FWALLS', 1); newframe(); good, forced, flags, light, cbl = cullrun()
ok(good and forced == [4] and petf()[-2:] == [2, 2], 'durch Waende alle (ohne Gruppe): Ziel erzwungen, nicht die Pets nur zum Sortieren (PETF 2) %s' % forced)
flag('FWALLSGRP', 1); flag('FPARTY', 1); newframe(); good, forced, flags, light, cbl = cullrun()
ok(good and forced == [0, 4, 5], 'durch Waende alle + Gruppe: Gruppe, Pet, Ziel %s' % forced)
flag('FWALLS', 0); newframe(); good, forced, flags, light, cbl = cullrun()
ok(good and forced == [0, 5], 'GMODE 1 (Gruppe durch Waende): Gruppe und Pet %s' % forced)
e.w32(DEV + 0x1CC, 0); newframe(); good, forced, flags, light, cbl = cullrun(); e.w32(DEV + 0x1CC, 5)
ok(good and forced == [], 'ohne d3d9-Geraet: nichts erzwungen')
for k in FL: flag(k, 0)
# 33) agent_feet: nur wo verdeckt - alle Kopien auf der Vorderseite des Huellquaders (c4 = (ZC + SPHK * KZ) * c5)
F32 = lambda x: struct.unpack('<f', struct.pack('<f', x))[0]
def m2model(addr, box, rad, mat, parent=0, stamp=True, loaded=True, hdr=True):
    # CM2Model: +0x28 Szene, +0x3C Bild-Stempel, +0x2C CM2Shared (+8 Bit 0 geladen, +0x150 M2-Kopf), +0x48 Eltern, +0xF4 Modell->Sicht
    mu.mem_write(addr, b'\0' * 0x200); sh = addr + 0x200; hd = addr + 0x300
    mu.mem_write(sh, b'\0' * 0x100); mu.mem_write(hd, b'\0' * 0x100)
    e.w32(addr + 0x28, M2SC); e.w32(addr + 0x3C, FRAME if stamp else FRAME - 1); e.w32(addr + 0x2C, sh); e.w32(addr + 0x48, parent)
    e.w32(sh + 8, 0x101 if loaded else 0x100); e.w32(sh + 0x150, hd if hdr else 0)
    mu.mem_write(hd + 0xA0, struct.pack('<7f', *(box + (rad,))))
    mu.mem_write(addr + 0xF4, struct.pack('<16f', *mat))
def rot(ax, ay, az, sc, t):   # Zeilenvektoren: v_sicht = v_lokal * M, M = sc * Rx * Ry * Rz, letzte Zeile = Verschiebung
    def mm(a, b): return [[sum(a[i][k] * b[k][j] for k in range(3)) for j in range(3)] for i in range(3)]
    cx, sx, cy, sy, cz, sz = math.cos(ax), math.sin(ax), math.cos(ay), math.sin(ay), math.cos(az), math.sin(az)
    R = mm(mm([[1, 0, 0], [0, cx, sx], [0, -sx, cx]], [[cy, 0, -sy], [0, 1, 0], [sy, 0, cy]]), [[cz, sz, 0], [-sz, cz, 0], [0, 0, 1]])
    return [sc * R[0][0], sc * R[0][1], sc * R[0][2], 0, sc * R[1][0], sc * R[1][1], sc * R[1][2], 0, sc * R[2][0], sc * R[2][1], sc * R[2][2], 0, t[0], t[1], t[2], 1]
def gax(mat, P=P):   # g_i = c5.xyz . Zeile i (Aenderung von w je Einheit entlang der Modellachse i)
    m = [F32(x) for x in mat]; c5 = [F32(x) for x in P[12:16]]
    return [sum(c5[j] * m[4 * i + j] for j in range(3)) for i in range(3)]
def ebox(box, mat, full=False, P=P):   # Abstand der Vorderseite von der Mitte entlang c5 (mal |c5|)
    b = [F32(x) for x in box]; h = [F32(abs(b[3 + j] - b[j]) * 0.5) for j in range(3)]; g = gax(mat, P)
    return h[0] * abs(g[0]) + h[1] * abs(g[1]) + h[2] * (abs(g[2]) if full else max(g[2], 0.0))
def front(box, rad, mat, P=P, full=False):
    # Referenz wie der Code: Quader-Vorderseite + SPHM in NDC (z/w), 0 bei w <= 0 oder z/w < 0
    m = [F32(x) for x in mat]; b = [F32(x) for x in box]; c4 = [F32(x) for x in P[8:12]]; c5 = [F32(x) for x in P[12:16]]
    sc = [F32((b[j] + b[3 + j]) * 0.5) for j in range(3)]
    sv = [F32(sc[0] * m[j] + sc[1] * m[4 + j] + sc[2] * m[8 + j] + m[12 + j]) for j in range(3)]
    zt = F32(math.sqrt(c5[0] ** 2 + c5[1] ** 2 + c5[2] ** 2))
    zr = F32(F32(ebox(box, mat, full, P) / zt) + F32(o.SPHM))
    w = F32(F32(sum(c5[j] * sv[j] for j in range(3)) + c5[3]) - F32(zr * zt))
    z = F32(F32(sum(c4[j] * sv[j] for j in range(3)) + c4[3]) - F32(sum(c4[j] * c5[j] for j in range(3)) / zt * zr))
    if w <= 0: return 0.0
    q = F32(z / w)
    return q if q >= 0 else 0.0
def corners(box, full=False):   # Ecken, die zaehlen: alle 8 (Anbauteil) bzw. Unterseite und Mittelebene (Figur, Reittier)
    zs_ = (box[2], box[5]) if full else (box[2], (box[2] + box[5]) * 0.5)
    return [(x, y, z) for x in (box[0], box[3]) for y in (box[1], box[4]) for z in zs_]
def zw_of(pt, mat, P=P):   # z/w eines Modellpunkts
    v = [pt[0] * mat[j] + pt[1] * mat[4 + j] + pt[2] * mat[8 + j] + mat[12 + j] for j in range(3)]
    return sum(P[8 + j] * v[j] for j in range(3)) + P[11], sum(P[12 + j] * v[j] for j in range(3)) + P[15]
def front_bf(box, mat, full=False, P=P):
    # unabhaengig: vorderste der zaehlenden Ecken, dann SPHM entlang c5 zur Kamera (P: c4.xyz parallel zu c5.xyz)
    best = min(corners(box, full), key=lambda pt: zw_of(pt, mat, P)[1]); z, w = zw_of(best, mat, P)
    zt = math.sqrt(sum(P[12 + j] ** 2 for j in range(3))); a = sum(P[8 + j] * P[12 + j] for j in range(3)) / zt
    z -= o.SPHM * a; w -= o.SPHM * zt
    return 0.0 if w <= 0 or z / w < 0 else z / w
def kz_ref(P=P):
    A = (P[8] * P[12] + P[9] * P[13] + P[10] * P[14]) / (P[12] ** 2 + P[13] ** 2 + P[14] ** 2)
    return o.KAPPA * (P[11] / A - P[15])
def zc(): return struct.unpack('<f', struct.pack('<I', e.r32(DO['ZC'])))[0]
def fr(name): return struct.unpack('<f', struct.pack('<I', e.r32(DO[name])))[0]
def copies():   # c4-Zeilen der 8 Kopien und die Matrix danach
    vs = [c for c in calls if c[0] == 'SetVSConst']; return vs
def c4rows_are(vs, kz):   # c4 der Kopien = kz * c5, c5 und c2/c3 wie sonst
    return len(vs) == 9 and all(all(abs(v[4][8 + i] - kz * P[12 + i]) < 1e-6 for i in range(4)) and v[4][12:16] == P32[12:16] for v in vs[:8]) and vs[8][4] == P32
M2SC = H + 0xF0000; FRAME = 0x1234; mu.mem_write(M2SC, b'\0' * 0x100); e.w32(M2SC + 0x14, FRAME)
BODY = ((-0.5, -0.6, 0.0, 0.5, 0.6, 2.2), 1.3)
MB = rot(-1.4, 0.3, 0.5, 1.2, (0.7, -1.5, 10.0))
m2model(PM, BODY[0], BODY[1], MB)
raid([]); guid(0xBD1948, 0); guid(0xBD1950, 0); guid(0xBD1958, 0); guid(0xBD1960, 0); guid(0xBD07B0, 0x111); guid(0xBD07A0, 0x222); objlist([])
e.w32(POBJ + 0x98C, 0); e.w32(DO['GLFAIL'], 0)
flag('FHIDDEN', 1); newframe(); r, keep = batch(PM)
ok(r == [1] and keep and e.r32(DO['CURM']) == PM and e.r32(DO['SELFCAT']) == 1, 'Batch merkt das gezeichnete Modell (CURM = [esi+0x60]), ich = Kategorie 1')
fsw0 = mu.reg_read(UC_X86_REG_FPSW)
ok(marked(1), 'Quader: Stack und Register erhalten')
zb = front(*BODY, MB); kz = kz_ref(); vs = copies(); dips, seg = parts()
SK = o.SPHK
ok(0.9 < zb < 1.0 and abs(zc() - zb) < 1e-6 and abs(zb - front_bf(BODY[0], MB)) < 2e-6, 'ZC = Quader-Vorderseite der Figur + SPHM in NDC (%.6f, Referenz %.6f, Ecken %.6f)' % (zc(), zb, front_bf(BODY[0], MB)))
ok(abs(fr('KZ') - (zb + SK * kz)) < 1e-6 and e.r32(DO['ZA']) == 0, 'KZ = ZC + SPHK * KZ (%.6f), ZA = 0' % fr('KZ'))
ok(c4rows_are(vs, zb + SK * kz), 'Kopien: c4 = (ZC + SPHK * KZ) * c5 (z/w gleich fuer jeden Punkt), c5 unveraendert, danach Projektion original')
ok(copy_offsets(vs) == [tuple(float(x) for x in xy) for xy in o.OFFS], 'Kopien weiter nach OFFS verschoben (c2/c3) %s' % copy_offsets(vs))
ok(len(dips) == 9 and (23, 5) in seg(dips[0], dips[1]) and (14, 0) in seg(dips[0], dips[1]) and [v for (st, v) in seg(dips[0], dips[1]) if st == 54] == [1], 'Quader: weiter ZFUNC GREATER, ohne Tiefe, ZFAIL KEEP')
ok((mu.reg_read(UC_X86_REG_FPSW) >> 11) & 7 == (fsw0 >> 11) & 7, 'Quader: FPU-Stapel ausgeglichen')
# Probe: fuer beliebige Punkte im Sichtraum ist z/w der Kopien = ZC + KZ
c4n = vs[0][4][8:12]; c5n = vs[0][4][12:16]
pts = [(0.3, -1.2, 9.1), (-2.0, 0.5, 11.7), (0.0, 0.0, 10.4)]
ok(all(abs(sum(a * b for a, b in zip(c4n, pt + (1,))) / sum(a * b for a, b in zip(c5n, pt + (1,))) - (zb + SK * kz)) < 1e-6 for pt in pts), 'Kopien: z/w konstant = Quader-Vorderseite + SPHK * KZ')
# Vorderseite vor Unterseite und Mittelebene: jede dieser Ecken hat z/w >= ZC (die vorderste liegt SPHM dahinter)
zz_ = [zw_of(pt, MB) for pt in corners(BODY[0])]; zz_ = [z / w for z, w in zz_]
ok(all(q >= zb for q in zz_) and min(zz_) - zb < 0.01, 'jede Ecke von Unterseite und Mittelebene liegt hinter ZC, die vorderste knapp (Zuschlag SPHM)')
# Figur von unten (g2 > 0, MB): die Unterseite (was am Boden steht) zaehlt; von oben (g2 < 0, MDN): der Kopf zaehlt nicht
g_ = gax(MB); MDN = rot(-1.75, 0.3, 0.5, 1.2, (0.7, -1.5, 10.0)); gd_ = gax(MDN)
ok(gd_[2] < 0 < g_[2], 'Lage der Testmatrizen: MB von unten (g2 %.3f), MDN von oben (g2 %.3f)' % (g_[2], gd_[2]))
ok(abs(zb - front(*BODY, MB, full=True)) < 1e-9 and all(zw_of(pt, MB)[0] / zw_of(pt, MB)[1] >= zb for pt in corners(BODY[0], True)),
   'von unten: Unterseite zaehlt, alle 8 Ecken liegen hinter ZC')
m2model(PM, BODY[0], BODY[1], MDN); marked(1); zd_ = front(*BODY, MDN)
top_ = min(zw_of(pt, MDN)[0] / zw_of(pt, MDN)[1] for pt in corners(BODY[0], True))
ok(abs(zc() - zd_) < 1e-6 and abs(zd_ - front_bf(BODY[0], MDN)) < 2e-6 and top_ < zd_ and zd_ - front(*BODY, MDN, full=True) > 1e-4,
   'von oben: ZC ohne Kopf (%.6f), obere Ecken liegen davor (%.6f) und zaehlen nicht' % (zd_, top_))
m2model(PM, BODY[0], BODY[1], MB); marked(1)
# Waffe (Kind der Figur) naeher an der Kamera: ihr Quader zaehlt (CURM)
WM = H + 0xF1000; WEAPB = ((-0.1, -0.1, -0.8, 0.1, 0.1, 0.8), 0.82); MW = rot(2.9, 0.1, 0.0, 1.0, (0.5, 0.0, 8.0))
m2model(WM, WEAPB[0], WEAPB[1], MW, parent=PM)
r, _ = batch(WM); ok(r == [1] and e.r32(DO['CURM']) == WM, 'Waffe: Kategorie der Figur, CURM = Waffe')
marked(1); zw_ = front(*WEAPB, MW, full=True)
ok(zw_ < zb and abs(zc() - zw_) < 1e-6 and c4rows_are(copies(), zw_ + SK * kz), 'vorderste Vorderseite gewinnt: Waffe vor der Figur (%.6f < %.6f)' % (zw_, zb))
ok(gax(MW)[2] < 0 and abs(zw_ - front_bf(WEAPB[0], MW, True)) < 2e-6 and zw_ < front(*WEAPB, MW) - 1e-4, 'Anbauteil (nicht Figur/Reittier der Tabelle): ganze Hoehe zaehlt, auch von oben (Stab am Boden)')
m2model(WM, WEAPB[0], WEAPB[1], rot(2.9, 0.1, 0.0, 1.0, (0.5, 0.0, 12.0)), parent=PM); marked(1)
ok(abs(zc() - zb) < 1e-6, 'Waffe hinter der Figur: Vorderseite der Figur')
# Reittier: Quader des Reittiers (UNITS +12), auch wenn gerade die Figur gezeichnet wird
MNT = H + 0xF2000; MNTB = ((-1.5, -0.8, 0.0, 1.5, 0.8, 2.0), 2.2); MM_ = rot(-1.4, 0.3, 2.0, 1.0, (0.7, -2.5, 10.2))
m2model(MNT, MNTB[0], MNTB[1], MM_); e.w32(POBJ + 0x98C, MNT); m2model(PM, BODY[0], BODY[1], MB, parent=MNT)
newframe(); batch(PM); u = units()
ok(u[0][1:3] == (PM, MNT), 'Tabelle: Figur und Reittier')
marked(1); zm_ = front(*MNTB, MM_)
ok(zm_ < zb and abs(zc() - zm_) < 1e-6 and c4rows_are(copies(), zm_ + SK * kz), 'beritten: Vorderseite des Reittiers liegt vorn (%.6f)' % zm_)
hf_ = [zw_of(pt, MM_) for pt in corners(MNTB[0]) if pt[2] == MNTB[0][2]]
ok(all(z / w >= zm_ for z, w in hf_), 'Reittier: alle Ecken der Unterseite (Hufe am Boden) liegen hinter ZC')
e.w32(DO['CURM'], MNT); marked(1); ok(abs(zc() - zm_) < 1e-6, 'Teil des Reittiers: dieselbe Tiefe')
e.w32(POBJ + 0x98C, 0); m2model(PM, BODY[0], BODY[1], MB); newframe(); batch(PM)
# Pruefungen: nur bewegte, geladene Modelle mit Kopf und Radius > 0; sonst wie bisher (c4 + KZ * c5)
for what, kw in (('nicht in diesem Bild bewegt', dict(stamp=False)), ('nicht geladen', dict(loaded=False)), ('kein M2-Kopf', dict(hdr=False))):
    m2model(PM, BODY[0], BODY[1], MB, **kw); marked(1); vs = copies()
    ok(e.r32(DO['ZC']) == 0x7F800000 and e.r32(DO['ZA']) == 0x3F800000 and abs(fr('KZ') - kz) < 1e-9 and
       all(all(abs(v[4][8 + i] - (P[8 + i] + kz * P[12 + i])) < 1e-6 for i in range(4)) for v in vs[:8]), '%s: kein Quader, Kopien wie bisher c4 + KZ * c5' % what)
m2model(PM, BODY[0], 0.0, MB); marked(1); ok(e.r32(DO['ZC']) == 0x7F800000, 'Radius 0 (Kopf ungueltig): kein Quader')
m2model(PM, BODY[0], -1.0, MB); marked(1); ok(e.r32(DO['ZC']) == 0x7F800000, 'Radius negativ: kein Quader')
m2model(PM, BODY[0], float('nan'), MB); marked(1); ok(e.r32(DO['ZC']) == 0x7F800000 and e.r32(DO['ZA']) == 0x3F800000, 'Radius NaN: kein Quader (Kopf ungueltig)')
m2model(PM, BODY[0], float('inf'), MB); marked(1); ok(e.r32(DO['ZC']) == 0x7F800000 and e.r32(DO['ZA']) == 0x3F800000, 'Radius unendlich: kein Quader (Kopf ungueltig)')
m2model(PM, (float('nan'),) + BODY[0][1:], BODY[1], MB); marked(1); ok(e.r32(DO['ZC']) in (0x7F800000, 0) and (mu.reg_read(UC_X86_REG_FPSW) >> 11) & 7 == (fsw0 >> 11) & 7, 'Quader mit NaN: keine Vorderseite oder 0 (kein Rand), FPU-Stapel ausgeglichen')
e.w32(DO['CURM'], 0); e.w32(POBJ + 0xB4, 0); newframe(); batch(OTHER)
ok(units()[0][1] == 0, 'Figur ohne Modell in der Tabelle')
marked(1); ok(e.r32(DO['ZC']) == 0x7F800000 and e.r32(DO['ZA']) == 0x3F800000, 'kein Modell (0): kein Quader, wie bisher')
e.w32(POBJ + 0xB4, PM)
# Kamera im Quader bzw. Vorderseite vor der nahen Ebene: ZC 0, Kopien bei z/w = SPHK * KZ < 0 (ganz abgeschnitten, kein Rand)
cz_ = sum(x * m for x, m in zip((0.0, 0.0, 1.1), rot(-1.4, 0.3, 0.5, 1.2, (0, 0, 0))[2:12:4]))   # z-Anteil der Mitte
eb_ = ebox(BODY[0], MB) + o.SPHM   # Vorderseite vor der Mitte (|c5| = 1)
m2model(PM, BODY[0], BODY[1], rot(-1.4, 0.3, 0.5, 1.2, (0.1, 0.2, 0.5 * eb_ - cz_))); newframe(); batch(PM); marked(1)
ok(e.r32(DO['ZC']) == 0 and c4rows_are(copies(), SK * kz) and kz < 0, 'Kamera im Quader (w <= 0): ZC 0, z/w der Kopien = SPHK * KZ < 0')
tz_ = 0.05 - cz_ + eb_   # Vorderseite bei w = 0.05 (nahe Ebene bei w = 0.0999)
m2model(PM, BODY[0], BODY[1], rot(-1.4, 0.3, 0.5, 1.2, (0.1, 0.2, tz_))); marked(1)
w_ = tz_ + cz_ - eb_
ok(0 < w_ < 0.0999 and e.r32(DO['ZC']) == 0 and c4rows_are(copies(), SK * kz), 'Vorderseite vor der nahen Ebene (w = %.3f): z/w < 0 -> ZC 0' % w_)
# andere Modi: kein zfront
m2model(PM, BODY[0], BODY[1], MB); newframe(); batch(PM)
e.w32(DO['ZC'], 0x12345678); marked(2); vs = copies()
ok(e.r32(DO['ZC']) == 0x12345678 and e.r32(DO['ZA']) == 0x3F800000 and e.r32(DO['KZ']) == 0 and all(v[4][8:12] == P32[8:12] for v in vs[:8]), 'Ziel (normal): kein Quader, c4 der Kopien unveraendert')
flag('FWALLS', 1); e.w32(DO['ZC'], 0x12345678); marked(2)
ok(e.r32(DO['ZC']) == 0x12345678 and e.r32(DO['KZ']) == 0, 'durch Waende: kein Quader'); flag('FWALLS', 0)
# Gruppe bei GMODE 2: Quader des Gruppenmitglieds
GB = ((-0.6, -0.6, 0.0, 0.6, 0.6, 2.6), 1.5); MG = rot(-1.3, 0.0, 1.0, 1.0, (-3.0, -1.0, 25.0))
m2model(GM, GB[0], GB[1], MG); flag('FHIDDEN', 0); flag('FWALLSGRP', 1); guid(0xBD1948, 0x444)
newframe(); batch(GM); u = units()
ok([x[0] for x in u] == [0x444, 0x111, 0x222] and gstate() == (1, 2, 0) and e.r32(DO['CURM']) == GM, 'GMODE 2: Gruppenmitglied Kategorie 1, CURM = sein Modell')
marked(1); zg = front(*GB, MG)
ok(abs(zc() - zg) < 1e-6 and c4rows_are(copies(), zg + SK * kz), 'GMODE 2: Kopien auf seiner Quader-Vorderseite (%.6f)' % zg)
# Sicherheit: Tabellen-Zeiger werden nie gelesen - nur das gezeichnete Modell und seine Eltern-Kette
flag('FWALLSGRP', 0); flag('FHIDDEN', 1); guid(0xBD1948, 0); m2model(PM, BODY[0], BODY[1], MB); newframe(); batch(PM)
ent = DO['UNITS'] + 24 * (e.r32(DO['SELFCAT']) - 1)
e.w32(ent + 12, 0x7FFF0000)   # Reittier-Zeiger in der Tabelle zeigt auf ungemappten Speicher
try:
    marked(e.r32(DO['SELFCAT'])); crash = False
except UcError:
    crash = True
ok(not crash and abs(zc() - zb) < 1e-6, 'veralteter Reittier-Zeiger in der Tabelle (nicht in der Eltern-Kette) wird nicht gelesen')
e.w32(ent + 12, 0)
VEH = H + 0xF3000; VEHB = ((-4.0, -4.0, 0.0, 4.0, 4.0, 5.0), 6.0); MV_ = rot(-1.4, 0.3, 0.5, 1.0, (0.7, -1.5, 9.0))
m2model(VEH, VEHB[0], VEHB[1], MV_); m2model(PM, BODY[0], BODY[1], MB, parent=VEH); marked(e.r32(DO['SELFCAT']))
ok(front(*VEHB, MV_) < zb and abs(zc() - zb) < 1e-6, 'Eltern-Modell, das nicht Figur/Reittier der Einheit ist (Fahrzeug): Quader zaehlt nicht')
m2model(PM, BODY[0], BODY[1], MB)
# SPHK und SPHM aus dem Datenbereich
ok(fr('SPK') == F32(o.SPHK) and o.SPHK == 0.1 and fr('SPM') == F32(o.SPHM) and o.SPHM == 0.05, 'SPHK = 0.1 und SPHM = 0.05 Yards im Datenbereich')
for k in FL: flag(k, 0)
guid(0xBD1948, 0)
# 34) Kollisionsstrahlen (agent_ray): rayframe vor RenderWorld, Strahl-Tabelle, zhit beim Zeichnen
LB = {k: OUT + v for k, v in o.LAB.items()}
def f32b(a, n=1): return struct.unpack('<%df' % n, bytes(mu.mem_read(a, 4 * n)))
def fpu_top(): return (mu.reg_read(UC_X86_REG_FPSW) >> 11) & 7
WF = H + 0xD0000; CAM = H + 0xD1000; VTU = H + 0xD2000; GP = H + 0xD2800
mu.mem_write(WF, b'\0' * 0x8000); mu.mem_write(CAM, b'\0' * 0x100)
e.w32(0xB7436C, WF); e.w32(WF + 0x7E20, CAM)
def camera(x, y, z): mu.mem_write(CAM + 8, struct.pack('<3f', x, y, z))
mu.mem_write(0xBD0792, b'\x01'); mu.mem_write(0xBD0790, b'\x00')
TR = []; TLFN = [lambda st, en, fr: None]
def traceline(em, a):
    st = f32b(a[0], 3); en = f32b(a[1], 3); fr = f32b(a[3])[0]
    TR.append(dict(st=st, en=en, hit=a[2], fr=fr, fl=a[4], info=a[5]))
    h = TLFN[0](st, en, fr)
    if h is not None and h <= fr:
        mu.mem_write(a[3], struct.pack('<f', h)); return 1
    return 0x12345600   # AL = 0, Rest beliebig
e.stub(0x7A3B70, traceline, 6, 0)
POS = {}
def getpos(em, a):
    ob = mu.reg_read(UC_X86_REG_ECX); ST.setdefault('gp', []).append(ob)
    mu.mem_write(a[0], struct.pack('<3f', *POS[ob]))
e.w32(VTU + 0x2C, GP); e.stub(GP, getpos, 1, 4)
for ob in (POBJ, GOBJ, TOBJ, MOBJ, ROBJ): e.w32(ob, VTU)
def height(ob, h): mu.mem_write(ob + 0x854, struct.pack('<f', h))
def rq(cat): return mu.mem_read(DO['RAYREQ'] + cat, 1)[0]
def slot(cat):
    b = DO['RT'] + 48 * (cat - 1); st = bytes(mu.mem_read(b + 8, 4))
    return dict(g=(e.r32(b), e.r32(b + 4)), state=st[0], free=st[1], n=st[2], pts=[f32b(b + 12 + 12 * k, 3) for k in range(3)])
def rayframe():
    TR.clear(); ST['obj'] = []; ST['gp'] = []; t0 = fpu_top()
    e.call(LB['rayframe']); return fpu_top() == t0
def near(a, b, tol=1e-4): return all(abs(x - y) <= tol * max(1.0, abs(y)) for x, y in zip(a, b))
# Bild mit "nur wo verdeckt" fuer mich: Anforderung beim Zeichnen
for k in FL: flag(k, 0)
guid(0xBD1948, 0); m2model(PM, BODY[0], BODY[1], MB); e.w32(POBJ + 0x98C, 0)
flag('FHIDDEN', 1); newframe(); batch(PM); SC_ = e.r32(DO['SELFCAT']); NU = e.r32(DO['NUNITS'])
ok(SC_ >= 1 and units()[SC_ - 1][0] == 0x333 and all(rq(c) == 0 for c in range(64)), 'Bildbeginn: RAYREQ leer, ich = Kategorie %d' % SC_)
marked(SC_); ok(rq(SC_) == 1 and sum(rq(c) for c in range(64)) == 1, 'Kopien nur wo verdeckt: RAYREQ[ich] = 1')
TC_ = [i + 1 for i, x in enumerate(units()) if x[0] == 0x111][0]
marked(TC_); ok(rq(TC_) == 0, 'Ziel (normal gezeichnet): keine Anforderung')
# Strahlen: 3 je Einheit von der Kamera zu Knie/Brust/Kopf, Ende RAYS Yards vor dem Ziel, Flags, kein hitOut/hitInfo
POS[POBJ] = (100.0, 200.0, 10.0); height(POBJ, 2.0); camera(90.0, 204.0, 15.0)
e.w32(DO['RCUR'], 0); seq0 = e.r32(DO['RAYSEQ'])
ok(rayframe(), 'rayframe: FPU-Stapel ausgeglichen')
Cm = (90.0, 204.0, 15.0)
def exp_rays(pos, h, ks):
    out = []
    for k in ks:
        T = (pos[0], pos[1], F32(F32(k) * F32(h) + F32(pos[2]))); L = math.dist(T, Cm)
        out.append((T, L, 1 - o.RAYS / L))
    return out
EX = exp_rays(POS[POBJ], 2.0, o.KFR)
ok(len(TR) == 3 and all(near(t['st'], Cm) and near(t['en'], x[0]) and abs(t['fr'] - x[2]) < 1e-6 and t['fl'] == 0x100111 and t['hit'] == 0 and t['info'] == 0 for t, x in zip(TR, EX)),
   '3 Strahlen Kamera -> Knie/Brust/Kopf (z %s), frac = 1 - 0.4/L, Flags 0x100111, ohne hitOut/hitInfo' % [round(t['en'][2], 3) for t in TR])
ok(ST['obj'] == [0x333] and ST['gp'] == [POBJ] and e.r32(DO['RAYSEQ']) == seq0 + 1 and e.r32(DO['RBUD']) == o.RAYB - 3, 'Objekt frisch per GUID, Fusspunkt ueber vtbl+0x2C, RAYSEQ + 1, Budget - 3')
sl = slot(SC_); ok(sl['g'] == (0x333, 0x0F000000) and sl['state'] == 0 and sl['n'] == 0, 'kein Treffer: frei, Eintrag mit GUID')
# Treffer am Brust-Strahl bei frac 0.5: blockiert, Punkt RAYD hinter dem Treffer
TLFN[0] = lambda st, en, fr: 0.5 if abs(en[2] - EX[1][0][2]) < 1e-4 else None
rayframe(); sl = slot(SC_); T, L, _ = EX[1]; fp = 0.5 + o.RAYD / L
ok(sl['state'] == 1 and sl['free'] == 0 and sl['n'] == 1 and near(sl['pts'][0], tuple(Cm[j] + (T[j] - Cm[j]) * fp for j in range(3))), 'Treffer: sofort blockiert, Punkt %.3f Yards hinter dem Treffer gemerkt' % o.RAYD)
TLFN[0] = lambda st, en, fr: 0.9
rayframe(); sl = slot(SC_); ok(sl['state'] == 1 and sl['n'] == 3, 'alle 3 Strahlen blockiert: 3 Punkte')
# frei erst nach RAYFREE freien Pruefungen
TLFN[0] = lambda st, en, fr: None
seq = []
for i in range(o.RAYFREE):
    rayframe(); sl = slot(SC_); seq.append((sl['state'], sl['free'], sl['n']))
ok(seq == [(1, 1, 3), (1, 2, 3), (0, 0, 0)] and o.RAYFREE == 3, 'frei erst nach 3 freien Pruefungen, Punkte bleiben bis dahin %s' % seq)
# Figur tritt vor die Mauer (naeher zur Kamera): gemerkte Punkte hinter ihr fallen bei freien Pruefungen weg
TLFN[0] = lambda st, en, fr: 0.9; rayframe(); ok(slot(SC_)['n'] == 3, '(blockiert, 3 Punkte)')
POS[POBJ] = (95.0, 202.0, 10.0); TLFN[0] = lambda st, en, fr: None; rayframe(); sl = slot(SC_)
ok(sl['state'] == 1 and sl['free'] == 1 and sl['n'] == 0, 'Figur vor die Mauer getreten: noch blockiert, Punkte hinter ihr verworfen')
POS[POBJ] = (100.0, 200.0, 10.0); TLFN[0] = lambda st, en, fr: 0.9; rayframe(); ok(slot(SC_)['n'] == 3, '(wieder 3 Punkte)')
TLFN[0] = lambda st, en, fr: None; rayframe(); sl = slot(SC_)
ok(sl['state'] == 1 and sl['n'] == 3, 'Figur bleibt stehen, frei geprueft: Punkte vor ihr bleiben')
for i in range(o.RAYFREE): rayframe()
ok(slot(SC_)['state'] == 0, '(frei)')
# Waechter: nicht in der Welt, Laden, kein WorldFrame, keine Kamera, Kamera nicht endlich
def guard(desc, setup, undo):
    setup(); s0 = e.r32(DO['RAYSEQ']); rayframe(); undo()
    ok(TR == [] and e.r32(DO['RAYSEQ']) == s0, 'kein Strahl: %s' % desc)
guard('nicht in der Welt', lambda: mu.mem_write(0xBD0792, b'\0'), lambda: mu.mem_write(0xBD0792, b'\x01'))
guard('Laden aktiv', lambda: mu.mem_write(0xBD0790, b'\x01'), lambda: mu.mem_write(0xBD0790, b'\0'))
guard('kein WorldFrame', lambda: e.w32(0xB7436C, 0), lambda: e.w32(0xB7436C, WF))
guard('keine Kamera', lambda: e.w32(WF + 0x7E20, 0), lambda: e.w32(WF + 0x7E20, CAM))
for j, v in ((0, float('nan')), (1, float('inf')), (2, float('-inf'))):
    guard('Kamera %s in Koordinate %d' % (v, j), lambda: mu.mem_write(CAM + 8 + 4 * j, struct.pack('<f', v)), lambda: camera(*Cm))
# Laenge: unter 1 bzw. ueber 150 Yards kein Strahl (Budget bleibt)
camera(100.0, 200.0, 12.4); rayframe()
ok([round(t['en'][2], 2) for t in TR] == [10.6, 11.2] and e.r32(DO['RBUD']) == o.RAYB - 2, 'Kamera dicht am Kopf (L < 1): nur Knie und Brust, Budget - 2')
camera(300.0, 200.0, 15.0); rayframe(); ok(TR == [] and e.r32(DO['RBUD']) == o.RAYB, 'ueber 150 Yards: kein Strahl')
camera(*Cm)
# Hoehe ausserhalb 0.3..40 (oder NaN): 2 Yards; beritten: Anteile 0.55/0.75/0.95
for hv in (0.1, 50.0, float('nan'), -2.0):
    height(POBJ, hv); rayframe()
    ok([round(t['en'][2], 4) for t in TR] == [round(x[0][2], 4) for x in exp_rays(POS[POBJ], 2.0, o.KFR)], 'Hoehe %s -> 2 Yards' % hv)
height(POBJ, 3.0); rayframe(); ok([round(t['en'][2], 4) for t in TR] == [round(x[0][2], 4) for x in exp_rays(POS[POBJ], 3.0, o.KFR)], 'Hoehe 3 Yards: Knie 0.9, Brust 1.8, Kopf 2.7 ueber dem Fusspunkt')
e.w32(POBJ + 0x98C, MNT); rayframe(); e.w32(POBJ + 0x98C, 0)
ok([round(t['en'][2], 4) for t in TR] == [round(x[0][2], 4) for x in exp_rays(POS[POBJ], 3.0, o.KFRM)], 'beritten: 0.55/0.75/0.95 der Hoehe')
height(POBJ, 2.0)
# Objekt nicht mehr da: frei, kein Strahl
TLFN[0] = lambda st, en, fr: 0.9; rayframe(); ok(slot(SC_)['state'] == 1, '(wieder blockiert)')
OBJ.pop(0x333); TLFN[0] = lambda st, en, fr: None; rayframe(); OBJ[0x333] = POBJ
sl = slot(SC_); ok(TR == [] and sl['state'] == 0 and sl['n'] == 0 and ST['obj'] == [0x333], 'GUID ohne Objekt: frei, kein Strahl, nichts gelesen')
# andere GUID im Eintrag: neu angelegt
b = DO['RT'] + 48 * (SC_ - 1); e.w32(b, 0x999); mu.mem_write(b + 8, b'\x01\x02\x03\x00')
rayframe(); sl = slot(SC_); ok(sl['g'] == (0x333, 0x0F000000) and sl['state'] == 0 and sl['n'] == 0, 'andere GUID im Eintrag: neu angelegt')
# Budget und reihum: 8 Einheiten mit Anforderung -> 6 pro Bild (18 Strahlen), dann weiter
NX = [(0x900 + i, H + 0xE0000 + 0x1000 * i) for i in range(8)]
for i, (g, ob) in enumerate(NX):
    mu.mem_write(ob, b'\0' * 0x1000); e.w32(ob, VTU); POS[ob] = (100.0 + i, 210.0, 10.0); height(ob, 2.0); OBJ[g] = ob
    u = DO['UNITS'] + 24 * i; e.w32(u, g); e.w32(u + 4, 0x0F000000)
e.w32(DO['NUNITS'], 8); mu.mem_write(DO['RAYREQ'], b'\0' + b'\x01' * 8 + b'\0' * 55); e.w32(DO['RCUR'], 0)
rayframe(); f1 = list(ST['obj']); n1 = len(TR); rayframe(); f2 = list(ST['obj']); n2 = len(TR)
ok(n1 == 18 and n2 == 18 and f1 == [0x900 + i for i in range(6)] and f2 == [0x906, 0x907, 0x900, 0x901, 0x902, 0x903], 'Budget 18 Strahlen: 6 Einheiten pro Bild, reihum weiter %s / %s' % ([hex(x) for x in f1], [hex(x) for x in f2]))
mu.mem_write(DO['RAYREQ'] + 2, b'\0\0\0\0'); e.w32(DO['RCUR'], 0); rayframe()
ok(ST['obj'] == [0x900, 0x905, 0x906, 0x907] and len(TR) == 12, 'ohne Anforderung uebersprungen (kein Budget), jede Einheit hoechstens einmal pro Bild')
e.w32(DO['NUNITS'], 0); rayframe(); ok(TR == [] and ST['obj'] == [], 'keine Einheiten: nichts')
e.w32(DO['NUNITS'], 60); rayframe(); ok(TR == [] and ST['obj'] == [], 'NUNITS ueber 48: nichts')
for g, ob in NX: OBJ.pop(g)
# Hook bei VA 0x4FB036: call raystub statt 0x7E6480; raystub ruft das Original, dann die Strahlen, Register erhalten
rel = struct.unpack('<i', D[0x4FB037 - 0x400C00:0x4FB03B - 0x400C00])[0]
ok(D[0x4FB036 - 0x400C00] == 0xE8 and 0x4FB03B + rel == LB['raystub'], 'VA 0x4FB036: call raystub')
ORD = []
e.stub(0x7E6480, lambda em, a: ORD.append('orig'), 0, 0)
newframe(); batch(PM); marked(SC_); POS[POBJ] = (100.0, 200.0, 10.0)
TLFN[0] = lambda st, en, fr: (ORD.append('trace'), None)[1]
TR.clear(); t0 = fpu_top()
run(0x4FB036, 0x4FB03B, {UC_X86_REG_ESI: 0x5151, UC_X86_REG_EDI: 0x7171, UC_X86_REG_EBX: 0x8181, UC_X86_REG_EBP: 0x200E8000})
ok(ORD[:1] == ['orig'] and ORD.count('trace') == 3 and [mu.reg_read(r) for r in (UC_X86_REG_ESI, UC_X86_REG_EDI, UC_X86_REG_EBX, UC_X86_REG_EBP, UC_X86_REG_ESP)] == [0x5151, 0x7171, 0x8181, 0x200E8000, 0x200F0000] and fpu_top() == t0,
   'Hook: erst 0x7E6480, dann 3 Strahlen; ESI/EDI/EBX/EBP/ESP und FPU erhalten')
# --- Zeichnen (zhit): blockiert -> die tiefste gemerkte Stelle ersetzt KZ, wenn sie weiter hinten liegt ---
# Welt -> Sicht: v = (p - C) * R (R Drehung, Kamera im Ursprung), Projektion P (w = v.z)
def mrot(ax, ay, az):
    m = rot(ax, ay, az, 1.0, (0, 0, 0)); return [m[0:3], m[4:7], m[8:11]]
def mmul(a, b): return [[sum(a[i][k] * b[k][j] for k in range(3)) for j in range(3)] for i in range(3)]
def vmul(v, m): return [sum(v[k] * m[k][j] for k in range(3)) for j in range(3)]
CW = (50.0, -20.0, 30.0); RV = mrot(0.3, -0.2, 0.7)
UW = [CW[j] + x for j, x in enumerate(vmul([0.3, -0.5, 12.0], [list(r) for r in zip(*RV)]))]   # Einheit 12 Yards vor der Kamera
RW = mrot(0.1, -0.05, 1.1); SW = 1.15; W3 = [[SW * x for x in r] for r in RW]
MV3 = mmul(W3, RV); MVt = vmul([UW[j] - CW[j] for j in range(3)], RV)
def setmodel(m):
    m2model(m, BODY[0], BODY[1], [MV3[0][0], MV3[0][1], MV3[0][2], 0, MV3[1][0], MV3[1][1], MV3[1][2], 0, MV3[2][0], MV3[2][1], MV3[2][2], 0, MVt[0], MVt[1], MVt[2], 1])
    mu.mem_write(m + 0xB4, struct.pack('<16f', *(W3[0] + [0] + W3[1] + [0] + W3[2] + [0] + list(UW) + [1])))
setmodel(PM)
def zw_world(p):   # z/w eines Weltpunkts
    v = vmul([p[j] - CW[j] for j in range(3)], RV); return (1.001 * v[2] - 0.1) / v[2]
def setslot(cat, g, state, pts):
    b = DO['RT'] + 48 * (cat - 1); e.w32(b, g); e.w32(b + 4, 0x0F000000); mu.mem_write(b + 8, bytes([state, 0, len(pts), 0]))
    for k, p in enumerate(pts): mu.mem_write(b + 12 + 12 * k, struct.pack('<3f', *p))
def rayok(on):   # RAYOK fuer das naechste Bild: rayframe lief (RAYSEQ geaendert) oder nicht
    if on: e.w32(DO['RAYSEQ'], e.r32(DO['RAYSEQ']) + 1)
    newframe(); batch(PM)
fwd = [list(r) for r in zip(*RV)][2]   # Blickrichtung in Welt
def along(d): return [UW[j] + 1.1 * [list(r) for r in zip(*RV)][2][j] * 0 + 0 for j in range(3)]
UC = [UW[j] + 1.1 * W3[2][j] / SW * SW for j in range(3)]   # Mitte des Koerpers (Hoehe 1.1 im Modell, mal Skalierung)
rayok(True); ok(e.r32(DO['RAYOK']) == 1, 'RAYOK: rayframe lief seit dem letzten Bild')
marked(SC_); zb_ = zc(); kzb = fr('KZ'); kz_ = kz_ref()
ok(e.r32(DO['ZMOD']) == PM and abs(kzb - (zb_ + o.SPHK * kz_)) < 1e-6, 'frei: Quader wie bisher (ZMOD = Figur)')
# Mauer 0.15 Yards vor der Koerpermitte auf der Sichtlinie (innerhalb der Quader-Vorderseite)
WALL = [UC[j] - 0.15 * fwd[j] for j in range(3)]
setslot(SC_, 0x333, 1, [WALL]); marked(SC_); zr_ = zw_world(WALL)
ok(zr_ > zb_ + o.SPHK * kz_ and abs(fr('KZ') - zr_) < 2e-6 and c4rows_are(copies(), fr('KZ')), 'blockiert, Mauer dicht vor der Figur: Kopien auf ihrer Tiefe (%.6f statt %.6f)' % (fr('KZ'), kzb))
FARW = [CW[j] + 3.0 * fwd[j] for j in range(3)]
setslot(SC_, 0x333, 1, [FARW]); marked(SC_); ok(abs(fr('KZ') - kzb) < 1e-7, 'blockiert, Hindernis weit vorn: Quader bleibt (weiter hinten)')
setslot(SC_, 0x333, 1, [FARW, WALL, [CW[j] + 6.0 * fwd[j] for j in range(3)]]); marked(SC_)
ok(abs(fr('KZ') - zr_) < 2e-6, '3 Punkte: der hinterste zaehlt')
setslot(SC_, 0x333, 0, [WALL]); marked(SC_); ok(abs(fr('KZ') - kzb) < 1e-7, 'frei (Zustand 0): Punkte zaehlen nicht')
setslot(SC_, 0x334, 1, [WALL]); marked(SC_); ok(abs(fr('KZ') - kzb) < 1e-7, 'andere GUID im Eintrag: zaehlt nicht')
setslot(SC_, 0x333, 1, [[CW[j] - 2.0 * fwd[j] for j in range(3)]]); marked(SC_); ok(abs(fr('KZ') - kzb) < 1e-7, 'Punkt hinter der Kamera (w <= 0): zaehlt nicht')
setslot(SC_, 0x333, 1, [WALL]); rayok(False); marked(SC_); ok(e.r32(DO['RAYOK']) == 0 and abs(fr('KZ') - kzb) < 1e-7, 'rayframe lief nicht (RAYOK 0): Quader wie bisher')
rayok(True); setslot(SC_, 0x333, 1, [WALL]); mu.mem_write(PM + 0xB4, b'\0' * 48); marked(SC_)
ok(abs(fr('KZ') - kzb) < 1e-7 and (mu.reg_read(UC_X86_REG_FPSW) >> 11) & 7 == fsw0 >> 11 & 7, 'Welt-Matrix 0 (Division durch 0): Punkt verworfen, FPU ausgeglichen')
setmodel(PM); marked(SC_); ok(abs(fr('KZ') - zr_) < 2e-6, '(wieder) Mauer zaehlt')
# Waffe als gezeichnetes Teil: ZMOD = Figur (Eltern), nicht die Waffe
m2model(WM, WEAPB[0], WEAPB[1], MW, parent=PM); e.w32(DO['CURM'], WM); marked(SC_)
ok(e.r32(DO['ZMOD']) == PM and abs(fr('KZ') - zr_) < 2e-6, 'Waffe gezeichnet: Umrechnung ueber die Figur (ZMOD = Eltern)')
# andere Modi: keine Anforderung, kein zhit
e.w32(DO['CURM'], PM); marked(TC_); ok(rq(TC_) == 0, 'Ziel normal: keine Anforderung')
for k in FL: flag(k, 0)
print('FAILS', fails)
