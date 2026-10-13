# per-angle straight-edge pumping: std over 8 sub-pixel phases of line mass, glow mass, composite mass per unit edge length
import sys, math, json, numpy as np
import lookstudy as LS, tipstudy as S
def circ(r, a0, n=8): return [(r * math.cos(math.radians(a0 + 360.0 * i / n)), r * math.sin(math.radians(a0 + 360.0 * i / n))) for i in range(n)]
OF = dict(S.OFFS); OF.update({'c1.4b': circ(1.4, 0), 'pin8': [(1, .5), (1, -.5), (-1, .5), (-1, -.5), (.5, 1), (-.5, 1), (.5, -1), (-.5, -1)]})
def M(name, ok, line, k, gk, gs='ring'): return (name, OF[ok], line, k, gk, gs)
METH = [M('current', 'cur8', 'stencil', 0, 2.5), M('circ8', 'circ8', 'stencil', 0, 2.5), M('r1x8 k4 gL2.0', 'r1x8', 'post', 4, 2.0, 'line'),
        M('c1.4b k3 gL2.0', 'c1.4b', 'post', 3, 2.0, 'line'), M('pin8 k4 gL2.0', 'pin8', 'post', 4, 2.0, 'line')]
if len(sys.argv) > 1: METH = [m for m in METH if m[0] in sys.argv[1].split(',')]
ANG = (0, 5, 11.25, 18.43, 26.57, 33.75, 40, 45)
res = {}
for m in METH:
    out = {}
    for pat in ('bin', 'ms4'):
        rows = []
        for a in ANG:
            L, G, C = LS.profile(m, pat, a, 8)
            rows.append((L.std(), G.std(), C.std(), C.mean()))
        out[pat] = rows
    res[m[0]] = out
    for pat in ('bin', 'ms4'):
        r = out[pat]
        print('%-15s %s Lstd %s | Gstd %s | Cstd%% %s' % (m[0], pat, ' '.join('%.3f' % x[0] for x in r), ' '.join('%.3f' % x[1] for x in r),
              ' '.join('%.2f' % (100 * x[2] / x[3]) for x in r)), flush=True)
json.dump(res, open('runlook3.json', 'w'), indent=1)
