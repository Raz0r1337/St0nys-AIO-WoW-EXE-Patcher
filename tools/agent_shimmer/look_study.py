# look_study.py - does a variant keep the look? Glow profile across a straight edge (analytic ring, phase-averaged,
# i.e. the average look), plus a preview image like glowsim/vorschau_schein.png.
import sys, numpy as np, glowlib as G, edge_study as E
from PIL import Image
VARS = {'current': dict(down='box'), 'a tent': dict(down='tent'), 'c gain3': dict(down='box', gain=3.0),
        'c soft k2 (gain4 tail)': dict(down='box', curve_mode='soft', gain=4.0), 'c soft k2.5': dict(down='box', curve_mode='soft', gain=5.0),
        'a+c tent soft k2.5': dict(down='tent', curve_mode='soft', gain=5.0), 'b full-res 9tap': dict(down='full', full_sigma=3.6)}
def profile(kw, theta=0.0):
    h, w, x0 = 16, 72, 24.0
    poly, n, c = E.halfplane(theta, 0.0, h, w, x0)
    F, R = G.ring_cov(G.raster([poly], G.pattern('ideal'), h, w))
    base = {k: v for k, v in kw.items() if k in ('down', 'up', 'full_sigma')}
    a = G.curve(G.phase_avg(R, **base), kw.get('curve_mode', 'hard'), kw.get('gain', 4.0))
    row = a[h // 2]; d = np.arange(w) + 0.5 - (x0 + 2)           # distance from the ring's outer edge
    return d, row
if __name__ == '__main__':
    print('%-24s %s' % ('glow alpha at distance d (px) outside the ring, straight edge:', ''))
    print('%-24s ' % 'variant' + ' '.join('%5.1f' % x for x in np.arange(0.5, 12.5, 1.0)) + '   d50   d10  energy')
    for nm, kw in VARS.items():
        d, a = profile(kw)
        m = d > 0; dd = d[m]; aa = a[m]
        d50 = np.interp(0.5, aa[::-1], dd[::-1]); d10 = np.interp(0.1, aa[::-1], dd[::-1])
        print('%-24s ' % nm + ' '.join('%5.2f' % x for x in aa[:12]) + '  %5.1f %5.1f %6.2f' % (d50, d10, aa.sum()))
