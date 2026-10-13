# look_images.py - look_compare.png: sim, current vs fix (tent + soft curve in V), gold and shaman blue, no MSAA;
# gpu_delta.png: Wine renders, |frame-to-frame change| (x8) of the glow for a 0.25 px move, old vs fix.
import numpy as np, glowlib as G, gpu_load as L, seq_study as Q, seq_study3 as S3
from PIL import Image
W, H = G.W, G.H
def background():
    y = np.linspace(0, 1, H)[:, None]; x = np.linspace(0, 1, W)[None, :]
    r = 0.30 + 0.10 * y + 0.03 * np.sin(x * 20); g = 0.28 + 0.12 * y; b = 0.22 + 0.05 * y
    bg = np.stack([r * np.ones_like(x), g * np.ones_like(x), b * np.ones_like(x)], -1)
    return np.clip(bg + np.random.default_rng(1).normal(0, 0.02, bg.shape), 0, 1)
def render(col, kw, F, R):
    img = background(); body = np.array([0.55, 0.45, 0.40]); yy = np.linspace(0.7, 1.1, H)[:, None, None]
    figc = body * yy * np.ones((H, W, 1))
    pre = G.pipe(R, quant=True, linear_out=False, **kw) if False else None
    chans = []
    for c in list(col) + [1.0]:
        chans.append(G.pipe(R * c, quant=True, **kw))
    glow = np.stack(chans, -1)
    lc = np.array(col) * 0.625 + 94 / 255.0
    out = glow[..., :3] + img * (1 - glow[..., 3:4])
    Fm = F[..., None]; Rm = R[..., None]
    out = Fm * figc + Rm * lc + np.clip(1 - Fm - Rm, 0, 1) * out
    return (np.clip(out, 0, 1) * 255).astype(np.uint8)
gold = (1.0, 0.82, 0.0); sham = (0.0, 0.44, 0.87)
F, R = G.scene('bin', tx=0.3, ty=0.2)
cur = dict(down='box'); fix = dict(down='tent', vgain=True, curve_mode='soft', gain=5.0)
rows = []
for col in (gold, sham):
    a = render(col, cur, F, R); b = render(col, fix, F, R)
    rows.append(np.concatenate([a, np.full((H, 6, 3), 255, np.uint8), b], 1))
full = np.concatenate([rows[0], np.full((6, rows[0].shape[1], 3), 255, np.uint8), rows[1]], 0)
Image.fromarray(full).save('look_compare.png')
crop = lambda im: im[50:170, 120:330]
z = [np.kron(crop(render(c, k, F, R)), np.ones((3, 3, 1), np.uint8)) for c in (gold,) for k in (cur, fix)]
Image.fromarray(np.concatenate([z[0], np.full((z[0].shape[0], 6, 3), 255, np.uint8), z[1]], 1)).save('look_compare_zoom.png')
# GPU temporal difference: sub_x frames 6 -> 7 (0.25 px move), no MSAA
idx = L.seq_index('sub_x'); k0, k1 = idx[6], idx[7]
tiles = []
for run in ('old_ms0', 'tsv_ms0'):
    g = L.load(run); d = np.abs(g['A'][k1] - g['A'][k0]) * 255
    m = g['clean'][k0] & g['clean'][k1]
    v = np.clip(d * 8 * m, 0, 255).astype(np.uint8)
    tiles.append(np.stack([v, v, v], -1)[40:310, 90:360])
Image.fromarray(np.concatenate([tiles[0], np.full((tiles[0].shape[0], 6, 3), 255, np.uint8), tiles[1]], 1)).save('gpu_delta.png')
print('ok')
