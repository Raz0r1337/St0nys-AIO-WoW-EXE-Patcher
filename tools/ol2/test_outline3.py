# Emulationstest fuer Add-Outline mit Optionen. Aufruf: test_outline3.py <Wow.exe mit Nr. 68>
import sys, os, struct
sys.path.insert(0, '/tmp/claude-0/-home-user-St0nys-WoW-EXE-Patcher/49e16a66-3a63-5e77-ae4f-92ef019273b7/scratchpad/tm')
sys.path.insert(0, '/tmp/claude-0/-home-user-St0nys-WoW-EXE-Patcher/49e16a66-3a63-5e77-ae4f-92ef019273b7/scratchpad/ol2')
from emu2 import *
import outline2 as o
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
# Einheiten: Ziel 0x111, Mouseover 0x222, ich 0x333, Gruppe 0x444 (Paladin), 0x555 (nicht in Reichweite)
TOBJ = H + 0x40000; MOBJ = H + 0x41000; POBJ = H + 0x42000; GOBJ = H + 0x43000
TM = H + 0x50000; TMOUNT = H + 0x51000; MM = H + 0x52000; WEAP = H + 0x53000; OTHER = H + 0x54000; PM = H + 0x55000; GM = H + 0x56000
PF = H + 0x57000; GF = H + 0x58000; TF = H + 0x59000
e.w32(TOBJ + 0xB4, TM); e.w32(TOBJ + 0x98C, TMOUNT); e.w32(TOBJ + 0xD0, TF); e.mu.mem_write(TF + 0x45, b'\x01')
e.w32(MOBJ + 0xB4, MM); e.w32(MOBJ + 0x98C, 0)
e.w32(POBJ + 0xB4, PM); e.w32(POBJ + 0x98C, 0); e.w32(POBJ + 0xD0, PF); e.mu.mem_write(PF + 0x45, b'\x08')   # Magier
e.w32(GOBJ + 0xB4, GM); e.w32(GOBJ + 0x98C, 0); e.w32(GOBJ + 0xD0, GF); e.mu.mem_write(GF + 0x45, b'\x02')   # Paladin
e.w32(WEAP + 0x48, TM)
OBJ = {0x111: TOBJ, 0x222: MOBJ, 0x333: POBJ, 0x444: GOBJ}
def objptr(em, a):
    ST.setdefault('obj', []).append(a[0])
    ok(a[2] == 0x18 and a[3] == 0xA22CD4, 'ObjectPtr mit Typmaske 0x18') if a[2] != 0x18 else None
    return OBJ.get(a[0], 0)
e.stub(0x4D4DB0, objptr, 5, 0)
SELC = {0x111: 0xFFFF0000, 0x222: 0xFF00FF00, 0x333: 0xFF0000FF, 0x444: 0xFF0000FE}
def selcol(em, a):
    g = em.r32(a[0]); em.w32(a[1], SELC[g]); ST.setdefault('col', []).append((g, a[2]))
e.stub(0x521BF0, selcol, 3, 0)
e.stub(0x4D3790, lambda em, a: (em.mu.reg_write(UC_X86_REG_EDX, 0x0F000000), 0x333)[1], 0, 0)
e.stub(0x685970, lambda em, a: ST.setdefault('dirty', []).append(a[0]), 1, 4)
e.stub(0x685A70, lambda em, a: ST.__setitem__('force', ST.get('force', 0) + 1), 0, 0)
e.stub(0x4F6F90, lambda em, a: ST.__setitem__('circles', em.mu.reg_read(UC_X86_REG_ECX)), 0, 0)
SCENE = H + 0x60000; e.w32(0xCD754C, SCENE)
def guid(a, lo): e.w32(a, lo); e.w32(a + 4, 0x0F000000 if lo else 0)
guid(0xBD07B0, 0x111); guid(0xBD07A0, 0x222)
for i in range(4): guid(0xBD1948 + 8 * i, 0)
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
def mods(): return [(e.r32(DO['MOD'] + 8 * c), e.r32(DO['MOD'] + 8 * c + 4)) for c in range(8)]
def cols(): return [e.r32(DO['COL'] + 4 * c) for c in range(8)]
def newframe(): e.w32(DO['VALID'], 0); ST['obj'] = []; ST['col'] = []
# 2) Standard (keine Optionen): nur Ziel (6) und Mouseover (7)
newframe()
r, keep = batch(TM); ok(r == [6] and keep, 'Ziel-Modell -> CUR 6, Register erhalten')
ok(e.r32(DO['CUR']) == 0, 'CUR nach dem Batch wieder 0')
ok(ST['obj'] == [0x111, 0x222] and cols()[6] == 0xFFFF0000 and cols()[7] == 0xFF00FF00 and ST['col'] == [(0x111, 1), (0x222, 1)], 'einmal pro Bild nachgeschlagen, Farben vom Auswahlkreis')
m = mods(); ok(m[6] == (TM, TMOUNT) and m[7] == (MM, 0) and all(m[c] == (0, 0) for c in (1, 2, 3, 4, 5)), 'nur Ziel und Mouseover eingetragen')
r, _ = batch(TMOUNT); ok(r == [6], 'Reittier -> 6')
r, _ = batch(WEAP); ok(r == [6], 'Waffe (Eltern = Ziel) -> 6')
r, _ = batch(MM); ok(r == [7], 'Mouseover -> 7')
r, _ = batch(PM); ok(r == [0], 'eigener Charakter ohne Option -> 0')
r, _ = batch(OTHER); ok(r == [0], 'anderes Modell -> 0')
r, _ = batch(TM, scene=H + 0x61000); ok(r == [0], 'andere Szene -> 0')
ok(ST['obj'] == [0x111, 0x222], 'keine weiteren Nachschlagungen im selben Bild')
# 3) eigener Charakter + Gruppe, Klassenfarbe
flag('FSELF', 1); flag('FPARTY', 1)
guid(0xBD1948, 0x444); guid(0xBD1950, 0); guid(0xBD1958, 0x111); guid(0xBD1960, 0x555)
newframe(); r, _ = batch(PM)
ok(r == [5], 'eigener Charakter -> 5')
ok(ST['obj'] == [0x111, 0x222, 0x333, 0x444, 0x555], 'nachgeschlagen: Ziel, Mouseover, ich, Gruppe (Ziel in der Gruppe uebersprungen)')
m = mods(); c = cols()
ok(m[5] == (PM, 0) and c[5] == o.CLASSCOL[8], 'ich: Modell und Klassenfarbe Magier')
ok(m[1] == (GM, 0) and c[1] == o.CLASSCOL[2], 'Gruppe 1: Modell und Klassenfarbe Paladin')
ok(m[2] == (0, 0) and m[3] == (0, 0) and m[4] == (0, 0), 'leerer Platz, Ziel und nicht sichtbares Mitglied ohne Eintrag')
ok(ST['col'] == [(0x111, 1), (0x222, 1)], 'Klassenfarbe ohne Auswahlkreis-Farbe')
r, _ = batch(GM); ok(r == [1], 'Gruppenmitglied -> 1')
r, _ = batch(TM); ok(r == [6], 'Ziel ist auch in der Gruppe -> Ziel (6) geht vor')
# ich bin das Ziel
guid(0xBD07B0, 0x333); newframe(); r, _ = batch(PM)
ok(r == [6] and mods()[5] == (0, 0), 'ich als Ziel -> 6, keine eigene Kategorie')
guid(0xBD07B0, 0x111)
# 4) Gesinnungsfarbe statt Klassenfarbe
flag('FREACT', 1); newframe(); batch(PM)
c = cols(); ok(c[5] == 0xFF0000FF and c[1] == 0xFF0000FE and (0x333, 1) in ST['col'] and (0x444, 1) in ST['col'], 'Option Gesinnungsfarbe: Farbe vom Auswahlkreis')
flag('FREACT', 0)
# 5) unbekannte Klasse -> Auswahlkreis-Farbe
for cls in (10, 12, 0):
    mu.mem_write(PF + 0x45, bytes([cls])); newframe(); batch(PM)
    ok(cols()[5] == 0xFF0000FF, 'Klasse %d ohne Farbe -> Auswahlkreis-Farbe' % cls)
mu.mem_write(PF + 0x45, b'\x08')
flag('FSELF', 0); flag('FPARTY', 0)
for i in range(4): guid(0xBD1948 + 8 * i, 0)
newframe(); batch(TM)
# 6) DIP ohne Markierung
DIP = OUT + o.LAB['dip']; POST = OUT + o.LAB['post']; RET = 0x31000000
args = [D3D, 4, 0, 0, 100, 0, 50]
calls.clear(); e.w32(DO['CUR'], 0); e.w32(DO['MARKED'], 0)
sp = run(DIP, RET, {UC_X86_REG_EBX: 1, UC_X86_REG_ESI: 2, UC_X86_REG_EDI: 3, UC_X86_REG_EBP: 4}, [RET] + args)
ok([c[0] for c in calls] == ['DIP'] and calls[0][1:] == tuple(args[1:]), 'unmarkiert: ein normaler DIP')
ok(mu.reg_read(UC_X86_REG_ESP) == sp + 4 + 28, 'unmarkiert: Stack ausgeglichen (ret 0x1C)')
# 7) DIP markiert, normal (Ziel)
def marked(cat, walls):
    flag('FWALLS', walls); calls.clear(); e.w32(DO['CUR'], cat); e.w32(DEV + 0x3E60, 0); e.w32(DEV + 0x3E88, 4); ST['dirty'] = []; e.w32(DO['SMODE'], 0)
    sp = run(DIP, RET, {UC_X86_REG_EBX: 1, UC_X86_REG_ESI: 2, UC_X86_REG_EDI: 3, UC_X86_REG_EBP: 4}, [RET] + args)
    good = mu.reg_read(UC_X86_REG_ESP) == sp + 4 + 28 and [mu.reg_read(r) for r in (UC_X86_REG_EBX, UC_X86_REG_ESI, UC_X86_REG_EDI, UC_X86_REG_EBP)] == [1, 2, 3, 4]
    return good
good = marked(6, 0); seq = [c[0] for c in calls]
ok(good, 'markiert: Stack und Register erhalten')
ok(seq.count('DIP') == 10, 'markiert: echtes Teil + Ring + 8 Kopien (%d)' % seq.count('DIP'))
dips = [k for k, c in enumerate(calls) if c[0] == 'DIP']
b0 = [c[1:3] for c in calls[:dips[0]] if c[0] == 'SRS']
ok((52, 1) in b0 and (56, 8) in b0 and (57, 8) in b0 and (55, 3) in b0 and (54, 1) in b0, 'echtes Teil: Stencil ALWAYS/REPLACE 8, ZFAIL KEEP')
b1 = [c[1:3] for c in calls[dips[0]:dips[1]] if c[0] == 'SRS']
ok((56, 3) in b1 and (57, 14) in b1 and (58, 7) in b1 and (23, 8) in b1, 'Ring: EQUAL (Ref 6|8, Maske 7), ZFUNC ALWAYS')
b2 = [c[1:3] for c in calls[dips[1]:dips[2]] if c[0] == 'SRS']
ok(b2[0] == (23, 4) and (58, 0xFF) in b2 and (56, 5) in b2 and (57, 6) in b2 and (168, 0) in b2 and (14, 1) in b2, 'Kopien: ZFUNC zurueck (4), GREATER Ref 6, keine Farbe, Tiefe schreiben')
srs = [c[1:3] for c in calls if c[0] == 'SRS']
ok(srs[-1] == (52, 0) and (54, 3) not in srs, 'am Ende Stencil aus, ZFAIL nie REPLACE')
vs = [c for c in calls if c[0] == 'SetVSConst']
ok(len(vs) == 9 and all(c[1] == 2 and c[3] == 4 for c in vs), '9 VS-Konstanten-Uploads c2..c5')
mm = vs[0][4]; ox = 2 * 2 / 1920
ok(all(abs(mm[i] - (P[i] + ox * P[12 + i])) < 1e-6 for i in range(4)), 'Kopie 0: c2 um 2 Pixel verschoben')
ok(e.r32(DEV + 0x3E70) == 0xFFFFFFFF and ST['dirty'] == [15, 16] and e.r32(DO['MARKED']) == 1, 'Zustaende ungueltig gemacht, MARKED gesetzt')
# 8) DIP markiert, durch Waende
good = marked(5, 1); seq = [c[0] for c in calls]
ok(good, 'Waende: Stack und Register erhalten')
ok(seq.count('DIP') == 9, 'Waende: echtes Teil + 8 Kopien, kein Ring (%d)' % seq.count('DIP'))
dips = [k for k, c in enumerate(calls) if c[0] == 'DIP']
b0 = [c[1:3] for c in calls[:dips[0]] if c[0] == 'SRS']
ok((57, 8) in b0 and (54, 3) in b0, 'Waende: Figur auch verdeckt markiert (ZFAIL REPLACE)')
b1 = [c[1:3] for c in calls[dips[0]:dips[1]] if c[0] == 'SRS']
ok((56, 5) in b1 and (57, 5) in b1 and (168, 0) in b1 and (14, 0) in b1 and (23, 8) in b1 and (58, 3) not in b1 and (58, 7) not in b1, 'Waende: Kopien GREATER Ref 5 ohne Tiefentest und ohne Tiefe')
after = [c[1:3] for c in calls[dips[-1]:] if c[0] == 'SRS']
ok(after[-3:] == [(23, 4), (54, 1), (52, 0)], 'Waende: danach ZFUNC 4, ZFAIL KEEP, Stencil aus')
# 9) Verdecken durch spaeter Gezeichnetes: normal ja, durch Waende nicht
for walls in (0, 1):
    flag('FWALLS', walls); calls.clear(); e.w32(DO['CUR'], 0); e.w32(DO['MARKED'], 1); e.w32(DO['SMODE'], 0); e.w32(DEV + 0x3E70, 1)
    run(DIP, RET, {}, [RET] + args)
    srs = [c[1:3] for c in calls if c[0] == 'SRS']
    if walls: ok([c[0] for c in calls] == ['DIP'] and e.r32(DO['SMODE']) == 0, 'Waende: spaeter Gezeichnetes loescht den Rand nicht')
    else: ok((52, 1) in srs and (57, 0) in srs and (55, 3) in srs and e.r32(DO['SMODE']) == 1, 'normal: Tiefe schreibendes loescht den Rand (Stencil 0)')
flag('FWALLS', 0); e.w32(DEV + 0x3E70, 0xFFFFFFFF); e.w32(DO['SMODE'], 0)
# 10) ohne Shader / mit Blending
calls.clear(); e.w32(0xD43020, 0); marked(6, 1); seq = [c[0] for c in calls]
ok(seq.count('DIP') == 1 and [c[1:3] for c in calls if c[0] == 'SRS'][-2:] == [(54, 1), (52, 0)], 'ohne Shader: nur echtes Teil, ZFAIL zurueck, Stencil aus')
e.w32(0xD43020, 1); flag('FWALLS', 0)
calls.clear(); e.w32(DO['CUR'], 6); e.w32(DEV + 0x3E60, 1); run(DIP, RET, {}, [RET] + args)
ok([c[0] for c in calls] == ['DIP'], 'Blending: nur normal zeichnen'); e.w32(DEV + 0x3E60, 0)
# 11) Post: ein Viereck je aktiver Kategorie
flag('FSELF', 1); flag('FPARTY', 1); guid(0xBD1948, 0x444)
newframe(); batch(PM)
calls.clear(); ST['force'] = 0; e.w32(DO['MARKED'], 1)
regs = {UC_X86_REG_EAX: 0xA, UC_X86_REG_EBX: 0xB, UC_X86_REG_ECX: 0xC, UC_X86_REG_EDX: 0xD, UC_X86_REG_ESI: 0xE, UC_X86_REG_EDI: 0xF, UC_X86_REG_EBP: 0x10}
run(POST, RET, regs, [RET])
seq = [c[0] for c in calls]
ok('CreatePS' in seq, 'Pixelshader angelegt')
dp = [k for k, c in enumerate(calls) if c[0] == 'DPUP']
refs = []; colors = []
for k in dp:
    refs.append([c[2] for c in calls[:k] if c[0] == 'SRS' and c[1] == 57][-1])
    colors.append(struct.unpack('<I', calls[k][5][16:20])[0])
ok(refs == [7, 6, 5, 1], 'Vierecke fuer Mouseover, Ziel, ich, Gruppe 1 (%s)' % refs)
ok(colors == [0xFF00FF00, 0xFFFF0000, o.CLASSCOL[8], o.CLASSCOL[2]], 'jeweils in ihrer Farbe')
v = struct.unpack('<4f I 4f I 4f I 4f I', calls[dp[0]][5])
ok(v[0] == -0.5 and v[5] == 1919.5 and v[11] == 1079.5 and v[3] == 1.0, 'Viereck deckt den Viewport ab')
ok(any(c[0] == 'Clear' and c[1:4] == (0, 0, 4) for c in calls), 'Stencil geleert')
ok(e.r32(DO['MARKED']) == 0 and e.r32(DO['VALID']) == 0 and e.r32(DO['SMODE']) == 0, 'MARKED/VALID/SMODE zurueckgesetzt')
ok(ST.get('circles') == 0xC and all(mu.reg_read(r) == v for r, v in regs.items() if r != UC_X86_REG_EAX), 'weiter zu den Auswahlkreisen, Register erhalten')
# 12) Post ohne Markierung, ohne Stencil-Format
calls.clear(); ST['force'] = 0; run(POST, RET, regs, [RET]); seq = [c[0] for c in calls]
ok(seq.count('Clear') == 1 and 'DPUP' not in seq, 'unmarkiertes Bild: nur Stencil leeren')
calls.clear(); e.w32(DEV + 0x1CC, 7); newframe()
r, _ = batch(TM); ok(r == [0], 'kein Stencil (D32): keine Markierung')
run(POST, RET, regs, [RET]); ok(len(calls) == 0, 'kein Stencil: Post macht nichts')
print('FAILS', fails)
