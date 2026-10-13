import sys, math, json, numpy as np
import lookstudy as LS, tipstudy as S, patterns
OF = dict(S.OFFS); OF.update(patterns.P)
def M(name, ok, line, k, gk, gs='ring'): return (name, OF[ok], line, k, gk, gs)
METH = [M('r1x8 k4 gL2.0', 'r1x8', 'post', 4, 2.0, 'line')] + [M('%s k4 gL2.0' % p, p, 'post', 4, 2.0, 'line') for p in ('sq4in4', 'sq4in4d', 'dia4in4', 'sq4in4q')] + [M('dia4in4 k5 gL2.0', 'dia4in4', 'post', 5, 2.0, 'line')]
ANG = (0, 5, 11.25, 18.43, 26.57, 33.75, 40, 45)
for m in METH:
    for pat in ('bin', 'ms4'):
        r = []
        for a in ANG:
            L, G, C = LS.profile(m, pat, a, 8); r.append((L.std(), G.std(), C.std(), C.mean(), L.mean()))
        print('%-17s %s Lmean %s | Cstd%% %s' % (m[0], pat, ' '.join('%.2f' % x[4] for x in r), ' '.join('%.2f' % (100 * x[2] / x[3]) for x in r)), flush=True)
    Lid = [LS.profile(m, 'ideal', a, 4)[0].mean() for a in ANG]; d20 = LS.disc_thickness(m, 20.0)
    print('%-17s ideal line %s mean %.2f disc20 %.2f/%.2f/%.2f' % (m[0], ' '.join('%.2f' % x for x in Lid), np.mean(Lid), *d20), flush=True)
