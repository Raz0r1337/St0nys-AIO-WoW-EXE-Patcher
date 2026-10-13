# glowlib.py - simulation of the outline10 soft glow (ol2/outline10.py: glow, g_pass, mkq) for the shimmer study.
# Figure = union of convex polygons (same parts as glowsim/sim.py figure()), so it can be moved by sub-pixels,
# rotated and scaled. Rasterised per sample like D3D9 (pixel (i,j) centre at (i+0.5, j+0.5) in these coordinates):
#   'bin'   1 sample at the centre (no MSAA)
#   'ms4'   standard 4x pattern (offsets in 1/16 px: (-2,-6) (6,-2) (-6,2) (2,6))
#   'ideal' 16x16 ordered grid = analytic coverage for reference
# Ring like the game: 8 copies shifted by +-2 px (integer pixel shifts, so per sample) minus the figure,
# resolve = mean over samples (StretchRect of the MSAA target).
import numpy as np

W, H = 400, 340                      # canvas (even, like typical resolutions); figure offset by (20, 20) vs sim.py
OX, OY = 20.0, 20.0
CX, CY = 200.5, 175.5                # rotation / scale centre (canvas coordinates)
OFFS = [(2, 0), (-2, 0), (0, 2), (0, -2), (2, 2), (2, -2), (-2, 2), (-2, -2)]

def _ellipse(cx, cy, rx, ry, n=96):
    a = 2 * np.pi * (np.arange(n) + 0.5) / n
    return np.stack([cx + rx * np.cos(a), cy + ry * np.sin(a)], 1)
def _rrect(x0, y0, x1, y1, r, n=16):
    pts = []
    for (cx, cy, a0) in ((x1 - r, y0 + r, -90), (x1 - r, y1 - r, 0), (x0 + r, y1 - r, 90), (x0 + r, y0 + r, 180)):
        for k in range(n + 1):
            a = np.radians(a0 + 90.0 * k / n); pts.append((cx + r * np.cos(a), cy + r * np.sin(a)))
    return np.array(pts)
def figure_polys():
    c = 180; e = 0.5          # sim.py pixel indices -> continuous coordinates (pixel centre = index + 0.5)
    P = [_ellipse(c + e, 64 + e, 22.5, 24.5),
         _rrect(c - 42, 86, c + 43, 191, 18),
         np.array([(c - 42, 95), (c - 78, 175), (c - 64, 182), (c - 34, 120)], float) + e,
         np.array([(c + 42, 95), (c + 86, 150), (c + 76, 160), (c + 34, 120)], float) + e,
         np.array([(c - 36, 185), (c - 44, 270), (c - 22, 270), (c - 8, 190)], float) + e,
         np.array([(c + 36, 185), (c + 40, 270), (c + 18, 270), (c + 8, 190)], float) + e,
         np.array([(c + 80, 140), (c + 130, 40), (c + 136, 44), (c + 88, 150)], float) + e]
    out = []
    for p in P:
        p = p + (OX, OY)
        area = 0.5 * np.sum(p[:, 0] * np.roll(p[:, 1], -1) - np.roll(p[:, 0], -1) * p[:, 1])
        if area < 0: p = p[::-1]
        d = np.roll(p, -1, 0) - p; cr = d[:, 0] * np.roll(d, -1, 0)[:, 1] - d[:, 1] * np.roll(d, -1, 0)[:, 0]
        assert (cr > -1e-9).all(), 'not convex'
        out.append(p)
    return out
POLYS = figure_polys()

def transform(polys, tx=0.0, ty=0.0, rot_deg=0.0, scale=1.0):
    a = np.radians(rot_deg); R = np.array([[np.cos(a), -np.sin(a)], [np.sin(a), np.cos(a)]]) * scale
    c = np.array([CX, CY])
    return [(p - c) @ R.T + c + (tx, ty) for p in polys]

def pattern(name):
    if name == 'bin': return np.array([[0.5, 0.5]])
    if name == 'ms4': return 0.5 + np.array([[-2, -6], [6, -2], [-6, 2], [2, 6]]) / 16.0
    if name == 'ideal':
        g = (np.arange(16) + 0.5) / 16; xx, yy = np.meshgrid(g, g); return np.stack([xx.ravel(), yy.ravel()], 1)
    raise ValueError(name)

def raster(polys, pat, h=H, w=W):
    """per-sample inside mask (S, h, w) of the union of convex polygons"""
    S = len(pat); out = np.zeros((S, h, w), bool)
    for p in polys:
        x0 = max(int(np.floor(p[:, 0].min())) - 1, 0); x1 = min(int(np.ceil(p[:, 0].max())) + 1, w)
        y0 = max(int(np.floor(p[:, 1].min())) - 1, 0); y1 = min(int(np.ceil(p[:, 1].max())) + 1, h)
        d = np.roll(p, -1, 0) - p; L = np.hypot(d[:, 0], d[:, 1])
        jj, ii = np.mgrid[y0:y1, x0:x1]
        px = ii + 0.5; py = jj + 0.5
        # signed distance to each edge line, positive inside
        def edist(qx, qy):
            return (d[:, 0, None] * (qy[None] - p[:, 1, None]) - d[:, 1, None] * (qx[None] - p[:, 0, None])) / L[:, None]
        m = edist(px.ravel(), py.ravel()).min(0).reshape(px.shape)
        full = m > 0.75; band = (m >= -0.75) & ~full
        out[:, y0:y1, x0:x1] |= full[None]
        bj, bi = np.nonzero(band)
        if len(bj):
            qx = (bi + x0)[None, :] + pat[:, 0, None]; qy = (bj + y0)[None, :] + pat[:, 1, None]
            ins = (edist(qx.ravel(), qy.ravel()).min(0) >= 0).reshape(S, -1)
            out[:, bj + y0, bi + x0] |= ins
    return out

def shift(m, dx, dy):
    o = np.zeros_like(m)
    ys = slice(max(dy, 0), m.shape[-2] + min(dy, 0)); yd = slice(max(-dy, 0), m.shape[-2] + min(-dy, 0))
    xs = slice(max(dx, 0), m.shape[-1] + min(dx, 0)); xd = slice(max(-dx, 0), m.shape[-1] + min(-dx, 0))
    o[..., ys, xs] = m[..., yd, xd]; return o

def ring_cov(fig_s):
    """fig_s (S,h,w) -> (figure coverage F, ring coverage R), ring per sample like the stencil copies"""
    r = np.zeros_like(fig_s)
    for dx, dy in OFFS: r |= shift(fig_s, dx, dy)
    r &= ~fig_s
    return fig_s.mean(0), r.mean(0)

def scene(pat, **tf):
    f = raster(transform(POLYS, **tf), pattern(pat))
    return ring_cov(f)

# ---------------------------------------------------------------- pipeline
def sample(img, u, v):
    """D3D9 bilinear, clamp, texel centres at (k+0.5)/size; img (h,w) float"""
    h, w = img.shape
    x = u * w - 0.5; y = v * h - 0.5
    x0 = np.floor(x).astype(int); y0 = np.floor(y).astype(int); fx = x - x0; fy = y - y0
    def t(yy, xx): return img[np.clip(yy, 0, h - 1), np.clip(xx, 0, w - 1)]
    return (t(y0, x0) * (1 - fx) * (1 - fy) + t(y0, x0 + 1) * fx * (1 - fy) + t(y0 + 1, x0) * (1 - fx) * fy + t(y0 + 1, x0 + 1) * fx * fy)

BLUR_W = (0.2270270, 0.3162162, 0.0702703); BLUR_O = (1.3846154, 3.2307692)

def taps5(src, ow, oh, du, dv, w=BLUR_W, o=BLUR_O):
    j, i = np.mgrid[0:oh, 0:ow]; u = (i + 0.5) / ow; v = (j + 0.5) / oh
    r = sample(src, u, v) * w[0]
    for k in (1, 2):
        r = r + (sample(src, u + du * o[k - 1], v + dv * o[k - 1]) + sample(src, u - du * o[k - 1], v - dv * o[k - 1])) * w[k]
    return r

def gauss_linear_taps(sigma, radius):
    """discrete Gaussian on 2*radius+1 texels -> linear-sampling taps (weights, offsets), centre first"""
    k = np.arange(-radius, radius + 1); g = np.exp(-k ** 2 / (2 * sigma ** 2)); g /= g.sum()
    ws = [g[radius]]; os_ = [0.0]
    for a in range(1, radius + 1, 2):
        b = a + 1
        wa = g[radius + a]; wb = g[radius + b] if b <= radius else 0.0
        ws.append(wa + wb); os_.append((a * wa + b * wb) / (wa + wb))
    return np.array(ws), np.array(os_)

def tapsN(src, ow, oh, du, dv, ws, os_):
    j, i = np.mgrid[0:oh, 0:ow]; u = (i + 0.5) / ow; v = (j + 0.5) / oh
    r = sample(src, u, v) * ws[0]
    for wk, ok in zip(ws[1:], os_[1:]):
        r = r + (sample(src, u + du * ok, v + dv * ok) + sample(src, u - du * ok, v - dv * ok)) * wk
    return r

def q8(x): return np.round(np.clip(x, 0, 1) * 255) / 255

def curve(x, mode, gain):
    if mode == 'hard': return np.clip(gain * x, 0, 1)
    if mode == 'lin': return gain * x                          # no clamp (analysis only)
    if mode == 'soft':                                         # 1-(1-y)^2, y = sat(gain/2 * x): same slope at 0
        y = np.clip(gain / 2 * x, 0, 1); return y * (2 - y)
    raise ValueError(mode)

def pipe(R, down='box', up='bilinear', quant=False, curve_mode='hard', gain=4.0, full_sigma=None, vgain=False, linear_out=False):
    """R: resolved ring alpha (H,W). Returns glow alpha at full res (what the composite blends), or the
    pre-curve value if linear_out. down: 'box' (current: 5 taps at the 2x2 block corner), 'tent' (4 bilinear taps at
    (+-0.75,+-0.75) full-res texels = [1 3 3 1]/8 per axis), 'full' (no downsample, blur at full res with
    9 linear taps of a Gaussian full_sigma). up: 'bilinear' (current composite), 'bspline' (4-tap cubic B-spline),
    'vfused' (vertical blur evaluated in the composite at full-res rows). vgain: gain applied (mul_sat) in the last
    blur pass instead of the composite (8-bit precision of TEX1)."""
    h, w = R.shape; Q = q8 if quant else (lambda x: x)
    src = Q(R)
    if down == 'full':
        ws, os_ = gauss_linear_taps(full_sigma, 8)
        t2 = Q(tapsN(src, w, h, 1.0 / w, 0, ws, os_))
        t1 = tapsN(t2, w, h, 0, 1.0 / h, ws, os_)
        G = t1
        if vgain: return Q(curve(G, curve_mode, gain)) if not linear_out else G
        G = Q(G)
        return G if linear_out else (Q(curve(G, curve_mode, gain)) if quant else curve(G, curve_mode, gain))
    w2, h2 = (w + 1) // 2, (h + 1) // 2
    if down == 'box':
        t1 = taps5(src, w2, h2, 0, 0)
    elif down == 'tent':
        j, i = np.mgrid[0:h2, 0:w2]; u = (i + 0.5) / w2; v = (j + 0.5) / h2; a = 0.75 / w; b = 0.75 / h
        t1 = 0.25 * (sample(src, u + a, v + b) + sample(src, u - a, v - b) + sample(src, u + a, v - b) + sample(src, u - a, v + b))
    else: raise ValueError(down)
    t1 = Q(t1)
    t2 = Q(taps5(t1, w2, h2, 1.0 / w2, 0))
    jj, ii = np.mgrid[0:h, 0:w]; U = (ii + 0.5) / w; V = (jj + 0.5) / h
    if up == 'vfused':
        G = sum(wk * (sample(t2, U, V + s * ok / h2) if ok else sample(t2, U, V)) for wk, ok, s in
                ((BLUR_W[0], 0, 1), (BLUR_W[1], BLUR_O[0], 1), (BLUR_W[1], BLUR_O[0], -1), (BLUR_W[2], BLUR_O[1], 1), (BLUR_W[2], BLUR_O[1], -1)))
        if linear_out: return G
        return Q(curve(G, curve_mode, gain)) if quant else curve(G, curve_mode, gain)
    t1 = taps5(t2, w2, h2, 0, 1.0 / h2)
    if vgain:
        t1 = Q(curve(t1, curve_mode, gain))
    else:
        t1 = Q(t1)
    if up == 'bilinear':
        G = sample(t1, U, V)
    elif up == 'bspline':
        G = bspline_up(t1, U, V)
    else: raise ValueError(up)
    if linear_out: return G
    if vgain: return Q(G)
    return Q(curve(G, curve_mode, gain)) if quant else curve(G, curve_mode, gain)

def bspline_up(img, U, V):
    """cubic B-spline reconstruction with 4 bilinear taps (Sigg & Hadwiger), texel units of img"""
    h, w = img.shape
    def axis(c, n):
        x = c * n - 0.5; i = np.floor(x); f = x - i
        w0 = (1 - f) ** 3 / 6; w1 = (4 - 6 * f ** 2 + 3 * f ** 3) / 6; w2 = (1 + 3 * f + 3 * f ** 2 - 3 * f ** 3) / 6; w3 = f ** 3 / 6
        g0 = w0 + w1; g1 = w2 + w3
        h0 = (i - 1 + w1 / g0 + 0.5) / n; h1 = (i + 1 + w3 / g1 + 0.5) / n
        return g0, g1, h0, h1
    gx0, gx1, hx0, hx1 = axis(U, w); gy0, gy1, hy0, hy1 = axis(V, h)
    return (gy0 * (gx0 * sample(img, hx0, hy0) + gx1 * sample(img, hx1, hy0)) +
            gy1 * (gx0 * sample(img, hx0, hy1) + gx1 * sample(img, hx1, hy1)))

def phase_avg(R, **kw):
    """shift-invariant reference of a pipeline: average of the 4 sub-grid phases (pre-curve value)"""
    acc = 0
    for sx in (0, 1):
        for sy in (0, 1):
            g = pipe(np.roll(R, (sy, sx), (0, 1)), linear_out=True, **kw)
            acc = acc + np.roll(g, (-sy, -sx), (0, 1))
    return acc / 4
