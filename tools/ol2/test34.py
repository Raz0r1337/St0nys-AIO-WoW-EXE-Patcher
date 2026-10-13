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
