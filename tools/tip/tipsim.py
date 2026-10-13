# Duenner Keil (Ohrspitze), der sich in kleinen Schritten bewegt: Rand = Vereinigung verschobener Kopien minus Figur.
import numpy as np
H, W = 40, 60
yy, xx = np.mgrid[0:H, 0:W] + 0.5
def wedge(dx, dy, ang=0.0):
    # Keil: Spitze bei (45+dx, 20+dy), oeffnet nach links, halbe Breite = 0.06 * Abstand zur Spitze
    x = xx - (45 + dx); y = yy - (20 + dy)
    c, s = np.cos(ang), np.sin(ang); u = c * x + s * y; v = -s * x + c * y
    return (u < 0) & (np.abs(v) < -0.06 * u)
def ring(F, offs):
    R = np.zeros_like(F)
    for ox, oy in offs: R |= np.roll(np.roll(F, oy, 0), ox, 1)
    return R & ~F
P = {
 'jetzt 8x r2':      [(2,0),(-2,0),(0,2),(0,-2),(2,2),(2,-2),(-2,2),(-2,-2)],
 '8x r2 rund':       [(2,0),(-2,0),(0,2),(0,-2),(1,1),(1,-1),(-1,1),(-1,-1)],
 '12x (+4 r1)':      [(2,0),(-2,0),(0,2),(0,-2),(2,2),(2,-2),(-2,2),(-2,-2),(1,0),(-1,0),(0,1),(0,-1)],
 '16x (r1+r2)':      [(a,b) for a in (-2,-1,0,1,2) for b in (-2,-1,0,1,2) if (a,b)!=(0,0) and max(abs(a),abs(b)) in (1,2) and (abs(a)+abs(b) in (1,2,4) or (abs(a),abs(b)) in ((1,1),(2,2)))],
}
rng = np.random.default_rng(1)
steps = [(0.1 * k, 0.07 * k, 0.004 * k) for k in range(40)]
for name, offs in P.items():
    rs = [ring(wedge(dx, dy, a), offs) for dx, dy, a in steps]
    fl = [np.sum(rs[k] ^ rs[k + 1]) for k in range(len(rs) - 1)]
    holes = []
    for (dx, dy, a), r in zip(steps, rs):
        F = wedge(dx, dy, a)
        # Loecher: Pixel mit Abstand <= 1.5 zur Figur, die weder Figur noch Rand sind
        near = np.zeros_like(F)
        for ox in (-1, 0, 1):
            for oy in (-1, 0, 1): near |= np.roll(np.roll(F, oy, 0), ox, 1)
        holes.append(np.sum(near & ~F & ~r))
    print('%-14s Kopien %2d  Rand-Wechsel/Bild Mittel %.1f Max %d  Loecher direkt am Rand Mittel %.1f Max %d' % (name, len(offs), np.mean(fl), max(fl), np.mean(holes), max(holes)))
