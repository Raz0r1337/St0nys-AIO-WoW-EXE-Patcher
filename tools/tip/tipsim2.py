# Wie tipsim.py, aber die Kopien werden wie im Spiel als verschobene Geometrie gerastert (Pixelmitten), Versatz in Pixeln (float).
import numpy as np, math
H, W = 48, 64
yy, xx = np.mgrid[0:H, 0:W] + 0.5
def wedge(dx, dy, ang):
    x = xx - (48 + dx); y = yy - (24 + dy)
    c, s = math.cos(ang), math.sin(ang); u = c * x + s * y; v = -s * x + c * y
    return (u < 0) & (np.abs(v) < -0.06 * u)
def disk(r, cx=32, cy=24):
    return (xx - cx) ** 2 + (yy - cy) ** 2 < r * r
def ring(fig, offs):
    F = fig(0, 0); R = np.zeros_like(F)
    for ox, oy in offs: R |= fig(ox, oy)
    return F, R & ~F
r2 = math.sqrt(2)
P = {
 'jetzt (2,2)-Ecken':   [(2,0),(-2,0),(0,2),(0,-2),(2,2),(2,-2),(-2,2),(-2,-2)],
 'Kreis r=2':           [(2,0),(-2,0),(0,2),(0,-2),(r2,r2),(r2,-r2),(-r2,r2),(-r2,-r2)],
 'Kreis r=2, 22.5 Grad':[(2*math.cos(math.radians(22.5+45*k)), 2*math.sin(math.radians(22.5+45*k))) for k in range(8)],
 '(1,1)-Ecken':         [(2,0),(-2,0),(0,2),(0,-2),(1,1),(1,-1),(-1,1),(-1,-1)],
 '16: r=1 und r=2':     [(math.cos(math.radians(45*k))*r, math.sin(math.radians(45*k))*r) for k in range(8) for r in (1.0, 2.0)],
}
steps = [(0.1 * k, 0.07 * k, 0.004 * k) for k in range(60)]
print('%-22s %6s %10s %12s %16s' % ('Muster', 'Kopien', 'Loecher', 'Loecher-Wechsel', 'Randdicke min/mittel/max'))
for name, offs in P.items():
    rs, hs = [], []
    for dx, dy, a in steps:
        F, R = ring(lambda ox, oy: wedge(dx + ox, dy + oy, a), offs)
        near = np.zeros_like(F)
        for ox in (-1, 0, 1):
            for oy in (-1, 0, 1): near |= np.roll(np.roll(F, oy, 0), ox, 1)
        hole = near & ~F & ~R
        rs.append(R); hs.append(hole)
    hc = [int(h.sum()) for h in hs]; hw = [int((hs[k] ^ hs[k + 1]).sum()) for k in range(len(hs) - 1)]
    # Randdicke an einer grossen Scheibe je Richtung: Anzahl Randpixel entlang eines Strahls
    F, R = ring(lambda ox, oy: disk(14, 32 + ox, 24 + oy), offs)
    th = []
    for deg in range(0, 360, 5):
        t = 0
        for s in np.arange(10, 20, 0.05):
            x = 32 + s * math.cos(math.radians(deg)); y = 24 + s * math.sin(math.radians(deg))
            t += 0.05 * R[int(y), int(x)]
        th.append(t)
    print('%-22s %6d %6.1f/%-3d %8.1f/%-3d %8.2f/%.2f/%.2f' % (name, len(offs), np.mean(hc), max(hc), np.mean(hw), max(hw), min(th), np.mean(th), max(th)))
