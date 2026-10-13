# v2 vs v1 image comparison, alpha check for the A8R8G8B8 RT0 variant, TTFF sensitivity control.
import os, struct
import numpy as np
from PIL import Image
D = '/tmp/claude-0/-home-user-St0nys-WoW-EXE-Patcher/49e16a66-3a63-5e77-ae4f-92ef019273b7/scratchpad/agent_d3d9'
def load(d, pre, n):
    b = open('%s/%s/%s_%s.raw' % (D, d, pre, n), 'rb').read(); w, h = struct.unpack('<II', b[:8])
    return np.frombuffer(b[8:], np.uint8).reshape(h, w, 4)[..., [2, 1, 0, 3]]
def cmp_rgb(a, b):
    d = np.abs(a[..., :3].astype(int) - b[..., :3])
    return 'identical' if d.max() == 0 else 'DIFFER: %d px, max %d' % (int((d.max(-1) > 0).sum()), d.max())
FR = ['f0', 'f1', 'f1b', 'f2', 'f3', 'f4']
print('1) v2 vs v1, X8R8G8B8 backbuffer (RGB):')
for v2d, v1d, v1p in (('out_v2_4x', 'out_4x', 'r4x'), ('out_v2_none', 'out_none', 'r0')):
    res = {f: cmp_rgb(load(v2d, 'r', f), load(v1d, v1p, f)) for f in FR}
    tex = {t: cmp_rgb(load(v2d, 'r', 'f1_' + t), load(v1d, v1p, 'f1_' + t)) + ('' if (load(v2d, 'r', 'f1_' + t)[..., 3] == load(v1d, v1p, 'f1_' + t)[..., 3]).all() else ' (ALPHA DIFFERS)') for t in ('tex0', 'tex2', 'tex1')}
    print('   %-12s frames %s' % (v2d, res))
    print('   %-12s textures %s' % ('', tex))
print('2) A8R8G8B8 render target as RT0 (cleared to alpha 0x40):')
for a8d, refd, refp in (('out_v2_a8_4x', 'out_4x', 'r4x'), ('out_v2_a8_none', 'out_none', 'r0'), ('out_v1_a8_4x', 'out_4x', 'r4x')):
    f0 = load(a8d, 'r', 'f0'); f1 = load(a8d, 'r', 'f1'); ref = load(refd, refp, 'f1')
    a0 = f0[..., 3].astype(int); a1 = f1[..., 3].astype(int)
    glowpx = (np.abs(f1[..., :3].astype(int) - f0[..., :3]).max(-1) > 0) & (a0 == 0x40)    # pixels the composite changed (outside ring/figure)
    print('   %-15s RGB vs v1 X8 run (%s): %s' % (a8d, refd, cmp_rgb(f1, ref)))
    print('   %-15s alpha f1 == alpha f0 (no-glow frame): %s; changed px %d (max alpha there %d); glow-affected px with alpha 0x40: %d of %d' % (
        '', bool((a0 == a1).all()), int((a0 != a1).sum()), int(a1[a0 != a1].max()) if (a0 != a1).any() else 0, int((a1[glowpx] == 0x40).sum()), int(glowpx.sum())))
    vals, cnt = np.unique(a1, return_counts=True)
    print('   %-15s alpha histogram f1: %s' % ('', ', '.join('0x%02X:%d' % (v, c) for v, c in zip(vals, cnt))))
    if a8d == 'out_v1_a8_4x':
        Image.fromarray(np.concatenate([a1.astype(np.uint8), load('out_v2_a8_4x', 'r', 'f1')[..., 3]], 1)).save(D + '/out_v1_a8_4x/alpha_v1_left_v2_right.png')
print('3) TTFF sensitivity control (glow does NOT reset TTFF, texture matrices non-identity) vs v2:')
c = load('out_ctl_ttff_noreset', 'r', 'f1'); v = load('out_v2_4x', 'r', 'f1')
print('   f1 RGB: %s; TEX1: %s' % (cmp_rgb(c, v), cmp_rgb(load('out_ctl_ttff_noreset', 'r', 'f1_tex1'), load('out_v2_4x', 'r', 'f1_tex1'))))
