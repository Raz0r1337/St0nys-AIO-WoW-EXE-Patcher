# Emulationstest fuer Add-Outline (outline10: weicher Schein per Weichzeichner, duenne Linie fuer Schlachtzug; outline8: Sortierung von Pass 0; outline7: Durch Waende nur Gruppe/Schlachtzug; outline6: nur wo verdeckt mit ZFAIL KEEP und Tiefen-Abstand). Aufruf: test_outline5.py <Wow.exe mit Nr. 68>
import sys, os, struct
sys.path.insert(0, '/tmp/claude-0/-home-user-St0nys-WoW-EXE-Patcher/49e16a66-3a63-5e77-ae4f-92ef019273b7/scratchpad/tm')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
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
ok(len(vs) == 9 and all(abs(mm[i] - (P[i] + ox * P[12 + i])) < 1e-6 for i in range(4)), '9 VS-Uploads, Kopie 0 um 2 Pixel verschoben')
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
# 19) Schlachtzug-Mitglieder ausserhalb der 5er-Gruppe: THIN (duenne Linie ohne Schein)
for k in FL: flag(k, 0)
flag('FRAID', 1); guid(0xBD07B0, 0x111); guid(0xBD07A0, 0x222)
guid(0xBD1948, 0x444); guid(0xBD1950, 0); guid(0xBD1958, 0); guid(0xBD1960, 0)
raid([0x666, 0x444, 0x333]); newframe(); batch(OTHER); u = units()
def thins(): return [mu.mem_read(DO['THIN'] + c, 1)[0] for c in range(1, e.r32(DO['NUNITS']) + 1)]
ok([x[0] for x in u] == [0x666, 0x444, 0x111, 0x222] and thins() == [1, 0, 0, 0], 'THIN: Priester (nur Schlachtzug) 1, Paladin (5er-Gruppe), Ziel, Mouseover 0 %s' % thins())
marked(1); dips, seg = parts(); ok(len(dips) == 10, 'duenne Linie: dieselben Zeichenaufrufe wie die anderen (10 DIPs)')
guid(0xBD1950, 0x666); newframe(); batch(OTHER)
ok(thins()[0] == 0, 'Priester jetzt in der 5er-Gruppe: THIN wieder 0')
flag('FRAID', 0); flag('FPARTY', 1); raid([]); guid(0xBD1950, 0); newframe(); batch(OTHER)
ok(thins() == [0] * len(units()), 'ohne Schlachtzug: niemand duenn')
# 20) Weicher Schein: Ablauf im ersten Bild
f32 = lambda x: struct.unpack('<f', struct.pack('<f', x))[0]
O1, O2 = f32(o.BLUR_O[0]), f32(o.BLUR_O[1])
def light(c): return 0xFF000000 | sum((((c >> s) & 0xFF) - (((c >> s) & 0xFF) >> 2) - (((c >> s) & 0xFF) >> 3) + 0x5E) << s for s in (0, 8, 16))
def symmap():
    m = {SURF['bb']: 'BB', SURF['ds']: 'DS', DO['VP']: '&VP', DO['VERTT']: '&VERTT', DO['VERTS']: '&VERTS', DO['DESC']: '&DESC', DO['BBP']: '&BBP', DO['DSP']: '&DSP',
         DO['GPS']: '&GPS', DO['CPS']: '&CPS', DO['PS']: '&PS', DO['GPSCODE']: '&GPSCODE', DO['CPSCODE']: '&CPSCODE', DO['PSCODE']: '&PSCODE'}
    for i, n in enumerate(o.GLRES_NAMES): m[DO['GLRES'] + 4 * i] = '&' + n
    for nm, k in (('GPS', 'GPS'), ('CPS', 'CPS'), ('PS', 'PS')):
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
def ringpart(cs):
    n = e.r32(DO['NUNITS']); dp = [k for k, c in enumerate(cs) if c[0] == 'DPUP'][-n:]
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
EXP = [('CreatePS', '&GPSCODE', '&GPS'), ('CreatePS', '&CPSCODE', '&CPS'), ('GetRT', 0, '&BBP'), ('GetDesc', 'BB'),
       ('CreateRT', 1920, 1080, 21, 4, 0, 0, '&MSRT', 0),
       ('CreateTex', 1920, 1080, 1, 1, 21, 0, '&TEX0', 0), ('GetLevel', 'TEX0', 0),
       ('CreateTex', 960, 540, 1, 1, 21, 0, '&TEX1', 0), ('GetLevel', 'TEX1', 0),
       ('CreateTex', 960, 540, 1, 1, 21, 0, '&TEX2', 0), ('GetLevel', 'TEX2', 0),
       ('GetDS', '&DSP'), ('SRS', 174, 0), ('SetRT', 0, 'MSRT'), ('Clear', 0, 0, 1, 0, 0x3F800000, 0)] + SRC + [
       ('StretchRect', 'MSRT', 0, 'TEX0S', 0, 0), ('SetDS', 0), ('SRS', 7, 0), ('SRS', 52, 0), ('SetPS', 'GPS'), ('SetFVF', 0x504),
       ('SSS', 0, 5, 2), ('SSS', 0, 6, 2), ('SSS', 0, 7, 0), ('SSS', 0, 1, 3), ('SSS', 0, 2, 3)] + TSSL + [
       ('SetTex', 0, 'TEX0'), ('SetRT', 0, 'TEX1S'), ('DPUP', 5, 2, '&VERTT', 56),
       ('SetTex', 0, 'TEX1'), ('SetRT', 0, 'TEX2S'), ('DPUP', 5, 2, '&VERTT', 56),
       ('SetTex', 0, 'TEX2'), ('SetRT', 0, 'TEX1S'), ('DPUP', 5, 2, '&VERTT', 56),
       ('SetRT', 0, 'BB'), ('SetDS', 'DS'), ('SetVP', '&VP'), ('SRS', 7, 1), ('SRS', 52, 1),
       ('SRS', 56, 5), ('SRS', 57, 0x80), ('SRS', 58, 0xFF), ('SRS', 27, 1), ('SRS', 19, 2), ('SRS', 20, 6), ('SRS', 168, 7), ('SetPS', 'CPS'), ('SetTex', 0, 'TEX1'), ('DPUP', 5, 2, '&VERTT', 56),
       ('SetTex', 0, 0), ('SRS', 27, 0), ('SRS', 56, 3), ('SRS', 168, 0xF), ('SetPS', 'PS'), ('SetFVF', 0x44)] + [('TSS', i, 24, 0) for i in range(5)] + [('Release', 'DS'), ('Release', 'BB')]
RING = []
for cat in (4, 3, 2, 1): RING += [('SRS', 57, 0x40 | cat), ('SRS', 58, 0xFF), ('DPUP', 5, 2, '&VERTS', 20)]
EXP += RING + [('SRS', 59, 0xFF), ('Clear', 0, 0, 4, 0, 0x3F800000, 0), ('SRS', 52, 0)]
ok(gn == EXP, 'erstes Bild: Shader und Texturen anlegen, Ringfarben in die Render-Textur, aufloesen, verkleinern, waagrecht, senkrecht, einblenden, alles zurueck')
if gn != EXP:
    for k, (a, b) in enumerate(zip(gn, EXP)):
        if a != b: print('   erste Abweichung bei', k, a, b); break
    print('   Laenge', len(gn), len(EXP))
cp = [c for c in g if c[0] == 'CreatePS']
ok(cp[0][3] == o.psasm.blur_ps(*o.BLUR_W)[:20] and cp[1][3] == o.psasm.comp_ps(o.GLOW_GAIN)[:20], 'Pixelshader-Code aus dem Datenbereich (Weichzeichner, Einblenden)')
ok(bytes(mu.read if False else mu.mem_read(DO['GPSCODE'], o.SIZES['GPSCODE'])) == o.psasm.blur_ps(*o.BLUR_W) and bytes(mu.mem_read(DO['CPSCODE'], o.SIZES['CPSCODE'])) == o.psasm.comp_ps(o.GLOW_GAIN), 'Shader-Bytes vollstaendig wie psasm')
dps = [c for c in g if c[0] == 'DPUP']
srcq = dps[:4]; ok([struct.unpack('<I', c[5][16:20])[0] for c in srcq] == [cols[c] | 0xFF000000 for c in (4, 3, 2, 1)], 'Render-Textur: Ringfarben in voller Deckkraft')
pz = [c for c in dps if c[4] == 56]
r1 = quad_ok(pz[0][5], -0.5, -0.5, 959.5, 539.5, 0.0, 0.0, 1.0, 1.0, 0.0, 0.0)
ok(r1[0], 'Verkleinern: Viereck ueber 960x540, alle Abgriffe in der Mitte %s' % (r1[1][:1] if not r1[0] else ''))
du = f32(1 / 960); dv = f32(1 / 540)
r2 = quad_ok(pz[1][5], -0.5, -0.5, 959.5, 539.5, 0.0, 0.0, 1.0, 1.0, du, 0.0)
ok(r2[0], 'Waagrecht: Abgriffe u +/- 1.3846 und 3.2308 Texel (1/960) %s' % ((r2[1][1], r2[2][1]) if not r2[0] else ''))
r3 = quad_ok(pz[2][5], -0.5, -0.5, 959.5, 539.5, 0.0, 0.0, 1.0, 1.0, 0.0, dv)
ok(r3[0], 'Senkrecht: Abgriffe v +/- 1.3846 und 3.2308 Texel (1/540) %s' % ((r3[1][2], r3[2][2]) if not r3[0] else ''))
r4 = quad_ok(pz[3][5], -0.5, -0.5, 1919.5, 1079.5, 0.0, 0.0, 1.0, 1.0, 0.0, 0.0)
ok(r4[0], 'Einblenden: Viereck ueber den Viewport, Textur 0..1')
vp = [c for c in g if c[0] == 'SetVP'][0]; ok(vp[2] == struct.pack('<4I2f', 0, 0, 1920, 1080, 0.0, 1.0), 'Viewport wieder gesetzt')
refs, rc = ringpart(cs)
ok(refs == [0x44, 0x43, 0x42, 0x41] and rc == [light(cols[c]) for c in (4, 3, 2, 1)], 'danach duenne Linien aufgehellt (Farbe * 5/8 + 0x5E) %s' % [hex(x) for x in rc])
ok(e.r32(DO['GLOK']) == 1 and e.r32(DEV + 0xF6C) == 1 and e.r32(DEV + 0x2534) == 1, 'GLOK 1, Viewport und Scissor beim Spiel als geaendert markiert')
ok(OBJS[SURF['bb']]['refs'] == 1 and OBJS[SURF['ds']]['refs'] == 1, 'Render-Target und Tiefenpuffer wieder freigegeben (Referenzen wie vorher)')
res = [e.r32(DO['GLRES'] + 4 * i) for i in range(7)]
ok(all(OBJS[p]['refs'] == 1 for p in res) and e.r32(DO['RTDEV']) == D3D and (e.r32(DO['RTW2']), e.r32(DO['RTH2'])) == (960, 540), 'Texturen gehalten (je 1 Referenz), RTDEV, halbe Groesse 960x540')
ok(all(mu.reg_read(r) == v for r, v in regs.items() if r != UC_X86_REG_EAX) and ST.get('circles') == 0xC, 'Post mit Schein: Register erhalten, weiter zu den Auswahlkreisen')
ok((mu.reg_read(UC_X86_REG_FPSW) >> 11) & 7 == (fsw0 >> 11) & 7, 'FPU-Stapel ausgeglichen')
# 21) zweites Bild: nichts neu anlegen
cs = post(); g = nob(sym(glowpart(cs)))
ok(not any(c[0] in ('CreatePS', 'CreateRT', 'CreateTex', 'GetLevel') for c in g) and g[:3] == [('GetRT', 0, '&BBP'), ('GetDesc', 'BB'), ('GetDS', '&DSP')], 'zweites Bild: Shader und Texturen wiederverwendet')
ok(OBJS[SURF['bb']]['refs'] == 1 and OBJS[SURF['ds']]['refs'] == 1 and all(OBJS[p]['refs'] == 1 for p in res), 'zweites Bild: Referenzen ausgeglichen')
# 22) Viewport mit Versatz
mu.mem_write(DO['VP'], struct.pack('<4I2f', 100, 50, 800, 600, 0.0, 1.0)); cs = post(); g = sym(glowpart(cs))
pz = [c for c in g if c[0] == 'DPUP' and c[4] == 56]
r = quad_ok(pz[3][5], 99.5, 49.5, 899.5, 649.5, f32(100 / 1920), f32(50 / 1080), f32(900 / 1920), f32(650 / 1080), 0.0, 0.0)
ok(r[0], 'Viewport 100,50 800x600: Viereck und Texturkoordinaten passend %s' % (r[1][0] if not r[0] else ''))
ok([c for c in g if c[0] == 'SetVP'][0][2] == struct.pack('<4I2f', 100, 50, 800, 600, 0.0, 1.0), 'versetzter Viewport wiederhergestellt')
mu.mem_write(DO['VP'], struct.pack('<4I2f', 0, 0, 1920, 1080, 0.0, 1.0))
# 23) andere Groesse / Kantenglaettung: alte Texturen frei, neue an
old = res
OBJS[SURF['bb']].update(w=1281, h=721, ms=8, mq=2); cs = post(); g = nob(sym(glowpart(cs)))
ok(all(OBJS[p]['refs'] == 0 for p in old), 'Groesse geaendert: alte 7 Objekte freigegeben')
cr = [c for c in g if c[0] in ('CreateRT', 'CreateTex')]
ok(cr == [('CreateRT', 1281, 721, 21, 8, 2, 0, '&MSRT', 0), ('CreateTex', 1281, 721, 1, 1, 21, 0, '&TEX0', 0), ('CreateTex', 641, 361, 1, 1, 21, 0, '&TEX1', 0), ('CreateTex', 641, 361, 1, 1, 21, 0, '&TEX2', 0)],
   'neu: 1281x721 mit 8x/Qualitaet 2, halbe Groesse aufgerundet 641x361 %s' % cr)
res = [e.r32(DO['GLRES'] + 4 * i) for i in range(7)]
OBJS[SURF['bb']].update(w=1920, h=1080, ms=4, mq=0); cs = post()
ok(all(OBJS[p]['refs'] == 0 for p in res) and e.r32(DO['RTW']) == 1920, 'zurueck auf 1920x1080: wieder neu angelegt')
res = [e.r32(DO['GLRES'] + 4 * i) for i in range(7)]
# 24) Reset/Abbau: Freigabe ueber die drei Aufrufe von 0x690150
ok(all(callto(va) == OUT + o.LAB['glrel'] for va in o.RESETSITES), 'Aufrufe bei 0x69029D, 0x6A337F, 0x69040B zeigen auf glrel')
RF = []
e.stub(0x690150, lambda em, a: RF.append((em.mu.reg_read(UC_X86_REG_ECX), a[0])), 1, 4)
e.w32(DO['GLFAIL'], 0x1234)
sp = run(0x69029D, 0x6902A2, {UC_X86_REG_ECX: DEV, UC_X86_REG_ESI: 5, UC_X86_REG_EDI: 6, UC_X86_REG_EBX: 7}, [0])
ok(RF == [(DEV, 0)] and mu.reg_read(UC_X86_REG_ESP) == sp + 4 and [mu.reg_read(r) for r in (UC_X86_REG_ESI, UC_X86_REG_EDI, UC_X86_REG_EBX)] == [5, 6, 7], 'glrel: weiter zu 0x690150 mit ecx und Argument, Stack ausgeglichen')
ok(all(OBJS[p]['refs'] == 0 for p in res) and all(e.r32(DO['GLRES'] + 4 * i) == 0 for i in range(7)) and e.r32(DO['RTDEV']) == 0 and e.r32(DO['GLFAIL']) == 0, 'vor Reset: alle 7 Objekte frei, GLFAIL geloescht')
ok(e.r32(DO['GPS']) != 0 and e.r32(DO['PS']) != 0 and e.r32(DO['GPSDEV']) == D3D, 'vor Reset: Pixelshader bleiben')
cs = post(); g = nob(sym(glowpart(cs)))
ok(sum(1 for c in g if c[0] in ('CreateRT', 'CreateTex')) == 4 and not any(c[0] == 'CreatePS' for c in g) and e.r32(DO['GLOK']) == 1, 'nach Reset: Texturen neu, Shader weiter')
shaders = [e.r32(DO['GPS']), e.r32(DO['CPS']), e.r32(DO['PS'])]; res = [e.r32(DO['GLRES'] + 4 * i) for i in range(7)]
RF.clear(); sp = run(0x69040B, 0x690410, {UC_X86_REG_ECX: DEV}, [1])
ok(RF == [(DEV, 1)] and all(OBJS[p]['refs'] == 0 for p in shaders + res) and e.r32(DO['GPSDEV']) == 0 and e.r32(DO['PSDEV']) == 0 and e.r32(DO['PS']) == 0, 'Abbau (Argument 1): auch die 3 Pixelshader frei')
RF.clear(); run(0x6A337F, 0x6A3384, {UC_X86_REG_ECX: DEV}, [0]); ok(RF == [(DEV, 0)], 'verlorenes Geraet (0x6A337F): ebenso ueber glrel')
cs = post(); ok(sum(1 for c in cs if c[0] == 'CreatePS') == 3 and e.r32(DO['GLOK']) == 1, 'nach dem Abbau: alle 3 Shader neu')
# 25) Fehler: Textur laesst sich nicht anlegen -> nur duenne Linien
run(0x69029D, 0x6902A2, {UC_X86_REG_ECX: DEV}, [0])
FAIL['CreateTex'] = 2; cs = post(); g = nob(sym(glowpart(cs)))
made = [c for c in g if c[0] in ('CreateRT', 'CreateTex')]
ok(len(made) == 3 and e.r32(DO['GLFAIL']) == D3D and e.r32(DO['GLOK']) == 0 and all(e.r32(DO['GLRES'] + 4 * i) == 0 for i in range(7)), 'TEX1 fehlt: Angelegtes frei, GLFAIL = Geraet')
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
# 26) nur duenne Linien (Schlachtzug ausserhalb der Gruppe), gemischt
for k in FL: flag(k, 0)
flag('FRAID', 1); guid(0xBD1948, 0); guid(0xBD07B0, 0); guid(0xBD07A0, 0); raid([0x666])
cs = post(); ok(thins() == [1] and not any(c[0] == 'GetRT' for c in cs) and e.r32(DO['GLOK']) == 0 and ringpart(cs)[1] == [o.CLASSCOL[5]], 'nur duenne Linien: kein Schein, Linie in Klassenfarbe')
guid(0xBD1948, 0x444); raid([0x666, 0x444]); guid(0xBD07B0, 0x111); cs = post(); u = units(); g = nob(sym(glowpart(cs)))
ok([x[0] for x in u] == [0x666, 0x444, 0x111] and thins() == [1, 0, 0], 'gemischt: Priester duenn, Paladin und Ziel mit Schein')
src = [c for c in g if c[0] == 'SRS' and c[1] == 57][:2]
ok(src == [('SRS', 57, 0x43), ('SRS', 57, 0x42)] and sum(1 for c in g if c[0] == 'DPUP' and c[4] == 20) == 2 + 3, 'Render-Textur nur mit Ziel und Paladin (Priester fehlt)')
refs, rc = ringpart(cs); cl = [x[3] for x in u]
ok(refs == [0x43, 0x42, 0x41] and rc == [light(cl[2]), light(cl[1]), cl[0]], 'Linien: Ziel und Paladin aufgehellt, Priester normal %s' % [hex(x) for x in rc])
guid(0xBD07B0, 0x666); cs = post(); u = units()
ok([x[0] for x in u] == [0x444, 0x666] and thins() == [0, 0] and ringpart(cs)[1] == [light(x[3]) for x in reversed(u)], 'Schlachtzug-Mitglied als Ziel: Schein statt duenner Linie')
guid(0xBD07B0, 0); guid(0xBD07A0, 0x666); cs = post(); u = units()
ok([x[0] for x in u] == [0x444, 0x666] and thins() == [0, 0] and e.r32(DO['GLOK']) == 1, 'Schlachtzug-Mitglied unter der Maus: Schein')
guid(0xBD07A0, 0)
# 27) anderes Geraet: Shader und Texturen neu
D3D2 = H + 0x1800; e.w32(D3D2, VT); e.w32(DEV + 0x397C, D3D2); old = [e.r32(DO['GLRES'] + 4 * i) for i in range(7)]
cs = post(); g = nob(sym(glowpart(cs)))
ok(sum(1 for c in cs if c[0] == 'CreatePS') == 3 and sum(1 for c in g if c[0] in ('CreateRT', 'CreateTex')) == 4 and all(OBJS[p]['refs'] == 0 for p in old) and e.r32(DO['RTDEV']) == D3D2, 'neues Geraet: Shader und Texturen neu, alte frei')
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
FAIL['SetRT'] = 3; cs = post(); g = nob(sym(glowpart(cs)))
ok(e.r32(DO['GLFAIL']) == D3D and e.r32(DO['GLOK']) == 0 and ('SetPS', 'CPS') not in g, 'SetRenderTarget-Fehler im Durchgang: GLFAIL, kein Einblenden')
ok(('SetRT', 0, 'BB') in g and ('SetDS', 'DS') in g and OBJS[SURF['bb']]['refs'] == 1 and OBJS[SURF['ds']]['refs'] == 1, 'SetRenderTarget-Fehler: Render-Target und Tiefenpuffer zurueck, Referenzen ausgeglichen')
k = g.index(('SetRT', 0, 'TEX2S'))
ok(g[k + 1] == ('SetRT', 0, 'BB') and not any(c[0] == 'DPUP' and c[4] == 56 for c in g[k:]), 'nach dem Fehler kein Zeichnen und kein weiterer Durchgang (keine Rueckkopplung TEX1 -> TEX1S)')
run(0x6A337F, 0x6A3384, {UC_X86_REG_ECX: DEV}, [0])
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
ok(u[1][3] == o.CLASSCOL[2] and u[1][4] == 0 and thins()[1] == 0, 'Pet in der Farbe des Besitzers (Paladin), kein Puls, THIN wie der Besitzer')
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
ok(thins() == [1, 0, 0, 1, 0, 0, 0, 1] and u[3][3] == o.CLASSCOL[5] and gstate() == (4, 2, 0), 'Pet des Priesters (nur Schlachtzug) THIN 1 in Priesterfarbe, GRPN 4 %s %s' % (thins(), gstate()))
marked(3); dips, seg = parts()
ok(len(dips) == 9 and (23, 5) in seg(dips[0], dips[1]), 'Gruppen-Pet bei GMODE 2 nur wo verdeckt (wie die Gruppe)')
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
print('FAILS', fails)
