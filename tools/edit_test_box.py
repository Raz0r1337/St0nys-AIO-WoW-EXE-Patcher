import sys
p = sys.argv[1]
s = open(p, encoding='utf-8').read()
def rep(old, new, cnt=1):
    global s
    n = s.count(old)
    assert n == cnt, (n, old[:80])
    s = s.replace(old, new)
rep("# 33) agent_feet: nur wo verdeckt - alle Kopien auf der Vorderseite der Huellkugel (c4 = (ZC + KZ) * c5)",
    "# 33) agent_feet: nur wo verdeckt - alle Kopien auf der Vorderseite des Huellquaders (c4 = (ZC + SPHK * KZ) * c5)")
a = s.index("def front(box, rad, mat, P=P):")
b = s.index("def kz_ref(P=P):")
s = s[:a] + '''def gax(mat, P=P):   # g_i = c5.xyz . Zeile i (Aenderung von w je Einheit entlang der Modellachse i)
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
''' + s[b:]
rep("""ok(0.9 < zb < 1.0 and abs(zc() - zb) < 1e-6, 'ZC = Kugel-Vorderseite der Figur in NDC (%.6f, Referenz %.6f)' % (zc(), zb))
ok(abs(fr('KZ') - (zb + kz)) < 1e-6 and e.r32(DO['ZA']) == 0, 'KZ = ZC + SPHK * KZ (%.6f), ZA = 0' % fr('KZ'))
ok(c4rows_are(vs, zb + kz), 'Kopien: c4 = (ZC + KZ) * c5 (z/w gleich fuer jeden Punkt), c5 unveraendert, danach Projektion original')""",
"""SK = o.SPHK
ok(0.9 < zb < 1.0 and abs(zc() - zb) < 1e-6 and abs(zb - front_bf(BODY[0], MB)) < 2e-6, 'ZC = Quader-Vorderseite der Figur + SPHM in NDC (%.6f, Referenz %.6f, Ecken %.6f)' % (zc(), zb, front_bf(BODY[0], MB)))
ok(abs(fr('KZ') - (zb + SK * kz)) < 1e-6 and e.r32(DO['ZA']) == 0, 'KZ = ZC + SPHK * KZ (%.6f), ZA = 0' % fr('KZ'))
ok(c4rows_are(vs, zb + SK * kz), 'Kopien: c4 = (ZC + SPHK * KZ) * c5 (z/w gleich fuer jeden Punkt), c5 unveraendert, danach Projektion original')""")
rep("""ok(all(abs(sum(a * b for a, b in zip(c4n, pt + (1,))) / sum(a * b for a, b in zip(c5n, pt + (1,))) - (zb + kz)) < 1e-6 for pt in pts), 'Kopien: z/w konstant = Kugel-Vorderseite + KZ')
# Vorderseite vor allen Punkten der Kugel: jeder Punkt der Kugel hat z/w >= ZC
sv = [sum(F32(x) * m for x, m in zip((0.0, 0.0, 1.1, 1.0), MB[j::4])) for j in range(3)]
rr = 1.3 * 1.2; zs = lambda pt: (1.001 * pt[2] - 0.1) / pt[2]
ok(all(zs((sv[0] + rr * a, sv[1] + rr * b, sv[2] + rr * c)) >= zb - 1e-6 for a, b, c in ((0, 0, -1), (0.6, 0, -0.8), (0, -0.6, -0.8), (1, 0, 0))), 'jeder Punkt der Kugel liegt hinter (oder auf) ZC')""",
"""ok(all(abs(sum(a * b for a, b in zip(c4n, pt + (1,))) / sum(a * b for a, b in zip(c5n, pt + (1,))) - (zb + SK * kz)) < 1e-6 for pt in pts), 'Kopien: z/w konstant = Quader-Vorderseite + SPHK * KZ')
# Vorderseite vor Unterseite und Mittelebene: jede dieser Ecken hat z/w >= ZC (die vorderste liegt SPHM dahinter)
zz_ = [zw_of(pt, MB) for pt in corners(BODY[0])]; zz_ = [z / w for z, w in zz_]
ok(all(q >= zb for q in zz_) and min(zz_) - zb < 0.01, 'jede Ecke von Unterseite und Mittelebene liegt hinter ZC, die vorderste knapp (Zuschlag SPHM)')
# Figur von oben (g2 < 0): der Kopf zaehlt nicht; von unten (g2 > 0): die Unterseite (was am Boden steht) zaehlt
g_ = gax(MB); MUP = rot(-1.75, 0.3, 0.5, 1.2, (0.7, -1.5, 10.0)); gu_ = gax(MUP)
ok(g_[2] < 0 < gu_[2], 'Lage der Testmatrizen: MB von oben (g2 %.3f), MUP von unten (g2 %.3f)' % (g_[2], gu_[2]))
top_ = min(zw_of(pt, MB)[0] / zw_of(pt, MB)[1] for pt in corners(BODY[0], True))
ok(top_ < zb and abs(front(*BODY, MB) - front(*BODY, MB, full=True)) > 1e-4, 'von oben: obere Ecken (Kopf) liegen vor ZC und zaehlen nicht (%.6f < %.6f)' % (top_, zb))
m2model(PM, BODY[0], BODY[1], MUP); marked(1); zu_ = front(*BODY, MUP)
ok(abs(zc() - zu_) < 1e-6 and abs(zu_ - front_bf(BODY[0], MUP)) < 2e-6 and abs(zu_ - front(*BODY, MUP, full=True)) < 1e-9 and
   all(zw_of(pt, MUP)[0] / zw_of(pt, MUP)[1] >= zu_ for pt in corners(BODY[0], True)), 'von unten: Unterseite zaehlt, alle 8 Ecken hinter ZC (%.6f)' % zu_)
m2model(PM, BODY[0], BODY[1], MB); marked(1)""")
rep("""WM = H + 0xF1000; WEAPB = ((-0.1, -0.1, -0.8, 0.1, 0.1, 0.8), 0.82)
m2model(WM, WEAPB[0], WEAPB[1], rot(0.2, 0.1, 0.0, 1.0, (0.5, 0.0, 8.0)), parent=PM)
r, _ = batch(WM); ok(r == [1] and e.r32(DO['CURM']) == WM, 'Waffe: Kategorie der Figur, CURM = Waffe')
marked(1); zw_ = front(*WEAPB, rot(0.2, 0.1, 0.0, 1.0, (0.5, 0.0, 8.0)))
ok(zw_ < zb and abs(zc() - zw_) < 1e-6 and c4rows_are(copies(), zw_ + kz), 'vorderste Kugel gewinnt: Waffe vor der Figur (%.6f < %.6f)' % (zw_, zb))
m2model(WM, WEAPB[0], WEAPB[1], rot(0.2, 0.1, 0.0, 1.0, (0.5, 0.0, 12.0)), parent=PM); marked(1)
ok(abs(zc() - zb) < 1e-6, 'Waffe hinter der Figur: Kugel der Figur')""",
"""WM = H + 0xF1000; WEAPB = ((-0.1, -0.1, -0.8, 0.1, 0.1, 0.8), 0.82); MW = rot(2.9, 0.1, 0.0, 1.0, (0.5, 0.0, 8.0))
m2model(WM, WEAPB[0], WEAPB[1], MW, parent=PM)
r, _ = batch(WM); ok(r == [1] and e.r32(DO['CURM']) == WM, 'Waffe: Kategorie der Figur, CURM = Waffe')
marked(1); zw_ = front(*WEAPB, MW, full=True)
ok(zw_ < zb and abs(zc() - zw_) < 1e-6 and c4rows_are(copies(), zw_ + SK * kz), 'vorderste Vorderseite gewinnt: Waffe vor der Figur (%.6f < %.6f)' % (zw_, zb))
ok(gax(MW)[2] < 0 and abs(zw_ - front_bf(WEAPB[0], MW, True)) < 2e-6 and zw_ < front(*WEAPB, MW) - 1e-4, 'Anbauteil (nicht Figur/Reittier der Tabelle): ganze Hoehe zaehlt, auch von oben (Stab am Boden)')
m2model(WM, WEAPB[0], WEAPB[1], rot(2.9, 0.1, 0.0, 1.0, (0.5, 0.0, 12.0)), parent=PM); marked(1)
ok(abs(zc() - zb) < 1e-6, 'Waffe hinter der Figur: Vorderseite der Figur')""")
rep("""marked(1); zm_ = front(*MNTB, MM_)
ok(zm_ < zb and abs(zc() - zm_) < 1e-6 and c4rows_are(copies(), zm_ + kz), 'beritten: Kugel des Reittiers liegt vorn (%.6f)' % zm_)""",
"""marked(1); zm_ = front(*MNTB, MM_)
ok(zm_ < zb and abs(zc() - zm_) < 1e-6 and c4rows_are(copies(), zm_ + SK * kz), 'beritten: Vorderseite des Reittiers liegt vorn (%.6f)' % zm_)
hf_ = [zw_of(pt, MM_) for pt in corners(MNTB[0]) if pt[2] == MNTB[0][2]]
ok(all(z / w >= zm_ for z, w in hf_), 'Reittier: alle Ecken der Unterseite (Hufe am Boden) liegen hinter ZC')""")
rep("""ok(e.r32(DO['ZC']) == 0x7F800000 and e.r32(DO['ZA']) == 0x3F800000, 'kein Modell (0): keine Kugel, wie bisher')""",
    """ok(e.r32(DO['ZC']) == 0x7F800000 and e.r32(DO['ZA']) == 0x3F800000, 'kein Modell (0): kein Quader, wie bisher')""")
rep("""# Kamera in der Kugel bzw. Vorderseite vor der nahen Ebene: ZC 0, Kopien bei z/w = KZ < 0 (ganz abgeschnitten, kein Rand)
m2model(PM, BODY[0], BODY[1], rot(-1.4, 0.3, 0.5, 1.2, (0.1, 0.2, 0.8))); newframe(); batch(PM); marked(1)
ok(e.r32(DO['ZC']) == 0 and c4rows_are(copies(), kz) and kz < 0, 'Kamera in der Kugel (w <= 0): ZC 0, z/w der Kopien = KZ < 0')
cz_ = sum(x * m for x, m in zip((0.0, 0.0, 1.1), rot(-1.4, 0.3, 0.5, 1.2, (0, 0, 0))[2:12:4]))   # z-Anteil der Mitte
tz_ = 0.05 - cz_ + 1.3 * 1.2   # Vorderseite bei w = 0.05 (nahe Ebene bei w = 0.0999)
m2model(PM, BODY[0], BODY[1], rot(-1.4, 0.3, 0.5, 1.2, (0.1, 0.2, tz_))); marked(1)
w_ = tz_ + cz_ - 1.3 * 1.2""",
"""# Kamera im Quader bzw. Vorderseite vor der nahen Ebene: ZC 0, Kopien bei z/w = SPHK * KZ < 0 (ganz abgeschnitten, kein Rand)
cz_ = sum(x * m for x, m in zip((0.0, 0.0, 1.1), rot(-1.4, 0.3, 0.5, 1.2, (0, 0, 0))[2:12:4]))   # z-Anteil der Mitte
eb_ = ebox(BODY[0], MB) + o.SPHM   # Vorderseite vor der Mitte (|c5| = 1)
m2model(PM, BODY[0], BODY[1], rot(-1.4, 0.3, 0.5, 1.2, (0.1, 0.2, 0.5 * eb_ - cz_))); newframe(); batch(PM); marked(1)
ok(e.r32(DO['ZC']) == 0 and c4rows_are(copies(), SK * kz) and kz < 0, 'Kamera im Quader (w <= 0): ZC 0, z/w der Kopien = SPHK * KZ < 0')
tz_ = 0.05 - cz_ + eb_   # Vorderseite bei w = 0.05 (nahe Ebene bei w = 0.0999)
m2model(PM, BODY[0], BODY[1], rot(-1.4, 0.3, 0.5, 1.2, (0.1, 0.2, tz_))); marked(1)
w_ = tz_ + cz_ - eb_""")
rep("""ok(0 < w_ < 0.0999 and e.r32(DO['ZC']) == 0 and c4rows_are(copies(), kz), 'Vorderseite vor der nahen Ebene (w = %.3f): z/w < 0 -> ZC 0' % w_)""",
    """ok(0 < w_ < 0.0999 and e.r32(DO['ZC']) == 0 and c4rows_are(copies(), SK * kz), 'Vorderseite vor der nahen Ebene (w = %.3f): z/w < 0 -> ZC 0' % w_)""")
rep("""ok(e.r32(DO['ZC']) == 0x12345678 and e.r32(DO['ZA']) == 0x3F800000 and e.r32(DO['KZ']) == 0 and all(v[4][8:12] == P32[8:12] for v in vs[:8]), 'Ziel (normal): keine Kugel, c4 der Kopien unveraendert')""",
    """ok(e.r32(DO['ZC']) == 0x12345678 and e.r32(DO['ZA']) == 0x3F800000 and e.r32(DO['KZ']) == 0 and all(v[4][8:12] == P32[8:12] for v in vs[:8]), 'Ziel (normal): kein Quader, c4 der Kopien unveraendert')""")
rep("""ok(e.r32(DO['ZC']) == 0x12345678 and e.r32(DO['KZ']) == 0, 'durch Waende: keine Kugel'); flag('FWALLS', 0)""",
    """ok(e.r32(DO['ZC']) == 0x12345678 and e.r32(DO['KZ']) == 0, 'durch Waende: kein Quader'); flag('FWALLS', 0)""")
rep("""# Gruppe bei GMODE 2: Kugel des Gruppenmitglieds""", """# Gruppe bei GMODE 2: Quader des Gruppenmitglieds""")
rep("""ok(abs(zc() - zg) < 1e-6 and c4rows_are(copies(), zg + kz), 'GMODE 2: Kopien auf seiner Kugel-Vorderseite (%.6f)' % zg)""",
    """ok(abs(zc() - zg) < 1e-6 and c4rows_are(copies(), zg + SK * kz), 'GMODE 2: Kopien auf seiner Quader-Vorderseite (%.6f)' % zg)""")
rep("""ok(front(*VEHB, MV_) < zb and abs(zc() - zb) < 1e-6, 'Eltern-Modell, das nicht Figur/Reittier der Einheit ist (Fahrzeug): Kugel zaehlt nicht')""",
    """ok(front(*VEHB, MV_) < zb and abs(zc() - zb) < 1e-6, 'Eltern-Modell, das nicht Figur/Reittier der Einheit ist (Fahrzeug): Quader zaehlt nicht')""")
rep("""# SPHK aus dem Datenbereich
ok(fr('SPK') == o.SPHK == 1.0, 'SPHK = 1.0 im Datenbereich')""",
"""# SPHK und SPHM aus dem Datenbereich
ok(fr('SPK') == F32(o.SPHK) and o.SPHK == 0.1 and fr('SPM') == F32(o.SPHM) and o.SPHM == 0.05, 'SPHK = 0.1 und SPHM = 0.05 Yards im Datenbereich')""")
open(p, 'w', encoding='utf-8').write(s)
