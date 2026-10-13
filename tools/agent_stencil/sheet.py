# Builds labelled contact sheets (PNG) from stenciltest.exe output (BMP colour images, .s8 stencil maps).
# usage: python3 -I sheet.py <outdir>
import sys, os
from PIL import Image, ImageDraw
import numpy as np
D = sys.argv[1]
W, H = 256, 160
RING = {1: (255, 209, 0), 2: (0, 160, 255), 3: (255, 64, 255)}

def stencil_img(name, enc):
    s = np.fromfile(os.path.join(D, name + '.s8'), dtype=np.uint8).reshape(H, W)
    out = np.zeros((H, W, 3), np.uint8)
    for v in np.unique(s):
        m = s == v
        v = int(v)
        if v == 0: c = (0, 0, 0)
        elif v == 0xFF: c = (255, 255, 255)
        elif enc == 'phys':
            if v in RING: c = RING[v]
            elif v == 0x80: c = (200, 200, 200)
            elif v & 0x80 and (v & 0x7F) in RING: c = tuple((200 + 2 * x) // 3 for x in RING[v & 0x7F])
            else: c = (255, 0, 0)
        else:
            if v & 0x40 and not v & 0x80 and (v & 0x3F) in RING: c = RING[v & 0x3F]
            elif v < 0x40 and v in RING: c = tuple(x // 3 for x in RING[v])
            elif v == 0xC0: c = (200, 200, 200)
            elif v & 0xC0 == 0xC0 and (v & 0x3F) in RING: c = tuple((200 + 2 * x) // 3 for x in RING[v & 0x3F])
            else: c = (255, 0, 0)
        out[m] = c
    return Image.fromarray(out)

def color_img(name):
    return Image.open(os.path.join(D, name + '.bmp')).convert('RGB')

def sheet(fn, rows, scale=2):
    cw, ch = W * scale, H * scale
    lab = 30
    ncol = max(len(r) for r in rows)
    img = Image.new('RGB', (ncol * (cw + 8) + 8, len(rows) * (ch + lab + 8) + 8), (255, 255, 255))
    dr = ImageDraw.Draw(img)
    for ri, r in enumerate(rows):
        for ci, (kind, name, label) in enumerate(r):
            x = 8 + ci * (cw + 8); y = 8 + ri * (ch + lab + 8)
            try:
                im = color_img(name) if kind == 'c' else stencil_img(name, kind)
            except FileNotFoundError:
                continue
            img.paste(im.resize((cw, ch), Image.NEAREST), (x, y + lab))
            for k, line in enumerate(label.split('\n')):
                dr.text((x, y + 2 + 13 * k), line, fill=(0, 0, 0))
    img.save(os.path.join(D, fn))
    print('wrote', fn, img.size)

g = 'grad_%s_vs_a%d'
# 1: bug A (WPROT 0)
sheet('sheet1_bugA_wprot0.png', [
    [('c', 'w0_%s_REF' % (g % ('DIP', 0)), 'unpatched: colour after later geometry L\n(L = green, depth 0.25 left .. 0.75 right)'),
     ('c', 'w0_%s_CUR_after' % (g % ('DIP', 0)), 'outline10 now (LESS ref WPROT=0), DrawIndexedPrimitive:\nL drawn only where stencil > 0'),
     ('c', 'w0_%s_CUR_after' % (g % ('DP', 0)), 'same with DrawPrimitive\n(state inherited, identical result)'),
     ('c', 'w0_%s_CUR_final' % (g % ('DIP', 0)), 'outline10 now: after post')],
    [('phys', 'w0_%s_CUR_s0' % (g % ('DIP', 0)), 'stencil before L: figure 0x80 grey,\nring 1 gold, ring 2 blue'),
     ('phys', 'w0_%s_P' % (g % ('DIP', 0)), 'probe: where L passes the depth test\n(white)'),
     ('phys', 'w0_%s_S1_s1' % (g % ('DIP', 1)), 'fix S1 (ALWAYS, ZERO), alpha-tested L:\nstencil after L'),
     ('c', 'w0_%s_S1_final' % (g % ('DIP', 1)), 'fix S1, alpha-tested L: after post\n(L complete, outline hidden where L in front)')],
])
# 2: WPROT 1 (A = group member through walls, cat 1 protected; B = target cat 2)
sheet('sheet2_wprot1.png', [
    [('c', 'w1_%s_REF' % (g % ('DIP', 1)), 'WPROT 1, unpatched colour after alpha-tested L\n(A: group member through the wall)'),
     ('c', 'w1_%s_CUR_after' % (g % ('DIP', 1)), 'outline10 now (LESS ref 1):\nL lost on stencil 0 and on ring 1'),
     ('c', 'w1_%s_S1_final' % (g % ('DIP', 1)), 'S1 alone (ALWAYS, ZERO): protected ring 1\nalso cleared where L is in front (wrong)'),
     ('c', 'w1_%s_S2_final' % (g % ('DIP', 1)), 'S2 two passes: ring 1 kept, ring 2 hidden\nwhere L is in front')],
    [('phys', 'w1_%s_S2_s0' % (g % ('DIP', 1)), 'stencil before L (physical encoding)'),
     ('phys', 'w1_%s_S2_s1' % (g % ('DIP', 1)), 'S2: stencil after L'),
     ('U', 'w1_%s_S3_s1' % (g % ('DIP', 1)), 'S3 (U bit): stencil after L\n(dim = covered, U bit cleared)'),
     ('c', 'w1_%s_S3_final' % (g % ('DIP', 1)), 'S3 single pass: after post\n(identical to S2)')],
])
# 3: multipart
sheet('sheet3_multipart.png', [
    [('c', 'mp_w0_DIP_REF', 'multi-part WPROT 0: unpatched\n(L, weapon of B, unit C, second L)'),
     ('c', 'mp_w0_DIP_CUR_final', 'outline10 now: after post'),
     ('c', 'mp_w0_DIP_S1_final', 'S1: after post'),
     ('c', 'mp_w0_DIP_S3_final', 'S3: after post (identical to S1)')],
    [('c', 'mp_w1_DIP_REF', 'multi-part WPROT 1: unpatched'),
     ('c', 'mp_w1_DIP_CUR_final', 'outline10 now: after post'),
     ('c', 'mp_w1_DIP_S2_final', 'S2: after post'),
     ('c', 'mp_w1_DIP_S3_final', 'S3: after post (identical to S2)')],
])
# 4: bug B
sheet('sheet4_bugB.png', [
    [('c', 'bugB_v0_after', 'unpatched: d1 DIP small opaque, d2 DP\ntransparent (no Z write), d3 DP opaque'),
     ('c', 'bugB_v1_after', 'outline10 now: DP not hooked, inherits\nLESS ref 0 from d1 -> d2, d3 lost on stencil 0'),
     ('c', 'bugB_v2_final', 'S1 on DIP only: all drawn, but transparent\nd2 clears the outline under it (after post)'),
     ('c', 'bugB_v3_final', 'S1 on DIP and DP: correct\n(after post)')],
])
