# tipstudy.py - flicker at thin features: head with two long thin ears, a thin spike and a thin bar (constant 0.7 px),
# moved by sub-pixels + small rotation per frame. Methods = copy offsets x line rendering; no MSAA ('bin') and 4x ('ms4').
# Metrics (8-bit LSB, ROI = pixels within 7 px of the thin parts, not near the head):
#   own   : mean |d(M - A)|, A = same method with analytic coverage (16x16): pops from aliasing only
#   ideal : mean |d(M - I)|, I = ideal outline (line = analytic {0 < dist <= 2}, glow from it): change beyond true motion
#   big   : pixels per frame with |d(M - I)| >= 32 LSB (clearly visible pops)
#   holes : mean uncovered part of the ideal 2 px band next to the thin parts (look: gaps/double lines), analytic
# usage: python3 tipstudy.py [quick]
import sys, os, json, math, numpy as np
import tiplib as T

H, W = 120, 170
HEAD = (62.0, 64.0, 13.0)
def scene_polys(k):
    cx, cy, r = HEAD
    P = [T.disc(cx, cy, r)]
    P.append(T.wedge((cx - 9, cy - 6), 200, 36, 4.5))           # long ear, ~3.6 deg half angle
    P.append(T.wedge((cx + 9, cy - 6), -23, 30, 3.0))           # thinner ear
    P.append(T.wedge((cx + 4, cy + 11), 64, 34, 1.4, 0.25))     # thin spike (weapon edge)
    P.append(T.wedge((cx - 4, cy + 12), 172, 34, 0.7, 0.7))     # thin bar, constant 0.7 px
    P = T.rot(P, 0.3 * k, (cx, cy))
    return T.tr(P, 0.11 * k + 10, 0.067 * k)
NF = 40
THIN = slice(1, 5)

def dist_union(polys, X, Y):
    """Euclidean distance to the union of convex polygons (0 inside)"""
    best = np.full(X.shape, np.inf)
    for p in polys:
        p = T.ccw(p); a = p; b = np.roll(p, -1, 0); d = b - a; L2 = (d ** 2).sum(1)
        inside = np.ones(X.shape, bool); dm = np.full(X.shape, np.inf)
        for i in range(len(p)):
            qx = X - a[i, 0]; qy = Y - a[i, 1]
            cr = d[i, 0] * qy - d[i, 1] * qx
            inside &= cr >= 0
            t = np.clip((qx * d[i, 0] + qy * d[i, 1]) / L2[i], 0, 1)
            dm = np.minimum(dm, np.hypot(qx - t * d[i, 0], qy - t * d[i, 1]))
        best = np.minimum(best, np.where(inside, 0.0, dm))
    return best

def ideal_frame(polys, rad=2.0, ss=8):
    g = (np.arange(ss) + 0.5) / ss
    jj, ii = np.mgrid[0:H, 0:W]
    F = np.zeros((H, W)); R = np.zeros((H, W))
    for sy in g:
        for sx in g:
            d = dist_union(polys, ii + sx, jj + sy)
            F += d == 0; R += (d > 0) & (d <= rad)
    F /= ss * ss; R /= ss * ss
    g_ = T.glow(R)
    C = R * T.LC + (1 - F - R) * g_ * T.GC
    return F, R, (1 - F) * g_, C

R2 = math.sqrt(2)
OFFS = {
    'cur8':    [(2, 0), (-2, 0), (0, 2), (0, -2), (2, 2), (2, -2), (-2, 2), (-2, -2)],
    'circ8':   [(2, 0), (-2, 0), (0, 2), (0, -2), (R2, R2), (R2, -R2), (-R2, R2), (-R2, -R2)],
    'cur8+ax4': [(2, 0), (-2, 0), (0, 2), (0, -2), (2, 2), (2, -2), (-2, 2), (-2, -2), (1, 0), (-1, 0), (0, 1), (0, -1)],
    'disc12':  [(1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1), (2, 0), (-2, 0), (0, 2), (0, -2)],
    'cur8+r1': [(2, 0), (-2, 0), (0, 2), (0, -2), (2, 2), (2, -2), (-2, 2), (-2, -2), (1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)],
    'r1x8':    [(1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)],
    'r1x4':    [(1, 0), (-1, 0), (0, 1), (0, -1)],
}
METHODS = [  # name, offsets, line, k (line gain), glow gain
    ('current: cur8 stencil', 'cur8', 'stencil', 0, 2.5),
    ('circ8 stencil', 'circ8', 'stencil', 0, 2.5),
    ('cur8+ax4 (12) stencil', 'cur8+ax4', 'stencil', 0, 2.5),
    ('disc12 stencil', 'disc12', 'stencil', 0, 2.5),
    ('cur8+r1 (16) stencil', 'cur8+r1', 'stencil', 0, 2.5),
    ('cur8 post k1.33', 'cur8', 'post', 4 / 3, 2.5),
    ('r1x8 post k4', 'r1x8', 'post', 4.0, 5.0),
    ('r1x8 post k3', 'r1x8', 'post', 3.0, 5.0),
    ('r1x4 post k4', 'r1x4', 'post', 4.0, 5.0),
    ('r1x4 post k6', 'r1x4', 'post', 6.0, 5.0),
]

def dil(m, r):
    o = m.copy()
    for dy in range(-r, r + 1):
        for dx in range(-r, r + 1):
            if dx * dx + dy * dy <= r * r: o |= np.roll(np.roll(m, dy, 0), dx, 1)
    return o
def roi_mask(frames_polys):
    th = np.zeros((H, W), bool); hd = np.zeros((H, W), bool)
    for P in frames_polys:
        th |= T.raster(P[THIN], 'bin', H, W)[0]; hd |= T.raster(P[:1], 'bin', H, W)[0]
    return dil(th, 7) & ~dil(hd, 7), dil(hd, 7) & ~dil(th, 9)

def run(methods=METHODS, nf=NF, cache='cache_tip.npz', pats=('bin', 'ms4')):
    FP = [scene_polys(k) for k in range(nf)]
    roi, roi_thick = roi_mask(FP)
    here = os.path.dirname(os.path.abspath(__file__)); cf = os.path.join(here, cache)
    if os.path.exists(cf): z = np.load(cf); IDL = {k: z[k] for k in z.files}
    else:
        I = [ideal_frame(P) for P in FP]
        IDL = {n: np.array([x[i] for x in I]) for i, n in enumerate(('F', 'R', 'G', 'C'))}
        np.savez_compressed(cf, **IDL)
    out = {}
    for m in methods:
        name, ok, line, k, gk = m[:5]; gs = m[5] if len(m) > 5 else 'ring'
        offs = OFFS[ok]; res = {}
        A = [T.frame(P, offs, 'ideal', H, W, line, k, gk, gsrc=gs) for P in FP]
        hole = []; mass = []
        for i in range(nf):
            band = IDL['R'][i] * roi
            hole.append(float((np.clip(band - A[i][1], 0, 1)).sum() / max(band.sum(), 1e-9)))
            mass.append(float(A[i][1][roi].sum() / max(band.sum(), 1e-9)))
        res['holes'] = float(np.mean(hole)); res['mass'] = float(np.mean(mass))
        for pat in pats:
            M = [T.frame(P, offs, pat, H, W, line, k, gk, gsrc=gs) for P in FP]
            r = {}
            for rn, rm in (('thin', roi), ('thick', roi_thick)):
                for ci, cn in ((1, 'L'), (2, 'G'), (3, 'C')):
                    own = []; idl = []; big = []; out_ = []; pops = []
                    for i in range(nf - 1):
                        dM = M[i + 1][ci] - M[i][ci]; dA = A[i + 1][ci] - A[i][ci]
                        cI = 'R' if cn == 'L' else cn; dI = IDL[cI][i + 1] - IDL[cI][i]
                        outside = rm & (M[i][0] == 0) & (M[i + 1][0] == 0) & (A[i][0] < 0.02) & (A[i + 1][0] < 0.02)
                        own.append(np.abs(dM - dA)[rm].mean() * 255); idl.append(np.abs(dM - dI)[rm].mean() * 255)
                        big.append(int((np.abs(dM - dI)[rm] * 255 >= 32).sum()))
                        out_.append(np.abs(dM - dA)[outside].sum() * 255 / rm.sum())
                        pops.append(int((np.abs(dM - dA)[outside] >= 0.25).sum()))
                    r[rn + cn] = dict(own=float(np.mean(own)), ideal=float(np.mean(idl)), big=float(np.mean(big)), out=float(np.mean(out_)), pops=float(np.mean(pops)))
            res[pat] = r
        out[name] = res
        line_ = '%-24s holes %.3f mass %.2f' % (name, res['holes'], res['mass'])
        for pat in pats:
            q = res[pat]
            line_ += ' | %s thin C own %5.2f out %5.2f pops %5.1f, L out %5.2f, G out %5.2f; thick C own %5.2f' % (pat, q['thinC']['own'], q['thinC']['out'], q['thinL']['pops'], q['thinL']['out'], q['thinG']['out'], q['thickC']['own'])
        print(line_, flush=True)
    return out

if __name__ == '__main__':
    out = run()
    json.dump(out, open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'tipstudy.json'), 'w'), indent=1)
