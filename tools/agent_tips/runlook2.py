import sys, math, json, numpy as np
import lookstudy as LS, tipstudy as S
OF = S.OFFS
def M(name, ok, line, k, gk, gs='ring', filt=0.5): return (name, OF[ok], line, k, gk, gs)
METH = [M('current', 'cur8', 'stencil', 0, 2.5)]
for k in (3, 4, 5):
    for gk in (1.7, 2.0, 2.2):
        METH.append(M('r1x8 k%g gL%.1f' % (k, gk), 'r1x8', 'post', k, gk, 'line'))
for gk in (4.0, 5.0):
    METH.append(M('r1x8 k4 gR%.1f' % gk, 'r1x8', 'post', 4, gk, 'ring'))
ANG = (0, 11.25, 22.5, 33.75, 45)
for m in METH:
    Lid = []; Gid = []; sb = []; sm = []
    for a in ANG:
        L, Gm, C = LS.profile(m, 'ideal', a, 4); Lid.append(L.mean()); Gid.append(Gm.mean())
        sb.append(LS.profile(m, 'bin', a)[2].std()); sm.append(LS.profile(m, 'ms4', a)[2].std())
    gp = LS.glow_profile(m)
    print('%-16s line %s mean %.2f | glow %s mean %.2f | Cstd bin %s ms4 %s | glow prof %s' % (m[0], ' '.join('%.2f' % x for x in Lid), np.mean(Lid),
          ' '.join('%.2f' % x for x in Gid), np.mean(Gid), ' '.join('%.3f' % x for x in sb), ' '.join('%.3f' % x for x in sm),
          ' '.join('%.2f' % gp[b][1] for b in range(0, 10))), flush=True)
