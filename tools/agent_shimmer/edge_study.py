# edge_study.py - straight silhouette edge (half-plane figure) at angle theta, moved by p = 0..2 px in 1/16 px.
# For every variant: glow alpha a(x; p) in the visible region (outside figure and ring). Reported:
#   E  = glow energy per unit edge length (sum of a along the normal)  -> "pumping" (whole edge brighter/darker)
#   P  = peak a in the visible region                                   -> near-ring brightness
#   e  = RMS / max |a - a_ideal| (8-bit LSB), a_ideal = own phase-averaged pipeline on analytic coverage
#   flick = RMS over p of the frame-to-frame artifact change |d(a - a_ideal)| for 1/16 px steps and for 1 px steps
import sys, numpy as np
import glowlib as G

def halfplane(theta_deg, p, h, w, x0):
    # figure = left of a line through (x0 + p, h/2) tilted by theta from vertical
    t = np.radians(theta_deg); n = np.array([np.cos(t), -np.sin(t)])        # outward normal
    c = np.array([x0 + p, h / 2]); d = np.array([np.sin(t), np.cos(t)])        # along-edge direction
    L = 4000.0
    poly = np.array([c - d * L, c + d * L, c + d * L - n * L, c - d * L - n * L])
    area = 0.5 * np.sum(poly[:, 0] * np.roll(poly[:, 1], -1) - np.roll(poly[:, 0], -1) * poly[:, 1])
    if area < 0: poly = poly[::-1]
    return poly, n, c

VARIANTS = {k: v for k, v in {
    'current(box,bilin,x4 hard)': dict(down='box'),
    'tent down':                  dict(down='tent'),
    'box + bspline up':           dict(down='box', up='bspline'),
    'tent + bspline up':          dict(down='tent', up='bspline'),
    'box + vfused':               dict(down='box', up='vfused'),
    'tent + vfused':              dict(down='tent', up='vfused'),
    'full-res blur s=3.6':        dict(down='full', full_sigma=3.6),
}.items() if 'vfused' not in k}

def run(theta, pats=('ideal', 'ms4', 'bin'), steps=33, quant=False, variants=VARIANTS, extra=None):
    if theta == 0: h, w, x0 = 16, 72, 24.0
    else: h, w, x0 = 192, 192, 80.0
    ps = np.arange(steps) / 16.0
    res = {}
    for pat in pats:
        for vn, kw in variants.items():
            kw = dict(kw, **(extra or {}))
            A = []; I = []; V = []
            for p in ps:
                poly, n, c = halfplane(theta, p, h, w, x0)
                f = G.raster([poly], G.pattern(pat), h, w); F, R = G.ring_cov(f)
                if pat == 'ideal': Ri = R
                else: Ri = G.ring_cov(G.raster([poly], G.pattern('ideal'), h, w))[1]
                a = G.pipe(R, quant=quant, **kw)
                ia = G.curve(G.phase_avg(Ri, **{k: v for k, v in kw.items() if k not in ('curve_mode', 'gain', 'vgain')}),
                             kw.get('curve_mode', 'hard'), kw.get('gain', 4.0))
                vis = np.clip(1 - F - R, 0, 1)
                if theta != 0:          # central window along the edge, away from canvas borders
                    jj, ii = np.mgrid[0:h, 0:w]; along = (ii + 0.5 - c[0]) * np.sin(np.radians(theta)) + (jj + 0.5 - c[1]) * np.cos(np.radians(theta))
                    nrm = (ii + 0.5 - c[0]) * n[0] + (jj + 0.5 - c[1]) * n[1]
                    win = (np.abs(along) < 48) & (np.abs(nrm) < 24)
                    vis = vis * win
                A.append(a); I.append(ia); V.append(vis)
            A = np.array(A); I = np.array(I); V = np.array(V)
            vis_both = np.minimum(V[1:], V[:-1]) > 0.999
            norm = h if theta == 0 else 96.0
            E = (A * V).sum((1, 2)) / norm; Ei = (I * V).sum((1, 2)) / norm
            P = np.array([a[v > 0.999].max() for a, v in zip(A, V)])
            err = (A - I) * 255
            m = V > 0.999
            d1 = np.diff(A - I, axis=0) * 255                       # artifact change for 1/16 px steps
            d16 = (A[16:] - I[16:]) - (A[:-16] - I[:-16])            # 1 px steps
            vis16 = np.minimum(V[16:], V[:-16]) > 0.999
            dt = np.diff(A, axis=0) * 255; di = np.diff(I, axis=0) * 255
            res[(pat, vn)] = dict(
                E=E, Ei=Ei, P=P,
                Emod=(E.max() - E.min()) / E.mean() * 100, Eimod=(Ei.max() - Ei.min()) / Ei.mean() * 100,
                Pmod=(P.max() - P.min()) * 255,
                erms=np.sqrt((err[m] ** 2).mean()), emax=np.abs(err[m]).max(),
                f16=np.sqrt((d1[vis_both] ** 2).mean()), f1px=np.sqrt(((d16 * 255)[vis16] ** 2).mean()),
                f1pxmax=np.abs(d16 * 255)[vis16].max(),
                tot16=np.sqrt((dt[vis_both] ** 2).mean()), mot16=np.sqrt((di[vis_both] ** 2).mean()),
                mc=mc1px(A, V, theta))
    return res

def mc1px(A, V, theta):
    # motion-compensated residual for a 1 px step along x: A(p+1)(x+1) - A(p)(x); exact zero for a shift-invariant pipeline
    if theta != 0: return (np.nan, np.nan)
    d = (A[16:, :, 1:] - A[:-16, :, :-1]) * 255
    m = np.minimum(V[16:, :, 1:], V[:-16, :, :-1]) > 0.999
    return (np.sqrt((d[m] ** 2).mean()), np.abs(d[m]).max())

def table(res, title):
    print(title)
    print('  %-6s %-28s %7s %7s %7s %7s %7s %11s %10s' % ('ring', 'variant', 'E mod%', 'Ei mod%', 'err rms', 'err max', 'flk1/16', 'mc1px rms/max', 'tot/mot16'))
    for (pat, vn), r in res.items():
        print('  %-6s %-28s %7.2f %7.2f %7.2f %7.1f %7.2f %5.2f/%-5.1f %4.1f/%-4.1f' % (pat, vn, r['Emod'], r['Eimod'], r['erms'], r['emax'], r['f16'], r['mc'][0], r['mc'][1], r['tot16'], r['mot16']))

if __name__ == '__main__':
    thetas = [float(x) for x in sys.argv[1:] if not x.startswith('--')] or [0.0]
    q = '--q' in sys.argv
    for th in thetas:
        table(run(th, quant=q), '=== edge theta %.1f deg, %s pipeline (E mod: energy modulation over p, actual and ideal; err/flk in 8-bit LSB of glow alpha) ===' % (th, '8-bit' if q else 'float'))
