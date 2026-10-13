# tiplib.py - simulation of the outline at thin features (ear tips, spikes, thin edges).
# Figure = union of convex polygons, rasterised per sample like D3D9 (glowlib.raster: 'bin' 1 sample, 'ms4' standard 4x,
# 'ideal' 16x16 = analytic coverage). Copies = figure shifted by offsets (integer: shift of the sample planes, exact;
# fractional: re-rasterised). Stencil per sample: ring = union(copies) & ~figure.
# Post (outline10): TEX0 = resolved ring coverage; glow = tent down, H blur, V blur + soft curve (glowlib.pipe 'tsv');
# line variants:
#   'stencil'  current: per sample, ring samples get the line colour (opaque), resolved at present
#   'post'     new: a = sat(k * tent3(TEX0)) (4 bilinear taps at (+-0.5,+-0.5) = [1 2 1]x[1 2 1]/16), blended over
#              glow on all non-figure samples (stencil < 0x80)
import numpy as np, math
import glowlib as G

def disc(cx, cy, r, n=None):
    n = n or max(48, int(2 * math.pi * r / 1.5))
    a = 2 * np.pi * (np.arange(n) + 0.5) / n
    return np.stack([cx + r * np.cos(a), cy + r * np.sin(a)], 1)

def ccw(p):
    p = np.asarray(p, float)
    area = 0.5 * np.sum(p[:, 0] * np.roll(p[:, 1], -1) - np.roll(p[:, 0], -1) * p[:, 1])
    return p[::-1] if area < 0 else p

def rot(polys, deg, c):
    a = math.radians(deg); R = np.array([[math.cos(a), -math.sin(a)], [math.sin(a), math.cos(a)]]); c = np.asarray(c, float)
    return [(p - c) @ R.T + c for p in polys]

def tr(polys, dx, dy): return [p + (dx, dy) for p in polys]

def wedge(base, ang_deg, length, wbase, wtip=0.0):
    """thin wedge/spike from base point, direction ang, base width wbase, tip width wtip (convex quad/tri)"""
    a = math.radians(ang_deg); d = np.array([math.cos(a), math.sin(a)]); n = np.array([-d[1], d[0]])
    b = np.asarray(base, float); t = b + d * length
    if wtip > 0: P = [b - n * wbase / 2, t - n * wtip / 2, t + n * wtip / 2, b + n * wbase / 2]
    else: P = [b - n * wbase / 2, t, b + n * wbase / 2]
    return ccw(np.array(P))

PATS = {k: G.pattern(k) for k in ('bin', 'ms4', 'ideal')}

def raster(polys, pat, h, w):
    return G.raster([ccw(p) for p in polys], PATS[pat] if isinstance(pat, str) else pat, h, w)

def ring_planes(polys, offs, pat, h, w):
    """per-sample figure and ring planes (S,h,w)"""
    F = raster(polys, pat, h, w); R = np.zeros_like(F)
    for ox, oy in offs:
        if float(ox).is_integer() and float(oy).is_integer(): R |= G.shift(F, int(ox), int(oy))
        else: R |= raster(tr(polys, ox, oy), pat, h, w)
    return F, R & ~F

def tex_sample(img, x, y):
    """bilinear sample at continuous pixel coords (texel centres at k+0.5), clamp"""
    h, w = img.shape
    x = x - 0.5; y = y - 0.5; x0 = np.floor(x).astype(int); y0 = np.floor(y).astype(int); fx = x - x0; fy = y - y0
    def t(yy, xx): return img[np.clip(yy, 0, h - 1), np.clip(xx, 0, w - 1)]
    return t(y0, x0) * (1 - fx) * (1 - fy) + t(y0, x0 + 1) * fx * (1 - fy) + t(y0 + 1, x0) * (1 - fx) * fy + t(y0 + 1, x0 + 1) * fx * fy

def tent3(img, r=0.5):
    h, w = img.shape; jj, ii = np.mgrid[0:h, 0:w] + 0.5
    return 0.25 * (tex_sample(img, ii + r, jj + r) + tex_sample(img, ii - r, jj - r) + tex_sample(img, ii + r, jj - r) + tex_sample(img, ii - r, jj + r))

def q8(x): return np.round(np.clip(x, 0, 1) * 255) / 255

GLOW_K = 2.5
def glow(T0, k=GLOW_K):
    return G.pipe(T0, down='tent', quant=True, curve_mode='soft', gain=2 * k, vgain=True)

LCURVE = 'hard'               # line: 'hard' sat(k x) (shader line_ps) or 'soft' 1-(1-sat(k/2 x))^2
GC = 0.6                      # glow colour (one channel)
LC = GC * 0.625 + 94 / 255.0  # light(colour)
def frame(polys, offs, pat, h, w, line='stencil', k=4.0, gk=GLOW_K, filt=0.5, want=False, gsrc='ring'):
    F, R = ring_planes(polys, offs, pat, h, w)
    f = F.mean(0); r = R.mean(0)
    T0 = q8(r) if pat != 'ideal' else r
    a = None
    if line == 'post' or gsrc == 'line':
        if LCURVE == 'soft':
            y = np.clip(k / 2 * tent3(T0, filt), 0, 1); a = y * (2 - y)
        else:
            a = np.clip(k * tent3(T0, filt), 0, 1)
        if pat != 'ideal': a = q8(a)
    g = glow(a if gsrc == 'line' else T0, gk)
    if line == 'stencil':
        L = r; C = r * LC + (1 - f - r) * g * GC
    elif line == 'post':
        L = (1 - f) * a; C = (1 - f) * (a * LC + (1 - a) * g * GC)
    elif line == 'none':
        L = np.zeros_like(r); C = (1 - f) * g * GC
    else: raise ValueError(line)
    if want: return dict(f=f, r=r, L=L, g=g * (1 - f), C=C)
    return f, L, (1 - f) * g, C
