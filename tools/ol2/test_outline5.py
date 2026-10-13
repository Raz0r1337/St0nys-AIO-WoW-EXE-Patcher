# Emulationstest fuer Add-Outline mit Optionen und rotem Puls. Aufruf: test_outline5.py <Wow.exe mit Nr. 68>
import sys, os, struct
sys.path.insert(0, '/tmp/claude-0/-home-user-St0nys-WoW-EXE-Patcher/49e16a66-3a63-5e77-ae4f-92ef019273b7/scratchpad/tm')
sys.path.insert(0, '/tmp/claude-0/-home-user-St0nys-WoW-EXE-Patcher/49e16a66-3a63-5e77-ae4f-92ef019273b7/scratchpad/ol2')
from emu2 import *
import outline4 as o
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
names = {0x148: 'DIP', 0xE4: 'SRS', 0x178: 'SetVSConst', 0x1A8: 'CreatePS', 0x170: 'SetVS', 0x1AC: 'SetPS', 0x164: 'SetFVF', 0x14C: 'DPUP', 0xAC: 'Clear'}
nargs = {0x148: 7, 0xE4: 3, 0x178: 4, 0x1A8: 3, 0x170: 2, 0x1AC: 2, 0x164: 2, 0x14C: 5, 0xAC: 7}
for off, nm in names.items():
    a = STUBS + off; e.w32(VT + off, a)
    def mk(nm, off):
        def f(em, args):
            rec = (nm,) + tuple(args[1:])
            if nm == 'SetVSConst': rec = rec + (struct.unpack('<16f', bytes(em.mu.mem_read(args[2], 64))),)
            if nm == 'DPUP': rec = rec + (bytes(em.mu.mem_read(args[3], 80)),)
            if nm == 'CreatePS': em.w32(args[2], 0x5050); rec = rec + (bytes(em.mu.mem_read(args[1], 20)),)
            calls.append(rec); return 0
        return f
    e.stub(a, mk(nm, off), nargs[off], 4 * nargs[off])
P = [1.5, 0, 0, 0, 0, 2.0, 0, 0, 0, 0, 1.001, -0.1, 0, 0, 1.0, 0]
e.mu.mem_write(0xC5F008, struct.pack('<16f', *P))
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
b0 = seg(0, dips[0]); ok((57, 0x80) in b0 and (54, 1) in b0 and (55, 3) in b0, 'normal: Figur Stencil 0x80, ZFAIL KEEP')
b1 = seg(dips[0], dips[1]); ok((56, 3) in b1 and (57, 0x83) in b1 and (58, 0x7F) in b1 and (23, 8) in b1, 'Ring: EQUAL Ref 0x83, Maske 0x7F, ZFUNC ALWAYS')
b2 = seg(dips[1], dips[2]); ok(b2[0] == (23, 4) and (56, 5) in b2 and (57, 3) in b2 and (14, 1) in b2 and (168, 0) in b2, 'Kopien: ZFUNC 4, GREATER Ref 3, Tiefe schreiben, keine Farbe')
ok(seg(dips[-1], len(calls))[-1] == (52, 0) and (54, 3) not in seg(0, len(calls)), 'Ende: Stencil aus, ZFAIL nie REPLACE')
vs = [c for c in calls if c[0] == 'SetVSConst']; mm = vs[0][4]; ox = 2 * 2 / 1920
ok(len(vs) == 9 and all(abs(mm[i] - (P[i] + ox * P[12 + i])) < 1e-6 for i in range(4)), '9 VS-Uploads, Kopie 0 um 2 Pixel verschoben')
ok(e.r32(DEV + 0x3E70) == 0xFFFFFFFF and ST['dirty'] == [15, 16] and e.r32(DO['MARKED']) == 1, 'Zustaende ungueltig, MARKED gesetzt')
# 9) nur wo verdeckt: eigener Charakter (2) -> Kopien mit ZFUNC GREATER; Ziel normal
flag('FSELF', 0); flag('FHIDDEN', 1); newframe(); batch(PM)
ok(e.r32(DO['SELFCAT']) == 1 and [x[0] for x in units()] == [0x333, 0x111, 0x222], 'nur verdeckt: ich in der Tabelle (Kategorie 1)')
ok(marked(1), 'verdeckt: Stack und Register erhalten')
dips, seg = parts()
ok(len(dips) == 9, 'verdeckt: echtes Teil + 8 Kopien, kein Ring (%d)' % len(dips))
ok((54, 3) in seg(0, dips[0]), 'verdeckt: Figur auch verdeckt markiert (ZFAIL REPLACE)')
b1 = seg(dips[0], dips[1]); ok((23, 5) in b1 and (14, 0) in b1 and (56, 5) in b1 and (57, 1) in b1, 'verdeckt: Kopien mit ZFUNC GREATER, ohne Tiefe, GREATER Ref 1')
ok(seg(dips[-1], len(calls))[-3:] == [(23, 4), (54, 1), (52, 0)], 'verdeckt: danach ZFUNC 4, ZFAIL KEEP, Stencil aus')
marked(2); dips, seg = parts(); ok(len(dips) == 10, 'Ziel bleibt normal (10 DIPs)')
# 10) durch Waende: alle mit ZFUNC ALWAYS; mit nur-verdeckt bleibt ich bei GREATER
flag('FWALLS', 1); marked(2); dips, seg = parts()
ok(len(dips) == 9 and (23, 8) in seg(dips[0], dips[1]) and (54, 3) in seg(0, dips[0]), 'Waende: Ziel ohne Ring, Kopien ZFUNC ALWAYS, ZFAIL REPLACE')
marked(1); dips, seg = parts(); ok((23, 5) in seg(dips[0], dips[1]), 'Waende + nur verdeckt: ich weiter mit ZFUNC GREATER')
# 11) Verdecken durch spaeter Gezeichnetes: normal ja, durch Waende nicht
for walls in (0, 1):
    flag('FWALLS', walls); calls.clear(); e.w32(DO['CUR'], 0); e.w32(DO['MARKED'], 1); e.w32(DO['SMODE'], 0); e.w32(DEV + 0x3E70, 1)
    run(DIP, RET, {}, [RET] + args)
    srs = [c[1:3] for c in calls if c[0] == 'SRS']
    if walls: ok([c[0] for c in calls] == ['DIP'] and e.r32(DO['SMODE']) == 0, 'Waende: spaeter Gezeichnetes loescht den Rand nicht')
    else: ok((52, 1) in srs and (57, 0) in srs and (55, 3) in srs and e.r32(DO['SMODE']) == 1, 'normal: Tiefe schreibendes loescht den Rand (Stencil 0)')
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
ok(refs == [4, 3, 2, 1], 'Vierecke fuer alle 4 Einheiten (%s)' % refs)
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
    return dict(zip(refs, [struct.unpack('<I', calls[k][5][16:20])[0] for k in dp]))
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
print('FAILS', fails)
