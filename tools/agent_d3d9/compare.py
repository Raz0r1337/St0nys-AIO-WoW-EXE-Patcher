# Compares the Wine/wined3d render of glowtest.exe with glowsim/sim.py (same arithmetic as the planned shaders).
# usage: python3 -I compare.py <outdir> <prefix> [frame]
import sys, os, struct
S = '/tmp/claude-0/-home-user-St0nys-WoW-EXE-Patcher/49e16a66-3a63-5e77-ae4f-92ef019273b7/scratchpad'
sys.path.insert(0, os.path.join(S, 'glowsim'))
import numpy as np
from PIL import Image
import sim

OUT, PRE = sys.argv[1], sys.argv[2]
FR = sys.argv[3] if len(sys.argv) > 3 else 'f1'
OX, OY = 40, 60
GOLD = (0xFF, 0xD1, 0x00); BLUE = (0x00, 0x70, 0xDE); BG = (0x38, 0x40, 0x30); FIGC = (0x8C, 0x8C, 0x8C)
def light(c): return tuple(x - (x >> 2) - (x >> 3) + 0x5E for x in c)

def load(name):
    p = os.path.join(OUT, '%s_%s.raw' % (PRE, name))
    b = open(p, 'rb').read(); w, h = struct.unpack('<II', b[:8])
    a = np.frombuffer(b[8:], np.uint8).reshape(h, w, 4)
    return a[..., [2, 1, 0, 3]].copy()          # BGRA -> RGBA
f0 = load('f0'); f1 = load(FR); t0 = load(FR + '_tex0'); t1 = load(FR + '_tex1'); t2 = load(FR + '_tex2')
H, W = f1.shape[:2]; W2, H2 = (W + 1) // 2, (H + 1) // 2
sim.W, sim.H = W, H                             # sim's helpers use module globals W, H
print('frame', FR, 'size %dx%d, half %dx%d' % (W, H, W2, H2))

# --- determinism across frames / Reset ---
for other in ('f1b', 'f2', 'f3', 'f4'):
    if other != FR and os.path.exists(os.path.join(OUT, '%s_%s.raw' % (PRE, other))):
        o = load(other); print('  %s vs %s: identical=%s maxdiff=%d' % (FR, other, (o[..., :3] == f1[..., :3]).all(), np.abs(o[..., :3].astype(int) - f1[..., :3]).max()))

# --- ideal masks (figure 1 exact) ---
m1s = np.load(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'fig1_mask.npy'))
fig1 = np.zeros((H, W), bool); fig1[OY:OY + m1s.shape[0], OX:OX + m1s.shape[1]] = m1s
ring1 = np.zeros_like(fig1)
for dx, dy in [(2, 0), (-2, 0), (0, 2), (0, -2), (2, 2), (2, -2), (-2, 2), (-2, -2)]: ring1 |= sim.shift(fig1, dx, dy)
ring1 &= ~fig1
reg1 = np.zeros((H, W), bool); reg1[:, :420] = True      # figure-1 region (figure 2 glow is > 90 px away)

def eq(img, col): return (img[..., 0] == col[0]) & (img[..., 1] == col[1]) & (img[..., 2] == col[2])
# A) TEX0 (resolved MSRT) against the ideal ring
exp_t0 = np.zeros((H, W, 4), np.uint8); exp_t0[ring1] = GOLD + (255,)
d = np.abs(t0.astype(int) - exp_t0)[reg1]
print('A) TEX0 vs ideal ring source (figure 1 region): max|diff| %d, pixels differing %d of %d ring px' % (d.max(), int((d.max(-1) > 0).sum()), int(ring1.sum())))
fig2ring_px = eq(t0, BLUE) & (t0[..., 3] == 255); partial2 = (t0[..., 3] > 0) & (t0[..., 3] < 255)
print('   figure 2 (MSAA circle): full-coverage ring px %d, partial-coverage px %d, alpha values %s' % (fig2ring_px.sum(), partial2.sum(), sorted(set(t0[..., 3][partial2].tolist()))))
print('   TEX0 outside both rings nonzero px: %d' % int(((t0.max(-1) > 0) & ~ring1 & reg1).sum()))

# B) blur passes: sim on the ACTUAL TEX0 vs actual TEX2/TEX1
src = t0.astype(np.float64) / 255
q = lambda x: np.round(np.clip(x, 0, 1) * 255) / 255
s1 = sim.blurpass(src, W2, H2, 0, 0); s2 = sim.blurpass(s1, W2, H2, 1.0 / W2, 0); s3 = sim.blurpass(s2, W2, H2, 0, 1.0 / H2)
q1 = q(sim.blurpass(src, W2, H2, 0, 0)); q2 = q(sim.blurpass(q1, W2, H2, 1.0 / W2, 0)); q3 = q(sim.blurpass(q2, W2, H2, 0, 1.0 / H2))
for nm_, act, fl, qq in (('TEX2 (horizontal)', t2, s2, q2), ('TEX1 (vertical)', t1, s3, q3)):
    a = act.astype(np.float64)
    df = np.abs(a - fl * 255); dq = np.abs(a - qq * 255)
    print('B) %s vs sim(actual TEX0): float model max %.2f mean %.4f LSB | 8-bit-per-pass model max %.0f mean %.4f, %d texels off by >1' % (nm_, df.max(), df.mean(), dq.max(), dq.mean(), int((dq > 1).sum())))

# C) final frame: composite / figure / ring pixels
up = np.clip(sim.sample(t1.astype(np.float64) / 255, (np.mgrid[0:H, 0:W][1] + 0.5) / W, (np.mgrid[0:H, 0:W][0] + 0.5) / H) * 4.0, 0, 1)
bgf = np.array(BG, float) / 255
comp = (up[..., :3] + bgf * (1 - up[..., 3:4])) * 255
outside = eq(f0, BG) & ~ring1
lr = light(GOLD); lb = light(BLUE)
ringpx = eq(f1, lr) | eq(f1, lb)
dc = np.abs(f1[..., :3].astype(float) - comp)[outside & ~ringpx]
print('C) composite px (f0 == background): %d px, vs upsample(actual TEX1)*4 over BG: max %.2f mean %.4f LSB' % (dc.shape[0], dc.max(), dc.mean()))
onfig = eq(f0, FIGC)
print('   figure px: %d, all unchanged by glow: %s' % (onfig.sum(), bool((f1[onfig][:, :3] == FIGC).all())))
r1f0 = eq(f0, GOLD); r2f0 = eq(f0, BLUE)
print('   ring px (f0 thin line gold/blue): %d/%d; in glow frame lightened to %s/%s: %s/%s' % (r1f0.sum(), r2f0.sum(), '#%02X%02X%02X' % lr, '#%02X%02X%02X' % lb,
      bool(eq(f1, lr)[r1f0].all()), bool(eq(f1, lb)[r2f0].all())))
print('   figure-1 ring in f0 == ideal ring mask: %s' % bool((r1f0 & reg1 == ring1 & reg1).all()))
# garbage: anything != BG farther than 24 px from any non-background pixel of f0
nonbg = ~eq(f0, BG); dil = nonbg.copy()
for _ in range(24): dil = dil | np.roll(dil, 1, 0) | np.roll(dil, -1, 0) | np.roll(dil, 1, 1) | np.roll(dil, -1, 1)
far = ~dil
print('   far px (>24 px from figures/rings): %d, all exactly BG in f1: %s; glow reach (max dist with f1!=f0 outside fig/ring): see D' % (far.sum(), bool(eq(f1, BG)[far].all())))

# D) end-to-end: sim pipeline from the IDEAL ring (figure 1), same background, gain 4, scale 1, half=True
g, ring = sim.glow(np.array(GOLD) / 255.0, fig1, 4.0, 1.0, True)
exp = (g[..., :3] + bgf * (1 - g[..., 3:4]))
exp[fig1] = np.array(FIGC) / 255; exp[ring] = np.array(lr) / 255
exp8 = np.round(exp * 255)
dd = np.abs(f1[..., :3].astype(float) - exp8)
print('D) final vs sim (float pipeline), figure-1 region: max %d mean %.4f LSB; px off by >2: %d, >4: %d' % (dd[reg1].max(), dd[reg1].mean(), int((dd[reg1].max(-1) > 2).sum()), int((dd[reg1].max(-1) > 4).sum())))
glowmask = reg1 & ~fig1 & ~ring1 & (np.abs(f1[..., :3].astype(int) - np.array(BG)).max(-1) > 0)
ry, rx = np.nonzero(ring1); gy, gx = np.nonzero(glowmask); dmin = np.full(gy.shape, 1e9)
for k in range(0, len(ry), 256):
    dmin = np.minimum(dmin, np.sqrt((gy[:, None] - ry[None, k:k + 256]) ** 2 + (gx[:, None] - rx[None, k:k + 256]) ** 2).min(1))
sg, _ = sim.glow(np.array(GOLD) / 255.0, fig1, 4.0, 1.0, True); sexp = reg1 & ~fig1 & ~ring1 & (np.round(sg[..., 3] * 255) > 0)
print('   glow reach beyond ring: actual max %.1f px (%d px changed); sim: %d px with alpha>0' % (dmin.max(), len(dmin), int(sexp.sum())))
for dist in (1, 2, 3, 4, 6, 8, 10, 12):
    sel = (dmin >= dist - 0.5) & (dmin < dist + 0.5)
    if sel.any():
        v = (f1[gy[sel], gx[sel], :3].astype(float) - np.array(BG)).mean(0)
        e = (exp8[gy[sel], gx[sel]] - np.array(BG)).mean(0)
        print('     dist %2d px from ring: mean (f1-BG) RGB %s   sim %s' % (dist, np.round(v, 1), np.round(e, 1)))

# E) alignment: shift the sim glow field by (sx, sy) px and see which fits the actual frame best
def resample(img, sx, sy):
    j, i = np.mgrid[0:H, 0:W]; return sim.sample(img, (i - sx + 0.5) / W, (j - sy + 0.5) / H)
gm = reg1 & ~fig1 & ~ring1
res = []
for sx in (-1, -0.5, -0.25, 0, 0.25, 0.5, 1):
    for sy in (-1, -0.5, -0.25, 0, 0.25, 0.5, 1):
        gs = resample(g, sx, sy) if (sx or sy) else g
        e = np.round((gs[..., :3] + bgf * (1 - gs[..., 3:4])) * 255)
        res.append((np.abs(f1[..., :3].astype(float) - e)[gm].mean(), sx, sy))
res.sort()
print('E) shift search (mean |diff| in glow area): best %s; (0,0): %.4f; worst %s' % (['(%+.2f,%+.2f)=%.4f' % (sx, sy, m) for m, sx, sy in res[:3]], [m for m, sx, sy in res if sx == 0 and sy == 0][0], '(%+.2f,%+.2f)=%.4f' % (res[-1][1], res[-1][2], res[-1][0])))
def centroid(a, half):
    j, i = np.mgrid[0:a.shape[0], 0:a.shape[1]].astype(float)
    if half: i, j = (i + 0.5) * W / W2 - 0.5, (j + 0.5) * H / H2 - 0.5   # half-res texel centre in full-res pixel coords
    w = a.astype(float); return (w * i).sum() / w.sum(), (w * j).sum() / w.sum()
for nm_, sel0, sel1 in (('figure 1', reg1, reg1[::2, ::2]), ('figure 2', ~reg1, ~reg1[::2, ::2])):
    c0 = centroid(np.where(sel0, t0[..., 3], 0), False); c2 = centroid(np.where(sel1, t2[..., 3], 0), True); c1 = centroid(np.where(sel1, t1[..., 3], 0), True)
    print('   alpha centroid (full-res px) %s: TEX0 (%.3f, %.3f)  TEX2 (%.3f, %.3f)  TEX1 (%.3f, %.3f)  -> shift TEX1-TEX0 (%+.3f, %+.3f)' % (nm_, c0[0], c0[1], c2[0], c2[1], c1[0], c1[1], c1[0] - c0[0], c1[1] - c0[1]))
print('   (figure 2 circle centre (515.3, 250.6); D3D pixel k centre = k)')

# F) blockiness: actual vs sim variants (bilinear vs point-sampled composite upsample)
def point(img, u, v):
    h, w = img.shape[:2]; return img[np.clip(np.floor(v * h).astype(int), 0, h - 1), np.clip(np.floor(u * w).astype(int), 0, w - 1)]
j, i = np.mgrid[0:H, 0:W]
upp = np.clip(point(t1.astype(float) / 255, (i + 0.5) / W, (j + 0.5) / H) * 4, 0, 1)
compp = (upp[..., :3] + bgf * (1 - upp[..., 3:4])) * 255
m = outside & ~ringpx
print('F) composite model error: bilinear upsample %.4f, point-sampled upsample %.4f (mean LSB) -> %s' % (np.abs(f1[..., :3] - comp)[m].mean(), np.abs(f1[..., :3] - compp)[m].mean(),
      'bilinear (no blockiness)' if np.abs(f1[..., :3] - comp)[m].mean() < np.abs(f1[..., :3] - compp)[m].mean() else 'POINT SAMPLING?'))
# 2x2 block artefact: second difference along x at even vs odd columns in the glow area
d2 = np.abs(f1[..., :3].astype(float)[:, 2:] - 2 * f1[..., :3].astype(float)[:, 1:-1] + f1[..., :3].astype(float)[:, :-2]).sum(-1)
gm2 = (gm & outside)[:, 1:-1]
cols = np.arange(1, W - 1)[None, :].repeat(H, 0)
print('   mean |2nd diff| in glow area: even cols %.3f odd cols %.3f (strong asymmetry would indicate 2x2 blocks)' % (d2[gm2 & (cols % 2 == 0)].mean(), d2[gm2 & (cols % 2 == 1)].mean()))
d2s = np.abs(exp8[:, 2:] - 2 * exp8[:, 1:-1] + exp8[:, :-2]).sum(-1)
print('   same for sim: even %.3f odd %.3f' % (d2s[gm2 & (cols % 2 == 0)].mean(), d2s[gm2 & (cols % 2 == 1)].mean()))

# profiles
def prof(y, x0, x1):
    return ' '.join('%3d' % v for v in f1[y, x0:x1, 0]), ' '.join('%3d' % v for v in exp8[y, x0:x1, 0].astype(int))
y = OY + 64
xs = np.nonzero(fig1[y])[0][0]
a, e = prof(y, xs - 16, xs + 2)
print('profile row y=%d (left of head, x %d..%d, red channel; figure starts at x=%d):\n   actual %s\n   sim    %s' % (y, xs - 16, xs + 1, xs, a, e))

# images
crop = (slice(OY + 20, OY + 290), slice(OX + 80, OX + 340))
diff = np.clip(dd * 20, 0, 255).astype(np.uint8)
side = np.concatenate([f1[crop][..., :3], exp8[crop].astype(np.uint8), diff[crop]], 1)
Image.fromarray(side).resize((side.shape[1] * 2, side.shape[0] * 2), Image.NEAREST).save(os.path.join(OUT, '%s_%s_vs_sim.png' % (PRE, FR)))
ref = sim.render((1.0, 0.82, 0.0), 'glow', 4.0, 1.0, True) if False else None
