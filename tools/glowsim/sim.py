# Vorschau des Weichzeichner-Scheins (gleiche Rechenschritte wie der geplante Shader-Ablauf)
import numpy as np, sys
from PIL import Image, ImageDraw
W, H = 360, 300
def figure():
    im = Image.new('L', (W, H), 0); d = ImageDraw.Draw(im)
    cx = W // 2
    d.ellipse([cx-22, 40, cx+22, 88], fill=255)            # Kopf
    d.rounded_rectangle([cx-42, 86, cx+42, 190], 18, fill=255)  # Rumpf
    d.polygon([(cx-42, 95), (cx-78, 175), (cx-64, 182), (cx-34, 120)], fill=255)  # Arm l
    d.polygon([(cx+42, 95), (cx+86, 150), (cx+76, 160), (cx+34, 120)], fill=255)  # Arm r
    d.polygon([(cx-36, 185), (cx-44, 270), (cx-22, 270), (cx-8, 190)], fill=255)  # Bein l
    d.polygon([(cx+36, 185), (cx+40, 270), (cx+18, 270), (cx+8, 190)], fill=255)  # Bein r
    d.polygon([(cx+80, 140), (cx+130, 40), (cx+136, 44), (cx+88, 150)], fill=255)  # Stab
    return np.array(im) > 127
def background():
    y = np.linspace(0, 1, H)[:, None]; x = np.linspace(0, 1, W)[None, :]
    r = 0.30 + 0.10 * y + 0.03 * np.sin(x * 20); g = 0.28 + 0.12 * y; b = 0.22 + 0.05 * y
    bg = np.stack([r * np.ones_like(x), g * np.ones_like(x), b * np.ones_like(x)], -1)
    # Hintergrund-Struktur
    rng = np.random.default_rng(1); bg += rng.normal(0, 0.02, bg.shape)
    return np.clip(bg, 0, 1)
def shift(m, dx, dy):
    o = np.zeros_like(m); ys = slice(max(dy, 0), H + min(dy, 0)); yd = slice(max(-dy, 0), H + min(-dy, 0))
    xs = slice(max(dx, 0), W + min(dx, 0)); xd = slice(max(-dx, 0), W + min(-dx, 0))
    o[ys, xs] = m[yd, xd]; return o
def sample(img, u, v):  # bilinear, clamp, D3D-Texelzentren
    h, w = img.shape[:2]; x = u * w - 0.5; y = v * h - 0.5
    x0 = np.floor(x).astype(int); y0 = np.floor(y).astype(int); fx = (x - x0)[..., None]; fy = (y - y0)[..., None]
    def t(yy, xx): return img[np.clip(yy, 0, h - 1), np.clip(xx, 0, w - 1)]
    return (t(y0, x0) * (1 - fx) * (1 - fy) + t(y0, x0 + 1) * fx * (1 - fy) + t(y0 + 1, x0) * (1 - fx) * fy + t(y0 + 1, x0 + 1) * fx * fy)
WT = (0.2270270, 0.3162162, 0.0702703); OF = (1.3846154, 3.2307692)
def blurpass(src, ow, oh, du, dv, scale=1.0):
    j, i = np.mgrid[0:oh, 0:ow]; u = (i + 0.5) / ow; v = (j + 0.5) / oh
    o1, o2 = OF[0] * scale, OF[1] * scale
    r = sample(src, u, v) * WT[0]
    r += (sample(src, u + du * o1, v + dv * o1) + sample(src, u - du * o1, v - dv * o1)) * WT[1]
    r += (sample(src, u + du * o2, v + dv * o2) + sample(src, u - du * o2, v - dv * o2)) * WT[2]
    return r
def glow(col, fig, gain, scale, half=True, px=2):
    ring = np.zeros_like(fig)
    for dx, dy in [(px, 0), (-px, 0), (0, px), (0, -px), (px, px), (px, -px), (-px, px), (-px, -px)]: ring |= shift(fig, dx, dy)
    ring &= ~fig
    src = np.zeros((H, W, 4)); src[ring] = list(col) + [1.0]
    if half:
        W2, H2 = (W + 1) // 2, (H + 1) // 2
        t1 = blurpass(src, W2, H2, 0, 0)               # verkleinern
        t2 = blurpass(t1, W2, H2, 1.0 / W2, 0, scale)  # waagrecht
        t1 = blurpass(t2, W2, H2, 0, 1.0 / H2, scale)  # senkrecht
    else:
        t2 = blurpass(src, W, H, 1.0 / W, 0, scale); t1 = blurpass(t2, W, H, 0, 1.0 / H, scale)
    j, i = np.mgrid[0:H, 0:W]; g = sample(t1, (i + 0.5) / W, (j + 0.5) / H)
    return np.clip(g * gain, 0, 1), ring
def render(col, mode, gain=3.0, scale=1.0, half=True, light=True):
    fig = figure(); img = background()
    body = np.array([0.55, 0.45, 0.40]); yy = np.linspace(0.7, 1.1, H)[:, None, None]
    img[fig] = (body * yy * np.ones((H, W, 1)))[fig]
    ring = None
    if mode == 'thin':
        _, ring = glow(col, fig, 0, scale)
        img[ring] = col
    else:
        g, ring = glow(col, fig, gain, scale, half)
        m = ~fig
        img[m] = g[m][:, :3] + img[m] * (1 - g[m][:, 3:4])
        c = np.array(col)
        lc = (c * 0.625 + 94 / 255.0) if light else c
        img[ring] = lc
    return (np.clip(img, 0, 1) * 255).astype(np.uint8)
if __name__ == '__main__':
    gold = (1.0, 0.82, 0.0); green = (0.25, 1.0, 0.25); pal = (0.96, 0.55, 0.73); red = (1.0, 0.0, 0.0); sham = (0.0, 0.44, 0.87)
    rows = []
    for col in (gold, sham):
        tiles = [render(col, 'thin'), render(col, 'glow', 3.0, 1.0), render(col, 'glow', 2.0, 0.6), render(col, 'glow', 3.0, 1.0, half=False)]
        rows.append(np.concatenate(tiles, 1))
    out = np.concatenate(rows, 0)
    Image.fromarray(out).save(sys.argv[1] if len(sys.argv) > 1 else 'preview.png')
