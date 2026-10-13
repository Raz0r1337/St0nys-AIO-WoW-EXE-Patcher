import sys, math, json, numpy as np
import lookstudy as LS, tipstudy as S
def circ(r, a0, n=8): return [(r * math.cos(math.radians(a0 + 360.0 * i / n)), r * math.sin(math.radians(a0 + 360.0 * i / n))) for i in range(n)]
OF = dict(S.OFFS); OF.update({'c1a': circ(1.0, 22.5), 'c1.2': circ(1.2, 22.5), 'c1.4': circ(1.4, 22.5), 'c1.4b': circ(1.4, 0), 'c1.2b': circ(1.2, 0), 'c1b': circ(1.0, 0),
    'pin8': [(1, .5), (1, -.5), (-1, .5), (-1, -.5), (.5, 1), (-.5, 1), (.5, -1), (-.5, -1)]})
def M(name, ok, line, k, gk, gs='ring'): return (name, OF[ok], line, k, gk, gs)
METH = [M('current', 'cur8', 'stencil', 0, 2.5), M('circ8', 'circ8', 'stencil', 0, 2.5),
        M('r1x8 k4 gL', 'r1x8', 'post', 4, 1.7, 'line'),
        M('c1a k4 gL', 'c1a', 'post', 4, 1.7, 'line'), M('c1a k3 gL', 'c1a', 'post', 3, 1.7, 'line'),
        M('c1.2 k3 gL', 'c1.2', 'post', 3, 1.7, 'line'), M('c1.4 k2.5 gL', 'c1.4', 'post', 2.5, 1.7, 'line'),
        M('c1.4b k3 gL', 'c1.4b', 'post', 3, 1.7, 'line'), M('c1.2b k3 gL', 'c1.2b', 'post', 3, 1.7, 'line'), M('c1b k4 gL', 'c1b', 'post', 4, 1.7, 'line'),
        M('pin8 k4 gL', 'pin8', 'post', 4, 1.7, 'line')]
if len(sys.argv) > 1: METH = [m for m in METH if m[0] in sys.argv[1].split(',')]
ANG = (0, 11.25, 22.5, 33.75, 45)
res = {}
for m in METH:
    r = {}
    Lid = [LS.profile(m, 'ideal', a, 4)[0].mean() for a in ANG]
    Gid = [LS.profile(m, 'ideal', a, 4)[1].mean() for a in ANG]
    sb = [LS.profile(m, 'bin', a)[2] for a in ANG]; sm = [LS.profile(m, 'ms4', a)[2] for a in ANG]
    d8 = LS.disc_thickness(m, 8.0); d20 = LS.disc_thickness(m, 20.0)
    r = dict(line=Lid, glow=Gid, Cstd_bin=[float(x.std()) for x in sb], Cstd_ms4=[float(x.std()) for x in sm], d8=d8, d20=d20)
    res[m[0]] = r
    print('%-14s line(0..45) %s mean %.2f | glow %s | C std bin %.3f ms4 %.3f | disc8 %.2f/%.2f/%.2f disc20 %.2f/%.2f/%.2f' % (
        m[0], ' '.join('%.2f' % x for x in Lid), np.mean(Lid), ' '.join('%.2f' % x for x in Gid), np.mean(r['Cstd_bin']), np.mean(r['Cstd_ms4']), *d8, *d20), flush=True)
json.dump(res, open('runlook.json', 'w'), indent=1, default=float)
